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


class TestAccountManagerImportMerge:
    def test_parse_json(self, sample_accounts):
        """Test parsing import data."""
        # a record with essential fields and a record with optional fields
        json_data ="""
[
    {
        "issuer": "PayPal",
        "label": "steve@dottotech.com",
        "secret": "DITY7ULUVUIJK7X7"
    },
    {
        "issuer": "Gargle",
        "label": "me@gmail.com",
        "secret": "AB34",
        "last_used": "2025-01-31 16:38:59",
        "used_frequency": 2,
        "favorite": true,
        "icon":"favicon"
    }
]"""

        account_manager = AccountManager()  # Uses only the first tmp dir
        # Force vault path
        account_manager.vault_path = Path("/tmp/test_vault.json")
        print (f"Vault path: {account_manager.vault_path}")

        accounts_data = json.loads(json_data)
        result = account_manager.parse_json(accounts_data,import_mode=True)
        assert len(result) == 2
        assert result[1].icon == "favicon"

    def test_import_merge_preview(self, sample_accounts, account_manager):
        # Put 2 sample accounts into the list, Google and Github
        account_manager._accounts = [Account(**acc) for acc in sample_accounts]

        result = account_manager.import_preview("tests/test_data/import_preview_test.json")

        assert len(result) == 3
        assert result[0].issuer == 'Slack'
        assert result[1].issuer == 'LinkedIn'
        assert result[2].issuer == 'Dropbox'

    def test_import_merge(self, sample_accounts, account_manager):
        # Put 2 sample accounts into the list, Google and Github
        account_manager._accounts = [Account(**acc) for acc in sample_accounts]

        # Import 3 more accounts
        account_manager.import_accounts("tests/test_data/import_preview_test.json")
        result = account_manager.get_accounts()
        assert len(result) == 5
        assert result[2].issuer == 'Slack'
        assert result[3].issuer == 'LinkedIn'
        assert result[4].issuer == 'Dropbox'

    def test_import_merge_conflict(self, sample_accounts, account_manager):
        # Put 2 sample accounts into the list, Google and Github
        account_manager._accounts = [Account(**acc) for acc in sample_accounts]

        # Import 2 accounts with duplicate issuer & label. 1 has same secret (ignore), 1 has different secret (conflict)
        conflict_count = account_manager.import_accounts("tests/test_data/import_merge_conflict_test.json")
        result = account_manager.get_accounts()
        assert len(result) == 3
        assert result[2].issuer == 'GitHub!'
        assert conflict_count == 1



