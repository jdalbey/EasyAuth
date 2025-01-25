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
        encryped_secret = cipher_funcs.encrypt(self.secret)
        return Account(self.issuer, self.label, encryped_secret, "1980-01-01 00:00:00")


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
        if filename is None:
            config = AppConfig()
            self.data_dir = Path.home() / config.get_os_data_dir()
            filename = str(self.data_dir.joinpath("vault.json"))
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
            
            # Load accounts with validation
            self.accounts = self.load_accounts()
            self.initialized = True

    def set_accounts(self,account_string):
        """Set accounts from a string - dependency injection for testing
        @param account_string is JSON string of vault data"""
        content = json.loads(account_string)
        self.accounts = [Account(**acc) for acc in content]
        self.save_accounts()
        self.logger.info(f"Saved accounts : {account_string} ")

    def load_accounts(self) -> List['Account']:
        """Load accounts from vault with validation and backup recovery."""
        try:
            if not self.vault_path.exists():
                self.logger.warning(f"Vault file not found at {self.vault_path}")
                return []

            # Check for external modifications
            current_mtime = os.path.getmtime(self.vault_path)
            if self._last_modified_time and current_mtime != self._last_modified_time:
                self.logger.warning("Detected external modifications to vault file")
                self._handle_external_modification()

            # Read and validate primary vault
            with open(self.vault_path, 'r') as f:
                content = json.load(f)
                if not self._validate_account_data(content):
                    raise ValueError("Invalid account data format")
                # Assign the content to the account list
                accounts = [Account(**acc) for acc in content]
                self._last_modified_time = current_mtime
                return accounts

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Error loading vault: {str(e)}")
            return self._recover_from_backup()
        except Exception as e:
            self.logger.error(f"Unexpected error loading vault: {str(e)}")
            return []

    def save_accounts(self) -> bool:
        """Save accounts with atomic write and backup creation."""
        # Create temporary file path for atomic write
        temp_path = self.vault_path.with_suffix('.tmp')
        try:
            if not os.path.exists(os.path.dirname(self.vault_path)):
                os.makedirs(os.path.dirname(self.vault_path), exist_ok=True)

            # First write to temporary file
            with open(temp_path, 'w') as f:
                account_data = [acc.__dict__ for acc in self.accounts]
                json.dump(account_data, f, indent=2)

            # Create backup of current file if it exists
            if self.vault_path.exists():
                shutil.copy2(self.vault_path, self.backup_path)

            # Atomic rename of temporary file to actual file
            os.replace(temp_path, self.vault_path)
            self._last_modified_time = os.path.getmtime(self.vault_path)
            
            self.logger.info("Successfully saved accounts")
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
        """Save new account with duplicate checking."""
        try:
            # Check for duplicates
            if any(
                acc.issuer == otp_record.issuer and acc.label == otp_record.label
                for acc in self.accounts
            ):
                #raise ValueError("Account with same provider and label already exists")
                return False

            encrypted_secret = cipher_funcs.encrypt(otp_record.secret)
            account = Account(
                issuer=otp_record.issuer,
                label=otp_record.label,
                secret=encrypted_secret,
                last_used=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            self.accounts.insert(0, account)
            if self.save_accounts():
                self.logger.info(f"Successfully saved new account: {otp_record.issuer} ({otp_record.label})")
            else:
                raise RuntimeError("Failed to save account to vault")

            return True
        except Exception as e:
            self.logger.error(f"Error saving new account: {str(e)}")
            raise

    def update_account(self, index, account):
        self.accounts[index] = account
        self.save_accounts()
        self.logger.info(f"Updated account: {account.issuer} ({account.label})")

    def delete_account(self, account):
        self.accounts.remove(account)
        self.save_accounts()
        self.logger.info(f"Deleted account: {account.issuer} ({account.label})")

    def sort_alphabetically(self):
        self.accounts = sorted(self.accounts, key=lambda x: x.issuer)
        self.save_accounts()
        self.logger.info(f"Accounts sorted alphabetically.")

    def sort_recency(self):
        self.accounts = sorted(self.accounts, key=lambda x: x.last_used, reverse=True)
        self.save_accounts()
        self.logger.info(f"Accounts sorted by recently used.")

    def sort_frequency(self):
        self.accounts = sorted(self.accounts, key=lambda x: x.used_frequency, reverse=True)
        self.save_accounts()
        self.logger.info(f"Accounts sorted by used frequency.")

    def backup_accounts(self, file_path):
        self.write_accounts_file(file_path, 'json')
    def export_accounts(self, file_path, desired_format):
        self.write_accounts_file(file_path, desired_format, use_encrypted_keys=False)
    def write_accounts_file(self, file_path, desired_format='json', use_encrypted_keys=True):
        """Store the accounts in the desired_format in the given file_path.
          Accounts in the vault are encrypted.
            1. For backup they need no special treatment before writing.
            2. for export, they need to be decrypted before writing.
         @param file_path location of file
         @param desired_format 'json' or 'uri'
         @param use_encrypted_keys before writing accounts to the file. (False for exporting which wants decrypted keys)"""
        # Create a label for logging and error messages appropriate to mode
        target_label = "Export"
        if use_encrypted_keys:
            target_label = "Backup"

        vault_accounts = []

        # Check if accounts exist and are iterable
        if not hasattr(self, 'accounts') or not isinstance(self.accounts, list):
            self.logger.error(f"Internal error: No accounts to {target_label}. 'self.accounts' is not a list.")
            return

        # Convert accounts to plaintext
        uri_list = ""
        for account in self.accounts:
            try:
                # turn the Account object into a dictionary so it can be serialized by json.dump
                vault_account = account.__dict__.copy()
                # Export mode wants plain-text keys
                if not use_encrypted_keys:
                    vault_account['secret'] = cipher_funcs.decrypt(account.secret)
                    if desired_format == 'uri':
                        # Convert account to URI and append to string
                        # Expects encrypted keys that it converts to plain URI
                        uri_list += account.get_otp_auth_uri() + "\n"  # convert to URI and append to string
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
            self.logger.info(f"Successful {target_label} of {len(vault_accounts)} accounts to {file_path}")
        except (OSError, IOError) as e:
            self.logger.error(f"{target_label} failed to write to {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during {target_label}: {e}")

    def restore_accounts(self, file_path):
        self.read_accounts_file(file_path, import_mode=False)
    def import_accounts(self, file_path):
        self.read_accounts_file(file_path, import_mode=True)
    def import_preview(self, file_path):
        return self.read_accounts_file(file_path, import_mode=True, preview=True)
    # def read_accounts_file(self, file_path, import_mode=False, preview=False):
    #     """Read the accounts from the given file_path.
    #       Accounts in the vault are encrypted.
    #         1. for restore, the accounts from the file need no encryption.
    #         2. for import, the accounts from the file need to be encrypted.
    #      @param file_path location of file
    #      @param import_mode encrypt the keys before rebuilding the accounts."""
    #     self.logger.debug("Starting read_accounts_file")
    #     target = "Restore"
    #     if import_mode:
    #         target = "Import"
    #
    #     if not os.path.isfile(file_path):
    #         self.logger.error(f"{target} file {file_path} does not exist.")
    #         return
    #
    #     try:
    #         with open(file_path, 'r') as f:
    #             json_accounts = json.load(f)
    #     except (OSError, IOError) as e:
    #         self.logger.error(f"Failed to read {target} file {file_path}: {e}")
    #         return
    #     except json.JSONDecodeError as e:
    #         self.logger.error(f"Failed to decode JSON from {target} file {file_path}: {e}")
    #         return
    #
    #     # Validate and restore each account
    #     restored_accounts = []
    #     for json_account in json_accounts:
    #         try:
    #             # Assuming decrypted_account has the same structure as the original account
    #             # Restore will leave the secret encrypted
    #             # An Imported file has plaintext keys that must be encrypted before constructing the accounts
    #             secret_key = json_account['secret']
    #             if import_mode:
    #                 secret_key = cipher_funcs.encrypt(json_account['secret'])
    #             restored_account = Account(json_account['issuer'],json_account['label'],secret_key,json_account['last_used'])
    #
    #             restored_accounts.append(restored_account)
    #
    #         except KeyError as e:
    #             self.logger.error(f"Missing expected key in account data: {e}")
    #         except Exception as e:
    #             self.logger.error(f"Failed to read account from data {json_account}: {e}")
    #
    #     if preview:
    #         return restored_accounts
    #     # Assuming self.accounts is where you want to store the restored accounts
    #     self.accounts = restored_accounts
    #     self.logger.debug(f"Read these accounts: {self.accounts}")
    #     self.save_accounts()
    #     self.logger.info(f"Read completed for  {len(restored_accounts)} accounts from {file_path}")
    #     self.logger.info(self.accounts)

    def read_accounts_file(self, file_path, import_mode=False, preview=False):
        """Read the accounts from the given file_path.
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
            return

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
            self.accounts = accounts
            self.logger.debug(f"Read these accounts: {self.accounts}")
            self.save_accounts()
            self.logger.info(f"Read completed for  {len(accounts)} accounts from {file_path}")
            self.logger.info(self.accounts)

            self.logger.info(f"Successful {target} of accounts from {file_path}")

        except (OSError, IOError) as e:
            self.logger.error(f"{target} failed to read from {file_path}: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"{target} failed to parse JSON from {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during {target}: {e}")

    def parse_uris(self, uris):
        # parse URIs and return account objects
        accounts = []
        for uri in uris:
            # Parse each URI and create account objects
            try:
                totp_obj = pyotp.parse_uri(uri.strip())
            except ValueError as e:
                self.logger.warning(f"URI parsing failure during import.  Item {uri.strip()}.  Error {e}")
                #TODO: handle this error somehow.  Report count of parse failures?  Stop import?
                continue  # skip invalid URI's
            encrypted_secret = cipher_funcs.encrypt(totp_obj.secret)
            account = Account(totp_obj.issuer, totp_obj.name, encrypted_secret)
            accounts.append(account)
        return accounts

    def parse_json(self, accounts_data, import_mode):
        # parse JSON data and return account objects
        restored_accounts = []
        for json_account in accounts_data:
            try:
                # Assuming decrypted_account has the same structure as the original account
                # Restore will leave the secret encrypted
                # An Imported file has plaintext keys that must be encrypted before constructing the accounts
                secret_key = json_account['secret']
                if import_mode:
                    secret_key = cipher_funcs.encrypt(json_account['secret'])
                restored_account = Account(json_account['issuer'],json_account['label'],secret_key,json_account['last_used'])

                restored_accounts.append(restored_account)

            except KeyError as e:
                self.logger.error(f"Missing expected key in account data: {e}")
            except Exception as e:
                self.logger.error(f"Failed to read account from data {json_account}: {e}")
        return restored_accounts



    def _handle_external_modification(self):
        """Handle detected external modifications to the vault file."""
        self.logger.warning("Attempting to merge external changes")
        try:
            # Load both current memory state and disk state
            with open(self.vault_path, 'r') as f:
                disk_content = json.load(f)
                disk_accounts = {
                    self._account_key(acc): Account(**acc)
                    for acc in disk_content
                }

            memory_accounts = {
                self._account_key(acc.__dict__): acc
                for acc in self.accounts
            }

            # Merge changes, preferring memory state for conflicts
            merged = {**disk_accounts, **memory_accounts}
            self.accounts = list(merged.values())
            self.logger.info("Successfully merged external changes")

        except Exception as e:
            self.logger.error(f"Failed to handle external modifications: {str(e)}")
            self._recover_from_backup()

    def _recover_from_backup(self) -> List['Account']:
        """Attempt to recover accounts from backup file."""
        self.logger.info("Attempting recovery from backup")
        try:
            if self.backup_path.exists():
                with open(self.backup_path, 'r') as f:
                    content = json.load(f)
                    if self._validate_account_data(content):
                        self.logger.info("Successfully recovered from backup")
                        return [Account(**acc) for acc in content]

            self.logger.error("No valid backup found for recovery")
            return []

        except Exception as e:
            self.logger.error(f"Failed to recover from backup: {str(e)}")
            return []

    @staticmethod
    def _validate_account_data(content: list) -> bool:
        """Validate account data structure."""
        required_fields = {'issuer', 'label', 'secret', 'last_used'}
        for acct in content:
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
        list_copy = []
        for item in accounts:
            newitem = Account(
                issuer=item.issuer,
                label=item.label,
                secret=item.secret,
                last_used=item.last_used
            )
            list_copy.append(newitem)
        return list_copy

if __name__ == '__main__':
    am = AccountManager()