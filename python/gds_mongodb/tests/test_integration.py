"""Integration tests for gds_mongodb against a live MongoDB replica set.

These tests require a running 3-member MongoDB replica set. Start it with:

    cd docker/mongodb
    podman-compose up -d   # or docker compose up -d

The replica set should be accessible at:
    - mongodb1: localhost:27017
    - mongodb2: localhost:27018
    - mongodb3: localhost:27019

Run these tests with:
    pytest python/gds_mongodb/tests/test_integration.py -v -m integration

All tests are marked with @pytest.mark.integration and will be skipped
automatically if MongoDB is not reachable.
"""

from __future__ import annotations

import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Connection parameters for the local replica set
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_RS = "mdbreplset1"
MONGO_TIMEOUT_MS = 3000


def _can_connect() -> bool:
    """Check if MongoDB replica set is reachable."""
    try:
        client = MongoClient(
            MONGO_HOST,
            MONGO_PORT,
            serverSelectionTimeoutMS=MONGO_TIMEOUT_MS,
            directConnection=True,
        )
        client.admin.command("ping")
        client.close()
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError, Exception):
        return False


requires_mongodb = pytest.mark.skipif(
    not _can_connect(),
    reason="MongoDB replica set not available at localhost:27017",
)

pytestmark = [pytest.mark.integration, requires_mongodb]


@pytest.fixture(scope="module")
def mongo_client():
    """Create a MongoClient connected to the replica set."""
    client = MongoClient(
        MONGO_HOST,
        MONGO_PORT,
        serverSelectionTimeoutMS=5000,
        directConnection=True,
    )
    yield client
    client.close()


@pytest.fixture(scope="module")
def rs_client():
    """Create a MongoClient connected via replica set name."""
    client = MongoClient(
        MONGO_HOST,
        MONGO_PORT,
        replicaSet=MONGO_RS,
        serverSelectionTimeoutMS=5000,
    )
    yield client
    client.close()


@pytest.fixture
def test_db_name():
    """Generate a unique test database name."""
    return f"test_gds_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_db(mongo_client, test_db_name):
    """Create a test database and clean up after."""
    db = mongo_client[test_db_name]
    yield db
    mongo_client.drop_database(test_db_name)


class TestConnectionIntegration:
    """Test MongoDBConnection against a live MongoDB instance."""

    def test_connect_and_ping(self, mongo_client):
        """Connection can ping the server."""
        result = mongo_client.admin.command("ping")
        assert result.get("ok") == 1.0

    def test_server_info(self, mongo_client):
        """Server info returns version string."""
        info = mongo_client.server_info()
        assert "version" in info
        assert isinstance(info["version"], str)

    def test_list_databases(self, mongo_client):
        """Can list databases on server."""
        db_names = mongo_client.list_database_names()
        assert isinstance(db_names, list)
        assert "admin" in db_names

    def test_mongodb_connection_class(self, test_db_name):
        """MongoDBConnection connects and disconnects cleanly."""
        from gds_mongodb import MongoDBConnection

        conn = MongoDBConnection(
            host=MONGO_HOST,
            port=MONGO_PORT,
            database=test_db_name,
            server_selection_timeout_ms=MONGO_TIMEOUT_MS,
            directConnection=True,
        )
        conn.connect()
        assert conn.is_connected() is True

        info = conn.get_connection_info()
        assert info["connected"] is True
        assert info["database"] == test_db_name
        assert "server_version" in info

        conn.disconnect()
        assert conn.is_connected() is False

    def test_mongodb_connection_context_manager(self, test_db_name):
        """MongoDBConnection works as context manager."""
        from gds_mongodb import MongoDBConnection

        with MongoDBConnection(
            host=MONGO_HOST,
            port=MONGO_PORT,
            database=test_db_name,
            server_selection_timeout_ms=MONGO_TIMEOUT_MS,
            directConnection=True,
        ) as conn:
            assert conn.is_connected() is True


class TestCRUDIntegration:
    """Test CRUD operations against a live MongoDB instance."""

    def test_insert_one(self, test_db):
        """Insert a single document."""
        result = test_db.test_collection.insert_one({"name": "Alice", "age": 30})
        assert result.inserted_id is not None

    def test_insert_many(self, test_db):
        """Insert multiple documents."""
        docs = [
            {"name": "Bob", "age": 25},
            {"name": "Carol", "age": 35},
            {"name": "Dave", "age": 28},
        ]
        result = test_db.test_collection.insert_many(docs)
        assert len(result.inserted_ids) == 3

    def test_find(self, test_db):
        """Query documents."""
        test_db.users.insert_many([
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Carol", "age": 35},
        ])
        results = list(test_db.users.find({"age": {"$gte": 30}}))
        assert len(results) == 2
        names = {doc["name"] for doc in results}
        assert names == {"Alice", "Carol"}

    def test_update_one(self, test_db):
        """Update a single document."""
        test_db.users.insert_one({"name": "Alice", "age": 30})
        result = test_db.users.update_one(
            {"name": "Alice"},
            {"$set": {"age": 31}},
        )
        assert result.modified_count == 1

        doc = test_db.users.find_one({"name": "Alice"})
        assert doc["age"] == 31

    def test_delete_one(self, test_db):
        """Delete a single document."""
        test_db.users.insert_one({"name": "Alice", "age": 30})
        result = test_db.users.delete_one({"name": "Alice"})
        assert result.deleted_count == 1
        assert test_db.users.count_documents({"name": "Alice"}) == 0

    def test_mongodb_connection_crud(self, test_db_name):
        """CRUD operations via MongoDBConnection class."""
        from gds_mongodb import MongoDBConnection

        conn = MongoDBConnection(
            host=MONGO_HOST,
            port=MONGO_PORT,
            database=test_db_name,
            server_selection_timeout_ms=MONGO_TIMEOUT_MS,
            directConnection=True,
        )
        conn.connect()

        try:
            # Insert
            result = conn.insert_one("users", {"name": "Alice", "age": 30})
            assert result["inserted_id"] is not None

            # Insert many
            result = conn.insert_many("users", [
                {"name": "Bob", "age": 25},
                {"name": "Carol", "age": 35},
            ])
            assert len(result["inserted_ids"]) == 2

            # Query
            results = conn.execute_query("users", {"age": {"$gte": 30}})
            assert len(results) == 2

            # Update
            result = conn.update_one("users", {"name": "Alice"}, {"$set": {"age": 31}})
            assert result["modified_count"] == 1

            # Delete
            result = conn.delete_one("users", {"name": "Bob"})
            assert result["deleted_count"] == 1

            # Collection names
            collections = conn.get_collection_names()
            assert "users" in collections

            # Column info
            fields = conn.get_column_info("users")
            field_names = [f["field_name"] for f in fields]
            assert "name" in field_names
            assert "age" in field_names

        finally:
            conn.disconnect()
            mongo_client = MongoClient(MONGO_HOST, MONGO_PORT, directConnection=True)
            mongo_client.drop_database(test_db_name)
            mongo_client.close()


class TestConfigurationIntegration:
    """Test MongoDBConfiguration against a live MongoDB instance."""

    def test_get_parameter(self, test_db_name):
        """Get a server parameter."""
        from gds_mongodb import MongoDBConfiguration, MongoDBConnection

        conn = MongoDBConnection(
            host=MONGO_HOST,
            port=MONGO_PORT,
            database=test_db_name,
            server_selection_timeout_ms=MONGO_TIMEOUT_MS,
            directConnection=True,
        )
        conn.connect()

        try:
            config = MongoDBConfiguration(conn)
            log_level = config.get("logLevel")
            assert log_level is not None
        finally:
            conn.disconnect()

    def test_get_all_parameters(self, test_db_name):
        """Get all server parameters."""
        from gds_mongodb import MongoDBConfiguration, MongoDBConnection

        conn = MongoDBConnection(
            host=MONGO_HOST,
            port=MONGO_PORT,
            database=test_db_name,
            server_selection_timeout_ms=MONGO_TIMEOUT_MS,
            directConnection=True,
        )
        conn.connect()

        try:
            config = MongoDBConfiguration(conn)
            all_params = config.get_all()
            assert isinstance(all_params, dict)
            assert len(all_params) > 0
        finally:
            conn.disconnect()


class TestEngineIntegration:
    """Test MongoDBEngine against a live MongoDB instance."""

    def test_engine_metadata(self, mongo_client):
        """Engine metadata returns valid server info."""
        from unittest.mock import MagicMock

        from gds_mongodb import MongoDBEngine

        mock_conn = MagicMock()
        mock_conn.client = mongo_client
        mock_conn.config = {"host": MONGO_HOST, "port": MONGO_PORT}

        engine = MongoDBEngine(connection=mock_conn)
        meta = engine.metadata
        assert meta.name == "mongodb"
        assert meta.version != "unknown"
        assert meta.status == "online"

    def test_engine_get_version(self, mongo_client):
        """Engine returns server version."""
        from unittest.mock import MagicMock

        from gds_mongodb import MongoDBEngine

        mock_conn = MagicMock()
        mock_conn.client = mongo_client
        mock_conn.config = {"host": MONGO_HOST, "port": MONGO_PORT}

        engine = MongoDBEngine(connection=mock_conn)
        version = engine.get_version()
        assert version != "unknown"
        # Version should look like X.Y.Z
        parts = version.split(".")
        assert len(parts) >= 2

    def test_engine_list_databases(self, mongo_client):
        """Engine lists databases."""
        from unittest.mock import MagicMock

        from gds_mongodb import MongoDBDatabase, MongoDBEngine

        mock_conn = MagicMock()
        mock_conn.client = mongo_client
        mock_conn.config = {"host": MONGO_HOST, "port": MONGO_PORT}

        engine = MongoDBEngine(connection=mock_conn)
        dbs = engine.list_databases()
        assert len(dbs) > 0
        assert all(isinstance(db, MongoDBDatabase) for db in dbs)

    def test_engine_get_metrics(self, mongo_client):
        """Engine returns server metrics."""
        from datetime import datetime
        from unittest.mock import MagicMock

        from gds_mongodb import MongoDBEngine

        mock_conn = MagicMock()
        mock_conn.client = mongo_client
        mock_conn.config = {"host": MONGO_HOST, "port": MONGO_PORT}

        engine = MongoDBEngine(connection=mock_conn)
        now = datetime.now()
        metrics = engine.get_metrics(now, now)
        assert len(metrics) > 0
        metric_names = [m.name for m in metrics]
        assert "connections_current" in metric_names

    def test_engine_get_configuration(self, mongo_client):
        """Engine returns server configuration."""
        from unittest.mock import MagicMock

        from gds_mongodb import MongoDBEngine

        mock_conn = MagicMock()
        mock_conn.client = mongo_client
        mock_conn.config = {"host": MONGO_HOST, "port": MONGO_PORT}

        engine = MongoDBEngine(connection=mock_conn)
        config = engine.get_configuration()
        assert isinstance(config, dict)
        assert len(config) > 0

    def test_engine_list_processes(self, mongo_client):
        """Engine lists active operations."""
        from unittest.mock import MagicMock

        from gds_mongodb import MongoDBEngine

        mock_conn = MagicMock()
        mock_conn.client = mongo_client
        mock_conn.config = {"host": MONGO_HOST, "port": MONGO_PORT}

        engine = MongoDBEngine(connection=mock_conn)
        procs = engine.list_processes()
        assert isinstance(procs, list)

    def test_database_metadata(self, mongo_client, test_db_name):
        """Database metadata returns valid info."""
        from unittest.mock import MagicMock

        from gds_database.metadata import DatabaseState, DatabaseType
        from gds_mongodb import MongoDBEngine

        # Create a collection so the DB actually exists
        mongo_client[test_db_name].create_collection("init")

        mock_conn = MagicMock()
        mock_conn.client = mongo_client
        mock_conn.config = {"host": MONGO_HOST, "port": MONGO_PORT}

        engine = MongoDBEngine(connection=mock_conn)
        db = engine.get_database(test_db_name)
        assert db.exists() is True

        meta = db.metadata
        assert meta.name == test_db_name
        assert meta.type == DatabaseType.MONGODB
        assert meta.state == DatabaseState.ONLINE

        # Clean up
        mongo_client.drop_database(test_db_name)

    def test_database_create_and_drop(self, mongo_client, test_db_name):
        """Database create and drop lifecycle."""
        from unittest.mock import MagicMock

        from gds_mongodb import MongoDBEngine

        mock_conn = MagicMock()
        mock_conn.client = mongo_client
        mock_conn.config = {"host": MONGO_HOST, "port": MONGO_PORT}

        engine = MongoDBEngine(connection=mock_conn)
        db = engine.get_database(test_db_name)

        # Create
        result = db.create()
        assert result.success is True
        assert db.exists() is True

        # Drop
        result = db.drop()
        assert result.success is True
        assert db.exists() is False


class TestReplicaSetIntegration:
    """Test replica set operations against a live replica set.

    These tests require the replica set to be initialized. If running
    against a standalone instance, these tests will be skipped.
    """

    @pytest.fixture
    def rs_manager(self, rs_client):
        """Create a MongoDBReplicaSetManager."""
        from gds_mongodb import MongoDBReplicaSetManager

        try:
            rs_client.admin.command("replSetGetStatus")
        except Exception:
            pytest.skip("Not connected to a replica set")

        return MongoDBReplicaSetManager(rs_client)

    def test_get_status(self, rs_manager):
        """Get replica set status."""
        status = rs_manager.get_status()
        assert "set" in status
        assert "members" in status
        assert len(status["members"]) >= 1

    def test_get_config(self, rs_manager):
        """Get replica set configuration."""
        config = rs_manager.get_config()
        assert "_id" in config
        assert "members" in config
        assert "version" in config

    def test_get_primary(self, rs_manager):
        """Get primary member."""
        primary = rs_manager.get_primary()
        assert primary is not None
        assert ":" in primary

    def test_get_secondaries(self, rs_manager):
        """Get secondary members."""
        secondaries = rs_manager.get_secondaries()
        assert isinstance(secondaries, list)

    def test_get_member_health(self, rs_manager):
        """Get member health status."""
        health = rs_manager.get_member_health()
        assert isinstance(health, dict)
        assert len(health) >= 1
        # At least one member should be healthy
        assert any(health.values())

    def test_get_member_states(self, rs_manager):
        """Get member states."""
        states = rs_manager.get_member_states()
        assert isinstance(states, dict)
        # Should have at least a PRIMARY
        assert "PRIMARY" in states.values()

    def test_get_replication_lag(self, rs_manager):
        """Get replication lag."""
        lag = rs_manager.get_replication_lag()
        assert isinstance(lag, dict)
        # All lag values should be non-negative
        for value in lag.values():
            assert value >= 0

    def test_get_replication_metrics(self, rs_manager):
        """Get replication metrics."""
        metrics = rs_manager.get_replication_metrics()
        assert "replication_lag" in metrics
        assert "member_states" in metrics
        assert "max_lag_seconds" in metrics

    def test_monitor_health(self, rs_manager):
        """Monitor replica set health."""
        health = rs_manager.monitor_health()
        assert "overall_health" in health
        assert "checks" in health
        assert "alerts" in health
        assert health["overall_health"] in {"healthy", "warning", "error", "critical"}

    def test_engine_replication_status(self, rs_client):
        """Engine reports replication status."""
        from unittest.mock import MagicMock

        from gds_mongodb import MongoDBEngine

        mock_conn = MagicMock()
        mock_conn.client = rs_client
        mock_conn.config = {"host": MONGO_HOST, "port": MONGO_PORT}

        engine = MongoDBEngine(connection=mock_conn)
        status = engine.get_replication_status()
        assert status.enabled is True
        assert status.role in {"primary", "secondary", "arbiter"}
        assert status.mode == "asynchronous"


class TestMonitoringIntegration:
    """Test monitoring against a live MongoDB instance."""

    def test_monitoring_check(self, test_db_name):
        """MongoDBMonitoring performs a health check."""
        from gds_mongodb import MongoDBConnection, MongoDBMonitoring

        conn = MongoDBConnection(
            host=MONGO_HOST,
            port=MONGO_PORT,
            database=test_db_name,
            server_selection_timeout_ms=MONGO_TIMEOUT_MS,
            directConnection=True,
        )
        conn.connect()

        try:
            monitoring = MongoDBMonitoring(conn)
            result = monitoring.check_health()
            assert result.is_healthy is True
            assert result.response_time_ms >= 0
        finally:
            conn.disconnect()

    def test_monitoring_server_status(self, test_db_name):
        """MongoDBMonitoring retrieves server status."""
        from gds_mongodb import MongoDBConnection, MongoDBMonitoring

        conn = MongoDBConnection(
            host=MONGO_HOST,
            port=MONGO_PORT,
            database=test_db_name,
            server_selection_timeout_ms=MONGO_TIMEOUT_MS,
            directConnection=True,
        )
        conn.connect()

        try:
            monitoring = MongoDBMonitoring(conn)
            status = monitoring.get_server_status()
            assert isinstance(status, dict)
            assert "connections" in status
        finally:
            conn.disconnect()
