"""
MongoDB-specific exception classes.

Provides domain-specific exceptions that inherit from the base
gds_database exceptions for consistent error handling across
all database implementations.
"""

from __future__ import annotations

from gds_database import (
    ConfigurationError,
    DatabaseConnectionError,
    QueryError,
)


class MongoDBConnectionError(DatabaseConnectionError):
    """Raised when a MongoDB connection operation fails."""


class MongoDBQueryError(QueryError):
    """Raised when a MongoDB query or CRUD operation fails."""


class MongoDBConfigurationError(ConfigurationError):
    """Raised when MongoDB configuration is invalid or a parameter operation fails."""


class MongoDBReplicaSetError(QueryError):
    """Raised when a replica set management operation fails."""


class MongoDBAuthenticationError(MongoDBConnectionError):
    """Raised when MongoDB authentication fails."""
