"""
Test OOP improvements and inheritance hierarchy.

This module tests the enhanced OOP design with proper inheritance,
abstract base classes, and design patterns.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from gds_snowflake.base import (
    BaseMonitor,
    ConfigurableComponent,
    DatabaseConnection,
    OperationResult,
    ResourceManager,
    RetryableOperation,
)
from gds_snowflake.connection import SnowflakeConnection
from gds_snowflake.monitor import SnowflakeMonitor


class TestBaseClasses(unittest.TestCase):
    """Test abstract base classes and common functionality."""

    def test_operation_result_creation(self):
        """Test OperationResult creation and methods."""
        # Test success result
        success_result = OperationResult.success_result("Operation completed", {"data": "test"})
        self.assertTrue(success_result.success)
        self.assertEqual(success_result.message, "Operation completed")
        self.assertEqual(success_result.data, {"data": "test"})

        # Test failure result
        failure_result = OperationResult.failure_result("Operation failed", "Connection timeout")
        self.assertFalse(failure_result.success)
        self.assertEqual(failure_result.message, "Operation failed")
        self.assertEqual(failure_result.error, "Connection timeout")

        # Test to_dict conversion
        result_dict = success_result.to_dict()
        self.assertIsInstance(result_dict, dict)
        self.assertTrue(result_dict["success"])

    def test_configurable_component(self):
        """Test ConfigurableComponent functionality."""

        class TestComponent(ConfigurableComponent):
            def validate_config(self) -> bool:
                return "required_key" in self.config

        # Test with valid config
        component = TestComponent({"required_key": "value"})
        self.assertTrue(component.validate_config())

        # Test configuration methods
        self.assertEqual(component.get_config("required_key"), "value")
        self.assertEqual(component.get_config("missing", "default"), "default")

        component.set_config("new_key", "new_value")
        self.assertEqual(component.get_config("new_key"), "new_value")

        component.update_config({"key1": "val1", "key2": "val2"})
        self.assertEqual(component.get_config("key1"), "val1")
        self.assertEqual(component.get_config("key2"), "val2")

    def test_resource_manager(self):
        """Test ResourceManager context manager functionality."""

        class TestResource(ResourceManager):
            def __init__(self):
                self.initialized = False
                self.cleaned_up = False

            def initialize(self) -> None:
                self.initialized = True

            def cleanup(self) -> None:
                self.cleaned_up = True

            def is_initialized(self) -> bool:
                return self.initialized

        # Test context manager
        with TestResource() as resource:
            self.assertTrue(resource.is_initialized())
            self.assertTrue(resource.initialized)
            self.assertFalse(resource.cleaned_up)

        # After context exit
        self.assertTrue(resource.cleaned_up)

    def test_retryable_operation(self):
        """Test RetryableOperation retry logic."""

        class TestOperation(RetryableOperation):
            def __init__(self, fail_count=2):
                super().__init__(max_retries=3, backoff_factor=1.0)
                self.fail_count = fail_count
                self.attempts = 0

            def _execute(self):
                self.attempts += 1
                if self.attempts <= self.fail_count:
                    raise ValueError(f"Attempt {self.attempts} failed")
                return f"Success on attempt {self.attempts}"

        # Test successful retry
        operation = TestOperation(fail_count=2)
        result = operation.execute_with_retry()
        self.assertEqual(result, "Success on attempt 3")
        self.assertEqual(operation.attempts, 3)

        # Test failure after max retries
        operation = TestOperation(fail_count=5)
        with self.assertRaises(ValueError):
            operation.execute_with_retry()


class TestSnowflakeConnectionInheritance(unittest.TestCase):
    """Test SnowflakeConnection inheritance from base classes."""

    def test_connection_inheritance(self):
        """Test that SnowflakeConnection properly inherits from base classes."""
        # Check inheritance
        self.assertTrue(issubclass(SnowflakeConnection, DatabaseConnection))
        self.assertTrue(issubclass(SnowflakeConnection, ConfigurableComponent))
        self.assertTrue(issubclass(SnowflakeConnection, ResourceManager))

    def test_connection_abstract_methods(self):
        """Test that all abstract methods are implemented."""
        with patch("gds_snowflake.connection.get_secret_from_vault") as mock_vault:
            mock_vault.return_value = {"private_key": "test_key"}

            conn = SnowflakeConnection(account="test_account", vault_secret_path="test/path")

            # Test abstract method implementations
            self.assertTrue(conn.validate_config())
            self.assertFalse(conn.is_initialized())
            self.assertFalse(conn.is_connected())

            # Test initialization
            conn.initialize()
            self.assertTrue(conn.is_initialized())

            # Test cleanup
            conn.cleanup()
            self.assertFalse(conn.is_initialized())

    def test_connection_context_manager(self):
        """Test connection context manager with inheritance."""
        with patch("gds_snowflake.connection.get_secret_from_vault") as mock_vault:
            mock_vault.return_value = {"private_key": "test_key"}

            with patch("snowflake.connector.connect") as mock_connect:
                mock_conn_obj = Mock()
                mock_conn_obj.is_closed.return_value = False
                mock_connect.return_value = mock_conn_obj

                with SnowflakeConnection(
                    account="test_account",
                    user="test_user",  # Add required user parameter
                    vault_secret_path="test/path",
                ) as conn:
                    self.assertTrue(conn.is_initialized())
                    # Connection should be initialized and connected
                    self.assertTrue(conn.is_connected())

    def test_connection_info(self):
        """Test connection info method."""
        with patch("gds_snowflake.connection.get_secret_from_vault") as mock_vault:
            mock_vault.return_value = {"private_key": "test_key"}

            conn = SnowflakeConnection(
                account="test_account", user="test_user", warehouse="test_warehouse", vault_secret_path="test/path"
            )

            info = conn.get_connection_info()
            self.assertEqual(info["account"], "test_account")
            self.assertEqual(info["user"], "test_user")
            self.assertEqual(info["warehouse"], "test_warehouse")
            self.assertFalse(info["connected"])


class TestSnowflakeMonitorInheritance(unittest.TestCase):
    """Test SnowflakeMonitor inheritance from BaseMonitor."""

    def test_monitor_inheritance(self):
        """Test that SnowflakeMonitor properly inherits from BaseMonitor."""
        self.assertTrue(issubclass(SnowflakeMonitor, BaseMonitor))

    @patch("gds_snowflake.monitor.SnowflakeConnection")
    def test_monitor_base_functionality(self, mock_conn_class):
        """Test BaseMonitor functionality in SnowflakeMonitor."""
        # Mock the connection
        mock_conn = Mock()
        mock_conn_class.return_value = mock_conn

        # Create monitor
        monitor = SnowflakeMonitor(account="test_account")

        # Test base class properties
        self.assertEqual(monitor.name, "SnowflakeMonitor-test_account")
        self.assertEqual(monitor.timeout, 30)  # Default timeout

        # Test stats before any checks
        stats = monitor.get_stats()
        self.assertEqual(stats["name"], "SnowflakeMonitor-test_account")
        self.assertEqual(stats["check_count"], 0)
        self.assertIsNone(stats["start_time"])
        self.assertIsNone(stats["last_check"])

    @patch("gds_snowflake.monitor.SnowflakeConnection")
    @patch("gds_snowflake.monitor.SnowflakeReplication")
    def test_monitor_check_method(self, mock_repl_class, mock_conn_class):
        """Test the check method implementation."""
        # Mock the connection and replication
        mock_conn = Mock()
        mock_conn_class.return_value = mock_conn
        mock_conn.test_connectivity.return_value = {
            "success": True,
            "response_time_ms": 100,
            "account_info": {"account_name": "test_account"},
            "error": None,
            "timestamp": datetime.now().isoformat(),
        }

        mock_repl = Mock()
        mock_repl_class.return_value = mock_repl
        mock_repl.get_failover_groups.return_value = []

        # Create monitor
        monitor = SnowflakeMonitor(account="test_account")

        # Test check method
        result = monitor.check()

        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("message", result)
        self.assertIn("duration_ms", result)
        self.assertIn("data", result)

        # Verify stats were recorded
        stats = monitor.get_stats()
        self.assertEqual(stats["check_count"], 1)
        self.assertIsNotNone(stats["start_time"])
        self.assertIsNotNone(stats["last_check"])


class TestEnhancedOOPFeatures(unittest.TestCase):
    """Test enhanced OOP features and design patterns."""

    def test_polymorphism_with_base_classes(self):
        """Test polymorphism using base classes."""

        class TestMonitor(BaseMonitor):
            def check(self) -> dict:
                return {"success": True, "message": "Test check completed", "duration_ms": 50}

        class TestConnection(DatabaseConnection):
            def connect(self):
                pass

            def disconnect(self):
                pass

            def execute_query(self, query: str, params=None):
                return []

            def is_connected(self) -> bool:
                return True

            def get_connection_info(self) -> dict:
                return {}

        # Test polymorphism - both inherit from base classes
        monitor = TestMonitor("test")
        connection = TestConnection()

        # Both should have common base functionality
        self.assertTrue(hasattr(monitor, "check"))
        self.assertTrue(hasattr(connection, "connect"))
        self.assertTrue(hasattr(connection, "execute_query"))

    def test_composition_pattern(self):
        """Test composition pattern in monitor."""
        with patch("gds_snowflake.monitor.SnowflakeConnection") as mock_conn_class:
            mock_conn = Mock()
            mock_conn_class.return_value = mock_conn

            monitor = SnowflakeMonitor(account="test_account")

            # Monitor should compose (contain) a connection
            self.assertIsInstance(monitor.connection, Mock)
            self.assertIsNotNone(monitor.connection)

    def test_factory_pattern_potential(self):
        """Test potential factory pattern usage."""

        # This demonstrates how we could use factory patterns
        def create_monitor(account: str, monitor_type: str = "standard"):
            if monitor_type == "standard":
                return SnowflakeMonitor(account=account)
            if monitor_type == "basic":
                # Could return a BasicMonitor class
                return SnowflakeMonitor(account=account)
            raise ValueError(f"Unknown monitor type: {monitor_type}")

        with patch("gds_snowflake.monitor.SnowflakeConnection"):
            # Test factory
            monitor = create_monitor("test_account", "standard")
            self.assertIsInstance(monitor, SnowflakeMonitor)
            self.assertEqual(monitor.account, "test_account")


class TestOOPBestPractices(unittest.TestCase):
    """Test adherence to OOP best practices."""

    def test_encapsulation(self):
        """Test proper encapsulation with private attributes."""
        with patch("gds_snowflake.connection.get_secret_from_vault") as mock_vault:
            mock_vault.return_value = {"private_key": "test_key"}

            conn = SnowflakeConnection(account="test_account", vault_secret_path="test/path")

            # Private attributes should be accessible but conventionally private
            self.assertTrue(hasattr(conn, "_initialized"))
            self.assertFalse(conn._initialized)  # Should start as False

    def test_inheritance_hierarchy(self):
        """Test proper inheritance hierarchy."""
        # Test multiple inheritance
        self.assertTrue(issubclass(SnowflakeConnection, DatabaseConnection))
        self.assertTrue(issubclass(SnowflakeConnection, ConfigurableComponent))
        self.assertTrue(issubclass(SnowflakeConnection, ResourceManager))

        # Test single inheritance
        self.assertTrue(issubclass(SnowflakeMonitor, BaseMonitor))

    def test_abstract_method_implementation(self):
        """Test that all abstract methods are properly implemented."""
        # SnowflakeConnection should implement all DatabaseConnection methods
        conn_methods = ["connect", "disconnect", "execute_query", "is_connected", "get_connection_info"]
        for method in conn_methods:
            self.assertTrue(hasattr(SnowflakeConnection, method))

        # SnowflakeMonitor should implement BaseMonitor check method
        self.assertTrue(hasattr(SnowflakeMonitor, "check"))

    def test_interface_segregation(self):
        """Test interface segregation principle."""
        # Each base class should have a focused interface
        base_monitor_methods = ["check", "get_stats"]
        for method in base_monitor_methods:
            self.assertTrue(hasattr(BaseMonitor, method))

        # Database connection should have database-specific methods
        db_methods = ["connect", "disconnect", "execute_query"]
        for method in db_methods:
            self.assertTrue(hasattr(DatabaseConnection, method))


if __name__ == "__main__":
    unittest.main()
