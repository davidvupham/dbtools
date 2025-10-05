"""
Base classes and abstract interfaces for the gds_snowflake package.

This module provides abstract base classes and common functionality
that can be inherited by specific implementations.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


class BaseMonitor(ABC):
    """
    Abstract base class for all monitoring operations.
    
    Provides common functionality for monitoring classes including:
    - Logging setup
    - Timeout handling
    - Result formatting
    - Error handling patterns
    """

    def __init__(
        self,
        name: str,
        timeout: int = 30,
        log_level: int = logging.INFO
    ):
        """
        Initialize base monitor.
        
        Args:
            name: Name of the monitor instance
            timeout: Default timeout for operations
            log_level: Logging level
        """
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(log_level)

        # Track monitoring state
        self._start_time: Optional[datetime] = None
        self._last_check: Optional[datetime] = None
        self._check_count = 0

    @abstractmethod
    def check(self) -> dict[str, Any]:
        """
        Perform the monitoring check.
        
        Returns:
            Dictionary containing check results
        """
        pass

    def _log_result(self, result: dict[str, Any]) -> None:
        """Log monitoring result with standardized format."""
        status = "SUCCESS" if result.get('success', False) else "FAILED"
        duration = result.get('duration_ms', 0)

        self.logger.info(
            "%s check %s in %dms - %s",
            self.name,
            status,
            duration,
            result.get('message', 'No message')
        )

    def _record_check(self, result: dict[str, Any]) -> None:
        """Record check statistics."""
        self._check_count += 1
        self._last_check = datetime.now()

        if self._start_time is None:
            self._start_time = self._last_check

    def get_stats(self) -> dict[str, Any]:
        """Get monitoring statistics."""
        uptime = None
        if self._start_time:
            uptime = (datetime.now() - self._start_time).total_seconds()

        return {
            'name': self.name,
            'check_count': self._check_count,
            'start_time': self._start_time,
            'last_check': self._last_check,
            'uptime_seconds': uptime,
            'timeout': self.timeout
        }


class DatabaseConnection(ABC):
    """
    Abstract base class for database connections.
    
    Defines the interface that all database connection classes must implement.
    """

    @abstractmethod
    def connect(self) -> Any:
        """Establish database connection."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> list[Any]:
        """Execute a query and return results."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active."""
        pass

    @abstractmethod
    def get_connection_info(self) -> dict[str, Any]:
        """Get connection information."""
        pass


class SecretProvider(ABC):
    """
    Abstract base class for secret providers.
    
    Defines the interface for retrieving secrets from various sources.
    """

    @abstractmethod
    def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
        """Retrieve a secret from the provider."""
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the secret provider."""
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        pass


class RetryableOperation(ABC):
    """
    Abstract base class for operations that support retry logic.
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
        """Execute the operation that may need retrying."""
        pass

    def execute_with_retry(self) -> Any:
        """Execute operation with retry logic."""
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


class ConfigurableComponent(ABC):
    """
    Abstract base class for components that support configuration.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize configurable component.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the current configuration."""
        pass

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
        self.validate_config()

    def update_config(self, config: dict[str, Any]) -> None:
        """Update multiple configuration values."""
        self.config.update(config)
        self.validate_config()


@dataclass
class OperationResult:
    """
    Standardized result object for operations.
    """
    success: bool
    message: str
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @classmethod
    def success_result(cls, message: str, data: Optional[dict[str, Any]] = None) -> 'OperationResult':
        """Create a successful result."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def failure_result(cls, message: str, error: Optional[str] = None) -> 'OperationResult':
        """Create a failure result."""
        return cls(success=False, message=message, error=error)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'error': self.error,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class ResourceManager(ABC):
    """
    Abstract base class for resource management.
    
    Provides context manager protocol and resource cleanup.
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
        """Initialize resources."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources."""
        pass

    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if resources are initialized."""
        pass
