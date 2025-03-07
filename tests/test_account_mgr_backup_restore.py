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
def account_manager():
    """Create an AccountManager instance with a test home directory."""
    temp_dir = tempfile.TemporaryDirectory()
    test_vault_dir = Path(temp_dir.name) / "data"
    test_vault_dir.mkdir()
    test_vault_path = test_vault_dir / "vault.json"
    test_vault_path.touch()

    manager = AccountManager(filename=str(test_vault_path))
    yield manager  # Provide the fixture to the test

    # Teardown code executes after the test
    temp_dir.cleanup()

# @pytest.fixture
# def account_manager(request):
#     """Create an AccountManager instance with a test home directory."""
#     test_vault_dir = tempfile.TemporaryDirectory().name
#     Path(test_vault_dir).mkdir()
#     test_vault_dir = test_vault_dir + "/data/"
#     Path(test_vault_dir).mkdir()
#     test_vault_path = test_vault_dir + "vault.json"
#     Path(test_vault_path).touch()
#     manager = AccountManager(filename=test_vault_path)
#
#     # Teardown method to remove the temp directory
#     def teardown():
#         print ("Entering teardown")
#         shutil.rmtree(test_vault_dir)
#
#     request.addfinalizer(teardown)
#     return manager

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
import stat
class TestAccountManager:
    def is_read_only(self, file_path):
        # Check if the file exists
        if os.path.exists(file_path):
            # Get the file's status using os.stat()
            file_stat = os.stat(file_path)

            # Check if the file is read-only
            # A file is read-only if the owner does not have write permissions
            return not bool(file_stat.st_mode & stat.S_IWUSR)
        else:
            return False  # File doesn't exist

    def test_permission_error(self,account_manager):
        acct2 = OtpRecord("Github", "Personal", "secret_2")
        account_manager.save_new_account(acct2)

        # Specify the file path in the tmp directory
        file_path = "/tmp/my_empty_file.txt"
        # See if it already exists
        if not self.is_read_only(file_path):
            # Create an empty file
            with open(file_path, 'w') as file:
                pass
            # Make the file read-only
            os.chmod(file_path, 0o400)
        try:
            account_manager.backup_accounts(file_path)
            assert False, "Backup succeeded on read-only file, when it shouldn't."
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
        account_manager.save_new_account(acct1)  # this will cause backup of acct2 in vault.backup.json
        accounts = account_manager.get_accounts()
        acct1up = accounts[0]
        acct1up.issuer = "Boogie"
        acct1up.used_frequency = 1
        acct1up.icon = 'Bullwinkle'
        account_manager.update_account(0,acct1up)
        # Backup these existing accounts
        account_manager.backup_accounts("/tmp/backup_test1.json")
        # assert that file exists with non-zero size
        assert os.path.isfile("/tmp/backup_test1.json")

        # Remove accounts for the test - simulating disaster
        account_manager._accounts = []

        # Restore from backup file
        account_manager.restore_accounts("/tmp/backup_test1.json")
        accounts = account_manager.get_accounts()
        print (F"acct1 {acct1.issuer}")
        assert accounts[0].issuer == acct1up.issuer
        assert accounts[1].issuer == acct2.issuer
        assert accounts[0].label == acct1up.label
        assert accounts[1].label == acct2.label
        assert accounts[0].secret == acct1up.secret
        assert cipher_funcs.decrypt(accounts[1].secret) == acct2.secret
        assert accounts[0].used_frequency == 1
        assert accounts[0].icon == 'Bullwinkle'
        # Also check the content of vault file
        with open(account_manager.vault_path, 'r') as f:
            vault_accounts = json.load(f)['vault']['entries']
            assert vault_accounts[0]['issuer'] == "Boogie"
        os.remove("/tmp/backup_test1.json")

        # remove the vault (but leave the backup)
        os.remove(account_manager.vault_path)
        # next time we save something it should NOT backup from the non-existant vault.
        account_manager.save_new_account(acct1)
        # check length of backup it should be > 0 (because save should have not changed it)
        file_size = os.path.getsize(account_manager.backup_path)
        assert file_size > 0

        # Delete the existing accounts
        accounts = account_manager.get_accounts()
        current_account = accounts[0]
        account_manager.delete_account(current_account)
        accounts = account_manager.get_accounts()
        current_account = accounts[0]
        account_manager.delete_account(current_account)
        accounts = account_manager.get_accounts()
        current_account = accounts[0]
        account_manager.delete_account(current_account)
        # next time we save something it should NOT backup from the EMPTY vault.
        account_manager.save_new_account(acct1)
        # check length of backup it should be > 0 (because save should have not changed it)
        file_size = os.path.getsize(account_manager.backup_path)
        print ("backup size ",file_size)
        vault_with_no_entries_size = 58
        assert file_size > vault_with_no_entries_size


    def test_export_and_import(self,account_manager, sample_accounts):
        # Erase accounts for a clean fixture
        account_manager._accounts = []
        # Create Account objects
        acct1 = OtpRecord("Boggle", "Work", "secret_1")
        acct2 = OtpRecord("Github", "Personal", "secret_2")
        account_manager.save_new_account(acct2)
        account_manager.save_new_account(acct1)
        accounts = account_manager.get_accounts()
        acct1up = accounts[0]
        acct1up.issuer = "Boogie"
        acct1up.used_frequency = 1
        acct1up.icon = 'Bullwinkle'
        account_manager.update_account(0,acct1up)
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
        account_manager._accounts = []

        # Import from exported file
        account_manager.import_accounts("/tmp/backup_test2.json")
        accounts = account_manager.get_accounts()
        assert accounts[0].issuer == acct1up.issuer
        assert accounts[1].issuer == acct2.issuer
        assert accounts[0].label == acct1up.label
        assert accounts[1].label == acct2.label
        assert cipher_funcs.decrypt(accounts[0].secret) == cipher_funcs.decrypt(acct1up.secret)
        assert cipher_funcs.decrypt(accounts[1].secret) == acct2.secret
        assert accounts[0].used_frequency == 1
        assert accounts[0].icon == 'Bullwinkle'
        # Also check the content of vault file
        with open(account_manager.vault_path, 'r') as f:
            vault_accounts = json.load(f)['vault']['entries']
            assert vault_accounts[0]['issuer'] == "Boogie"
        os.remove("/tmp/backup_test2.json")

    def test_import_preview(self,account_manager, sample_accounts):
        """Preview is just import that returns the account list before saving it."""
        # Erase accounts for a clean fixture
        account_manager._accounts = []
        # Create Account objects
        acct1 = OtpRecord("Boggle", "Work", "secret_1")
        acct2 = OtpRecord("Github", "Personal", "secret_2")
        account_manager.save_new_account(acct2)
        account_manager.save_new_account(acct1)
        # Export these existing accounts
        account_manager.export_accounts("/tmp/backup_test3.json",'json')
        # Remove accounts for the test - so we can verify that preview doesn't touch the vault.
        account_manager._accounts = []
        # Import from exported file
        account_list = account_manager.import_preview("/tmp/backup_test3.json")
        accounts = account_manager.get_accounts()
        assert len(accounts) == 0  # preview should not touch accounts
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
        account_manager._accounts = []
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
        account_manager._accounts = []

        # Import from exported file
        account_manager.import_accounts("/tmp/backup_test4.txt")
        accounts = account_manager.get_accounts()
        assert accounts[0].issuer == acct1.issuer
        assert accounts[1].issuer == acct2.issuer
        assert accounts[0].label == acct1.label
        assert accounts[1].label == acct2.label
        assert cipher_funcs.decrypt(accounts[0].secret) == acct1.secret
        assert cipher_funcs.decrypt(accounts[1].secret) == acct2.secret
        # Also check the content of vault file
        with open(account_manager.vault_path, 'r') as f:
            vault_accounts = json.load(f)['vault']['entries']
            assert vault_accounts[0]['issuer'] == "Boggle"
        os.remove("/tmp/backup_test4.txt")

    def test_import_uri_fail(self,account_manager):
        # Erase accounts for a clean fixture
        account_manager._accounts = []
        assert -1 == account_manager.import_accounts("/tmp/notexist")

        with open("/tmp/bad_uris.txt", 'w') as file:
            file.write("otpauth//")
        result = account_manager.import_accounts("/tmp/bad_uris.txt")
        assert result == -4

        with open("/tmp/bad_json.txt", 'w') as file:
            file.write("{'provider'")
        result = account_manager.import_accounts("/tmp/bad_json.txt")
        assert result == -3