import json
import logging
import os
import shutil
import threading
import urllib
from datetime import datetime
from pathlib import Path
import platform
from typing import List, Optional

import cryptography.fernet
import pyotp

import cipher_funcs
from dataclasses import dataclass
from appconfig import AppConfig

@dataclass
class Account:
    """ The information that authenticates someone with a provider. """
    issuer: str  # Referred to as "provider" in the GUI.
    label: str
    secret: str # encrypted secret key
    last_used: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    used_frequency: int = 0
    favorite: bool = False
    icon: str = None

    def get_otp_auth_uri(self):
        """ Convert account to otpauth URI """
        decrypted_secret = cipher_funcs.decrypt(self.secret)
        totp = pyotp.TOTP(decrypted_secret)
        uri = totp.provisioning_uri(name=self.label, issuer_name=self.issuer)
        return uri

    def __post_init__(self):
        if self.secret == "":
            raise ValueError("Can't create Account with empty secret.")
        try:
            cipher_funcs.decrypt(self.secret)
        except cryptography.fernet.InvalidToken as e:
            raise ValueError("Can't create Account with plain-text secret.")
        except Exception as e:
            raise (e)

@dataclass(frozen=True)
class OtpRecord:
    """ An OTP record as received from the provider with plain-text secret key """
    issuer: str
    label: str
    secret: str  # plain-text secret key

    def toAccount(self):
        """ Convert to account by encrypting the secret key and adding last used date."""
        encryped_secret = cipher_funcs.encrypt(self.secret)
        return Account(self.issuer, self.label, encryped_secret, "1980-01-01 00:00:00")

# Constant indicates vault data file format
kCurrent_Vault_Version = '1'

class AccountManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AccountManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, filename=None):
        """ Create an account manager using a vault at the given filename """
        if filename is None:
            config = AppConfig()
            # Note: if os_data_dir is absolute, prepending Path.home() has no effect
            # if os_data_dir is '.' it results in path to home directory
            # slash in following line is an operator to join the paths
            self.data_dir = Path.home() / config.get_os_data_dir()
            filename = str(self.data_dir.joinpath("vault.json"))
        # does vault directory exist?  If not, make it.
        if not Path(os.path.dirname(filename)).exists():
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        # Is vault directory writeable?
        if not os.access(os.path.dirname(filename), os.W_OK):
            raise ValueError(f"The directory for the file '{filename}' is not writable.")

        if not hasattr(self, 'initialized'):
            # Configure logging with more detail
            self.logger = logging.getLogger(__name__)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Add file handler for persistent logging
            log_path = Path(os.path.dirname(filename)).joinpath('logs')
            os.makedirs(log_path, exist_ok=True)
            fh = logging.FileHandler(log_path.joinpath('account_manager.log'))
            fh.setFormatter(formatter)
            if not self.logger.hasHandlers():
                self.logger.addHandler(fh)

            # Initialize paths
            self.vault_path = Path.home().joinpath(filename)
            self.backup_path = self.vault_path.with_suffix('.backup.json')
            
            # Track file modification time to detect external changes
            self._last_modified_time = None
            
            # Initialize accounts as None - lazy loading
            self._accounts = None
            self.initialized = True

    def get_accounts(self) -> List['Account']:
        """
        Get the current accounts list, checking for modifications first.
        This is the main method for accessing accounts and should be used
        instead of directly accessing self._accounts.
        @return list of Accounts
        """
        # First load if needed (lazy loading)
        if self._accounts is None:
            self._accounts = self._load_accounts_from_disk()
            return self._accounts
        
        # Check for external modifications
        if self.vault_path.exists():
            current_mtime = os.path.getmtime(self.vault_path)
            if self._last_modified_time and current_mtime != self._last_modified_time:
                self.logger.info("Detected external modifications to vault file")
                self._accounts = self._handle_external_modification()
        
        return self._accounts

    def set_accounts(self, account_string):
        """Set accounts from a string - dependency injection for testing
        @param account_string is JSON string of vault data"""
        content = json.loads(account_string)
        self._accounts = [Account(**acc) for acc in content]
        self.save_accounts()
        self.logger.debug(f"Saved accounts : {account_string} ")

    def _load_accounts_from_disk(self) -> List['Account']:
        """
        Load accounts from vault with validation and backup recovery.
        This is a private method that should be called by get_accounts()
        or other methods that need to load accounts directly from disk.

        This method loads accounts from the vault file into the account manager.

        Returns:
            list of accounts (may be empty)

        Raises:
            Exception: If any error occurs during the loading process.
        """

        try:
            if not self.vault_path.exists():
                self.logger.info(f"Vault file not found at {self.vault_path}")
                return []

            # Read and validate primary vault
            with open(self.vault_path, 'r') as f:
                content = json.load(f)
                if not self._validate_vault_data(content):
                    raise ValueError("Invalid vault format (wrong version?)")
                # Assign the content to the account list
                accounts = [Account(**acc) for acc in content["vault"]["entries"]]
                self._last_modified_time = os.path.getmtime(self.vault_path)
                return accounts

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Error loading vault: {str(e)}")
            return self._recover_from_backup()
        except Exception as e:
            self.logger.error(f"Unexpected error loading vault: {str(e)}")
            return []

    def save_accounts(self) -> bool:
        """
        Save all accounts to the vault.

        This method saves all accounts in the account manager to the vault file.

        Returns:
            bool: True if the accounts were saved successfully, False otherwise.

        Raises:
            Exception: If any error occurs during the saving process.
        """
        # Create temporary file path for atomic write
        temp_path = self.vault_path.with_suffix('.tmp')
        try:
            if not os.path.exists(os.path.dirname(self.vault_path)):
                os.makedirs(os.path.dirname(self.vault_path), exist_ok=True)

            # Ensure we have the latest accounts
            accounts = self.get_accounts()
            
            # Prepare the header string.
            vault_content = {
                "vault": {
                    "version": "1",
                    "entries": []
                        }
            }

            # First write to temporary file
            with open(temp_path, 'w') as f:
                account_data = [acc.__dict__ for acc in accounts]
                vault_content["vault"]["entries"] = account_data
                json.dump(vault_content, f, indent=2)

            # Magic number for length of string in a vault file with no entries
            empty_vault_size = 58
            # Create backup of current file if it exists AND has at least one entry.
            if self.vault_path.exists() and os.path.getsize(self.vault_path) > empty_vault_size:
                shutil.copy2(self.vault_path, self.backup_path)

            # Atomic rename of temporary file to actual file
            os.replace(temp_path, self.vault_path)
            self._last_modified_time = os.path.getmtime(self.vault_path)
            
            self.logger.debug("Successfully saved accounts")
            return True

        except (PermissionError, OSError) as e:
            self.logger.error(f"Permission or OS error while saving accounts: {str(e)}")
            try:
                if temp_path.exists():
                    os.remove(temp_path)
            except (PermissionError, OSError):
                # If cleanup fails, just log it
                self.logger.warning(f"Could not clean up temporary file: {temp_path}")
            return False

        except Exception as e:
            self.logger.error(f"Unexpected error while saving accounts: {str(e)}")
            try:
                if temp_path.exists():
                    os.remove(temp_path)
            except (PermissionError, OSError):
                self.logger.warning(f"Could not clean up temporary file: {temp_path}")
            return False

    def save_new_account(self, otp_record) -> bool:
        """
        Save a new account with duplicate checking.

        This method saves a new account to the account manager after checking for duplicates.
        It encrypts the secret key before saving and logs the operation.

        Args:
            otp_record (OtpRecord): The OTP record containing account details to be saved.

        Returns:
            bool: True if the account was saved successfully, False if a duplicate account exists.

        Raises:
            RuntimeError: If the account could not be saved to the vault.
            Exception: If any other error occurs during the saving process.
        """
        try:
            # Get latest accounts and check for duplicates
            accounts = self.get_accounts()
            if any(
                acc.issuer == otp_record.issuer and acc.label == otp_record.label
                for acc in accounts
            ):
                return False

            encrypted_secret = cipher_funcs.encrypt(otp_record.secret)
            account = Account(
                issuer=otp_record.issuer,
                label=otp_record.label,
                secret=encrypted_secret,
                # Note: default values for remaining fields are provided in dataclass
            )

            self._accounts.insert(0, account)
            if self.save_accounts():
                self.logger.debug(f"Successfully saved new account: {otp_record.issuer} ({otp_record.label})")
            else:
                raise RuntimeError("Failed to save account to vault")

            return True
        except Exception as e:
            self.logger.error(f"Error saving new account: {str(e)}")
            raise

    def update_account(self, index, account):
        """
        Update an existing account in the account manager.

        This method updates an existing account with new details and saves the updated list to the vault.

        Args:
            index: The index of the existing account to be updated.
            account (Account): The new account details to replace the old account.

        Returns:
            bool: True if the account was updated successfully, False if it's a duplicate account

        Raises:
            Exception: If any error occurs during the update process.
        """
        # Get latest accounts
        accounts = self.get_accounts()
        
        # Check for duplicates
        for item, acc in enumerate(accounts):
            # does info match and is it not me?
            if acc.issuer == account.issuer and acc.label == account.label and item != index:
                return False
                
        self._accounts[index] = account
        self.save_accounts()
        self.logger.debug(f"Updated account: {account.issuer} ({account.label})")
        return True

    def delete_account(self, account):
        """
        Delete an account from the account manager.

        This method deletes an account from the account manager and saves the updated list to the vault.

        Args:
            account (Account): The account to be deleted.

        Returns:
            bool: True if the account was deleted successfully, False otherwise.

        Raises:
            Exception: If any error occurs during the deletion process.
        """
        # Get latest accounts
        accounts = self.get_accounts()
        
        self._accounts.remove(account)
        self.save_accounts()
        self.logger.debug(f"Deleted account: {account.issuer} ({account.label})")

    # Update any method that directly accessed self.accounts to use get_accounts() instead
    # For example:
    def sort_alphabetically(self):
        """
        Sort the accounts alphabetically by issuer.
        """
        self._accounts = sorted(self.get_accounts(), key=lambda x: x.issuer)
        self.save_accounts()
        self.logger.debug(f"Accounts sorted alphabetically.")

    def sort_recency(self):
        """
        Sort the accounts by most recently used.
        """
        self._accounts = sorted(self.get_accounts(), key=lambda x: x.last_used, reverse=True)
        self.save_accounts()
        self.logger.debug(f"Accounts sorted by recently used.")

    def sort_frequency(self):
        """
        Sort the accounts by most frequently used.
        """
        self._accounts = sorted(self.get_accounts(), key=lambda x: x.used_frequency, reverse=True)
        self.save_accounts()
        self.logger.debug(f"Accounts sorted by used frequency.")

    def backup_accounts(self, file_path):
        """ Store the accounts in the given file path with encrypted secret keys.
            The file is in JSON format.
        """
        self.write_accounts_file(file_path, 'json')

    def export_accounts(self, file_path, desired_format):
        """ Store the accounts in the given file path with plain-text secret keys.
            @param desired_format is 'json' or 'uri'
        """
        self.write_accounts_file(file_path, desired_format, use_encrypted_keys=False)

    def write_accounts_file(self, file_path, desired_format='json', use_encrypted_keys=True):
        """Store the accounts in the desired_format in the given file_path.
          Accounts in the vault are encrypted.
            1. For backup they need no special treatment before writing.
            2. for export, they need to be decrypted before writing.
         Note that vault format includes version number, backup / export does not.
         @param file_path location of file
         @param desired_format 'json' or 'uri'
         @param use_encrypted_keys before writing accounts to the file. (False for exporting which wants decrypted keys)
         """
        # Create a label for logging and error messages appropriate to mode
        target_label = "Export"
        if use_encrypted_keys:
            target_label = "Backup"

        vault_accounts = []

        # Check if accounts exist and are iterable
        if not self.get_accounts():
            self.logger.error(f"Internal error: No accounts to {target_label}. 'self.accounts' is not a list.")
            return

        # Convert accounts to plaintext
        uri_list = ""
        for account in self.get_accounts():
            # Expects encrypted keys that it converts to plain URI
            uri_list += account.get_otp_auth_uri() + "\n"  # convert to URI and append to string
            try:
                # turn the Account object into a dictionary so it can be serialized by json.dump
                vault_account = account.__dict__.copy()
                # Export mode wants plain-text keys
                if not use_encrypted_keys:
                    vault_account['secret'] = cipher_funcs.decrypt(account.secret)
                vault_accounts.append(vault_account)
            except AttributeError as e:
                self.logger.error(f"Error processing account {account}: Missing required attribute - {e}")
                continue  # Skip this account, but continue with the others
            except Exception as e:
                self.logger.error(f"Failed to decrypt secret for account {account}: {e}")
                continue  # Skip this account, but continue with the others

        # Ensure the file path is valid
        if not os.path.dirname(file_path) or not os.access(os.path.dirname(file_path), os.W_OK):
            self.logger.error("invalid file path")
            raise OSError(8675309,"invalid file path")
        # If the file already exists, ensure the file is writeable
        if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
            self.logger.error("File is read-only.")
            raise OSError(8675309,"File is read-only.")

        # Convert accounts to string
        if desired_format == 'json':
            result = json.dumps(vault_accounts, indent=4)
        else:
            result = uri_list

        # Dump the string to a file
        try:
            with open(file_path, 'w') as f:
                f.write(result)
            self.logger.debug(f"Successful {target_label} of {len(vault_accounts)} accounts to {file_path}")
        except (OSError, IOError) as e:
            self.logger.error(f"{target_label} failed to write to {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during {target_label}: {e}")

    def restore_accounts(self, file_path):
        """Read the accounts from the given file_path. Autodetect file type.
           """
        self.read_accounts_file(file_path, import_mode=False)

    def import_accounts(self, file_path):
        """Read the accounts from the given file_path. Autodetect file type.
           Secret keys from a plain-text file are encrypted before being put in the vault.
           """
        return self.read_accounts_file(file_path, import_mode=True)
    
    def import_preview(self, file_path):
        """Read the accounts from the given file_path. Autodetect file type.
           Secret keys from a plain-text file are encrypted before being put in the vault.
           return the accounts so they can be displayed as a preview.
           """
        return self.read_accounts_file(file_path, import_mode=True, preview=True)

    def read_accounts_file(self, file_path, import_mode=False, preview=False):
        """Read the accounts from the given file_path. Autodetect file type.
          Accounts in the vault are encrypted.
            1. for restore, the accounts from the file need no encryption.
            2. for import, the accounts from the file need to be encrypted.
         @param file_path location of file
         @param import_mode encrypt the keys before rebuilding the accounts."""
        self.logger.debug("Starting read_accounts_file")
        target = "Restore"
        if import_mode:
            target = "Import"

        if not os.path.isfile(file_path):
            self.logger.error(f"{target} file {file_path} does not exist.")
            return -1

        try:
            with open(file_path, 'r') as f:
                first_line = f.readline().strip()
                f.seek(0)  # Reset file pointer to the beginning

                if first_line.startswith('otpauth'):
                    # Parse URIs
                    uris = f.readlines()
                    accounts = self.parse_uris(uris)
                else:
                    # Parse JSON
                    accounts_data = json.load(f)
                    accounts = self.parse_json(accounts_data, import_mode)

            if preview:
                return accounts

            # Update the active accounts from the restored data
            self._accounts = accounts
            self.logger.debug(f"Updating active accounts from restored data")
            self.save_accounts()
            self.logger.debug(f"Read completed for  {len(accounts)} accounts from {file_path}")
            self.logger.debug(self._accounts)

            self.logger.debug(f"Successful {target} of accounts from {file_path}")

        except (OSError, IOError) as e:
            self.logger.error(f"{target} failed to read from {file_path}: {e}")
            return -2
        except json.JSONDecodeError as e:
            self.logger.error(f"{target} failed to parse JSON from {file_path}: {e}")
            return -3
        except ValueError as e:
            self.logger.error(f"{target} failed to parse URI data from {file_path}: {e}")
            return -4
        except Exception as e:
            self.logger.error(f"Unexpected error during {target}: {e}")
            return -5

    def parse_uris(self, uris):
        """ (Helper method) Parse URIs and return account objects
        """
        accounts = []
        for uri in uris:
            # Parse each URI and create account objects
            try:
                totp_obj = pyotp.parse_uri(uri.strip())
            except ValueError as e:
                self.logger.warning(f"URI parsing failure during import.  Item {uri.strip()}.  Error {e}")
                raise e  # abort on parse error
            encrypted_secret = cipher_funcs.encrypt(totp_obj.secret)
            account = Account(totp_obj.issuer, totp_obj.name, encrypted_secret)
            accounts.append(account)
        return accounts

    def parse_json(self, accounts_data, import_mode):
        """ (Helper method) Parse JSON and return account objects
        """
        restored_accounts = []
        for json_account in accounts_data:
            try:
                # Assuming decrypted_account has the same structure as the original account
                # Restore will leave the secret encrypted
                # An Imported file has plaintext keys that must be encrypted before constructing the accounts
                secret_key = json_account['secret']
                if import_mode:
                    secret_key = cipher_funcs.encrypt(json_account['secret'])
                # required fields
                restored_account = Account(json_account['issuer'],json_account['label'],secret_key)
                # optional fields
                if 'last_used' in json_account:
                    restored_account.last_used = json_account['last_used']
                if 'used_frequency' in json_account:
                    restored_account.used_frequency = json_account['used_frequency']
                if 'favorite' in json_account:
                    restored_account.favorite = json_account['favorite']
                if 'icon' in json_account:
                    restored_account.icon = json_account['icon']

                restored_accounts.append(restored_account)

            except KeyError as e:
                self.logger.error(f"Missing expected key in account data: {e}")
            except Exception as e:
                self.logger.error(f"Failed to read account from data {json_account}: {e}")
        return restored_accounts


    def _handle_external_modification(self) -> List['Account']:
        """
        Handle detected external modifications to the vault file.
        Returns merged accounts list.
        """
        self.logger.debug("Attempting to load external changes")
        try:
            # Load both current memory state and disk state with correct structure
            with open(self.vault_path, 'r') as f:
                disk_content = json.load(f)
                if not self._validate_vault_data(disk_content):
                    raise ValueError("Invalid vault format in external modifications")
                    
                disk_accounts = {
                    self._account_key(acc): Account(**acc)
                    for acc in disk_content["vault"]["entries"]
                }
                self._last_modified_time = os.path.getmtime(self.vault_path)
                self.logger.debug("Successfully read external changes")
                return list(disk_accounts.values())

            # memory_accounts = {
            #     self._account_key(acc.__dict__): acc
            #     for acc in self._accounts
            # }
            # self.logger.debug(f"memory: {memory_accounts}")
            # self.logger.debug(f"disk: {disk_accounts}")
            #
            # # Merge changes, preferring memory state for conflicts
            # merged = {**disk_accounts, **memory_accounts}
            # merged_accounts = list(merged.values())
            #
            # # Update the modified time
            # self._last_modified_time = os.path.getmtime(self.vault_path)
            #
            # self.logger.debug("Successfully merged external changes")
            # return merged_accounts

        except Exception as e:
            self.logger.error(f"Failed to handle external modifications: {str(e)}")
            return self._recover_from_backup()

    def _recover_from_backup(self) -> List['Account']:
        """
        Attempt to recover accounts from backup file.
        """
        self.logger.debug("Attempting recovery from backup")
        try:
            if self.backup_path.exists():
                with open(self.backup_path, 'r') as f:
                    content = json.load(f)
                    if self._validate_vault_data(content):
                        self.logger.debug("Successfully recovered from backup")
                        return [Account(**acc) for acc in content['vault']['entries']]

            self.logger.error("No valid backup found for recovery")
            return []

        except Exception as e:
            self.logger.error(f"Failed to recover from backup: {str(e)}")
            return []

    @staticmethod
    def _validate_vault_data(content: list) -> bool:
        """
        Validate account data structure.
        """

        if "vault" in content:
            if "version" in content['vault']:
                if content['vault']['version'] == kCurrent_Vault_Version:
                    if "entries" in content["vault"]:
                        # Detected vaultv1 format
                        accounts_data = content["vault"]["entries"]
        else:
            print("ERROR - Vault data not in correct format.")
            return False

        required_fields = {'issuer', 'label', 'secret', 'last_used', 'used_frequency', 'favorite', 'icon'}
        for acct in accounts_data:
            if not isinstance(acct, dict):
                return False
            for field in required_fields:
                if field not in acct:
                    return False
            # Verify the secret can be decrypted
            try:
                cipher_funcs.decrypt(acct['secret'])
            except cryptography.fernet.InvalidToken as e:
                print (f"Found invalid secret loading accounts for {acct['issuer']}")
                print (e)
                return False
        return True

    @staticmethod
    def _account_key(account: dict) -> str:
        """Generate unique key for account used to detect external modification """
        return f"{account['issuer']}:{account['label']}"


    @staticmethod
    def duplicate_accounts(accounts):
        """ Return a copy of the accounts."""
        list_copy = []
        for item in accounts:
            newitem = Account(
                issuer=item.issuer,
                label=item.label,
                secret=item.secret,
                last_used=item.last_used,
                used_frequency=item.used_frequency,
                favorite=item.favorite,
                icon=item.icon
            )
            list_copy.append(newitem)
        return list_copy

if __name__ == '__main__':
    am = AccountManager()
