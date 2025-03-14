import unittest
import cipher_funcs
from account_mgr import Account, AccountManager



class TestMergeAccountLists(unittest.TestCase):
    def setUp(self):
        # Create some sample timestamps for consistent testing
        self.timestamp1 = "2025-03-12 10:00:00"
        self.timestamp2 = "2025-03-13 11:00:00"

        # Create some standard accounts for testing with encrypted secrets
        self.account1 = Account(
            "Google",
            "user1@gmail.com",
            cipher_funcs.encrypt("secret123"),
            self.timestamp1,
            5,
            True,
            "google_icon"
        )

        self.account2 = Account(
            "Microsoft",
            "user1@outlook.com",
            cipher_funcs.encrypt("secret456"),
            self.timestamp1,
            3,
            False,
            "ms_icon"
        )

        self.account3 = Account(
            "Amazon",
            "user1",
            cipher_funcs.encrypt("secret789"),
            self.timestamp1,
            1,
            False,
            "amazon_icon"
        )

    def test_empty_lists(self):
        """Test merging when one or both lists are empty."""
        # Test case 1: Both lists empty
        result, conflicts = AccountManager.merge_account_lists([], [])
        self.assertEqual(result, [])

        # Test case 2: First list empty
        list2 = [self.account1]
        result, conflicts = AccountManager.merge_account_lists([], list2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.account1)

        # Test case 3: Second list empty
        list1 = [self.account1]
        result, conflicts = AccountManager.merge_account_lists(list1, [])
        self.assertEqual(result, list1)
        self.assertIsNot(result, list1)  # Verify we get a copy, not the original

    def test_no_conflicts_or_duplicates(self):
        """Test merging lists with no overlapping accounts."""
        list1 = [self.account1]
        list2 = [self.account2, self.account3]

        result, conflicts = AccountManager.merge_account_lists(list1, list2)

        # Should have all three accounts
        self.assertEqual(len(result), 3)
        self.assertIn(self.account1, result)
        self.assertIn(self.account2, result)
        self.assertIn(self.account3, result)
        # Should be no conflicts
        assert conflicts == 0

    def test_duplicate_accounts(self):
        """Test merging lists with duplicate accounts (same issuer, label, secret)."""
        list1 = [self.account1, self.account2]

        # Create a duplicate of account1 with the same encrypted secret
        duplicate_account1 = Account(
            "Google",
            "user1@gmail.com",
            self.account1.secret,  # Same encrypted secret
            self.timestamp2,
            7,
            False,
            "different_icon"
        )

        list2 = [duplicate_account1, self.account3]

        result, conflicts = AccountManager.merge_account_lists(list1, list2)

        # Should have three accounts (not four, as one is a duplicate)
        self.assertEqual(len(result), 3)

        # Count occurrences of account1 - should be exactly 1
        account1_count = sum(1 for acc in result if acc.issuer == "Google" and acc.label == "user1@gmail.com")
        self.assertEqual(account1_count, 1)
        # Should be no conflicts
        assert conflicts == 0

    def test_conflicting_accounts(self):
        """Test merging lists with conflicting accounts (same issuer and label, different secret)."""
        list1 = [self.account1, self.account2]

        # Create a conflicting account (same issuer and label, different secret)
        conflict_account = Account(
            "Google",
            "user1@gmail.com",
            cipher_funcs.encrypt("different_secret"),  # Different encrypted secret
            self.timestamp2,
            2,
            False,
            "google_icon"
        )

        list2 = [conflict_account, self.account3]

        result, conflicts = AccountManager.merge_account_lists(list1, list2)

        # Should have 4 accounts (original 2 + modified conflict + new account)
        self.assertEqual(len(result), 4)

        # Check that the conflict was handled correctly - issuer should have '!' appended
        conflict_in_result = False
        for acc in result:
            if (acc.issuer == "Google!" and
                    acc.label == "user1@gmail.com" and
                    acc.secret == conflict_account.secret):
                conflict_in_result = True
                break

        self.assertTrue(conflict_in_result, "Conflicting account not properly marked with '!'")
        # Should be 1 conflict
        assert conflicts == 1

    def test_mixed_scenarios(self):
        """Test merging lists with a mix of new, duplicate, and conflicting accounts."""
        list1 = [self.account1, self.account2]

        # Create a duplicate of account1
        duplicate = Account(
            "Google",
            "user1@gmail.com",
            self.account1.secret,  # Same encrypted secret
            self.timestamp2,
            10,  # Different used_frequency
            True,
            "new_icon"  # Different icon
        )

        # Create a conflict with account2
        conflict = Account(
            "Microsoft",
            "user1@outlook.com",
            cipher_funcs.encrypt("new_secret"),  # Different encrypted secret
            self.timestamp2,
            7,
            True,
            "new_ms_icon"
        )

        # Create a completely new account
        new_account = Account(
            "Twitter",
            "user1",
            cipher_funcs.encrypt("twitter_secret"),
            self.timestamp2,
            0,
            False,
            "twitter_icon"
        )

        list2 = [duplicate, conflict, new_account]

        result, conflicts = AccountManager.merge_account_lists(list1, list2)

        # Expected: original 2 + conflict with '!' + new account = 4 total
        self.assertEqual(len(result), 4)

        # Verify the conflict was handled correctly
        conflict_found = False
        for acc in result:
            if (acc.issuer == "Microsoft!" and
                    acc.label == "user1@outlook.com" and
                    acc.secret == conflict.secret):
                conflict_found = True
                break

        self.assertTrue(conflict_found, "Conflict not properly handled")

        # Verify the new account was added
        new_account_found = False
        for acc in result:
            if acc.issuer == "Twitter" and acc.label == "user1":
                new_account_found = True
                break

        self.assertTrue(new_account_found, "New account not added properly")
        # Should be 1 conflict
        assert conflicts == 1

    def test_complex_scenario_with_multiple_conflicts(self):
        """Test a more complex scenario with multiple conflicts of different types."""
        list1 = [self.account1, self.account2, self.account3]

        # Create multiple conflicts and duplicates
        accounts_list2 = [
            # Duplicate of account1
            Account(
                "Google",
                "user1@gmail.com",
                self.account1.secret,
                self.timestamp2,
                8,
                True,
                "icon1"
            ),

            # Conflict with account1 (same issuer/label, different secret)
            Account(
                "Google",
                "user1@gmail.com",
                cipher_funcs.encrypt("conflict_secret1"),
                self.timestamp2,
                3,
                False,
                "icon2"
            ),

            # Conflict with account2 (same issuer/label, different secret)
            Account(
                "Microsoft",
                "user1@outlook.com",
                cipher_funcs.encrypt("conflict_secret2"),
                self.timestamp2,
                1,
                True,
                "icon3"
            ),

            # New unique account
            Account(
                "Dropbox",
                "user1",
                cipher_funcs.encrypt("dropbox_secret"),
                self.timestamp2,
                0,
                False,
                "dropbox_icon"
            )
        ]

        result, conflicts = AccountManager.merge_account_lists(list1, accounts_list2)

        # Expected: original 3 + 2 conflicts with '!' + 1 new account = 6 total
        # (duplicate is ignored)
        self.assertEqual(len(result), 6)

        # Check if specific accounts exist in the result
        def account_exists(issuer, label, secret):
            return any(acc.issuer == issuer and acc.label == label and acc.secret == secret for acc in result)

        # Verify original accounts are retained
        self.assertTrue(account_exists("Google", "user1@gmail.com", self.account1.secret))
        self.assertTrue(account_exists("Microsoft", "user1@outlook.com", self.account2.secret))
        self.assertTrue(account_exists("Amazon", "user1", self.account3.secret))

        # Verify conflicts are marked with '!'
        self.assertTrue(account_exists("Google!", "user1@gmail.com", accounts_list2[1].secret))
        self.assertTrue(account_exists("Microsoft!", "user1@outlook.com", accounts_list2[2].secret))

        # Verify new account was added
        self.assertTrue(account_exists("Dropbox", "user1", accounts_list2[3].secret))
        # Should be 2 conflicts
        assert conflicts == 2

    def test_original_list_unchanged(self):
        """Test that the original list1 is not modified."""
        list1 = [self.account1, self.account2]
        list1_original = list1.copy()
        list2 = [self.account3]

        result, conflicts = AccountManager.merge_account_lists(list1, list2)

        # Verify list1 is unchanged
        self.assertEqual(list1, list1_original)
        self.assertIsNot(result, list1)  # Make sure result is a new list


if __name__ == "__main__":
    unittest.main()