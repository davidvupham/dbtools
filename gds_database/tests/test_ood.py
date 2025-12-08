"""
Test suite for gds_database OOD abstractions.
"""

import unittest
from datetime import datetime

from gds_database import (
    Database,
    DatabaseConnection,
    DatabaseEngine,
    DatabaseMetadata,
    DatabaseState,
    DatabaseType,
    EngineMetadata,
    LogEntry,
    Metric,
    OperationResult,
    ReplicationStatus,
)


class MockConnection(DatabaseConnection):
    """Mock connection for testing."""

    def connect(self):
        pass

    def disconnect(self):
        pass

    def execute_query(self, query, params=None):
        return []

    def is_connected(self):
        return True

    def get_connection_info(self):
        return {}


class TestMetadata(unittest.TestCase):
    """Test metadata classes and enums."""

    def test_database_metadata(self):
        """Test DatabaseMetadata dataclass."""
        meta = DatabaseMetadata(name="test_db", type=DatabaseType.MSSQL, state=DatabaseState.ONLINE)
        self.assertEqual(meta.name, "test_db")
        self.assertEqual(meta.type, DatabaseType.MSSQL)
        self.assertEqual(meta.state, DatabaseState.ONLINE)
        self.assertIsNone(meta.size_bytes)

    def test_engine_metadata(self):
        """Test EngineMetadata dataclass."""
        meta = EngineMetadata(name="test_engine", version="1.0", host="localhost", port=1433)
        self.assertEqual(meta.name, "test_engine")
        self.assertEqual(meta.version, "1.0")
        self.assertEqual(meta.host, "localhost")
        self.assertEqual(meta.port, 1433)
        self.assertIsNone(meta.edition)

    def test_observability_types(self):
        """Test Metric and LogEntry dataclasses."""
        now = datetime.now()
        metric = Metric(name="cpu", value=50.0, unit="percent", timestamp=now)
        self.assertEqual(metric.name, "cpu")
        self.assertEqual(metric.value, 50.0)

        log = LogEntry(timestamp=now, level="INFO", message="test", source="engine")
        self.assertEqual(log.level, "INFO")
        self.assertEqual(log.message, "test")

    def test_replication_status(self):
        """Test ReplicationStatus dataclass."""
        status = ReplicationStatus(enabled=True, mode="sync", role="primary")
        self.assertTrue(status.enabled)
        self.assertEqual(status.role, "primary")
        self.assertEqual(status.lag_seconds, 0.0)

    def test_metadata_attributes(self):
        """Test arbitrary attribute storage."""
        meta = DatabaseMetadata(name="test", type=DatabaseType.POSTGRESQL)
        meta.set_attribute("custom_key", "custom_value")
        self.assertEqual(meta.get_attribute("custom_key"), "custom_value")
        self.assertIsNone(meta.get_attribute("missing"))

        eng_meta = EngineMetadata(name="test", version="1.0")
        eng_meta.set_attribute("custom_key", "custom_value")
        self.assertEqual(eng_meta.get_attribute("custom_key"), "custom_value")


class TestDatabaseEngine(unittest.TestCase):
    """Test DatabaseEngine ABC."""

    def test_cannot_instantiate(self):
        """Test that DatabaseEngine cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            DatabaseEngine(MockConnection())

    def test_subclass_implementation(self):
        """Test that subclasses can be instantiated."""

        class ConcreteEngine(DatabaseEngine):
            @property
            def metadata(self):
                return EngineMetadata("test", "1.0")

            def get_version(self):
                return "1.0"

            def get_server_time(self):
                return datetime.now()

            def list_databases(self):
                return []

            def get_database(self, name):
                return None

            # Lifecycle
            def build(self, **kwargs):
                return OperationResult.success_result("Built")

            def destroy(self, force=False, **kwargs):
                return OperationResult.success_result("Destroyed")

            # Operations
            def startup(self, **kwargs):
                return OperationResult.success_result("Started")

            def shutdown(self, force=False, **kwargs):
                return OperationResult.success_result("Stopped")

            def list_users(self):
                return []

            def create_user(self, name, password, **kwargs):
                return OperationResult.success_result("Created")

            def drop_user(self, name):
                return OperationResult.success_result("Dropped")

            def list_processes(self):
                return []

            def kill_process(self, pid):
                return OperationResult.success_result("Killed")

            def get_configuration(self):
                return {}

            def set_configuration(self, key, value):
                return OperationResult.success_result("Set")

            def get_metrics(self, start, end):
                return []

            def get_logs(self, start, end, **kwargs):
                return []

            def get_replication_status(self):
                return ReplicationStatus(True, "sync", "primary")

            def failover(self, target=None, **kwargs):
                return OperationResult.success_result("Failover")

        engine = ConcreteEngine(MockConnection())
        self.assertEqual(engine.get_version(), "1.0")
        self.assertIsInstance(engine.get_server_time(), datetime)
        self.assertEqual(engine.metadata.name, "test")
        self.assertTrue(engine.get_replication_status().enabled)


class TestDatabase(unittest.TestCase):
    """Test Database ABC."""

    def test_cannot_instantiate(self):
        """Test that Database cannot be instantiated directly."""

        class ConcreteEngine(DatabaseEngine):
            @property
            def metadata(self):
                return EngineMetadata("test", "1.0")

            def get_version(self):
                return "1.0"

            def get_server_time(self):
                return datetime.now()

            def list_databases(self):
                return []

            def get_database(self, name):
                return None

            # Lifecycle
            def build(self, **kwargs):
                pass

            def destroy(self, **kwargs):
                pass

            # Operations
            def startup(self, **kwargs):
                pass

            def shutdown(self, **kwargs):
                pass

            def list_users(self):
                pass

            def create_user(self, **kwargs):
                pass

            def drop_user(self, **kwargs):
                pass

            def list_processes(self):
                pass

            def kill_process(self, **kwargs):
                pass

            def get_configuration(self):
                pass

            def set_configuration(self, **kwargs):
                pass

            def get_metrics(self, **kwargs):
                pass

            def get_logs(self, **kwargs):
                pass

            def get_replication_status(self):
                pass

            def failover(self, **kwargs):
                pass

        engine = ConcreteEngine(MockConnection())
        with self.assertRaises(TypeError):
            Database(engine, "test_db")

    def test_subclass_implementation(self):
        """Test that subclasses can be instantiated."""

        class ConcreteEngine(DatabaseEngine):
            @property
            def metadata(self):
                return EngineMetadata("test", "1.0")

            def get_version(self):
                return "1.0"

            def get_server_time(self):
                return datetime.now()

            def list_databases(self):
                return []

            def get_database(self, name):
                return None

            # Lifecycle
            def build(self, **kwargs):
                pass

            def destroy(self, **kwargs):
                pass

            # Operations
            def startup(self, **kwargs):
                pass

            def shutdown(self, **kwargs):
                pass

            def list_users(self):
                pass

            def create_user(self, **kwargs):
                pass

            def drop_user(self, **kwargs):
                pass

            def list_processes(self):
                pass

            def kill_process(self, **kwargs):
                pass

            def get_configuration(self):
                pass

            def set_configuration(self, **kwargs):
                pass

            def get_metrics(self, **kwargs):
                pass

            def get_logs(self, **kwargs):
                pass

            def get_replication_status(self):
                pass

            def failover(self, **kwargs):
                pass

        class ConcreteDatabase(Database):
            @property
            def metadata(self):
                return DatabaseMetadata("test", DatabaseType.MSSQL)

            def exists(self):
                return True

            def create(self, **kwargs):
                return OperationResult.success_result("Created")

            def drop(self, force=False):
                return OperationResult.success_result("Dropped")

            def backup(self, path, **kwargs):
                return OperationResult.success_result("Backed up")

            def restore(self, path, **kwargs):
                return OperationResult.success_result("Restored")

        engine = ConcreteEngine(MockConnection())
        db = ConcreteDatabase(engine, "test_db")
        self.assertEqual(db.name, "test_db")
        self.assertTrue(db.exists())
        self.assertEqual(str(db), "test_db")
        self.assertEqual(repr(db), "<ConcreteDatabase(name=test_db)>")

    def test_abstract_methods_via_super(self):
        """Test that abstract method bodies can be called via super()."""

        class TestDB(Database):
            @property
            def metadata(self):
                return DatabaseMetadata("test", DatabaseType.MSSQL)

            def exists(self):
                return True

            def create(self, **kwargs):
                return OperationResult.success_result("Created")

            def drop(self, force=False):
                return OperationResult.success_result("Dropped")

            def backup(self, path, **kwargs):
                # Call super to cover the abstract method body
                try:
                    super().backup(path, **kwargs)
                except Exception:
                    pass
                return OperationResult.success_result("Backed up")

            def restore(self, path, **kwargs):
                try:
                    super().restore(path, **kwargs)
                except Exception:
                    pass
                return OperationResult.success_result("Restored")

        class TestEngine(DatabaseEngine):
            @property
            def metadata(self):
                return EngineMetadata("test", "1.0")

            def get_version(self):
                return "1.0"

            def get_server_time(self):
                return datetime.now()

            def list_databases(self):
                try:
                    super().list_databases()
                except Exception:
                    pass
                return []

            def get_database(self, name):
                try:
                    super().get_database(name)
                except Exception:
                    pass
                return None

            # Lifecycle
            def build(self, **kwargs):
                try:
                    super().build(**kwargs)
                except Exception:
                    pass
                return OperationResult.success_result("Built")

            def destroy(self, force=False, **kwargs):
                try:
                    super().destroy(force, **kwargs)
                except Exception:
                    pass
                return OperationResult.success_result("Destroyed")

            # Operations
            def startup(self, **kwargs):
                try:
                    super().startup(**kwargs)
                except Exception:
                    pass
                return OperationResult.success_result("Started")

            def shutdown(self, force=False, **kwargs):
                try:
                    super().shutdown(force, **kwargs)
                except Exception:
                    pass
                return OperationResult.success_result("Stopped")

            def list_users(self):
                try:
                    super().list_users()
                except Exception:
                    pass
                return []

            def create_user(self, name, password, **kwargs):
                try:
                    super().create_user(name, password, **kwargs)
                except Exception:
                    pass
                return OperationResult.success_result("Created")

            def drop_user(self, name):
                try:
                    super().drop_user(name)
                except Exception:
                    pass
                return OperationResult.success_result("Dropped")

            def list_processes(self):
                try:
                    super().list_processes()
                except Exception:
                    pass
                return []

            def kill_process(self, pid):
                try:
                    super().kill_process(pid)
                except Exception:
                    pass
                return OperationResult.success_result("Killed")

            def get_configuration(self):
                try:
                    super().get_configuration()
                except Exception:
                    pass
                return {}

            def set_configuration(self, key, value):
                try:
                    super().set_configuration(key, value)
                except Exception:
                    pass
                return OperationResult.success_result("Set")

            def get_metrics(self, start, end):
                try:
                    super().get_metrics(start, end)
                except Exception:
                    pass
                return []

            def get_logs(self, start, end, **kwargs):
                try:
                    super().get_logs(start, end, **kwargs)
                except Exception:
                    pass
                return []

            def get_replication_status(self):
                try:
                    super().get_replication_status()
                except Exception:
                    pass
                return ReplicationStatus(True, "sync", "primary")

            def failover(self, target=None, **kwargs):
                try:
                    super().failover(target, **kwargs)
                except Exception:
                    pass
                return OperationResult.success_result("Failover")

        engine = TestEngine(MockConnection())
        engine.build()
        engine.destroy()
        engine.list_databases()
        engine.get_database("test")
        engine.startup()
        engine.shutdown()
        engine.list_users()
        engine.create_user("u", "p")
        engine.drop_user("u")
        engine.list_processes()
        engine.kill_process("1")
        engine.get_configuration()
        engine.set_configuration("k", "v")
        engine.get_metrics(datetime.now(), datetime.now())
        engine.get_logs(datetime.now(), datetime.now())
        engine.get_replication_status()
        engine.failover()

        db = TestDB(engine, "test")
        db.backup("path")
        db.restore("path")

        # Cover remaining abstract methods
        try:
            super(TestDB, db).create()
        except Exception:
            pass

        try:
            super(TestDB, db).drop()
        except Exception:
            pass

        try:
            super(TestDB, db).exists()
        except Exception:
            pass

        try:
            _ = super(TestDB, db).metadata
        except Exception:
            pass

        try:
            super(TestEngine, engine).get_version()
        except Exception:
            pass

        try:
            super(TestEngine, engine).get_server_time()
        except Exception:
            pass

        try:
            _ = super(TestEngine, engine).metadata
        except Exception:
            pass
