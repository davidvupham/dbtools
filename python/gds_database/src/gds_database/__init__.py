"""
GDS Database - Abstract Database Interface Package

This package provides abstract base classes and interfaces for building
database connection libraries with consistent APIs.

Classes:
    DatabaseConnection: Abstract base class for database connections
    ConfigurableComponent: Base class for configurable components
    ResourceManager: Base class for resource management with context managers
    RetryableOperation: Base class for operations with retry logic
    OperationResult: Standardized result object for operations
    ConnectionPool: Abstract base class for connection pooling
    TransactionalConnection: Abstract base class with transaction support
    PerformanceMonitored: Mixin for performance monitoring

Protocols:
    Connectable: Protocol for connectable objects
    Queryable: Protocol for queryable objects

Exceptions:
    QueryError: Raised when query execution fails
    DatabaseConnectionError: Raised when database connection fails
    ConfigurationError: Raised when configuration is invalid
"""

from .base import (
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
from .database import Database
from .engine import DatabaseEngine
from .metadata import (
    BackupType,
    DatabaseMetadata,
    DatabaseState,
    DatabaseType,
    EngineMetadata,
    LogEntry,
    Metric,
    ReplicationStatus,
)

__version__ = "1.0.0"
__all__ = [
    "AsyncDatabaseConnection",
    "AsyncResourceManager",
    "Connectable",
    "ConfigurableComponent",
    "ConfigurationError",
    "ConnectionPool",
    "DatabaseConnection",
    "DatabaseConnectionError",
    "OperationResult",
    "PerformanceMonitored",
    "Queryable",
    "QueryError",
    "ResourceManager",
    "RetryableOperation",
    "TransactionalConnection",
    # New OOD Abstractions
    "DatabaseEngine",
    "Database",
    "DatabaseMetadata",
    "EngineMetadata",
    "Metric",
    "LogEntry",
    "ReplicationStatus",
    "DatabaseType",
    "DatabaseState",
    "BackupType",
]
