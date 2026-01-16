"""
Test suite for gds_database base classes.
"""

import asyncio
import unittest
from datetime import datetime

from gds_database import (
    AsyncDatabaseConnection,
    AsyncResourceManager,
    ConfigurableComponent,
    ConfigurationError,
    Connectable,
    ConnectionPool,
    DatabaseConnection,
    DatabaseConnectionError,
    OperationResult,
    PerformanceMonitored,
    Queryable,
    QueryError,
    ResourceManager,
    RetryableOperation,
    TransactionalConnection,
)


class TestDatabaseConnection(unittest.TestCase):
    """Test DatabaseConnection abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that DatabaseConnection cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            DatabaseConnection()

    def test_subclass_must_implement_all_methods(self):
        """Test that subclasses must implement all abstract methods."""

        class IncompleteDatabaseConnection(DatabaseConnection):
            def connect(self):
                pass

            # Missing other required methods

        with self.assertRaises(TypeError):
            IncompleteDatabaseConnection()

    def test_complete_implementation(self):
        """Test that complete implementation works."""

        class CompleteDatabaseConnection(DatabaseConnection):
            def connect(self):
                return "connected"

            def disconnect(self):
                pass

            def execute_query(self, query, params=None):
                return [{"result": "data"}]

            def is_connected(self):
                return True

            def get_connection_info(self):
                return {"host": "localhost", "database": "test"}

        # Should not raise any exceptions
        conn = CompleteDatabaseConnection()
        self.assertEqual(conn.connect(), "connected")
        self.assertTrue(conn.is_connected())
        self.assertEqual(conn.execute_query("SELECT 1"), [{"result": "data"}])
        self.assertEqual(conn.get_connection_info(), {"host": "localhost", "database": "test"})


class TestConfigurableComponent(unittest.TestCase):
    """Test ConfigurableComponent abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that ConfigurableComponent cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            ConfigurableComponent()

    def test_complete_implementation(self):
        """Test complete implementation of ConfigurableComponent."""

        class TestComponent(ConfigurableComponent):
            def validate_config(self):
                required_keys = ["host", "port"]
                for key in required_keys:
                    if key not in self.config:
                        raise ConfigurationError(f"Missing required config: {key}")
                return True

        # Test with valid config
        component = TestComponent({"host": "localhost", "port": 5432})
        self.assertEqual(component.get_config("host"), "localhost")
        self.assertEqual(component.get_config("port"), 5432)
        self.assertEqual(component.get_config("nonexistent", "default"), "default")

        # Test config updates
        component.set_config("database", "testdb")
        self.assertEqual(component.get_config("database"), "testdb")

        component.update_config({"user": "testuser", "password": "testpass"})
        self.assertEqual(component.get_config("user"), "testuser")

    def test_validation_error(self):
        """Test that validation errors are raised."""

        class TestComponent(ConfigurableComponent):
            def validate_config(self):
                if "required_field" not in self.config:
                    raise ConfigurationError("Missing required_field")
                return True

        # Should raise error on initialization
        with self.assertRaises(ConfigurationError):
            TestComponent({"other_field": "value"})

        # Should raise error on config update
        component = TestComponent({"required_field": "value"})
        with self.assertRaises(ConfigurationError):
            component.set_config("required_field", None)
            del component.config["required_field"]
            component.validate_config()


class TestResourceManager(unittest.TestCase):
    """Test ResourceManager abstract base class."""

    def test_context_manager_protocol(self):
        """Test context manager functionality."""

        class TestResourceManager(ResourceManager):
            def __init__(self):
                self.initialized = False
                self.cleaned_up = False

            def initialize(self):
                self.initialized = True

            def cleanup(self):
                self.cleaned_up = True

            def is_initialized(self):
                return self.initialized

        manager = TestResourceManager()
        self.assertFalse(manager.is_initialized())

        with manager as m:
            self.assertTrue(m.is_initialized())
            self.assertFalse(m.cleaned_up)

        self.assertTrue(manager.cleaned_up)

    def test_exception_handling(self):
        """Test that exceptions are not suppressed."""

        class TestResourceManager(ResourceManager):
            def initialize(self):
                pass

            def cleanup(self):
                pass

            def is_initialized(self):
                return True

        with self.assertRaises(ValueError):
            with TestResourceManager():
                raise ValueError("Test exception")


class TestRetryableOperation(unittest.TestCase):
    """Test RetryableOperation abstract base class."""

    def test_successful_operation(self):
        """Test operation that succeeds on first try."""

        class TestOperation(RetryableOperation):
            def _execute(self):
                return "success"

        op = TestOperation()
        result = op.execute_with_retry()
        self.assertEqual(result, "success")

    def test_retry_on_failure(self):
        """Test operation that fails then succeeds."""

        class TestOperation(RetryableOperation):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.attempt_count = 0

            def _execute(self):
                self.attempt_count += 1
                if self.attempt_count < 3:
                    raise ValueError(f"Attempt {self.attempt_count} failed")
                return f"success on attempt {self.attempt_count}"

        op = TestOperation(max_retries=5)
        result = op.execute_with_retry()
        self.assertEqual(result, "success on attempt 3")
        self.assertEqual(op.attempt_count, 3)

    def test_max_retries_exceeded(self):
        """Test operation that always fails."""

        class TestOperation(RetryableOperation):
            def _execute(self):
                raise ValueError("Always fails")

        op = TestOperation(max_retries=2)
        with self.assertRaises(ValueError) as cm:
            op.execute_with_retry()
        self.assertEqual(str(cm.exception), "Always fails")


class TestDatabaseConnectionSuperCalls(unittest.TestCase):
    """Test DatabaseConnection abstract method coverage via super()."""

    def test_abstract_method_bodies_via_super(self):
        """Test that abstract method bodies can be called via super()."""

        class TestConnection(DatabaseConnection):
            def connect(self):
                super().connect()  # Cover line 58
                return "connected"

            def disconnect(self):
                super().disconnect()  # Cover line 68

            def execute_query(self, query, params=None):
                super().execute_query(query, params)  # Cover line 86
                return []

            def is_connected(self):
                super().is_connected()  # Cover line 96
                return True

            def get_connection_info(self):
                super().get_connection_info()  # Cover line 111
                return {}

        conn = TestConnection()
        conn.connect()
        conn.disconnect()
        conn.execute_query("SELECT 1")
        conn.is_connected()
        conn.get_connection_info()


class TestConfigurableComponentSuperCalls(unittest.TestCase):
    """Test ConfigurableComponent abstract method coverage via super()."""

    def test_validate_config_via_super(self):
        """Test validate_config can be called via super()."""

        class TestComponent(ConfigurableComponent):
            def validate_config(self):
                super().validate_config()  # Cover line 142
                return True

        component = TestComponent({})
        component.validate_config()


class TestResourceManagerSuperCalls(unittest.TestCase):
    """Test ResourceManager abstract method coverage via super()."""

    def test_abstract_methods_via_super(self):
        """Test abstract method bodies can be called via super()."""

        class TestManager(ResourceManager):
            def initialize(self):
                super().initialize()  # Cover line 234

            def cleanup(self):
                super().cleanup()  # Cover line 244

            def is_initialized(self):
                super().is_initialized()  # Cover line 254
                return True

        manager = TestManager()
        manager.initialize()
        manager.cleanup()
        manager.is_initialized()


class TestRetryableOperationSuperCalls(unittest.TestCase):
    """Test RetryableOperation abstract method coverage via super()."""

    def test_execute_via_super(self):
        """Test _execute can be called via super()."""

        class TestOperation(RetryableOperation):
            def _execute(self):
                super()._execute()  # Cover line 290
                return "success"

        op = TestOperation()
        result = op.execute_with_retry()
        self.assertEqual(result, "success")


class TestRetryableOperationEdgeCases(unittest.TestCase):
    """Test edge cases for RetryableOperation."""

    def test_all_retries_fail(self):
        """Test behavior when all retries are exhausted."""

        class FailingOperation(RetryableOperation):
            def _execute(self):
                raise ValueError("Always fails")

        op = FailingOperation(max_retries=1)
        with self.assertRaises(ValueError) as cm:
            op.execute_with_retry()
        self.assertEqual(str(cm.exception), "Always fails")


class TestOperationResult(unittest.TestCase):
    """Test OperationResult data class."""

    def test_success_result(self):
        """Test creating success result."""
        result = OperationResult.success_result("Operation completed", {"count": 5})
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Operation completed")
        self.assertEqual(result.data, {"count": 5})
        self.assertIsNone(result.error)
        self.assertIsInstance(result.timestamp, datetime)

    def test_failure_result(self):
        """Test creating failure result."""
        result = OperationResult.failure_result("Operation failed", "Connection timeout")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Operation failed")
        self.assertEqual(result.error, "Connection timeout")
        self.assertIsNone(result.data)
        self.assertIsInstance(result.timestamp, datetime)

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = OperationResult.success_result("Test", {"key": "value"})
        result_dict = result.to_dict()

        expected_keys = {"success", "message", "data", "error", "duration_ms", "timestamp", "metadata"}
        self.assertEqual(set(result_dict.keys()), expected_keys)
        self.assertTrue(result_dict["success"])
        self.assertEqual(result_dict["message"], "Test")
        self.assertEqual(result_dict["data"], {"key": "value"})

    def test_is_success(self):
        """Test is_success helper method."""
        success = OperationResult.success_result("Success")
        failure = OperationResult.failure_result("Failure")
        self.assertTrue(success.is_success())
        self.assertFalse(failure.is_success())

    def test_is_failure(self):
        """Test is_failure helper method."""
        success = OperationResult.success_result("Success")
        failure = OperationResult.failure_result("Failure")
        self.assertFalse(success.is_failure())
        self.assertTrue(failure.is_failure())

    def test_with_metadata(self):
        """Test result with metadata."""
        metadata = {"user": "test", "version": "1.0"}
        result = OperationResult.success_result("Test", metadata=metadata)
        self.assertEqual(result.metadata, metadata)


class TestProtocols(unittest.TestCase):
    """Test Protocol classes."""

    def test_connectable_protocol(self):
        """Test Connectable protocol."""

        class MockConnectable:
            def connect(self):
                return "connected"

            def disconnect(self):
                pass

            def is_connected(self):
                return True

        obj = MockConnectable()
        self.assertIsInstance(obj, Connectable)

    def test_queryable_protocol(self):
        """Test Queryable protocol."""

        class MockQueryable:
            def execute_query(self, query, params=None):
                return [{"result": "data"}]

        obj = MockQueryable()
        self.assertIsInstance(obj, Queryable)


class TestConnectionPool(unittest.TestCase):
    """Test ConnectionPool abstract class."""

    def test_cannot_instantiate(self):
        """Test that ConnectionPool cannot be instantiated."""
        with self.assertRaises(TypeError):
            ConnectionPool()

    def test_complete_implementation(self):
        """Test complete ConnectionPool implementation."""

        class TestPool(ConnectionPool):
            def get_connection(self):
                return None

            def release_connection(self, conn):
                pass

            def close_all(self):
                pass

            def get_pool_status(self):
                return {"size": 10, "active": 2}

        pool = TestPool()
        self.assertEqual(pool.get_pool_status(), {"size": 10, "active": 2})


class TestTransactionalConnection(unittest.TestCase):
    """Test TransactionalConnection abstract class."""

    def test_cannot_instantiate(self):
        """Test that TransactionalConnection cannot be instantiated."""
        with self.assertRaises(TypeError):
            TransactionalConnection()

    def test_complete_implementation(self):
        """Test complete TransactionalConnection implementation."""

        class TestTransactional(TransactionalConnection):
            def __init__(self):
                self._in_transaction = False

            def connect(self):
                return "connected"

            def disconnect(self):
                pass

            def execute_query(self, query, params=None):
                return []

            def is_connected(self):
                return True

            def get_connection_info(self):
                return {}

            def begin_transaction(self):
                self._in_transaction = True

            def commit(self):
                self._in_transaction = False

            def rollback(self):
                self._in_transaction = False

            def in_transaction(self):
                return self._in_transaction

        conn = TestTransactional()
        self.assertFalse(conn.in_transaction())
        conn.begin_transaction()
        self.assertTrue(conn.in_transaction())
        conn.commit()
        self.assertFalse(conn.in_transaction())


class TestAsyncDatabaseConnection(unittest.TestCase):
    """Test AsyncDatabaseConnection abstract class."""

    def test_cannot_instantiate(self):
        """Test that AsyncDatabaseConnection cannot be instantiated."""
        with self.assertRaises(TypeError):
            AsyncDatabaseConnection()

    def test_complete_implementation(self):
        """Test complete async implementation."""

        class TestAsyncConnection(AsyncDatabaseConnection):
            async def connect(self):
                return "connected"

            async def disconnect(self):
                pass

            async def execute_query(self, query, params=None):
                return [{"result": "data"}]

            async def is_connected(self):
                return True

            def get_connection_info(self):
                return {"host": "localhost"}

        async def run_test():
            conn = TestAsyncConnection()
            result = await conn.connect()
            self.assertEqual(result, "connected")
            self.assertTrue(await conn.is_connected())

        asyncio.run(run_test())


class TestAsyncResourceManager(unittest.TestCase):
    """Test AsyncResourceManager abstract class."""

    def test_async_context_manager(self):
        """Test async context manager protocol."""

        class TestAsyncManager(AsyncResourceManager):
            def __init__(self):
                self.initialized = False
                self.cleaned_up = False

            async def initialize(self):
                self.initialized = True

            async def cleanup(self):
                self.cleaned_up = True

            async def is_initialized(self):
                return self.initialized

        async def run_test():
            manager = TestAsyncManager()
            self.assertFalse(manager.initialized)

            async with manager as m:
                self.assertTrue(m.initialized)
                self.assertFalse(m.cleaned_up)

            self.assertTrue(manager.cleaned_up)

        asyncio.run(run_test())


class TestPerformanceMonitored(unittest.TestCase):
    """Test PerformanceMonitored mixin."""

    def test_performance_monitoring(self):
        """Test performance monitoring functionality."""

        class TestMonitored(PerformanceMonitored):
            def do_work(self):
                with self._measure_time("test_operation"):
                    import time

                    time.sleep(0.01)

        monitored = TestMonitored()
        # Should not raise an exception
        monitored.do_work()


class TestExceptions(unittest.TestCase):
    """Test custom exceptions."""

    def test_query_error(self):
        """Test QueryError exception."""
        with self.assertRaises(QueryError):
            raise QueryError("Query failed")

    def test_connection_error(self):
        """Test DatabaseConnectionError exception."""
        with self.assertRaises(DatabaseConnectionError):
            raise DatabaseConnectionError("Connection failed")

    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        with self.assertRaises(ConfigurationError):
            raise ConfigurationError("Config invalid")


if __name__ == "__main__":
    unittest.main()
