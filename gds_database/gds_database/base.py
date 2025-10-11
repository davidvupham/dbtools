"""
Base classes and abstract interfaces for database connections.

This module provides abstract base classes and common functionality
that can be inherited by specific database implementations.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


class DatabaseConnection(ABC):
    """
    Abstract base class for database connections.
    
    Defines the interface that all database connection classes must implement.
    This ensures consistent behavior across different database implementations.
    
    Example:
        class MyDatabaseConnection(DatabaseConnection):
            def connect(self):
                # Implementation specific to your database
                pass
            
            def disconnect(self):
                # Implementation specific to your database
                pass
            
            def execute_query(self, query, params=None):
                # Implementation specific to your database
                pass
            
            def is_connected(self):
                # Implementation specific to your database
                pass
            
            def get_connection_info(self):
                # Implementation specific to your database
                pass
    """

    @abstractmethod
    def connect(self) -> Any:
        """
        Establish database connection.
        
        Returns:
            Database-specific connection object
            
        Raises:
            ConnectionError: If connection cannot be established
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close database connection.
        
        Should handle cleanup of any resources associated with the connection.
        Should not raise exceptions if connection is already closed.
        """
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> list[Any]:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query string to execute
            params: Optional parameters for parameterized queries
            
        Returns:
            List of query results. Format depends on implementation.
            
        Raises:
            QueryError: If query execution fails
            ConnectionError: If not connected to database
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if connection is active.
        
        Returns:
            True if connection is active, False otherwise
        """
        pass

    @abstractmethod
    def get_connection_info(self) -> dict[str, Any]:
        """
        Get connection information.
        
        Returns:
            Dictionary containing connection metadata such as:
            - host/server information
            - database name
            - user information
            - connection status
            - etc.
        """
        pass


class ConfigurableComponent(ABC):
    """
    Abstract base class for components that support configuration.
    
    Provides a standard interface for configuration management with validation.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize configurable component.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.validate_config()

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        pass

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Raises:
            ValueError: If resulting configuration is invalid
        """
        self.config[key] = value
        self.validate_config()

    def update_config(self, config: dict[str, Any]) -> None:
        """
        Update multiple configuration values.
        
        Args:
            config: Dictionary of configuration updates
            
        Raises:
            ValueError: If resulting configuration is invalid
        """
        self.config.update(config)
        self.validate_config()


class ResourceManager(ABC):
    """
    Abstract base class for resource management.
    
    Provides context manager protocol and resource cleanup patterns.
    Use this for classes that need to manage resources like connections,
    file handles, etc.
    
    Example:
        class MyResourceManager(ResourceManager):
            def initialize(self):
                self.resource = acquire_resource()
            
            def cleanup(self):
                if hasattr(self, 'resource'):
                    self.resource.close()
            
            def is_initialized(self):
                return hasattr(self, 'resource') and self.resource.is_open()
        
        # Usage
        with MyResourceManager() as manager:
            # Resource is automatically managed
            manager.do_something()
        # Resource is automatically cleaned up
    """

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False  # Don't suppress exceptions

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize resources.
        
        Called when entering context manager or when explicitly requested.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        Called when exiting context manager or when explicitly requested.
        Should handle cleanup gracefully even if resources are already cleaned up.
        """
        pass

    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Check if resources are initialized.
        
        Returns:
            True if resources are properly initialized, False otherwise
        """
        pass


class RetryableOperation(ABC):
    """
    Abstract base class for operations that support retry logic.
    
    Provides exponential backoff retry mechanism for operations that may fail
    transiently due to network issues, temporary service unavailability, etc.
    """

    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        """
        Initialize retryable operation.
        
        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    @abstractmethod
    def _execute(self) -> Any:
        """
        Execute the operation that may need retrying.
        
        This method should contain the actual operation logic.
        It will be called by execute_with_retry() with retry logic.
        
        Returns:
            Result of the operation
            
        Raises:
            Exception: Any exception that should trigger a retry
        """
        pass

    def execute_with_retry(self) -> Any:
        """
        Execute operation with retry logic.
        
        Uses exponential backoff between retries with a maximum delay cap.
        
        Returns:
            Result from successful execution
            
        Raises:
            Exception: The last exception if all retries are exhausted
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return self._execute()
            except Exception as e:
                last_exception = e
                if attempt == self.max_retries:
                    break

                # Calculate delay with exponential backoff
                delay = min(self.backoff_factor ** attempt, 60)  # Max 60 seconds
                time.sleep(delay)

        raise last_exception


@dataclass
class OperationResult:
    """
    Standardized result object for operations.
    
    Provides a consistent way to return operation results with
    success/failure status, messages, data, and timing information.
    """
    success: bool
    message: str
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @classmethod
    def success_result(cls, message: str, data: Optional[dict[str, Any]] = None) -> 'OperationResult':
        """
        Create a successful result.
        
        Args:
            message: Success message
            data: Optional result data
            
        Returns:
            OperationResult indicating success
        """
        return cls(success=True, message=message, data=data)

    @classmethod
    def failure_result(cls, message: str, error: Optional[str] = None) -> 'OperationResult':
        """
        Create a failure result.
        
        Args:
            message: Failure message
            error: Optional detailed error information
            
        Returns:
            OperationResult indicating failure
        """
        return cls(success=False, message=message, error=error)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation of the result
        """
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'error': self.error,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class QueryError(Exception):
    """Exception raised when query execution fails."""
    pass


class ConnectionError(Exception):
    """Exception raised when database connection fails."""
    pass


class ConfigurationError(Exception):
    """Exception raised when configuration is invalid."""
    pass
