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
        print(f"Teardown: Removing temporary directory {account_manager.vault_path}")
        os.remove(account_manager.vault_path)

    def test_singleton_pattern(self):
        """Test that AccountManager follows singleton pattern."""
        manager1 = AccountManager()
        manager2 = AccountManager()
        assert manager1 is manager2

    def test_otpauth_uri_from_account(self):
        account = Account("Woogle", "me@woogle.com",
                          "gAAAAABngpqkACjKleIWZa3xdgSjtAagXkdaAjRuMCpqHCcXAKbtZ6RpB9mKeHdToEn1TOIkhqmEXSiyfX0MgYekjYbU79k0TA==",
                          "2001-01-01 12:01")
        uri = account.get_otp_auth_uri()
        expected = "otpauth://totp/Woogle:me%40woogle.com?secret=ABC234&issuer=Woogle"
        assert uri == expected

    def test_load_accounts_empty_vault(self, account_manager):
        """Test loading accounts when vault doesn't exist."""
        print(f"Vault path: {account_manager.vault_path}")
        accounts = account_manager.get_accounts()
        assert isinstance(accounts, list)
        assert len(accounts) == 0

    def test_init_creates_directories(self, account_manager):
        """Test that AccountManager initialization creates necessary directory for logging.
        Note: AccountManager is a singleton initialized in fixture"""
        log_dir = Path.home() / '.var' / 'app' / 'org.redpoint.EasyAuth' / 'data' / 'logs'
        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_vault_data_validation(self, account_manager):
        """Test validation of account data structure."""
        invalid_data = [{"issuer": "Test"}]  # Not a vault

        assert not account_manager._validate_vault_data(invalid_data)

        # Vault missing required fields
        invalid_data = {"vault": {"version": "1",
                                  "entries": [{
                                      "issuer": "Test",
                                      "label": "Test",
                                      "secret": "secret",
                                      "last_used": "2024-01-14 12:00"
                                  }]}}

        assert not account_manager._validate_vault_data(invalid_data)

        # Contains all fields but secret is not encrypted
        invalid_data = {"vault": {"version": "1",
                                  "entries": [{
                                      "issuer": "Test",
                                      "label": "Test",
                                      "secret": "secret",
                                      "last_used": "2024-01-14 12:00",
                                      "used_frequency": 2,
                                      "favorite": False,
                                      "icon": None
                                  }]}}

        assert not account_manager._validate_vault_data(invalid_data)

        valid_data = {"vault": {"version": "1",
                                "entries": [{
                                    "issuer": "Test",
                                    "label": "Test",
                                    "secret": "gAAAAABnkHnoOtMp73O9EPlDqmSDIJneDqMih3lUVnuEN4vKXaTOEUGX0GuTlr6MhOFZocVBV-iNC2NiZTlqEV49vDPCRbSf_g==",
                                    "last_used": "2024-01-14 12:00",
                                    "used_frequency": 3,
                                    'favorite': False,
                                    "icon": None
                                }]}}

        assert account_manager._validate_vault_data(valid_data)

    def test_save_and_load_accounts(self, account_manager, sample_accounts):
        """Test saving and loading accounts."""
        # Create Account objects
        account_objs = [Account(**acc) for acc in sample_accounts]
        account_manager._accounts = account_objs

        # Save accounts
        assert account_manager.save_accounts()

        # Load accounts - force reload by setting _accounts to None
        account_manager._accounts = None
        loaded_accounts = account_manager.get_accounts()
        assert len(loaded_accounts) == len(sample_accounts)
        assert loaded_accounts[0].issuer == sample_accounts[0]["issuer"]
        assert loaded_accounts[0].label == sample_accounts[0]["label"]
        assert loaded_accounts[1].used_frequency == sample_accounts[1]["used_frequency"]
        assert loaded_accounts[1].favorite == sample_accounts[1]["favorite"]
        assert loaded_accounts[1].icon == sample_accounts[1]["icon"]

    def test_backup_creation(self, account_manager, sample_accounts):
        """Test that backup file is created when saving accounts."""
        test_accounts = [
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
        test_accounts[0]['secret'] = cipher_funcs.encrypt(test_accounts[0]['secret'])
        test_accounts[1]['secret'] = cipher_funcs.encrypt(test_accounts[1]['secret'])
        account_manager._accounts = [Account(**acc) for acc in test_accounts]
        account_manager.save_accounts()
        backup_path = account_manager.vault_path.with_suffix('.backup.json')
        account_manager.backup_accounts(backup_path)
        assert backup_path.exists()

    @patch('cipher_funcs.encrypt')
    def test_save_new_account(self, mock_encrypt, account_manager):
        """Test saving a new account."""

        encrypted_secret = 'gAAAAABnlSYl5cBXe7783zthq1-sSuRoccpcmsICsySJPKYYARcED4GB7XCMi5kzO8soJljShxSqXjVnFcJjeFLtq_hriG9IsA=='
        mock_encrypt.return_value = encrypted_secret
        # Clear any existing accounts
        account_manager._accounts = []
        # Save the new account
        try:
            account_manager.save_new_account(OtpRecord(
                issuer="Test",
                label="TestLabel",
                secret="test_secret")
            )
        except Exception as e:
            print(f"Exception during save: {e}")
            raise

        assert len(account_manager.get_accounts()) == 1
        new_account = account_manager.get_accounts()[0]
        assert new_account.issuer == "Test"
        assert new_account.label == "TestLabel"
        assert new_account.secret == encrypted_secret

        # Assert that trying to add a duplicate doesn't succeed
        try:
            # Add the same account
            result = account_manager.save_new_account(OtpRecord(
                issuer="Test",
                label="TestLabel",
                secret="test_secret")
            )
        except Exception as e:
            print(f"Exception during save: {e}")
            raise
        assert result == False

    @patch('cipher_funcs.encrypt')
    def test_update_account(self, mock_encrypt, account_manager):

        """Test updating an existing account."""
        vault_dir = os.path.dirname(account_manager.vault_path)

        encrypted_secret = 'gAAAAABnlSYl5cBXe7783zthq1-sSuRoccpcmsICsySJPKYYARcED4GB7XCMi5kzO8soJljShxSqXjVnFcJjeFLtq_hriG9IsA=='
        mock_encrypt.return_value = encrypted_secret

        # Clear any existing accounts
        account_manager._accounts = []
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
        revised_data = Account("Foobar", 'Barfoo', encrypted_secret, "2020-12-12 01:01", 2, False, "")
        try:
            account_manager.update_account(0, revised_data)
        except Exception as e:
            print(f"Exception during update: {e}")
            raise

        assert len(account_manager.get_accounts()) == 1
        updated_account = account_manager.get_accounts()[0]
        assert updated_account.issuer == "Foobar"
        assert updated_account.label == "Barfoo"
        assert updated_account.secret == encrypted_secret
        assert updated_account.used_frequency == 2
        assert updated_account.favorite == False
        assert updated_account.icon == ""
        # removes the tmp dir
        print(f"Teardown: Removing temporary directory {account_manager.vault_path}")
        os.remove(account_manager.vault_path)

    @patch('cipher_funcs.encrypt')
    def test_update_account_nochange(self, mock_encrypt, account_manager):

        """Test updating an existing account without changing anything."""
        vault_dir = os.path.dirname(account_manager.vault_path)

        encrypted_secret = 'gAAAAABnlSYl5cBXe7783zthq1-sSuRoccpcmsICsySJPKYYARcED4GB7XCMi5kzO8soJljShxSqXjVnFcJjeFLtq_hriG9IsA=='
        mock_encrypt.return_value = encrypted_secret

        # Clear any existing accounts
        account_manager._accounts = []
        # Save the new account
        try:
            account_manager.save_new_account(OtpRecord(
                issuer="Foobar",
                label="Barfoo",
                secret="test_secret")
            )
        except Exception as e:
            print(f"Exception during save: {e}")
            print(f"After exception - dir permissions: {oct(os.stat(vault_dir).st_mode)}")
            raise
        # Update the existing account
        revised_data = Account("Foobar", 'Barfoo', encrypted_secret, "2020-12-12 01:01")
        try:
            result = account_manager.update_account(0, revised_data)
            assert result
        except Exception as e:
            print(f"Exception during update: {e}")
            raise

        assert len(account_manager.get_accounts()) == 1
        updated_account = account_manager.get_accounts()[0]
        assert updated_account.issuer == "Foobar"
        assert updated_account.label == "Barfoo"
        assert updated_account.secret == encrypted_secret

    @patch('cipher_funcs.encrypt')
    def test_update_account_fail(self, mock_encrypt, account_manager):

        """Test updating an existing account with duplicate info."""
        vault_dir = os.path.dirname(account_manager.vault_path)

        encrypted_secret = 'gAAAAABnlSYl5cBXe7783zthq1-sSuRoccpcmsICsySJPKYYARcED4GB7XCMi5kzO8soJljShxSqXjVnFcJjeFLtq_hriG9IsA=='
        mock_encrypt.return_value = encrypted_secret

        # Clear any existing accounts
        account_manager._accounts = []

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
        # Save a second account (goes into index 0)
        try:
            account_manager.save_new_account(OtpRecord(
                issuer="Gargle",
                label="user@gargle.com",
                secret="test_secret")
            )
        except Exception as e:
            print(f"Exception during save: {e}")
            print(f"After exception - dir permissions: {oct(os.stat(vault_dir).st_mode)}")
            raise

        # Attempt Update the existing account
        revised_data = Account("Gargle", 'user@gargle.com', encrypted_secret, "2020-12-12 01:01")
        try:
            # updating item 1 with info matching item 0
            result = account_manager.update_account(1, revised_data)
            assert result == False
        except Exception as e:
            print(f"Exception during update: {e}")
            raise

    @patch('cipher_funcs.encrypt')
    def test_delete_account(self, mock_encrypt, account_manager):

        """Test deleting an existing account."""
        vault_dir = os.path.dirname(account_manager.vault_path)

        encrypted_secret = 'gAAAAABnlSYl5cBXe7783zthq1-sSuRoccpcmsICsySJPKYYARcED4GB7XCMi5kzO8soJljShxSqXjVnFcJjeFLtq_hriG9IsA=='
        mock_encrypt.return_value = encrypted_secret

        # Clear any existing accounts
        account_manager._accounts = []

        # Save the new account
        try:
            retcode = account_manager.save_new_account(OtpRecord("Foobar", 'Barfoo', "encrypted_test_secret"))
            assert retcode
        except Exception as e:
            print(f"Exception during save: {e}")
            raise
        # Retrieve the 1st account
        current_account = account_manager.get_accounts()[0]

        # Delete the existing account
        try:
            account_manager.delete_account(current_account)
        except Exception as e:
            print(f"Exception during update: {e}")
            raise

        assert len(account_manager.get_accounts()) == 0

    def test_save_duplicate_account(self, account_manager, sample_accounts):
        """Test that saving duplicate account returns False."""

        # Put a sample account into the list
        account_manager._accounts = [Account(**sample_accounts[0])]

        # create a new account from the components of the existing one.
        rec = OtpRecord(sample_accounts[0]["issuer"], sample_accounts[0]["label"],
                        secret="new_secret")
        retcode = account_manager.save_new_account(rec)
        assert not retcode

    def test_sort_alphabetically(self, account_manager, sample_accounts):
        # Put 2 sample accounts into the list, Google and Github
        account_objs = [Account(**acc) for acc in sample_accounts]
        account_manager._accounts = account_objs
        account_manager.sort_alphabetically()
        assert account_manager.get_accounts()[0] == account_objs[1]

    @patch('logging.Logger.error')
    def test_handle_save_failure(self, mock_log_error, account_manager, sample_accounts):
        """Test handling of save failures."""
        # Create a separate test directory
        test_dir = tempfile.mkdtemp()
        try:
            # Set up a test-specific vault path
            test_vault = Path(test_dir) / "test_vault.json"
            account_manager.vault_path = test_vault

            # Make directory read-only
            os.chmod(test_dir, 0o444)

            account_manager._accounts = [Account(**acc) for acc in sample_accounts]
            result = account_manager.save_accounts()

            assert not result
            mock_log_error.assert_called()
        finally:
            # Always restore permissions and clean up
            os.chmod(test_dir, 0o777)
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_external_modification_detection(self, account_manager, sample_accounts):
        """Test detection of external modifications to the vault file."""
        # First, set up initial accounts
        account_manager._accounts = [Account(**sample_accounts[0])]
        account_manager.save_accounts()

        # Now simulate an external modification by directly writing to the file
        # This bypasses the normal save mechanism to simulate another process writing to the file
        modified_content = {
            "vault": {
                "version": "1",
                "entries": [
                    {
                        "issuer": "ModifiedExternally",
                        "label": "Test",
                        "secret": sample_accounts[0]["secret"],
                        "last_used": "2024-01-14 12:00",
                        "used_frequency": 5,
                        "favorite": True,
                        "icon": None
                    }
                ]
            }
        }

        # Write modified content to file
        with open(account_manager.vault_path, 'w') as f:
            json.dump(modified_content, f)

        # Force reload by modifying the last modified time
        account_manager._last_modified_time = 1

        # Get accounts should detect the modification and reload
        accounts = account_manager.get_accounts()

        # Verify the modified account was loaded
        assert len(accounts) == 1
        assert accounts[0].issuer == "ModifiedExternally"
        assert accounts[0].used_frequency == 5
        assert accounts[0].favorite == True