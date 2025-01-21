import json
import logging
import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import cipher_funcs
from dataclasses import dataclass

# TODO: Disambiguate - sometimes secret is used as the shared key and sometimes as the encrypted key.

@dataclass
class Account:
    provider: str
    label: str
    secret: str
    last_used: str


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
            filename = str(Path.home() / ".var/app/org.redpoint.EasyAuth/data/vault.json")
        if not os.access(os.path.dirname(filename), os.W_OK):
            raise ValueError(f"The directory for the file '{filename}' is not writable.")

        if not hasattr(self, 'initialized'):
            # Configure logging with more detail
            self.logger = logging.getLogger(__name__)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Add file handler for persistent logging
            log_path = Path.home().joinpath('.var/app/org.redpoint.EasyAuth/logs')
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

    def save_new_account(self, provider: str, label: str, secret: str) -> bool:
        """Save new account with duplicate checking."""
        try:
            # Check for duplicates
            if any(
                acc.provider == provider and acc.label == label 
                for acc in self.accounts
            ):
                #raise ValueError("Account with same provider and label already exists")
                return False

            encrypted_secret = cipher_funcs.encrypt(secret)
            account = Account(
                provider=provider,
                label=label,
                secret=encrypted_secret,
                last_used=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            self.accounts.insert(0, account)
            if self.save_accounts():
                self.logger.info(f"Successfully saved new account: {provider} ({label})")
            else:
                raise RuntimeError("Failed to save account to vault")

            return True
        except Exception as e:
            self.logger.error(f"Error saving new account: {str(e)}")
            raise

    def update_account(self, index, account):
        self.accounts[index] = account
        self.save_accounts()
        self.logger.info(f"Updated account: {account.provider} ({account.label})")

    def delete_account(self, account):
        self.accounts.remove(account)
        self.save_accounts()
        self.logger.info(f"Deleted account: {account.provider} ({account.label})")

    def sort_alphabetically(self):
        self.accounts = sorted(self.accounts, key=lambda x: x.provider)
        self.save_accounts()
        self.logger.info(f"Accounts sorted alphabetically.")

    def sort_recency(self):
        self.accounts = sorted(self.accounts, key=lambda x: x.last_used, reverse=True)
        self.save_accounts()
        self.logger.info(f"Accounts sorted by recently used.")

    def backup_accounts(self, file_path):
        """Store the accounts as JSON in the given file_path after decrypting the secret keys."""
        decrypted_accounts = []

        # Check if accounts exist and are iterable
        if not hasattr(self, 'accounts') or not isinstance(self.accounts, list):
            self.logger.error("Internal error: No accounts to backup. 'self.accounts' is not a list.")
            return

        for account in self.accounts:
            try:
                decrypted_account = account.__dict__.copy()
                decrypted_account['secret'] = cipher_funcs.decrypt(account.secret)
                decrypted_accounts.append(decrypted_account)
            except AttributeError as e:
                self.logger.error(f"Error processing account {account}: Missing required attribute - {e}")
                continue  # Skip this account, but continue with the others
            except Exception as e:
                self.logger.error(f"Failed to decrypt secret for account {account}: {e}")
                continue  # Skip this account, but continue with the others

        # Ensure the file path is valid
        if not os.path.dirname(file_path) or not os.access(os.path.dirname(file_path), os.W_OK):
            self.logger.error(f"Invalid or inaccessible file path: {file_path}")
            return

        try:
            with open(file_path, 'w') as f:
                # Use JSON pretty printing for readability
                json.dump(decrypted_accounts, f, indent=4)
            self.logger.info(f"Successfully backed up {len(decrypted_accounts)} accounts to {file_path}")
        except (OSError, IOError) as e:
            self.logger.error(f"Failed to write backup to {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during backup: {e}")

    def restore_accounts(self, file_path):
        """Restore the accounts from the given file_path by encrypting the secret keys."""
        self.logger.debug("Starting restore_accounts")
        if not os.path.isfile(file_path):
            self.logger.error(f"Backup file {file_path} does not exist.")
            return

        try:
            with open(file_path, 'r') as f:
                decrypted_accounts = json.load(f)
        except (OSError, IOError) as e:
            self.logger.error(f"Failed to read backup file {file_path}: {e}")
            return
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON from backup file {file_path}: {e}")
            return

        # Validate and restore each account
        restored_accounts = []
        for decrypted_account in decrypted_accounts:
            try:
                # Assuming decrypted_account has the same structure as the original account
                #restored_account = decrypted_account  # Create a new account object (make sure Account is properly defined)
                shared_secret = decrypted_account['secret']
                restored_account = Account(decrypted_account['provider'],decrypted_account['label'],shared_secret,decrypted_account['last_used'])
                # Restore the secret by encrypting it
                restored_account.secret = cipher_funcs.encrypt(shared_secret)

                restored_accounts.append(restored_account)

            except KeyError as e:
                self.logger.error(f"Missing expected key in account data: {e}")
            except Exception as e:
                self.logger.error(f"Failed to restore account from data {decrypted_account}: {e}")

        # Assuming self.accounts is where you want to store the restored accounts
        self.accounts = restored_accounts
        self.logger.debug(f"Restored these accounts: {self.accounts}")
        self.save_accounts()
        self.logger.info(f"Restore completed for  {len(restored_accounts)} accounts from {file_path}")
        self.logger.info(self.accounts)

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
        required_fields = {'provider', 'label', 'secret', 'last_used'}
        return all(
            isinstance(acc, dict) and
            all(field in acc for field in required_fields)
            for acc in content
        )

    @staticmethod
    def _account_key(account: dict) -> str:
        """Generate unique key for account used to detect external modification """
        return f"{account['provider']}:{account['label']}"


    @staticmethod
    def duplicate_accounts(accounts):
        list_copy = []
        for item in accounts:
            newitem = Account(
                provider=item.provider,
                label=item.label,
                secret=item.secret,
                last_used=item.last_used
            )
            list_copy.append(newitem)
        return list_copy
