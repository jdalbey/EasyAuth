from pathlib import Path

import pytest
import threading
import os
import json
from unittest.mock import patch, mock_open
from account_mgr import AccountManager, Account, OtpRecord

@pytest.fixture
def sample_accounts():
    """Sample account data for testing."""
    return [
        {"issuer": "Provider1", "label": "Label1", "secret": "Secret1", "last_used": "2025-01-01 12:00"},
        {"issuer": "Provider2", "label": "Label2", "secret": "Secret2", "last_used": "2025-01-02 12:00"},
    ]

@pytest.fixture(autouse=True)
def reset_singleton():
    """Ensure the AccountManager singleton is reset before each test."""
    AccountManager._instance = None

def test_singleton_behavior():
    instance1 = AccountManager()
    instance2 = AccountManager()
    assert instance1 is instance2, "AccountManager is not a singleton instance"

def test_init_creates_directories():
    """Test that AccountManager initialization creates necessary directory for logging."""
    instance1 = AccountManager("/tmp/alpha/beta/acounts.json")
    log_dir = Path.home() / '/tmp' / 'alpha' / 'beta' /  'logs'
    assert log_dir.exists()
    assert log_dir.is_dir()
    os.remove("/tmp/alpha/beta/logs/account_manager.log")
    os.rmdir("/tmp/alpha/beta/logs")
    os.rmdir("/tmp/alpha/beta/")
    os.rmdir("/tmp/alpha/")

def test_thread_safety():
    instances = []

    def get_instance():
        instances.append(AccountManager())

    threads = [threading.Thread(target=get_instance) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert all(inst is instances[0] for inst in instances), "Singleton is not thread-safe"

@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps([]))
def test_load_accounts(mock_open, mock_exists):
    instance = AccountManager()
    accounts = instance.load_accounts()
    assert accounts == [], "load_accounts should return an empty list if the vault is empty"
    mock_open.assert_called_with(instance.vault_path, "r")

def test_typical_use():
    # Create a test vault
    outMessage = '{"vault": {"version": "1","entries":[{"issuer": "Bogus", "label": "boogum@badmail.com", "secret": "gAAAAABngeZPBmux2r-vLPKMp1_FNjoWbibd_bOoNiUeMCosqBnSwJEXXDuENHV8XVa8mYXu6k93IRzQsRMgurxH2ebaXl35PA==", "last_used": "", "used_frequency": 2, "favorite":false,"icon":null}, {"issuer": "MichaelangeloSite", "label": "Michael@woopmail.com", "secret": "gAAAAABngeZJ7iSx3k33zLLDh9KoTosnTxBooUGvzKLBlrqa-BwNEpgvsZfYRF4z8DxdvrqxvGgWWE7aealVfXzln5QKTiETEA==", "last_used": "", "used_frequency": 2, "favorite":false,"icon":null}]}}'
    text_file = open("/tmp/testvault.json", "w")
    text_file.write(outMessage)
    text_file.close()
    # load the test vault
    instance = AccountManager("/tmp/testvault.json")
    assert len(instance.accounts) == 2
    # Add a new item
    instance.save_new_account(OtpRecord("Woogle","me@woogle.com","ABC234"))
    assert len(instance.accounts) == 3
    assert instance.accounts[0].issuer == "Woogle"
    # Update an existing item
    update_me = Account("Bogus", "update_me@slowmail.com", "gAAAAABngeZPBmux2r-vLPKMp1_FNjoWbibd_bOoNiUeMCosqBnSwJEXXDuENHV8XVa8mYXu6k93IRzQsRMgurxH2ebaXl35PA==", "2000-01-01 12:01",2,False,"icon")
    instance.update_account(1,update_me)
    assert instance.accounts[1].label == "update_me@slowmail.com"
    assert instance.accounts[1].icon== "icon"
    # delete an item
    delete_me = update_me
    instance.delete_account(delete_me)
    assert len(instance.accounts) == 2
    # backup the accounts to a file
    instance.backup_accounts("/tmp/testbackup.json")
    # Read the file and compare to expected
    text_file = open("/tmp/testbackup.json", "r")
    actual = text_file.read()
    text_file.close()
    expected_begin = '[\n    {\n        "issuer": "Woogle",\n        "label": "me@woogle.com",\n        "secret":'
    expected_end = '{\n        "issuer": "MichaelangeloSite",\n        "label": "Michael@woopmail.com",\n        "secret": '
    print (actual)
    assert actual.startswith(expected_begin)
    assert actual.__contains__(expected_end)

def test_duplicate_accounts(sample_accounts):
    instance = AccountManager("/tmp/testvault.json")
    accounts = [OtpRecord(acc['issuer'],acc['label'],acc['secret']).toAccount() for acc in sample_accounts]
    duplicates = instance.duplicate_accounts(accounts)
    assert len(duplicates) == 2, "duplicate_accounts should create copies of all accounts"
    assert duplicates[0].issuer == accounts[0].issuer
    assert duplicates[0] is not accounts[0], "duplicate_accounts should create distinct copies"

    account3 = OtpRecord('issuer3','user3','secret3').toAccount()
    account3.last_used = "2000-01-02 00:01"
    account3.used_frequency = 1
    account3.icon = "icongoeshere"
    accounts.append(account3)

    duplicates = instance.duplicate_accounts(accounts)

    assert len(duplicates) == 3, "duplicate_accounts should create copies of all accounts"
    assert duplicates[2].issuer == account3.issuer
    assert duplicates[2].label == account3.label
    assert duplicates[2].used_frequency == account3.used_frequency
    assert duplicates[2].last_used == account3.last_used
    assert duplicates[2].used_frequency == account3.used_frequency
    assert duplicates[2].favorite == account3.favorite
    assert duplicates[2].icon == account3.icon
    assert duplicates[2] is not accounts[2], "duplicate_accounts should create distinct copies"
