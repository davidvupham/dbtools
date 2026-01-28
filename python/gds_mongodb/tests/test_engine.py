"""Tests for MongoDB engine and database implementations."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from gds_database.metadata import (
    DatabaseState,
    DatabaseType,
)
from gds_mongodb.connection import MongoDBConnection
from gds_mongodb.engine import MongoDBDatabase, MongoDBEngine
from pymongo.errors import OperationFailure


@pytest.fixture
def mock_connection():
    """Create a mock MongoDBConnection."""
    conn = MagicMock(spec=MongoDBConnection)
    conn.client = MagicMock()
    conn.client.admin = MagicMock()
    conn.config = {"host": "localhost", "port": 27017}
    return conn


@pytest.fixture
def engine(mock_connection):
    """Create a MongoDBEngine with mock connection."""
    return MongoDBEngine(connection=mock_connection)


@pytest.fixture
def database(engine):
    """Create a MongoDBDatabase."""
    return MongoDBDatabase(engine=engine, name="testdb")


class TestMongoDBDatabase:
    """Tests for MongoDBDatabase class."""

    def test_name(self, database):
        """Database has correct name."""
        assert database.name == "testdb"
        assert str(database) == "testdb"

    def test_repr(self, database):
        """Database repr is descriptive."""
        assert "MongoDBDatabase" in repr(database)
        assert "testdb" in repr(database)

    def test_metadata(self, database, mock_connection):
        """Metadata is fetched from server."""
        mock_db = MagicMock()
        mock_connection.client.__getitem__.return_value = mock_db
        mock_db.command.return_value = {
            "dataSize": 1024000,
            "collections": 5,
            "objects": 1000,
            "indexes": 10,
            "storageSize": 2048000,
            "indexSize": 512000,
        }

        meta = database.metadata
        assert meta.name == "testdb"
        assert meta.type == DatabaseType.MONGODB
        assert meta.size_bytes == 1024000
        assert meta.state == DatabaseState.ONLINE

    def test_metadata_cached(self, database, mock_connection):
        """Metadata is cached after first access."""
        mock_db = MagicMock()
        mock_connection.client.__getitem__.return_value = mock_db
        mock_db.command.return_value = {"dataSize": 100}

        _ = database.metadata
        _ = database.metadata
        mock_db.command.assert_called_once()

    def test_refresh_metadata(self, database, mock_connection):
        """Refresh metadata fetches fresh data."""
        mock_db = MagicMock()
        mock_connection.client.__getitem__.return_value = mock_db
        mock_db.command.return_value = {"dataSize": 100}

        _ = database.metadata
        database.refresh_metadata()
        assert mock_db.command.call_count == 2

    def test_metadata_error_returns_unknown(self, database, mock_connection):
        """Metadata fetch error returns unknown state."""
        mock_db = MagicMock()
        mock_connection.client.__getitem__.return_value = mock_db
        mock_db.command.side_effect = Exception("not authorized")

        meta = database.metadata
        assert meta.state == DatabaseState.UNKNOWN

    def test_exists_true(self, database, mock_connection):
        """Database exists returns True when in list."""
        mock_connection.client.list_database_names.return_value = ["admin", "testdb"]
        assert database.exists() is True

    def test_exists_false(self, database, mock_connection):
        """Database exists returns False when not in list."""
        mock_connection.client.list_database_names.return_value = ["admin"]
        assert database.exists() is False

    def test_create(self, database, mock_connection):
        """Create materializes database with placeholder collection."""
        mock_db = MagicMock()
        mock_connection.client.__getitem__.return_value = mock_db

        result = database.create()
        assert result.success is True
        mock_db.create_collection.assert_called_once_with("_placeholder")

    def test_create_custom_collection(self, database, mock_connection):
        """Create with custom collection name."""
        mock_db = MagicMock()
        mock_connection.client.__getitem__.return_value = mock_db

        result = database.create(collection="init_data")
        assert result.success is True
        mock_db.create_collection.assert_called_once_with("init_data")

    def test_create_failure(self, database, mock_connection):
        """Create failure returns failure result."""
        mock_db = MagicMock()
        mock_connection.client.__getitem__.return_value = mock_db
        mock_db.create_collection.side_effect = Exception("already exists")

        result = database.create()
        assert result.success is False

    def test_drop(self, database, mock_connection):
        """Drop removes the database."""
        result = database.drop()
        assert result.success is True
        mock_connection.client.drop_database.assert_called_once_with("testdb")

    def test_drop_failure(self, database, mock_connection):
        """Drop failure returns failure result."""
        mock_connection.client.drop_database.side_effect = Exception("not authorized")
        result = database.drop()
        assert result.success is False

    def test_backup_not_supported(self, database):
        """Backup returns failure with instructions."""
        result = database.backup("/tmp/backup")
        assert result.success is False
        assert "mongodump" in result.message

    def test_restore_not_supported(self, database):
        """Restore returns failure with instructions."""
        result = database.restore("/tmp/backup")
        assert result.success is False
        assert "mongorestore" in result.message


class TestMongoDBEngine:
    """Tests for MongoDBEngine class."""

    def test_connection(self, engine, mock_connection):
        """Engine holds reference to connection."""
        assert engine.connection is mock_connection

    def test_metadata(self, engine, mock_connection):
        """Engine metadata is fetched from server."""
        mock_connection.client.server_info.return_value = {"version": "7.0.0"}
        mock_connection.client.admin.command.return_value = {"modules": ["enterprise"]}

        meta = engine.metadata
        assert meta.name == "mongodb"
        assert meta.version == "7.0.0"
        assert meta.edition == "enterprise"
        assert meta.status == "online"

    def test_metadata_community(self, engine, mock_connection):
        """Engine metadata defaults to community edition."""
        mock_connection.client.server_info.return_value = {"version": "7.0.0"}
        mock_connection.client.admin.command.return_value = {"modules": []}

        meta = engine.metadata
        assert meta.edition == "community"

    def test_metadata_error(self, engine, mock_connection):
        """Engine metadata returns unknown on error."""
        mock_connection.client.server_info.side_effect = Exception("timeout")

        meta = engine.metadata
        assert meta.version == "unknown"
        assert meta.status == "unknown"

    def test_get_version(self, engine, mock_connection):
        """Get version returns server version string."""
        mock_connection.client.server_info.return_value = {"version": "7.0.4"}
        assert engine.get_version() == "7.0.4"

    def test_get_server_time(self, engine, mock_connection):
        """Get server time returns datetime."""
        now = datetime.now()
        mock_connection.client.admin.command.return_value = {"localTime": now}
        assert engine.get_server_time() == now

    def test_list_databases(self, engine, mock_connection):
        """List databases returns MongoDBDatabase objects."""
        mock_connection.client.list_database_names.return_value = ["admin", "testdb"]
        dbs = engine.list_databases()
        assert len(dbs) == 2
        assert all(isinstance(db, MongoDBDatabase) for db in dbs)
        assert dbs[0].name == "admin"
        assert dbs[1].name == "testdb"

    def test_get_database(self, engine):
        """Get database returns MongoDBDatabase handle."""
        db = engine.get_database("mydb")
        assert isinstance(db, MongoDBDatabase)
        assert db.name == "mydb"
        assert db.engine is engine

    def test_startup(self, engine, mock_connection):
        """Startup connects to MongoDB."""
        result = engine.startup()
        assert result.success is True
        mock_connection.connect.assert_called_once()

    def test_startup_failure(self, engine, mock_connection):
        """Startup failure returns failure result."""
        mock_connection.connect.side_effect = Exception("refused")
        result = engine.startup()
        assert result.success is False

    def test_shutdown(self, engine, mock_connection):
        """Shutdown sends shutdown command."""
        mock_connection.client.admin.command.return_value = {"ok": 1}
        result = engine.shutdown()
        assert result.success is True

    def test_list_users(self, engine, mock_connection):
        """List users returns usernames."""
        mock_connection.client.admin.command.return_value = {
            "users": [{"user": "admin"}, {"user": "appuser"}]
        }
        users = engine.list_users()
        assert users == ["admin", "appuser"]

    def test_create_user(self, engine, mock_connection):
        """Create user calls createUser command."""
        mock_db = MagicMock()
        mock_connection.client.__getitem__.return_value = mock_db
        result = engine.create_user("newuser", "password123")
        assert result.success is True

    def test_create_user_failure(self, engine, mock_connection):
        """Create user failure returns failure result."""
        mock_db = MagicMock()
        mock_connection.client.__getitem__.return_value = mock_db
        mock_db.command.side_effect = OperationFailure("already exists")
        result = engine.create_user("existing", "pass")
        assert result.success is False

    def test_drop_user(self, engine, mock_connection):
        """Drop user calls dropUser command."""
        result = engine.drop_user("olduser")
        assert result.success is True

    def test_list_processes(self, engine, mock_connection):
        """List processes returns operation info."""
        mock_connection.client.admin.command.return_value = {
            "inprog": [
                {"opid": 1, "client": "192.168.1.1", "op": "query", "microsecs_running": 5000, "ns": "test.users"},
            ]
        }
        procs = engine.list_processes()
        assert len(procs) == 1
        assert procs[0]["id"] == 1
        assert procs[0]["duration_ms"] == 5.0

    def test_kill_process(self, engine, mock_connection):
        """Kill process calls killOp."""
        result = engine.kill_process("123")
        assert result.success is True

    def test_get_configuration(self, engine, mock_connection):
        """Get configuration returns server parameters."""
        mock_connection.client.admin.command.return_value = {
            "ok": 1,
            "logLevel": 0,
            "maxConnections": 1000,
        }
        config = engine.get_configuration()
        assert "logLevel" in config
        assert "ok" not in config

    def test_set_configuration(self, engine, mock_connection):
        """Set configuration updates a parameter."""
        result = engine.set_configuration("logLevel", 2)
        assert result.success is True

    def test_set_configuration_failure(self, engine, mock_connection):
        """Set configuration failure returns failure result."""
        mock_connection.client.admin.command.side_effect = OperationFailure("read-only")
        result = engine.set_configuration("readOnly", True)
        assert result.success is False

    def test_get_metrics(self, engine, mock_connection):
        """Get metrics returns Metric objects."""
        mock_connection.client.admin.command.return_value = {
            "connections": {"current": 10, "available": 990},
            "mem": {"resident": 512},
            "opcounters": {"query": 100, "insert": 50},
        }
        metrics = engine.get_metrics(datetime.now(), datetime.now())
        names = [m.name for m in metrics]
        assert "connections_current" in names
        assert "memory_resident_mb" in names
        assert "opcounter_query" in names

    def test_get_logs(self, engine, mock_connection):
        """Get logs returns log entries."""
        mock_connection.client.admin.command.return_value = {
            "log": ["line 1", "line 2"]
        }
        logs = engine.get_logs(datetime.now(), datetime.now())
        assert len(logs) == 2
        assert logs[0].message == "line 1"

    def test_get_replication_status_enabled(self, engine, mock_connection):
        """Get replication status for replica set."""
        mock_connection.client.admin.command.return_value = {
            "myState": 1,
            "members": [
                {"name": "host1:27017", "stateStr": "PRIMARY", "optimeDate": datetime(2025, 1, 1, 12, 0, 0)},
                {"name": "host2:27017", "stateStr": "SECONDARY", "optimeDate": datetime(2025, 1, 1, 12, 0, 0)},
            ],
        }
        status = engine.get_replication_status()
        assert status.enabled is True
        assert status.role == "primary"
        assert status.mode == "asynchronous"

    def test_get_replication_status_standalone(self, engine, mock_connection):
        """Get replication status for standalone."""
        mock_connection.client.admin.command.side_effect = OperationFailure("not running with --replSet")
        status = engine.get_replication_status()
        assert status.enabled is False
        assert status.role == "standalone"

    def test_failover(self, engine, mock_connection):
        """Failover initiates step-down."""
        result = engine.failover()
        assert result.success is True

    def test_failover_failure(self, engine, mock_connection):
        """Failover failure returns failure result."""
        mock_connection.client.admin.command.side_effect = OperationFailure("not primary")
        result = engine.failover()
        assert result.success is False

    def test_build_not_supported(self, engine):
        """Build returns failure (requires external tooling)."""
        result = engine.build()
        assert result.success is False

    def test_destroy_not_supported(self, engine):
        """Destroy returns failure (requires external tooling)."""
        result = engine.destroy()
        assert result.success is False
