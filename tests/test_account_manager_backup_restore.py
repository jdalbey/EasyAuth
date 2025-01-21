import pytest
import json
import os
from pathlib import Path
import shutil
import tempfile
from unittest.mock import Mock, patch

import cipher_funcs
from account_manager import AccountManager, Account

@pytest.fixture
def account_manager():
    """Create an AccountManager instance with a test home directory."""
    test_vault_dir = tempfile.TemporaryDirectory().name
    Path(test_vault_dir).mkdir()
    test_vault_dir = test_vault_dir + "/data/"
    Path(test_vault_dir).mkdir()
    test_vault_path = test_vault_dir + "vault.json"
    Path(test_vault_path).touch()
    manager = AccountManager(filename=test_vault_path)
    return manager

@pytest.fixture
def sample_accounts():
    """Return sample account data for testing."""
    return [
        {
            "provider": "Google",
            "label": "Work",
            "secret": "encrypted_secret_1",
            "last_used": "2024-01-14 10:00"
        },
        {
            "provider": "GitHub",
            "label": "Personal",
            "secret": "encrypted_secret_2",
            "last_used": "2024-01-14 11:00"
        }
    ]

class TestAccountManager:

    def test_backup_and_restore(self,account_manager, sample_accounts):
        # Create Account objects
        acct1 = Account("Boggle", "Work", "secret_1", "2024-01-14 10:00")
        acct2 = Account("Github", "Personal", "secret_2", "2024-01-14 10:00")
        account_manager.save_new_account("Github", "Personal", "secret_2")
        account_manager.save_new_account("Boggle", "Work", "secret_1")
        # Backup these existing accounts
        account_manager.backup_accounts("/tmp/backup_test1.json")
        # assert that file exists with non-zero size
        assert os.path.isfile("/tmp/backup_test1.json")

        # Remove accounts for the test - simulating disaster
        account_manager.accounts = []

        # Restore from backup file
        account_manager.restore_accounts("/tmp/backup_test1.json")
        assert account_manager.accounts[0].provider == acct1.provider
        assert account_manager.accounts[1].provider == acct2.provider
        assert account_manager.accounts[0].label == acct1.label
        assert account_manager.accounts[1].label == acct2.label
        assert cipher_funcs.decrypt(account_manager.accounts[0].secret) == acct1.secret
        assert cipher_funcs.decrypt(account_manager.accounts[1].secret) == acct2.secret
        # Also check the content of vault file
        with open(account_manager.vault_path, 'r') as f:
            vault_accounts = json.load(f)
            assert vault_accounts[0]['provider'] == "Boggle"