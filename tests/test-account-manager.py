import pytest
import json
import os
from pathlib import Path
import shutil
import tempfile
from unittest.mock import Mock, patch

from account_manager import AccountManager, Account

#@pytest.fixture
# def temp_dir():
#     """Create a temporary directory for test files.
#      On completion of the context or destruction of the temporary directory object,
#      the newly created temporary directory and all its contents are removed from the filesystem."""
#     with tempfile.TemporaryDirectory() as tmpdirname:
#         yield tmpdirname
#
# @pytest.fixture
# def mock_home_dir(temp_dir, monkeypatch):
#     """Mock the home directory to use our temp directory."""
#     monkeypatch.setattr(Path, 'home', lambda: Path(temp_dir))
#     return temp_dir

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
    def test_account_manager_init(self, account_manager):
        """ must be first method in suite to ensure the singleton uses a tmp file for all other tests"""
        assert str(account_manager.vault_path).startswith("/tmp")

    def test_singleton_pattern(self):
        """Test that AccountManager follows singleton pattern."""
        manager1 = AccountManager()
        manager2 = AccountManager()
        assert manager1 is manager2

    def test_load_accounts_empty_vault(self, account_manager):
        """Test loading accounts when vault doesn't exist."""
        print (f"Vault path: {account_manager.vault_path}")
        accounts = account_manager.load_accounts()
        assert isinstance(accounts, list)
        assert len(accounts) == 0

    def test_init_creates_directories(self, account_manager):
        """Test that AccountManager initialization creates necessary directory for logging.
        Note: AccountManager is a singleton initialized in fixture"""
        log_dir = Path.home() / '.var' / 'app' / 'org.redpoint.EasyAuth' / 'logs'
        assert log_dir.exists()
        assert log_dir.is_dir()

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
        assert loaded_accounts[0].provider == sample_accounts[0]["provider"]
        assert loaded_accounts[0].label == sample_accounts[0]["label"]

    def test_backup_creation(self, account_manager, sample_accounts):
        """Test that backup file is created when saving accounts."""
        account_manager.accounts = [Account(**acc) for acc in sample_accounts]
        account_manager.save_accounts()
        
        backup_path = account_manager.vault_path.with_suffix('.backup.json')
        assert backup_path.exists()

    @patch('cipher_funcs.encrypt')
    def test_save_new_account(self, mock_encrypt, account_manager):

        """Test saving a new account."""
        vault_dir = os.path.dirname(account_manager.vault_path)

        mock_encrypt.return_value = "encrypted_test_secret"

        # Clear any existing accounts
        account_manager.accounts = []
        # Save the new account
        try:
            account_manager.save_new_account(
                provider="Test",
                label="TestLabel",
                secret="test_secret"
            )
        except Exception as e:
            print(f"Exception during save: {e}")
            print(f"After exception - dir permissions: {oct(os.stat(vault_dir).st_mode)}")
            raise

        assert len(account_manager.accounts) == 1
        new_account = account_manager.accounts[0]
        assert new_account.provider == "Test"
        assert new_account.label == "TestLabel"
        assert new_account.secret == "encrypted_test_secret"

    def test_save_duplicate_account(self, account_manager, sample_accounts):
        """Test that saving duplicate account raises error."""
        account_manager.accounts = [Account(**sample_accounts[0])]
        
        with pytest.raises(ValueError) as exc_info:
            account_manager.save_new_account(
                provider=sample_accounts[0]["provider"],
                label=sample_accounts[0]["label"],
                secret="new_secret"
            )
        assert "already exists" in str(exc_info.value)

    def test_handle_external_modification(self, account_manager, sample_accounts):
        """Test handling of external modifications to vault file."""
        # Set up initial state
        account_manager.accounts = [Account(**sample_accounts[0])]
        account_manager.save_accounts()
        
        # Simulate external modification
        modified_accounts = sample_accounts.copy()
        modified_accounts[0]["label"] = "Modified"
        with open(account_manager.vault_path, 'w') as f:
            json.dump(modified_accounts, f)
        
        # Force reload
        account_manager._last_modified_time = None
        loaded_accounts = account_manager.load_accounts()
        
        assert len(loaded_accounts) == len(modified_accounts)
        assert loaded_accounts[0].label == "Modified"

    def test_recover_from_backup(self, account_manager, sample_accounts):
        """Test recovery from backup when vault is corrupted."""
        # Set up initial state with backup
        account_manager.accounts = [Account(**acc) for acc in sample_accounts]
        account_manager.save_accounts()
        
        # Corrupt the main vault file
        with open(account_manager.vault_path, 'w') as f:
            f.write("corrupted json{")
        
        # Load should recover from backup
        loaded_accounts = account_manager.load_accounts()
        assert len(loaded_accounts) == len(sample_accounts)
        assert loaded_accounts[0].provider == sample_accounts[0]["provider"]

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

            account_manager.accounts = [Account(**acc) for acc in sample_accounts]
            result = account_manager.save_accounts()

            assert not result
            mock_log_error.assert_called()
        finally:
            # Always restore permissions and clean up
            os.chmod(test_dir, 0o777)
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_vault_data_validation(self, account_manager):
        """Test validation of account data structure."""
        invalid_data = [{"provider": "Test"}]  # Missing required fields
        
        assert not account_manager._validate_account_data(invalid_data)
        
        valid_data = [{
            "provider": "Test",
            "label": "Test",
            "secret": "secret",
            "last_used": "2024-01-14 12:00"
        }]
        
        assert account_manager._validate_account_data(valid_data)
