import pytest
import json
import os
from pathlib import Path
import shutil
import tempfile
from unittest.mock import Mock, patch

import cipher_funcs
from account_manager import AccountManager, Account, OtpRecord


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
            "issuer": "Google",
            "label": "Work",
            "secret": "encrypted_secret_1",
            "last_used": "2024-01-14 10:00"
        },
        {
            "issuer": "GitHub",
            "label": "Personal",
            "secret": "encrypted_secret_2",
            "last_used": "2024-01-14 11:00"
        }
    ]

class TestAccountManager:
    def test_permission_error(self,account_manager):
        # Specify the file path in the tmp directory
        file_path = "/tmp/my_empty_file.txt"
        # Create an empty file
        with open(file_path, 'w') as file:
            pass
        # Make the file read-only
        os.chmod(file_path, 0o400)
        try:
            account_manager.backup_accounts(file_path)
            assert False, "Backup succeed on read-only file"
        except OSError as e:
            # since the file is read-only, trying to backup should fail
            print (str(e))
            assert True
        os.remove(file_path)

        # Try invalid path
        file_path = "/tmpbad/my_empty_file.txt"
        try:
            account_manager.backup_accounts(file_path)
            assert False, "Backup succeeded on invalid file path"
        except OSError as e:
            # since the path is invalid, trying to backup should fail
            assert True

    def test_backup_and_restore(self,account_manager, sample_accounts):
        # Create Account objects
        acct1 = OtpRecord("Boggle", "Work", "secret_1")
        acct2 = OtpRecord("Github", "Personal", "secret_2")

        account_manager.save_new_account(acct2)
        account_manager.save_new_account(acct1)
        # Backup these existing accounts
        account_manager.backup_accounts("/tmp/backup_test1.json")
        # assert that file exists with non-zero size
        assert os.path.isfile("/tmp/backup_test1.json")

        # Remove accounts for the test - simulating disaster
        account_manager.accounts = []

        # Restore from backup file
        account_manager.restore_accounts("/tmp/backup_test1.json")
        assert account_manager.accounts[0].issuer == acct1.issuer
        assert account_manager.accounts[1].issuer == acct2.issuer
        assert account_manager.accounts[0].label == acct1.label
        assert account_manager.accounts[1].label == acct2.label
        assert cipher_funcs.decrypt(account_manager.accounts[0].secret) == acct1.secret
        assert cipher_funcs.decrypt(account_manager.accounts[1].secret) == acct2.secret
        # Also check the content of vault file
        with open(account_manager.vault_path, 'r') as f:
            vault_accounts = json.load(f)
            assert vault_accounts[0]['issuer'] == "Boggle"
        os.remove("/tmp/backup_test1.json")

    def test_export_and_import(self,account_manager, sample_accounts):
        # Erase accounts for a clean fixture
        account_manager.accounts = []
        # Create Account objects
        acct1 = OtpRecord("Boggle", "Work", "secret_1")
        acct2 = OtpRecord("Github", "Personal", "secret_2")
        account_manager.save_new_account(acct2)
        account_manager.save_new_account(acct1)
        # Export these existing accounts
        account_manager.export_accounts("/tmp/backup_test2.json",'json')
        # assert that file exists with non-zero size
        assert os.path.isfile("/tmp/backup_test2.json")
        # open the export file and read the secret - assert plaintext
        try:
            with open("/tmp/backup_test2.json", 'r') as f:
                json_accounts = json.load(f)
                assert json_accounts[0]['secret'] == "secret_1"
        except (OSError, IOError) as e:
            print(f"Failed to read file /tmp/backup_test2.json: {e}")
            assert False
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON from file /tmp/backup_test2.json: {e}")
            assert False
        # Remove accounts for the test - simulating disaster
        account_manager.accounts = []

        # Import from exported file
        account_manager.import_accounts("/tmp/backup_test2.json")
        assert account_manager.accounts[0].issuer == acct1.issuer
        assert account_manager.accounts[1].issuer == acct2.issuer
        assert account_manager.accounts[0].label == acct1.label
        assert account_manager.accounts[1].label == acct2.label
        assert cipher_funcs.decrypt(account_manager.accounts[0].secret) == acct1.secret
        assert cipher_funcs.decrypt(account_manager.accounts[1].secret) == acct2.secret
        # Also check the content of vault file
        with open(account_manager.vault_path, 'r') as f:
            vault_accounts = json.load(f)
            assert vault_accounts[0]['issuer'] == "Boggle"
        os.remove("/tmp/backup_test2.json")

    def test_import_preview(self,account_manager, sample_accounts):
        """Preview is just import that returns the account list before saving it."""
        # Erase accounts for a clean fixture
        account_manager.accounts = []
        # Create Account objects
        acct1 = OtpRecord("Boggle", "Work", "secret_1")
        acct2 = OtpRecord("Github", "Personal", "secret_2")
        account_manager.save_new_account(acct2)
        account_manager.save_new_account(acct1)
        # Export these existing accounts
        account_manager.export_accounts("/tmp/backup_test3.json",'json')
        # Remove accounts for the test - so we can verify that preview doesn't touch the vault.
        account_manager.accounts = []
        # Import from exported file
        account_list = account_manager.import_preview("/tmp/backup_test3.json")
        assert len(account_manager.accounts) == 0  # preview should not touch accounts
        assert account_list is not None
        assert len(account_list) == 2
        assert account_list[0].issuer == acct1.issuer
        assert account_list[1].issuer == acct2.issuer
        assert account_list[0].label == acct1.label
        assert account_list[1].label == acct2.label
        assert cipher_funcs.decrypt(account_list[0].secret) == acct1.secret
        assert cipher_funcs.decrypt(account_list[1].secret) == acct2.secret
        os.remove("/tmp/backup_test3.json")


    def test_export_and_import_uri(self,account_manager, sample_accounts):
        # Erase accounts for a clean fixture
        account_manager.accounts = []
        # Create Account objects
        acct1 = OtpRecord("Boggle", "Work", "secret_1")
        acct2 = OtpRecord("Github", "Personal", "secret_2")
        account_manager.save_new_account(acct2)
        account_manager.save_new_account(acct1)
        # Export these existing accounts
        account_manager.export_accounts("/tmp/backup_test4.txt","uri")
        # assert that file exists with non-zero size
        assert os.path.isfile("/tmp/backup_test4.txt")
        # open the export file and read the secret - assert plaintext
        try:
            with open("/tmp/backup_test4.txt", 'r') as f:
                otp1 = f.readline()
                assert otp1.startswith("otp")
        except (OSError, IOError) as e:
            print(f"Failed to read file /tmp/backup_test4.txt: {e}")
            assert False
        # Remove accounts for the test - simulating disaster
        account_manager.accounts = []

        # Import from exported file
        account_manager.import_accounts("/tmp/backup_test4.txt")
        assert account_manager.accounts[0].issuer == acct1.issuer
        assert account_manager.accounts[1].issuer == acct2.issuer
        assert account_manager.accounts[0].label == acct1.label
        assert account_manager.accounts[1].label == acct2.label
        assert cipher_funcs.decrypt(account_manager.accounts[0].secret) == acct1.secret
        assert cipher_funcs.decrypt(account_manager.accounts[1].secret) == acct2.secret
        # Also check the content of vault file
        with open(account_manager.vault_path, 'r') as f:
            vault_accounts = json.load(f)
            assert vault_accounts[0]['issuer'] == "Boggle"
        os.remove("/tmp/backup_test4.txt")

    def test_import_uri_fail(self,account_manager):
        # Erase accounts for a clean fixture
        account_manager.accounts = []
        assert -1 == account_manager.import_accounts("/tmp/notexist")

        with open("/tmp/bad_uris.txt", 'w') as file:
            file.write("otpauth//")
        result = account_manager.import_accounts("/tmp/bad_uris.txt")
        assert result == -4

        with open("/tmp/bad_json.txt", 'w') as file:
            file.write("{'provider'")
        result = account_manager.import_accounts("/tmp/bad_json.txt")
        assert result == -3

