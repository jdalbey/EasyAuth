import pytest
import json
import os
from pathlib import Path
import shutil
import tempfile
from unittest.mock import Mock, patch

import cipher_funcs
from account_mgr import AccountManager, Account, OtpRecord

@pytest.fixture
def account_manager(request):
    """Create an AccountManager instance with a test home directory."""
    temp_dir = tempfile.TemporaryDirectory()
    print(f"Setup: Creating {temp_dir.name}")  # Debugging output
    test_vault_dir = Path(temp_dir.name) / "data"
    test_vault_dir.mkdir()
    test_vault_path = test_vault_dir / "vault.json"
    test_vault_path.touch()
    manager = AccountManager(filename=test_vault_path)
    yield manager  # Provide the fixture to the test

    # Teardown code executes after the test
    print(f"Teardown: Removing temporary directory {temp_dir.name}")
    temp_dir.cleanup()

@pytest.fixture
def sample_accounts():
    """Return sample account data for testing."""
    return [
        {
            "issuer": "Google",
            "label": "Work",
            "secret": 'gAAAAABnkHnoOtMp73O9EPlDqmSDIJneDqMih3lUVnuEN4vKXaTOEUGX0GuTlr6MhOFZocVBV-iNC2NiZTlqEV49vDPCRbSf_g==',
            "last_used": "2024-01-14 10:00",
            "used_frequency": 0,
            "favorite": False,
            "icon": None
        },
        {
            "issuer": "GitHub",
            "label": "Personal",
            "secret": 'gAAAAABnkHqr0nPIqDdHwAEXwRiB53q5sgS3AUF-RG9SpbHwpNowsuLjqpuY2coo9VlqkZk5Fit3-vbduso6X7CzT2nKJG8TgQ==',
            "last_used": "2024-01-14 11:00",
            "used_frequency": 0,
            "favorite": False,
            "icon": None
        }
    ]

class TestAccountMgr:
    def test_account_manager_init(self, account_manager):
        """ must be first method in suite to ensure the singleton uses a tmp file for all other tests"""
        x = str(account_manager.vault_path)
        assert str(account_manager.vault_path).startswith("/tmp")
        # removes the tmp dir
        print(f"Teardown: Removing temporary dir {account_manager.vault_path}")
        os.remove(account_manager.vault_path)


    def test_handle_external_modification(self, account_manager, sample_accounts):
        """Test handling of external modifications to vault file."""
        print(f"Starting test with temporary dir {account_manager.vault_path}")
        # Set up initial state with just the first sample account
        original_account = Account(**sample_accounts[0])
        account_manager._accounts = [original_account]
        account_manager.save_accounts()

        # Remove the backup so that handling external modifications has no backup
        if account_manager.backup_path.exists():
            os.remove(account_manager.backup_path)

        # Simulate external modification to just the first account
        modified_accounts = [sample_accounts[0].copy()]
        modified_accounts[0]["label"] = "Modified"  # This changes the key

        with open(account_manager.vault_path, 'w') as f:
            vault_content = {
                "vault": {
                    "version": "1",
                    "entries": modified_accounts
                }
            }
            json.dump(vault_content, f, indent=2)

        # Force reload by modifying the last modified time
        account_manager._last_modified_time = 1

        # This should trigger the _handle_external_modification method internally
        loaded_accounts = account_manager.get_accounts()

        # We expect 2 accounts now - the original in memory and the modified one from disk
        assert len(loaded_accounts) == 2

        # Check that both versions exist in the result
        labels = [acc.label for acc in loaded_accounts]
        assert original_account.label in labels
        assert "Modified" in labels

    def test_recover_from_backup(self, account_manager, sample_accounts):
        """Test recovery from backup when vault is corrupted."""
        # Create a vault that will be backed up by save_accounts
        modified_accounts = sample_accounts.copy()
        with open(account_manager.vault_path, 'w') as f:
            vault_content = {
                "vault": {
                    "version": "1",
                    "entries": modified_accounts
                }
            }
            json.dump(vault_content, f, indent=2)

        # Save accounts to vault (causes backup)
        account_manager._accounts = [Account(**acc) for acc in sample_accounts]
        account_manager.save_accounts()

        # Corrupt the main vault file
        with open(account_manager.vault_path, 'w') as f:
            f.write("corrupted json{")

        # Load should recover from backup
        loaded_accounts = account_manager.get_accounts()
        assert len(loaded_accounts) == len(sample_accounts)
        assert loaded_accounts[0].issuer == sample_accounts[0]["issuer"]
        assert loaded_accounts[1].issuer == sample_accounts[1]["issuer"]
        assert loaded_accounts[1].label == sample_accounts[1]["label"]