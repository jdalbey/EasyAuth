import pytest
import json
import os
from pathlib import Path
import shutil
import tempfile
from unittest.mock import Mock, patch

import cipher_funcs
from account_mgr import AccountManager, Account, OtpRecord

""" sample V1 vault data for testing."""
sample_vault_string = """
{
  "vault": {
    "version": 1,
    "entries":     
    [
        {
            "issuer": "Google",
            "label": "Work",
            "secret": "gAAAAABnkHnoOtMp73O9EPlDqmSDIJneDqMih3lUVnuEN4vKXaTOEUGX0GuTlr6MhOFZocVBV-iNC2NiZTlqEV49vDPCRbSf_g==",
            "last_used": "2024-01-14 10:00",
            "used_frequency": "1",
            "favorite": "False",
            "icon": "None"
        },
        {
            "issuer": "GitHub",
            "label": "Personal",
            "secret": "gAAAAABnkHqr0nPIqDdHwAEXwRiB53q5sgS3AUF-RG9SpbHwpNowsuLjqpuY2coo9VlqkZk5Fit3-vbduso6X7CzT2nKJG8TgQ==",
            "last_used": "2024-01-14 11:00",
            "used_frequency": "0",
            "favorite": "False",
            "icon": "None"
        }
    ]
   }
}
"""

@pytest.fixture
def account_manager(request):
    """Create an AccountManager instance with a test home directory."""
    temp_dir = tempfile.TemporaryDirectory()   # create different tmp for each test
    print(f"Setup: Creating {temp_dir.name}")  # Debugging output
    test_vault_dir = Path(temp_dir.name) / "data"
    test_vault_dir.mkdir()
    test_vault_path = test_vault_dir / "vault.json"
    test_vault_path.touch()

    manager = AccountManager(filename=test_vault_path) # Uses only the first tmp dir
    print (len(manager.accounts))
    yield manager  # Provide the fixture to the test

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


class TestAccountManager:
    def test_account_manager_init(self, account_manager):
        """ must be first method in suite to ensure the singleton uses a tmp file for all other tests"""
        x = str(account_manager.vault_path)
        assert str(account_manager.vault_path).startswith("/tmp")
        # removes the tmp dir
        print(f"Teardown: Removing temporary directory {account_manager.vault_path}")
        os.remove(account_manager.vault_path)


    def test_vault_data_validation(self, account_manager):
        """Test validation of account data structure."""
        invalid_data = [{"issuer": "Test"}]  # Missing required fields

        assert not account_manager._validate_account_data(invalid_data)

        # Contains v0 fields but not v1
        invalid_data = [{
            "issuer": "Test",
            "label": "Test",
            "secret": "secret",
            "last_used": "2024-01-14 12:00",
        }]

        assert not account_manager._validate_account_data(invalid_data)

        # Contains all fields but secret is not encrypted
        invalid_data = [{
            "issuer": "Test",
            "label": "Test",
            "secret": "secret",
            "last_used": "2024-01-14 12:00",
            "used_frequency": 0,
            "favorite": False,
            "icon": None
        }]

        assert not account_manager._validate_account_data(invalid_data)

        valid_data = [{
            "issuer": "Test",
            "label": "Test",
            "secret": "gAAAAABnkHnoOtMp73O9EPlDqmSDIJneDqMih3lUVnuEN4vKXaTOEUGX0GuTlr6MhOFZocVBV-iNC2NiZTlqEV49vDPCRbSf_g==",
            "last_used": "2024-01-14 12:00",
            "used_frequency": 0,
            "favorite": False,
            "icon": None
        }]

        assert account_manager._validate_account_data(valid_data)

    def test_save_and_load_accounts(self, account_manager, sample_accounts):
        """Test saving and loading accounts."""
        # Create Account objects
        account_objs = [Account(**acc) for acc in sample_accounts]
        account_manager.accounts = account_objs

        # Save accounts
        assert account_manager.save_accounts()

        # Load accounts
        loaded_accounts = account_manager.load_accounts()
        assert len(loaded_accounts) == len(sample_accounts)
        assert loaded_accounts[0].issuer == sample_accounts[0]["issuer"]
        assert loaded_accounts[0].label == sample_accounts[0]["label"]
        assert loaded_accounts[1].used_frequency == sample_accounts[0]["used_frequency"]
        # removes the tmp dir
        print(f"Teardown: Removing temporary directory {account_manager.vault_path}")
        os.remove(account_manager.vault_path)

    @patch('cipher_funcs.encrypt')
    def test_update_account(self, mock_encrypt, account_manager):

        """Test updating an existing account."""
        vault_dir = os.path.dirname(account_manager.vault_path)

        encrypted_secret = 'gAAAAABnlSYl5cBXe7783zthq1-sSuRoccpcmsICsySJPKYYARcED4GB7XCMi5kzO8soJljShxSqXjVnFcJjeFLtq_hriG9IsA=='
        mock_encrypt.return_value = encrypted_secret

        # Clear any existing accounts
        account_manager.accounts = []
        # Save the new account
        try:
            account_manager.save_new_account(OtpRecord(
                issuer="Test",
                label="TestLabel",
                secret="test_secret")
            )
        except Exception as e:
            print(f"Exception during save: {e}")
            print(f"After exception - dir permissions: {oct(os.stat(vault_dir).st_mode)}")
            raise
        # Update the existing account
        revised_data = Account("Foobar",'Barfoo',encrypted_secret,"2020-12-12 01:01",2,False,"")
        try:
            account_manager.update_account(0, revised_data)
        except Exception as e:
            print(f"Exception during update: {e}")
            raise

        assert len(account_manager.accounts) == 1
        updated_account = account_manager.accounts[0]
        assert updated_account.issuer == "Foobar"
        assert updated_account.label == "Barfoo"
        assert updated_account.secret == encrypted_secret
        assert updated_account.used_frequency == 2

        # removes the tmp dir
        print(f"Teardown: Removing temporary directory {account_manager.vault_path}")
        os.remove(account_manager.vault_path)
