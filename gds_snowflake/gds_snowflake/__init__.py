"""
Snowflake data analysis and replication monitoring package.

Provides classes for connecting to Snowflake, managing databases and tables,
and monitoring replication status for failover groups.
"""

from .connection import SnowflakeConnection
from .database import SnowflakeDatabase
from .table import SnowflakeTable
from .replication import SnowflakeReplication, FailoverGroup
from .monitor import (
    SnowflakeMonitor,
    AlertSeverity,
    MonitoringResult,
    ConnectivityResult,
    ReplicationResult
)

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
    "ReplicationResult"
]
