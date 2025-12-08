"""
Unit tests for the SnowflakeAccount class.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from gds_snowflake.account import AccountInfo, SnowflakeAccount


class TestAccountInfo(unittest.TestCase):
    """Test cases for AccountInfo dataclass."""

    def test_account_info_creation(self):
        """Test creating an AccountInfo object."""
        account = AccountInfo(
            account_name="TEST_ACCOUNT",
            organization_name="TEST_ORG",
            account_locator="ABC123",
            region="us-west-2",
            cloud_provider="AWS",
        )

        self.assertEqual(account.account_name, "TEST_ACCOUNT")
        self.assertEqual(account.organization_name, "TEST_ORG")
        self.assertEqual(account.account_locator, "ABC123")
        self.assertEqual(account.region, "us-west-2")
        self.assertEqual(account.cloud_provider, "AWS")

    def test_account_info_to_dict(self):
        """Test converting AccountInfo to dictionary."""
        account = AccountInfo(
            account_name="TEST_ACCOUNT",
            organization_name="TEST_ORG",
            is_org_admin=True,
        )

        account_dict = account.to_dict()

        self.assertIsInstance(account_dict, dict)
        self.assertEqual(account_dict["account_name"], "TEST_ACCOUNT")
        self.assertEqual(account_dict["organization_name"], "TEST_ORG")
        self.assertEqual(account_dict["is_org_admin"], True)

    def test_account_info_defaults(self):
        """Test AccountInfo default values."""
        account = AccountInfo(account_name="TEST")

        self.assertIsNone(account.organization_name)
        self.assertIsNone(account.region)
        self.assertFalse(account.is_org_admin)
        self.assertFalse(account.is_current)


class TestSnowflakeAccount(unittest.TestCase):
    """Test cases for SnowflakeAccount class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.mock_connection.account = "TEST_ACCOUNT"

        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests."""
        # Clean up temp directory
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init_default_data_dir(self):
        """Test initialization with default data directory."""
        with patch.dict(os.environ, {}, clear=True):
            account_mgr = SnowflakeAccount(self.mock_connection)
            self.assertEqual(account_mgr.data_dir, Path("./data"))

    def test_init_with_env_data_dir(self):
        """Test initialization with GDS_DATA_DIR environment variable."""
        with patch.dict(os.environ, {"GDS_DATA_DIR": self.temp_dir}):
            account_mgr = SnowflakeAccount(self.mock_connection)
            self.assertEqual(account_mgr.data_dir, Path(self.temp_dir))

    def test_init_with_explicit_data_dir(self):
        """Test initialization with explicit data directory."""
        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)
        self.assertEqual(account_mgr.data_dir, Path(self.temp_dir))

    def test_data_directory_creation(self):
        """Test that data directory is created if it doesn't exist."""
        test_dir = os.path.join(self.temp_dir, "test_data")
        self.assertFalse(os.path.exists(test_dir))

        _account_mgr = SnowflakeAccount(self.mock_connection, data_dir=test_dir)

        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))

    def test_get_current_account(self):
        """Test get_current_account method."""
        mock_results = [
            {
                "ACCOUNT_NAME": "TEST_ACCOUNT",
                "ORGANIZATION_NAME": "TEST_ORG",
                "ACCOUNT_LOCATOR": "ABC123",
                "REGION": "us-west-2",
            }
        ]

        self.mock_connection.execute_query_dict.return_value = mock_results

        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)
        current_account = account_mgr.get_current_account()

        self.assertIsInstance(current_account, AccountInfo)
        self.assertEqual(current_account.account_name, "TEST_ACCOUNT")
        self.assertEqual(current_account.organization_name, "TEST_ORG")
        self.assertTrue(current_account.is_current)
        self.assertIsNotNone(current_account.retrieved_at)

    def test_get_all_accounts(self):
        """Test get_all_accounts method."""
        mock_results = [
            {
                "ACCOUNT_NAME": "ACCOUNT1",
                "ORGANIZATION_NAME": "TEST_ORG",
                "ACCOUNT_LOCATOR": "ABC123",
                "ACCOUNT_LOCATOR_URL": "https://abc123.snowflakecomputing.com",
                "REGION": "us-west-2",
                "CLOUD": "AWS",
                "CREATED_ON": datetime(2023, 1, 1),
                "COMMENT": "Test account 1",
                "IS_ORG_ADMIN": True,
                "EDITION": "ENTERPRISE",
            },
            {
                "ACCOUNT_NAME": "ACCOUNT2",
                "ORGANIZATION_NAME": "TEST_ORG",
                "ACCOUNT_LOCATOR": "XYZ789",
                "ACCOUNT_LOCATOR_URL": "https://xyz789.snowflakecomputing.com",
                "REGION": "us-east-1",
                "CLOUD": "AWS",
                "CREATED_ON": datetime(2023, 2, 1),
                "COMMENT": "Test account 2",
                "IS_ORG_ADMIN": False,
                "EDITION": "STANDARD",
            },
        ]

        self.mock_connection.execute_query_dict.return_value = mock_results

        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)
        accounts = account_mgr.get_all_accounts()

        self.assertEqual(len(accounts), 2)
        self.assertIsInstance(accounts[0], AccountInfo)
        self.assertEqual(accounts[0].account_name, "ACCOUNT1")
        self.assertEqual(accounts[0].cloud_provider, "AWS")
        self.assertTrue(accounts[0].is_org_admin)
        self.assertEqual(accounts[1].account_name, "ACCOUNT2")
        self.assertEqual(accounts[1].account_edition, "STANDARD")

    def test_get_account_parameters(self):
        """Test get_account_parameters method."""
        mock_results = [
            {"key": "TIMEZONE", "value": "America/Los_Angeles"},
            {"key": "WEEK_START", "value": "0"},
            {"KEY": "MAX_CONCURRENCY_LEVEL", "VALUE": "8"},
        ]

        self.mock_connection.execute_query_dict.return_value = mock_results

        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)
        parameters = account_mgr.get_account_parameters()

        self.assertIsInstance(parameters, dict)
        self.assertEqual(parameters["TIMEZONE"], "America/Los_Angeles")
        self.assertEqual(parameters["WEEK_START"], "0")
        self.assertEqual(parameters["MAX_CONCURRENCY_LEVEL"], "8")

    def test_save_accounts_to_json(self):
        """Test saving accounts to JSON file."""
        accounts = [
            AccountInfo(
                account_name="ACCOUNT1",
                organization_name="TEST_ORG",
                region="us-west-2",
                cloud_provider="AWS",
            ),
            AccountInfo(
                account_name="ACCOUNT2",
                organization_name="TEST_ORG",
                region="us-east-1",
                cloud_provider="Azure",
            ),
        ]

        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)
        filepath = account_mgr.save_accounts_to_json(accounts, filename="test_accounts.json")

        self.assertTrue(filepath.exists())
        self.assertEqual(filepath.name, "test_accounts.json")

        # Verify JSON content
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("metadata", data)
        self.assertIn("accounts", data)
        self.assertEqual(data["metadata"]["account_count"], 2)
        self.assertEqual(len(data["accounts"]), 2)
        self.assertEqual(data["accounts"][0]["account_name"], "ACCOUNT1")

    def test_save_accounts_with_auto_filename(self):
        """Test saving accounts with automatically generated filename."""
        accounts = [AccountInfo(account_name="ACCOUNT1", organization_name="TEST_ORG")]

        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)
        filepath = account_mgr.save_accounts_to_json(accounts)

        self.assertTrue(filepath.exists())
        self.assertTrue(filepath.name.startswith("snowflake_accounts_"))
        self.assertTrue(filepath.name.endswith(".json"))

    def test_load_accounts_from_json(self):
        """Test loading accounts from JSON file."""
        # Create test data
        test_data = {
            "metadata": {"retrieved_at": "2023-01-01T00:00:00", "account_count": 2},
            "accounts": [
                {
                    "account_name": "ACCOUNT1",
                    "organization_name": "TEST_ORG",
                    "account_locator": "ABC123",
                    "region": "us-west-2",
                    "cloud_provider": "AWS",
                    "account_url": None,
                    "created_on": None,
                    "comment": None,
                    "is_org_admin": True,
                    "account_edition": "ENTERPRISE",
                    "is_current": False,
                    "retrieved_at": "2023-01-01T00:00:00",
                },
                {
                    "account_name": "ACCOUNT2",
                    "organization_name": "TEST_ORG",
                    "account_locator": "XYZ789",
                    "region": "us-east-1",
                    "cloud_provider": "Azure",
                    "account_url": None,
                    "created_on": None,
                    "comment": None,
                    "is_org_admin": False,
                    "account_edition": "STANDARD",
                    "is_current": False,
                    "retrieved_at": "2023-01-01T00:00:00",
                },
            ],
        }

        # Save test data
        test_file = os.path.join(self.temp_dir, "test_load.json")
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        # Load accounts
        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)
        accounts = account_mgr.load_accounts_from_json("test_load.json")

        self.assertEqual(len(accounts), 2)
        self.assertIsInstance(accounts[0], AccountInfo)
        self.assertEqual(accounts[0].account_name, "ACCOUNT1")
        self.assertTrue(accounts[0].is_org_admin)
        self.assertEqual(accounts[1].account_name, "ACCOUNT2")

    def test_load_accounts_file_not_found(self):
        """Test loading accounts from non-existent file."""
        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)

        with self.assertRaises(FileNotFoundError):
            account_mgr.load_accounts_from_json("nonexistent.json")

    def test_get_account_summary(self):
        """Test generating account summary."""
        accounts = [
            AccountInfo(
                account_name="ACCOUNT1",
                organization_name="ORG1",
                region="us-west-2",
                cloud_provider="AWS",
                account_edition="ENTERPRISE",
                is_org_admin=True,
            ),
            AccountInfo(
                account_name="ACCOUNT2",
                organization_name="ORG1",
                region="us-east-1",
                cloud_provider="AWS",
                account_edition="STANDARD",
                is_org_admin=False,
            ),
            AccountInfo(
                account_name="ACCOUNT3",
                organization_name="ORG2",
                region="us-west-2",
                cloud_provider="Azure",
                account_edition="ENTERPRISE",
                is_org_admin=True,
            ),
        ]

        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)
        summary = account_mgr.get_account_summary(accounts)

        self.assertEqual(summary["total_accounts"], 3)
        self.assertEqual(summary["organizations"], 2)
        self.assertEqual(summary["regions"]["us-west-2"], 2)
        self.assertEqual(summary["regions"]["us-east-1"], 1)
        self.assertEqual(summary["cloud_providers"]["AWS"], 2)
        self.assertEqual(summary["cloud_providers"]["Azure"], 1)
        self.assertEqual(summary["editions"]["ENTERPRISE"], 2)
        self.assertEqual(summary["editions"]["STANDARD"], 1)
        self.assertEqual(summary["org_admin_accounts"], 2)

    def test_list_saved_account_files(self):
        """Test listing saved account files."""
        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)

        # Create some test files
        test_files = [
            "snowflake_accounts_20230101_120000.json",
            "snowflake_accounts_20230102_120000.json",
            "snowflake_accounts_20230103_120000.json",
        ]

        for filename in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"metadata": {}, "accounts": []}, f)

        # List files
        files = account_mgr.list_saved_account_files()

        self.assertEqual(len(files), 3)
        # Should be sorted in reverse order (most recent first)
        self.assertTrue(all(isinstance(f, Path) for f in files))

    def test_get_latest_account_file(self):
        """Test getting the latest account file."""
        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)

        # Create test files with different timestamps
        test_files = [
            "snowflake_accounts_20230101_120000.json",
            "snowflake_accounts_20230103_120000.json",  # Latest
            "snowflake_accounts_20230102_120000.json",
        ]

        for filename in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"metadata": {}, "accounts": []}, f)

        # Get latest file
        latest = account_mgr.get_latest_account_file()

        self.assertIsNotNone(latest)
        self.assertIn("20230103", latest.name)

    def test_get_latest_account_file_empty(self):
        """Test getting latest file when no files exist."""
        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)
        latest = account_mgr.get_latest_account_file()

        self.assertIsNone(latest)

    def test_error_handling_get_current_account(self):
        """Test error handling in get_current_account."""
        self.mock_connection.execute_query_dict.side_effect = Exception("Query failed")

        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)

        with self.assertRaises(Exception):
            account_mgr.get_current_account()

    def test_error_handling_get_all_accounts(self):
        """Test error handling in get_all_accounts."""
        self.mock_connection.execute_query_dict.side_effect = Exception("Permission denied")

        account_mgr = SnowflakeAccount(self.mock_connection, data_dir=self.temp_dir)

        with self.assertRaises(Exception):
            account_mgr.get_all_accounts()


if __name__ == "__main__":
    unittest.main()
