"""
Test suite for gds_database base classes.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock

from gds_database import (
    ConfigurableComponent,
    ConnectionError,
    ConfigurationError,
    DatabaseConnection,
    OperationResult,
    QueryError,
    ResourceManager,
    RetryableOperation,
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
                required_keys = ['host', 'port']
                for key in required_keys:
                    if key not in self.config:
                        raise ConfigurationError(f"Missing required config: {key}")
                return True

        # Test with valid config
        component = TestComponent({'host': 'localhost', 'port': 5432})
        self.assertEqual(component.get_config('host'), 'localhost')
        self.assertEqual(component.get_config('port'), 5432)
        self.assertEqual(component.get_config('nonexistent', 'default'), 'default')

        # Test config updates
        component.set_config('database', 'testdb')
        self.assertEqual(component.get_config('database'), 'testdb')

        component.update_config({'user': 'testuser', 'password': 'testpass'})
        self.assertEqual(component.get_config('user'), 'testuser')

    def test_validation_error(self):
        """Test that validation errors are raised."""
        
        class TestComponent(ConfigurableComponent):
            def validate_config(self):
                if 'required_field' not in self.config:
                    raise ConfigurationError("Missing required_field")
                return True

        # Should raise error on initialization
        with self.assertRaises(ConfigurationError):
            TestComponent({'other_field': 'value'})

        # Should raise error on config update
        component = TestComponent({'required_field': 'value'})
        with self.assertRaises(ConfigurationError):
            component.set_config('required_field', None)
            del component.config['required_field']
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
        
        expected_keys = {'success', 'message', 'data', 'error', 'duration_ms', 'timestamp'}
        self.assertEqual(set(result_dict.keys()), expected_keys)
        self.assertTrue(result_dict['success'])
        self.assertEqual(result_dict['message'], "Test")
        self.assertEqual(result_dict['data'], {"key": "value"})


if __name__ == '__main__':
    unittest.main()