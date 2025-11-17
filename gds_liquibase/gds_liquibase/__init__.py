"""
GDS Liquibase - Database Change Management CI/CD Package

This package provides Python wrappers for Liquibase database change management,
designed for use with GitHub Actions CI/CD pipelines.

Main components:
- LiquibaseConfig: Configuration management for Liquibase operations
- LiquibaseMigrationRunner: Execute Liquibase commands from Python
- ChangelogManager: Manage and generate changelog files
- Integration with gds_postgres, gds_mssql, gds_mongodb packages

Example usage:
    >>> from gds_liquibase import LiquibaseConfig, LiquibaseMigrationRunner
    >>> config = LiquibaseConfig.from_env()
    >>> runner = LiquibaseMigrationRunner(config)
    >>> runner.update()

For detailed documentation, see:
    https://github.com/davidvupham/dbtools/tree/main/gds_liquibase
"""

__version__ = "0.1.0"
__author__ = "GDS Team"
__license__ = "MIT"

from gds_liquibase.changelog import ChangelogManager
from gds_liquibase.config import LiquibaseConfig
from gds_liquibase.exceptions import (
    ConfigurationError,
    ExecutionError,
    LiquibaseError,
    ValidationError,
)
from gds_liquibase.runner import LiquibaseMigrationRunner

__all__ = [
    "LiquibaseConfig",
    "LiquibaseMigrationRunner",
    "ChangelogManager",
    "LiquibaseError",
    "ConfigurationError",
    "ExecutionError",
    "ValidationError",
    "__version__",
]
