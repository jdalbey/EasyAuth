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


class TestAccountManagerImport:
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
        account_manager.vault_path = "/tmp/test_vault.json"
        print (f"Vault path: {account_manager.vault_path}")

        accounts_data = json.loads(json_data)
        result = account_manager.parse_json(accounts_data,import_mode=True)
        assert len(result) == 2
        assert result[1].icon == "favicon"