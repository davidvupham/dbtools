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

Exceptions:
    QueryError: Raised when query execution fails
    ConnectionError: Raised when database connection fails
    ConfigurationError: Raised when configuration is invalid
"""

from .base import (
    ConfigurableComponent,
    ConfigurationError,
    ConnectionError,
    DatabaseConnection,
    OperationResult,
    QueryError,
    ResourceManager,
    RetryableOperation,
)

__version__ = "1.0.0"
__all__ = [
    "DatabaseConnection",
    "ConfigurableComponent",
    "ResourceManager",
    "RetryableOperation",
    "OperationResult",
    "QueryError",
    "ConnectionError",
    "ConfigurationError",
]
