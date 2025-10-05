"""
Snowflake data analysis and replication monitoring package.

Provides classes for connecting to Snowflake, managing databases and tables,
and monitoring replication status for failover groups.
"""

from .base import (
    BaseMonitor,
    ConfigurableComponent,
    DatabaseConnection,
    OperationResult,
    ResourceManager,
    RetryableOperation,
    SecretProvider,
)
from .connection import SnowflakeConnection
from .database import SnowflakeDatabase
from .monitor import AlertSeverity, ConnectivityResult, MonitoringResult, ReplicationResult, SnowflakeMonitor
from .replication import FailoverGroup, SnowflakeReplication
from .table import SnowflakeTable

__version__ = "1.0.0"
__all__ = [
    "SnowflakeConnection",
    "SnowflakeDatabase",
    "SnowflakeTable",
    "SnowflakeReplication",
    "FailoverGroup",
    "SnowflakeMonitor",
    "AlertSeverity",
    "MonitoringResult",
    "ConnectivityResult",
    "ReplicationResult",
    # Base classes
    "BaseMonitor",
    "DatabaseConnection",
    "SecretProvider",
    "ConfigurableComponent",
    "ResourceManager",
    "RetryableOperation",
    "OperationResult"
]
