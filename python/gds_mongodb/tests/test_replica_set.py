"""
Unit tests for MongoDB Replica Set Management functionality.

Tests the MongoDBReplicaSetManager class and its methods for managing
MongoDB replica sets.
"""

import unittest
from unittest.mock import MagicMock

from gds_database import (
    ConfigurationError,
    DatabaseConnectionError,
    QueryError,
)
from gds_mongodb.replica_set import MongoDBReplicaSetManager
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError


class TestMongoDBReplicaSetManager(unittest.TestCase):
    """Test cases for MongoDBReplicaSetManager class."""

    def setUp(self):
        """Set up test fixtures."""
        from gds_mongodb.connection import MongoDBConnection
        from pymongo import MongoClient

        # Create mock MongoClient
        self.mock_client = MagicMock(spec=MongoClient)
        self.mock_admin = MagicMock()
        self.mock_client.admin = self.mock_admin

        # Create mock connection
        self.mock_connection = MagicMock(spec=MongoDBConnection)
        self.mock_connection.client = self.mock_client

    def test_init_with_connection(self):
        """Test initialization with MongoDBConnection."""
        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        self.assertEqual(manager.client, self.mock_client)
        self.assertEqual(manager.connection, self.mock_connection)

    def test_init_with_client(self):
        """Test initialization with MongoClient."""
        manager = MongoDBReplicaSetManager(connection=self.mock_client)
        self.assertEqual(manager.client, self.mock_client)
        self.assertIsNone(manager.connection)

    def test_init_with_legacy_client_param(self):
        """Test initialization with legacy client parameter."""
        manager = MongoDBReplicaSetManager(client=self.mock_client)
        self.assertEqual(manager.client, self.mock_client)

    def test_init_no_connection(self):
        """Test initialization fails without connection."""
        with self.assertRaises(ValueError):
            MongoDBReplicaSetManager()

    def test_init_invalid_connection(self):
        """Test initialization fails with invalid connection type."""
        with self.assertRaises(ValueError):
            MongoDBReplicaSetManager(connection="invalid")

    def test_get_status_success(self):
        """Test successful replica set status retrieval."""
        expected_status = {
            "set": "myReplicaSet",
            "date": "2024-01-01T00:00:00Z",
            "myState": 1,
            "members": [
                {"name": "localhost:27017", "stateStr": "PRIMARY", "health": 1},
                {
                    "name": "localhost:27018",
                    "stateStr": "SECONDARY",
                    "health": 1,
                },
            ],
            "ok": 1,
        }
        self.mock_admin.command.return_value = expected_status

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        status = manager.get_status()

        self.assertEqual(status, expected_status)
        self.mock_admin.command.assert_called_once_with("replSetGetStatus")

    def test_get_status_not_replica_set(self):
        """Test get_status when not running as replica set."""
        self.mock_admin.command.side_effect = OperationFailure("not running with --replSet")

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)

        with self.assertRaises(DatabaseConnectionError) as context:
            manager.get_status()
        self.assertIn("not running as part of a replica set", str(context.exception))

    def test_get_status_operation_failure(self):
        """Test get_status with operation failure."""
        self.mock_admin.command.side_effect = OperationFailure("some error")

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)

        with self.assertRaises(QueryError):
            manager.get_status()

    def test_get_status_timeout(self):
        """Test get_status with server selection timeout."""
        self.mock_admin.command.side_effect = ServerSelectionTimeoutError("timeout")

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)

        with self.assertRaises(DatabaseConnectionError):
            manager.get_status()

    def test_get_config_success(self):
        """Test successful replica set configuration retrieval."""
        expected_config = {
            "_id": "myReplicaSet",
            "version": 1,
            "members": [
                {"_id": 0, "host": "localhost:27017"},
                {"_id": 1, "host": "localhost:27018"},
            ],
        }
        self.mock_admin.command.return_value = {"config": expected_config}

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        config = manager.get_config()

        self.assertEqual(config, expected_config)
        self.mock_admin.command.assert_called_once_with("replSetGetConfig")

    def test_add_member_success(self):
        """Test successful member addition."""
        existing_config = {
            "_id": "myReplicaSet",
            "version": 1,
            "members": [
                {"_id": 0, "host": "localhost:27017"},
                {"_id": 1, "host": "localhost:27018"},
            ],
        }

        # Mock get_config and reconfig
        self.mock_admin.command.side_effect = [
            {"config": existing_config},  # get_config
            {"ok": 1},  # reconfig
        ]

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        result = manager.add_member("localhost:27019")

        self.assertEqual(result["ok"], 1)

        # Verify reconfig was called with updated config
        calls = self.mock_admin.command.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1][0][0], "replSetReconfig")

        reconfig_arg = calls[1][0][1]
        self.assertEqual(reconfig_arg["version"], 2)
        self.assertEqual(len(reconfig_arg["members"]), 3)
        self.assertEqual(reconfig_arg["members"][2]["host"], "localhost:27019")

    def test_add_member_invalid_host(self):
        """Test add_member with invalid host format."""
        manager = MongoDBReplicaSetManager(connection=self.mock_connection)

        with self.assertRaises(ConfigurationError):
            manager.add_member("invalid_host")

    def test_add_member_already_exists(self):
        """Test add_member when member already exists."""
        existing_config = {
            "_id": "myReplicaSet",
            "version": 1,
            "members": [
                {"_id": 0, "host": "localhost:27017"},
                {"_id": 1, "host": "localhost:27018"},
            ],
        }
        self.mock_admin.command.return_value = {"config": existing_config}

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)

        with self.assertRaises(ConfigurationError) as context:
            manager.add_member("localhost:27017")
        self.assertIn("already exists", str(context.exception))

    def test_add_member_with_options(self):
        """Test add_member with various options."""
        existing_config = {
            "_id": "myReplicaSet",
            "version": 1,
            "members": [{"_id": 0, "host": "localhost:27017"}],
        }

        self.mock_admin.command.side_effect = [
            {"config": existing_config},
            {"ok": 1},
        ]

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        manager.add_member(
            "localhost:27019",
            priority=5,
            votes=1,
            hidden=False,
            tags={"dc": "east"},
        )

        # Get the reconfig call
        calls = self.mock_admin.command.call_args_list
        reconfig_arg = calls[1][0][1]
        new_member = reconfig_arg["members"][1]

        self.assertEqual(new_member["priority"], 5)
        self.assertEqual(new_member["tags"], {"dc": "east"})

    def test_add_member_arbiter(self):
        """Test adding an arbiter member."""
        existing_config = {
            "_id": "myReplicaSet",
            "version": 1,
            "members": [{"_id": 0, "host": "localhost:27017"}],
        }

        self.mock_admin.command.side_effect = [
            {"config": existing_config},
            {"ok": 1},
        ]

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        manager.add_member("localhost:27019", arbiter_only=True)

        calls = self.mock_admin.command.call_args_list
        reconfig_arg = calls[1][0][1]
        new_member = reconfig_arg["members"][1]

        self.assertTrue(new_member["arbiterOnly"])
        self.assertEqual(new_member["priority"], 0)

    def test_remove_member_success(self):
        """Test successful member removal."""
        existing_config = {
            "_id": "myReplicaSet",
            "version": 1,
            "members": [
                {"_id": 0, "host": "localhost:27017"},
                {"_id": 1, "host": "localhost:27018"},
                {"_id": 2, "host": "localhost:27019"},
            ],
        }

        self.mock_admin.command.side_effect = [
            {"config": existing_config},
            {"ok": 1},
        ]

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        result = manager.remove_member("localhost:27019")

        self.assertEqual(result["ok"], 1)

        calls = self.mock_admin.command.call_args_list
        reconfig_arg = calls[1][0][1]
        self.assertEqual(reconfig_arg["version"], 2)
        self.assertEqual(len(reconfig_arg["members"]), 2)

    def test_remove_member_not_found(self):
        """Test remove_member when member doesn't exist."""
        existing_config = {
            "_id": "myReplicaSet",
            "version": 1,
            "members": [{"_id": 0, "host": "localhost:27017"}],
        }
        self.mock_admin.command.return_value = {"config": existing_config}

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)

        with self.assertRaises(ConfigurationError) as context:
            manager.remove_member("localhost:27099")
        self.assertIn("not found", str(context.exception))

    def test_get_primary(self):
        """Test get_primary method."""
        status = {
            "set": "myReplicaSet",
            "members": [
                {"name": "localhost:27017", "stateStr": "PRIMARY"},
                {"name": "localhost:27018", "stateStr": "SECONDARY"},
            ],
        }
        self.mock_admin.command.return_value = status

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        primary = manager.get_primary()

        self.assertEqual(primary, "localhost:27017")

    def test_get_primary_none(self):
        """Test get_primary when no primary exists."""
        status = {
            "set": "myReplicaSet",
            "members": [
                {"name": "localhost:27017", "stateStr": "SECONDARY"},
                {"name": "localhost:27018", "stateStr": "SECONDARY"},
            ],
        }
        self.mock_admin.command.return_value = status

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        primary = manager.get_primary()

        self.assertIsNone(primary)

    def test_get_secondaries(self):
        """Test get_secondaries method."""
        status = {
            "set": "myReplicaSet",
            "members": [
                {"name": "localhost:27017", "stateStr": "PRIMARY"},
                {"name": "localhost:27018", "stateStr": "SECONDARY"},
                {"name": "localhost:27019", "stateStr": "SECONDARY"},
            ],
        }
        self.mock_admin.command.return_value = status

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        secondaries = manager.get_secondaries()

        self.assertEqual(len(secondaries), 2)
        self.assertIn("localhost:27018", secondaries)
        self.assertIn("localhost:27019", secondaries)

    def test_get_arbiters(self):
        """Test get_arbiters method."""
        status = {
            "set": "myReplicaSet",
            "members": [
                {"name": "localhost:27017", "stateStr": "PRIMARY"},
                {"name": "localhost:27018", "stateStr": "SECONDARY"},
                {"name": "localhost:27019", "stateStr": "ARBITER"},
            ],
        }
        self.mock_admin.command.return_value = status

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        arbiters = manager.get_arbiters()

        self.assertEqual(len(arbiters), 1)
        self.assertEqual(arbiters[0], "localhost:27019")

    def test_get_member_health(self):
        """Test get_member_health method."""
        status = {
            "set": "myReplicaSet",
            "members": [
                {"name": "localhost:27017", "health": 1},
                {"name": "localhost:27018", "health": 1},
                {"name": "localhost:27019", "health": 0},
            ],
        }
        self.mock_admin.command.return_value = status

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        health = manager.get_member_health()

        self.assertEqual(len(health), 3)
        self.assertTrue(health["localhost:27017"])
        self.assertTrue(health["localhost:27018"])
        self.assertFalse(health["localhost:27019"])

    def test_get_member_states(self):
        """Test get_member_states method."""
        status = {
            "set": "myReplicaSet",
            "members": [
                {"name": "localhost:27017", "stateStr": "PRIMARY"},
                {"name": "localhost:27018", "stateStr": "SECONDARY"},
                {"name": "localhost:27019", "stateStr": "RECOVERING"},
            ],
        }
        self.mock_admin.command.return_value = status

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        states = manager.get_member_states()

        self.assertEqual(states["localhost:27017"], "PRIMARY")
        self.assertEqual(states["localhost:27018"], "SECONDARY")
        self.assertEqual(states["localhost:27019"], "RECOVERING")

    def test_reconfigure_success(self):
        """Test successful reconfiguration."""
        new_config = {
            "_id": "myReplicaSet",
            "version": 2,
            "members": [{"_id": 0, "host": "localhost:27017"}],
        }

        self.mock_admin.command.return_value = {"ok": 1}

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        result = manager.reconfigure(new_config)

        self.assertEqual(result["ok"], 1)
        self.mock_admin.command.assert_called_once_with("replSetReconfig", new_config)

    def test_reconfigure_force(self):
        """Test forced reconfiguration."""
        new_config = {
            "_id": "myReplicaSet",
            "version": 2,
            "members": [{"_id": 0, "host": "localhost:27017"}],
        }

        self.mock_admin.command.return_value = {"ok": 1}

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        result = manager.reconfigure(new_config, force=True)

        self.assertEqual(result["ok"], 1)
        self.mock_admin.command.assert_called_once_with("replSetReconfig", new_config, force=True)

    def test_reconfigure_invalid_config(self):
        """Test reconfigure with invalid configuration."""
        manager = MongoDBReplicaSetManager(connection=self.mock_connection)

        # Missing version
        with self.assertRaises(ConfigurationError):
            manager.reconfigure({"_id": "myReplicaSet", "members": []})

        # Missing members
        with self.assertRaises(ConfigurationError):
            manager.reconfigure({"_id": "myReplicaSet", "version": 2})

        # Empty config
        with self.assertRaises(ConfigurationError):
            manager.reconfigure({})

    def test_step_down_success(self):
        """Test successful step down operation."""
        self.mock_admin.command.return_value = {"ok": 1}

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        result = manager.step_down(seconds=120)

        self.assertEqual(result["ok"], 1)
        self.mock_admin.command.assert_called_once_with("replSetStepDown", 120)

    def test_freeze_success(self):
        """Test successful freeze operation."""
        self.mock_admin.command.return_value = {"ok": 1}

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        result = manager.freeze(seconds=60)

        self.assertEqual(result["ok"], 1)
        self.mock_admin.command.assert_called_once_with("replSetFreeze", 60)

    def test_freeze_unfreeze(self):
        """Test unfreeze operation (freeze with 0 seconds)."""
        self.mock_admin.command.return_value = {"ok": 1}

        manager = MongoDBReplicaSetManager(connection=self.mock_connection)
        result = manager.freeze(seconds=0)

        self.assertEqual(result["ok"], 1)
        self.mock_admin.command.assert_called_once_with("replSetFreeze", 0)


if __name__ == "__main__":
    unittest.main()
