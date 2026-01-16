"""
Snowflake data analysis and replication monitoring package.

Provides classes for connecting to Snowflake, managing databases and tables,
and monitoring replication status for failover groups.
"""

from .account import AccountInfo, SnowflakeAccount

# Import database interfaces - prefer gds_database package if available
try:
    from gds_database import (
        ConfigurableComponent,
        DatabaseConnection,
        OperationResult,
        ResourceManager,
        RetryableOperation,
    )
except ImportError:
    # Fallback to local base classes if gds_database not available
    from .base import (
        ConfigurableComponent,
        DatabaseConnection,
        OperationResult,
        ResourceManager,
        RetryableOperation,
    )

from .base import (
    BaseMonitor,
    SecretProvider,
)
from .connection import SnowflakeConnection
from .database import SnowflakeDatabase
from .monitor import (
    AlertSeverity,
    ConnectivityResult,
    MonitoringResult,
    ReplicationResult,
    SnowflakeMonitor,
)
from .replication import FailoverGroup, SnowflakeReplication
from .table import SnowflakeTable

__version__ = "1.0.0"
__all__ = [
    "AccountInfo",
    "AlertSeverity",
    # Base classes
    "BaseMonitor",
    "ConfigurableComponent",
    "ConnectivityResult",
    "DatabaseConnection",
    "FailoverGroup",
    "MonitoringResult",
    "OperationResult",
    "ReplicationResult",
    "ResourceManager",
    "RetryableOperation",
    "SecretProvider",
    "SnowflakeAccount",
    "SnowflakeConnection",
    "SnowflakeDatabase",
    "SnowflakeMonitor",
    "SnowflakeReplication",
    "SnowflakeTable",
]
