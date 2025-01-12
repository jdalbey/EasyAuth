import pytest
import threading
import os
import json
from unittest.mock import patch, mock_open
from models_singleton import AccountManager, Account


@pytest.fixture
def sample_accounts():
    """Sample account data for testing."""
    return [
        {"provider": "Provider1", "label": "Label1", "secret": "Secret1", "last_used": "2025-01-01 12:00"},
        {"provider": "Provider2", "label": "Label2", "secret": "Secret2", "last_used": "2025-01-02 12:00"},
    ]

@pytest.fixture(autouse=True)
def reset_singleton():
    """Ensure the AccountManager singleton is reset before each test."""
    AccountManager._instance = None

def test_singleton_behavior():
    instance1 = AccountManager()
    instance2 = AccountManager()
    assert instance1 is instance2, "AccountManager is not a singleton instance"


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

@patch("os.path.exists", return_value=False)
def test_load_accounts_missing_file(mock_exists):
    instance = AccountManager()
    accounts = instance.load_accounts()
    assert accounts == [], "load_accounts should return an empty list if the vault file is missing"

def test_set_accounts(sample_accounts):
    data4loads = '[{"provider": "Provider1", "label": "Label1", "secret": "Secret1", "last_used": "2025-01-01 12:00"}, {"provider": "Provider2", "label": "Label2", "secret": "Secret2", "last_used": "2025-01-02 12:00"}]'
    data4dumps = [{"provider": "Provider1", "label": "Label1", "secret": "Secret1", "last_used": "2025-01-01 12:00"}, {"provider": "Provider2", "label": "Label2", "secret": "Secret2", "last_used": "2025-01-02 12:00"}]
    instance = AccountManager()
    instance.set_accounts(json.dumps(data4dumps))
    assert len(instance.accounts) == 2, "set_accounts should load accounts from JSON string"
    assert instance.accounts[0].provider == "Provider1"

def test_typical_use():
    # Create a test vault
    outMessage = '[{"provider": "Bogus", "label": "boogum@badmail.com", "secret": "gAAAAABngeZPBmux2r-vLPKMp1_FNjoWbibd_bOoNiUeMCosqBnSwJEXXDuENHV8XVa8mYXu6k93IRzQsRMgurxH2ebaXl35PA==", "last_used": ""}, {"provider": "MichaelangeloSite", "label": "Michael@woopmail.com", "secret": "gAAAAABngeZJ7iSx3k33zLLDh9KoTosnTxBooUGvzKLBlrqa-BwNEpgvsZfYRF4z8DxdvrqxvGgWWE7aealVfXzln5QKTiETEA==", "last_used": ""}]'
    text_file = open("/tmp/testvault.json", "w")
    text_file.write(outMessage)
    text_file.close()
    # load the test vault
    instance = AccountManager("/tmp/testvault.json")
    assert len(instance.accounts) == 2
    # Add a new item
    instance.save_new_account("Woogle","me@woogle.com","ABC234")
    assert len(instance.accounts) == 3
    assert instance.accounts[0].provider == "Woogle"
    # Update an existing item
    update_me = Account("Bogus", "update_me@slowmail.com", "gAAAAABngeZPBmux2r-vLPKMp1_FNjoWbibd_bOoNiUeMCosqBnSwJEXXDuENHV8XVa8mYXu6k93IRzQsRMgurxH2ebaXl35PA==", "2000-01-01 12:01")
    instance.update_account(1,update_me)
    assert instance.accounts[1].label == "update_me@slowmail.com"
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
    expected_begin = '[{"provider": "Woogle", "label": "me@woogle.com", "secret": "ABC234", "last_used": '
    expected_end = '{"provider": "MichaelangeloSite", "label": "Michael@woopmail.com", "secret": "CD333", "last_used": ""}]'
    print (actual)
    assert actual.startswith(expected_begin)
    assert actual.endswith(expected_end)

def test_duplicate_accounts(sample_accounts):
    instance = AccountManager("/tmp/testvault.json")
    accounts = [Account(**acc) for acc in sample_accounts]
    duplicates = instance.duplicate_accounts(accounts)
    assert len(duplicates) == 2, "duplicate_accounts should create copies of all accounts"
    assert duplicates[0].provider == accounts[0].provider
    assert duplicates[0] is not accounts[0], "duplicate_accounts should create distinct copies"
