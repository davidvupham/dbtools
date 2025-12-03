"""
Base classes and abstract interfaces for database connections.

This module provides abstract base classes and common functionality
that can be inherited by specific database implementations.
"""

import logging
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Optional, Protocol, runtime_checkable


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
    def execute_query(self, query: str, params: Optional[tuple[Any, ...]] = None) -> list[Any]:
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

    def __enter__(self) -> "ResourceManager":
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> Literal[False]:
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
        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                return self._execute()
            except Exception as e:
                last_exception = e
                if attempt == self.max_retries:
                    break

                # Calculate delay with exponential backoff
                delay = min(self.backoff_factor**attempt, 60)  # Max 60 seconds
                time.sleep(delay)

        if last_exception:
            raise last_exception
        # Defensive check for impossible condition
        raise RuntimeError(  # pragma: no cover
            "Retry logic failed without exception"
        )


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
    metadata: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def is_success(self) -> bool:
        """
        Check if operation was successful.

        Returns:
            True if successful, False otherwise
        """
        return self.success

    def is_failure(self) -> bool:
        """
        Check if operation failed.

        Returns:
            True if failed, False otherwise
        """
        return not self.success

    @classmethod
    def success_result(
        cls,
        message: str,
        data: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "OperationResult":
        """
        Create a successful result.

        Args:
            message: Success message
            data: Optional result data
            metadata: Optional additional metadata

        Returns:
            OperationResult indicating success
        """
        return cls(success=True, message=message, data=data, metadata=metadata)

    @classmethod
    def failure_result(
        cls,
        message: str,
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "OperationResult":
        """
        Create a failure result.

        Args:
            message: Failure message
            error: Optional detailed error information
            metadata: Optional additional metadata

        Returns:
            OperationResult indicating failure
        """
        return cls(success=False, message=message, error=error, metadata=metadata)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation of the result
        """
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata,
        }


# Protocol definitions for duck typing
@runtime_checkable
class Connectable(Protocol):
    """Protocol for objects that can connect and disconnect."""

    def connect(self) -> Any:
        """Establish connection."""
        ...

    def disconnect(self) -> None:
        """Close connection."""
        ...

    def is_connected(self) -> bool:
        """Check if connected."""
        ...


@runtime_checkable
class Queryable(Protocol):
    """Protocol for objects that can execute queries."""

    def execute_query(self, query: str, params: Optional[tuple[Any, ...]] = None) -> list[Any]:
        """Execute a query."""
        ...


# Connection Pool abstract class
class ConnectionPool(ABC):
    """
    Abstract base class for connection pooling.

    Manages a pool of database connections for efficient resource usage.
    """

    @abstractmethod
    def get_connection(self) -> DatabaseConnection:
        """
        Get a connection from the pool.

        Returns:
            DatabaseConnection object

        Raises:
            ConnectionError: If unable to provide a connection
        """
        ...

    @abstractmethod
    def release_connection(self, conn: DatabaseConnection) -> None:
        """
        Release a connection back to the pool.

        Args:
            conn: Connection to release
        """
        ...

    @abstractmethod
    def close_all(self) -> None:
        """Close all connections in the pool."""
        ...

    @abstractmethod
    def get_pool_status(self) -> dict[str, Any]:
        """
        Get pool status information.

        Returns:
            Dictionary with pool metrics (size, active, idle, etc.)
        """
        ...


# Transactional Connection abstract class
class TransactionalConnection(DatabaseConnection):
    """
    Abstract base class for database connections with transaction support.

    Extends DatabaseConnection with transaction management capabilities.
    """

    @abstractmethod
    def begin_transaction(self) -> None:
        """
        Begin a new transaction.

        Raises:
            ConnectionError: If not connected
        """
        ...

    @abstractmethod
    def commit(self) -> None:
        """
        Commit the current transaction.

        Raises:
            ConnectionError: If not connected or no active transaction
        """
        ...

    @abstractmethod
    def rollback(self) -> None:
        """
        Rollback the current transaction.

        Raises:
            ConnectionError: If not connected or no active transaction
        """
        ...

    @abstractmethod
    def in_transaction(self) -> bool:
        """
        Check if currently in a transaction.

        Returns:
            True if in a transaction, False otherwise
        """
        ...


# Performance monitoring mixin
class PerformanceMonitored:
    """
    Mixin class for performance monitoring.

    Provides timing utilities for monitoring operation performance.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize with optional logger."""
        super().__init__(*args, **kwargs)
        self.logger = kwargs.get("logger", logging.getLogger(__name__))

    @contextmanager
    def _measure_time(self, operation: str = "operation") -> Any:
        """
        Context manager to measure operation time.

        Args:
            operation: Name of the operation being measured

        Yields:
            None
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = (time.perf_counter() - start) * 1000
            self.logger.info(f"{operation} took {duration:.2f}ms")


# Async database connection support
class AsyncDatabaseConnection(ABC):
    """
    Abstract base class for asynchronous database connections.

    Similar to DatabaseConnection but with async/await support.
    """

    @abstractmethod
    async def connect(self) -> Any:
        """
        Establish database connection asynchronously.

        Returns:
            Database-specific connection object

        Raises:
            DatabaseConnectionError: If connection cannot be established
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close database connection asynchronously.

        Should handle cleanup of any resources associated with the connection.
        """
        ...

    @abstractmethod
    async def execute_query(self, query: str, params: Optional[tuple[Any, ...]] = None) -> list[Any]:
        """
        Execute a query asynchronously and return results.

        Args:
            query: SQL query string to execute
            params: Optional parameters for parameterized queries

        Returns:
            List of query results

        Raises:
            QueryError: If query execution fails
            DatabaseConnectionError: If not connected to database
        """
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if connection is active asynchronously.

        Returns:
            True if connection is active, False otherwise
        """
        ...

    @abstractmethod
    def get_connection_info(self) -> dict[str, Any]:
        """
        Get connection information.

        Returns:
            Dictionary containing connection metadata
        """
        ...


# Async context manager for resources
class AsyncResourceManager(ABC):
    """
    Abstract base class for asynchronous resource management.

    Provides async context manager protocol.
    """

    async def __aenter__(self) -> "AsyncResourceManager":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> Literal[False]:
        """Async context manager exit."""
        await self.cleanup()
        return False

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize resources asynchronously.

        Called when entering async context manager.
        """
        ...

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up resources asynchronously.

        Called when exiting async context manager.
        """
        ...

    @abstractmethod
    async def is_initialized(self) -> bool:
        """
        Check if resources are initialized.

        Returns:
            True if resources are initialized, False otherwise
        """
        ...


class QueryError(Exception):
    """Exception raised when query execution fails."""


class DatabaseConnectionError(Exception):
    """Exception raised when database connection fails."""


class ConfigurationError(Exception):
    """Exception raised when configuration is invalid."""
