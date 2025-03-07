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
    "version": "1",
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
def sample_accounts():
    """Return sample account data for testing."""
    return [
        {
            "issuer": "Gargle",
            "label": "Play",
            "secret": 'gAAAAABnkHnoOtMp73O9EPlDqmSDIJneDqMih3lUVnuEN4vKXaTOEUGX0GuTlr6MhOFZocVBV-iNC2NiZTlqEV49vDPCRbSf_g==',
            "last_used": "2024-01-14 10:00",
            "used_frequency": 2,
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

@patch('cipher_funcs.encrypt')
class TestAccountManager:
    def test_load_accounts(self, mock_encrypt, sample_accounts):
        """Test loading accounts."""
        temp_dir = tempfile.TemporaryDirectory()  # create different tmp for each test
        print(f"Setup: Creating {temp_dir.name}")  # Debugging output
        test_vault_dir = Path(temp_dir.name) / "data"
        test_vault_dir.mkdir()
        test_vault_path = test_vault_dir / "vault.json"
        test_vault_path.touch()

        vaultstuff = json.loads(sample_vault_string)
        with open(test_vault_path, 'w') as outfile:
            json.dump(vaultstuff, outfile, indent=4)

        account_manager = AccountManager(filename=test_vault_path)  # Uses only the first tmp dir
        # Force vault path
        account_manager.vault_path = test_vault_path
        print (f"Vault path: {account_manager.vault_path}")

        accounts = account_manager.get_accounts()
        assert isinstance(accounts, list)
        assert len(accounts) == 2

        """Test saving and loading accounts."""
        # Create Account objects
        account_objs = [Account(**acc) for acc in sample_accounts]
        account_manager._accounts = account_objs

        # Save accounts
        assert account_manager.save_accounts()

        # Load accounts
        loaded_accounts = account_manager.get_accounts()
        assert len(loaded_accounts) == len(sample_accounts)
        assert loaded_accounts[0].issuer == sample_accounts[0]["issuer"]
        assert loaded_accounts[0].label == sample_accounts[0]["label"]
        assert loaded_accounts[0].used_frequency == sample_accounts[0]["used_frequency"]
        # Teardown code executes after the test
        # Note, only removes the dir from the last test, not every tmp dir.
        print(f"Teardown: Removing temporary directory {temp_dir.name}")
        temp_dir.cleanup()


        """Test updating an existing account."""

        encrypted_secret = 'gAAAAABnlSYl5cBXe7783zthq1-sSuRoccpcmsICsySJPKYYARcED4GB7XCMi5kzO8soJljShxSqXjVnFcJjeFLtq_hriG9IsA=='
        mock_encrypt.return_value = encrypted_secret

        # Update the existing account
        revised_data = Account("Woogle",'sheep',encrypted_secret,"2020-12-12 01:02",7,False,"")
        try:
            account_manager.update_account(0, revised_data)
        except Exception as e:
            print(f"Exception during update: {e}")
            raise

        assert len(account_manager._accounts) == 2
        updated_account = account_manager._accounts[0]
        assert updated_account.issuer == "Woogle"
        assert updated_account.label == "sheep"
        assert updated_account.secret == encrypted_secret
        assert updated_account.used_frequency == 7

