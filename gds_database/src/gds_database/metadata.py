"""
Database metadata and enumeration definitions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DatabaseType(str, Enum):
    """Supported database types."""

    MSSQL = "mssql"
    SNOWFLAKE = "snowflake"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    MYSQL = "mysql"
    ORACLE = "oracle"
    SQLITE = "sqlite"


class DatabaseState(str, Enum):
    """Database operational states."""

    ONLINE = "online"
    OFFLINE = "offline"
    RESTORING = "restoring"
    RECOVERING = "recovering"
    SUSPECT = "suspect"
    EMERGENCY = "emergency"
    SINGLE_USER = "single_user"
    MULTI_USER = "multi_user"
    UNKNOWN = "unknown"


class BackupType(str, Enum):
    """Backup types."""

    FULL = "full"
    DIFFERENTIAL = "differential"
    INCREMENTAL = "incremental"
    TRANSACTION_LOG = "transaction_log"


@dataclass
class DatabaseMetadata:
    """
    Represents database metadata attributes.

    This is a flexible container that can hold different attributes
    based on the database type.
    """

    name: str
    type: DatabaseType
    created: Optional[datetime] = None
    size_bytes: Optional[int] = None
    owner: Optional[str] = None
    collation: Optional[str] = None
    state: Optional[DatabaseState] = None

    # Platform-specific attributes stored in additional_attributes
    additional_attributes: Dict[str, Any] = field(default_factory=dict)

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get platform-specific attribute."""
        return self.additional_attributes.get(key, default)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set platform-specific attribute."""
        self.additional_attributes[key] = value


@dataclass
class EngineMetadata:
    """
    Represents database engine metadata attributes.
    """

    name: str
    version: str
    edition: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    decommissioned_at: Optional[datetime] = None

    # Platform-specific attributes
    additional_attributes: Dict[str, Any] = field(default_factory=dict)

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get platform-specific attribute."""
        return self.additional_attributes.get(key, default)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set platform-specific attribute."""
        self.additional_attributes[key] = value


@dataclass
class Metric:
    """
    Represents a database metric point.
    """

    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class LogEntry:
    """
    Represents a database log entry.
    """

    timestamp: datetime
    level: str
    message: str
    source: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplicationStatus:
    """
    Represents database replication/HA status.
    """

    enabled: bool
    mode: str  # e.g., 'synchronous', 'asynchronous'
    role: str  # e.g., 'primary', 'secondary', 'witness'
    lag_seconds: float = 0.0
    sync_state: str = "unknown"  # e.g., 'synchronized', 'syncing'
    partners: List[str] = field(default_factory=list)
