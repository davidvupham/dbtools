"""
Unit tests for MongoDB Configuration Manager
"""

from unittest.mock import Mock

import pytest
from gds_mongodb.configuration import MongoDBConfiguration
from pymongo.errors import PyMongoError


class TestMongoDBConfiguration:
    """Test MongoDBConfiguration class"""

    def test_init_with_none_connection(self):
        """Test initialization with None connection raises ValueError"""
        with pytest.raises(ValueError, match="Connection cannot be None"):
            MongoDBConfiguration(None)

    def test_init_with_valid_connection(self):
        """Test initialization with valid connection"""
        mock_conn = Mock()
        config = MongoDBConfiguration(mock_conn)
        assert config._connection == mock_conn

    def test_get_single_configuration(self):
        """Test retrieving a single configuration"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        # Mock the command response
        mock_admin_db.command.return_value = {
            "logLevel": 0,
            "ok": 1,
            "$clusterTime": {},
            "operationTime": "timestamp",
        }

        config = MongoDBConfiguration(mock_conn)
        result = config.get("logLevel")

        assert result == 0
        mock_admin_db.command.assert_called_once_with("getParameter", 1, logLevel=1)

    def test_get_with_empty_name(self):
        """Test get with empty name raises ValueError"""
        mock_conn = Mock()
        config = MongoDBConfiguration(mock_conn)

        with pytest.raises(ValueError, match="Configuration name cannot be empty"):
            config.get("")

    def test_get_details(self):
        """Test retrieving configuration details"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        # Mock detailed response
        mock_admin_db.command.return_value = {
            "logLevel": {
                "value": 0,
                "settableAtRuntime": True,
                "settableAtStartup": True,
            },
            "ok": 1,
        }

        config = MongoDBConfiguration(mock_conn)
        result = config.get_details("logLevel")

        assert result["name"] == "logLevel"
        assert result["value"] == 0
        assert result["settable_at_runtime"] is True
        assert result["settable_at_startup"] is True

    def test_get_all(self):
        """Test retrieving all configurations"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        # Mock response with multiple parameters
        mock_admin_db.command.return_value = {
            "logLevel": 0,
            "quiet": False,
            "ok": 1,
            "$clusterTime": {},
        }

        config = MongoDBConfiguration(mock_conn)
        result = config.get_all()

        assert "logLevel" in result
        assert "quiet" in result
        assert "ok" not in result
        assert "$clusterTime" not in result

    def test_get_all_with_details(self):
        """Test retrieving all configurations with details"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {
            "logLevel": {
                "value": 0,
                "settableAtRuntime": True,
                "settableAtStartup": True,
            },
            "ok": 1,
        }

        config = MongoDBConfiguration(mock_conn)
        result = config.get_all(include_details=True)

        assert "logLevel" in result
        assert isinstance(result["logLevel"], dict)
        assert result["logLevel"]["value"] == 0

    def test_get_all_details(self):
        """Test retrieving all configurations as detail list"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {
            "logLevel": {
                "value": 0,
                "settableAtRuntime": True,
                "settableAtStartup": True,
            },
            "quiet": {"value": False, "settableAtRuntime": True},
            "ok": 1,
        }

        config = MongoDBConfiguration(mock_conn)
        result = config.get_all_details()

        assert len(result) == 2
        assert result[0]["name"] in ["logLevel", "quiet"]
        assert "value" in result[0]
        assert "settable_at_runtime" in result[0]

    def test_get_runtime_configurable(self):
        """Test retrieving runtime-configurable settings"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {
            "logLevel": 0,
            "quiet": False,
            "ok": 1,
        }

        config = MongoDBConfiguration(mock_conn)
        result = config.get_runtime_configurable()

        assert "logLevel" in result
        assert "ok" not in result

    def test_get_by_prefix(self):
        """Test retrieving configurations by prefix"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {
            "replSetName": "rs0",
            "replSetId": "123",
            "logLevel": 0,
            "ok": 1,
        }

        config = MongoDBConfiguration(mock_conn)
        result = config.get_by_prefix("repl")

        assert len(result) == 2
        assert "replSetName" in result
        assert "replSetId" in result
        assert "logLevel" not in result

    def test_get_by_prefix_empty(self):
        """Test get_by_prefix with empty prefix raises ValueError"""
        mock_conn = Mock()
        config = MongoDBConfiguration(mock_conn)

        with pytest.raises(ValueError, match="Prefix cannot be empty"):
            config.get_by_prefix("")

    def test_search_case_insensitive(self):
        """Test searching configurations (case insensitive)"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {
            "logLevel": 0,
            "systemLog": "/var/log/mongo.log",
            "quiet": False,
            "ok": 1,
        }

        config = MongoDBConfiguration(mock_conn)
        result = config.search("log")

        assert len(result) == 2
        assert "logLevel" in result
        assert "systemLog" in result

    def test_search_case_sensitive(self):
        """Test searching configurations (case sensitive)"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {
            "logLevel": 0,
            "LogFile": "/var/log/mongo.log",
            "quiet": False,
            "ok": 1,
        }

        config = MongoDBConfiguration(mock_conn)
        result = config.search("log", case_sensitive=True)

        assert len(result) == 1
        assert "logLevel" in result
        assert "LogFile" not in result

    def test_search_empty_keyword(self):
        """Test search with empty keyword raises ValueError"""
        mock_conn = Mock()
        config = MongoDBConfiguration(mock_conn)

        with pytest.raises(ValueError, match="Keyword cannot be empty"):
            config.search("")

    def test_set_configuration(self):
        """Test setting a configuration"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {"ok": 1, "was": 0}

        config = MongoDBConfiguration(mock_conn)
        result = config.set("logLevel", 2)

        assert result["ok"] == 1
        mock_admin_db.command.assert_called_once_with(setParameter=1, logLevel=2)

    def test_set_with_comment(self):
        """Test setting a configuration with comment"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {"ok": 1}

        config = MongoDBConfiguration(mock_conn)
        config.set("logLevel", 2, comment="Increase logging")

        mock_admin_db.command.assert_called_once_with(setParameter=1, logLevel=2, comment="Increase logging")

    def test_set_empty_name(self):
        """Test set with empty name raises ValueError"""
        mock_conn = Mock()
        config = MongoDBConfiguration(mock_conn)

        with pytest.raises(ValueError, match="Configuration name cannot be empty"):
            config.set("", 123)

    def test_set_startup_only_parameter(self):
        """Test setting startup-only configuration raises error"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.side_effect = PyMongoError("Parameter is settable at startup only")

        config = MongoDBConfiguration(mock_conn)

        with pytest.raises(PyMongoError, match="can only be set at startup, not at runtime"):
            config.set("someParam", 123)

    def test_set_multiple(self):
        """Test setting multiple configurations"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {"ok": 1}

        config = MongoDBConfiguration(mock_conn)
        settings = {"logLevel": 2, "quiet": False}
        result = config.set_multiple(settings)

        assert result["ok"] == 1
        mock_admin_db.command.assert_called_once_with(setParameter=1, logLevel=2, quiet=False)

    def test_set_multiple_with_comment(self):
        """Test setting multiple configurations with comment"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {"ok": 1}

        config = MongoDBConfiguration(mock_conn)
        settings = {"logLevel": 2, "quiet": False}
        config.set_multiple(settings, comment="Batch update")

        mock_admin_db.command.assert_called_once_with(setParameter=1, logLevel=2, quiet=False, comment="Batch update")

    def test_set_multiple_empty_dict(self):
        """Test set_multiple with empty dict raises ValueError"""
        mock_conn = Mock()
        config = MongoDBConfiguration(mock_conn)

        with pytest.raises(ValueError, match="Settings dictionary cannot be empty"):
            config.set_multiple({})

    def test_reset_known_default(self):
        """Test resetting a configuration with known default"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {"ok": 1}

        config = MongoDBConfiguration(mock_conn)
        result = config.reset("logLevel")

        assert result is True
        mock_admin_db.command.assert_called_once_with(setParameter=1, logLevel=0)

    def test_reset_unknown_default(self):
        """Test resetting configuration with unknown default"""
        mock_conn = Mock()
        config = MongoDBConfiguration(mock_conn)

        result = config.reset("unknownParam")
        assert result is False

    def test_to_dict(self):
        """Test converting to dictionary"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True
        mock_admin_db = Mock()
        mock_conn.get_client.return_value.admin = mock_admin_db

        mock_admin_db.command.return_value = {
            "logLevel": 0,
            "quiet": False,
            "ok": 1,
        }

        config = MongoDBConfiguration(mock_conn)
        result = config.to_dict()

        assert "logLevel" in result
        assert "quiet" in result

    def test_repr(self):
        """Test string representation"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = True

        config = MongoDBConfiguration(mock_conn)
        repr_str = repr(config)

        assert "MongoDBConfiguration" in repr_str
        assert "connected=True" in repr_str

    def test_not_connected_raises_error(self):
        """Test operations when not connected raise RuntimeError"""
        mock_conn = Mock()
        mock_conn.is_connected.return_value = False

        config = MongoDBConfiguration(mock_conn)

        with pytest.raises(
            RuntimeError,
            match="Connection must be established before accessing configuration",
        ):
            config.get("logLevel")
