# MongoDB ReplicaSet Class Design

## Complete OOP Design for MongoDB Replica Set Management

Based on MongoDB official documentation and best practices.

---

## ReplicaSet Class

### Overview
The `ReplicaSet` class represents a MongoDB replica set and manages its complete lifecycle from deployment to teardown, including all operational, monitoring, and maintenance functions.

### Class Definition

```python
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ReplicaSet:
    """
    Manages MongoDB replica set lifecycle and operations.

    Lifecycle: build() -> operate -> destroy()
    """

    def __init__(
        self,
        name: str,
        members: List['MemberConfig'],
        platform: str = "docker",  # docker, kubernetes, bare-metal
        settings: Optional['ReplicaSetSettings'] = None
    ):
        self.name = name
        self.members = members
        self.platform = platform
        self.settings = settings or ReplicaSetSettings()
        self._status: Optional['ReplicaSetStatus'] = None
        self._config: Optional['ReplicaSetConfig'] = None

    # ============================================
    # LIFECYCLE OPERATIONS
    # ============================================

    def build(self, **kwargs) -> 'OperationResult':
        """
        Build/provision the replica set.

        Steps:
        1. Start mongod instances (Docker containers / K8s pods)
        2. Wait for all instances to be ready
        3. Connect to first instance
        4. Execute rs.initiate() with configuration
        5. Add remaining members with rs.add()
        6. Wait for replica set to stabilize
        7. Verify primary election

        Returns:
            OperationResult with build status
        """
        pass

    def destroy(self, force: bool = False) -> 'OperationResult':
        """
        Destroy/teardown the replica set.

        Steps:
        1. Shutdown secondary members first
        2. Step down primary (if graceful)
        3. Shutdown primary
        4. Remove Docker containers / K8s resources
        5. Optionally clean up volumes/data

        Args:
            force: If True, force shutdown without graceful stepdown

        Returns:
            OperationResult with teardown status
        """
        pass

    def shutdown(self, graceful: bool = True) -> 'OperationResult':
        """
        Shutdown replica set members without removing infrastructure.

        Args:
            graceful: If True, perform graceful shutdown with quiesce period

        Returns:
            OperationResult with shutdown status
        """
        pass

    # ============================================
    # INITIALIZATION & CONFIGURATION
    # (Based on rs.initiate, rs.reconfig, etc.)
    # ============================================

    def initiate(self, config: Optional['ReplicaSetConfig'] = None) -> 'OperationResult':
        """
        Initialize replica set (wraps rs.initiate()).

        This is the MongoDB command to create a new replica set.
        Called during deploy().
        """
        pass

    def reconfigure(
        self,
        config: 'ReplicaSetConfig',
        force: bool = False
    ) -> 'OperationResult':
        """
        Reconfigure replica set (wraps rs.reconfig()).

        Used to modify member configurations, priorities, etc.

        Args:
            config: New configuration document
            force: Force reconfiguration (use with caution)
        """
        pass

    def reconfigure_psa(
        self,
        config: 'ReplicaSetConfig',
        force: bool = False
    ) -> 'OperationResult':
        """
        Safely reconfigure PSA replica set (wraps rs.reconfigForPSASet()).

        Use this for Primary-Secondary-Arbiter (PSA) architecture to avoid
        unsafe reconfigurations that could lead to data loss.

        Args:
            config: New configuration document
            force: Force reconfiguration (use with extreme caution)

        Note:
            This method is specifically for PSA replica sets or sets
            transitioning to PSA architecture.
        """
        pass

    def get_config(self) -> 'ReplicaSetConfig':
        """Get current replica set configuration (wraps rs.conf())."""
        pass

    # ============================================
    # MEMBER MANAGEMENT
    # (Based on rs.add, rs.remove, rs.addArb)
    # ============================================

    def add_member(
        self,
        host: str,
        member_config: Optional['MemberConfig'] = None
    ) -> 'OperationResult':
        """
        Add a member to the replica set (wraps rs.add()).

        Args:
            host: hostname:port of new member
            member_config: Optional configuration for the member
        """
        pass

    def remove_member(self, host: str) -> 'OperationResult':
        """
        Remove a member from replica set (wraps rs.remove()).

        Args:
            host: hostname:port of member to remove
        """
        pass

    def add_arbiter(self, host: str) -> 'OperationResult':
        """
        Add an arbiter member (wraps rs.addArb()).

        Args:
            host: hostname:port of arbiter
        """
        pass

    # ============================================
    # STATUS & MONITORING
    # (Based on rs.status, db.hello, etc.)
    # ============================================

    def get_status(self) -> 'ReplicaSetStatus':
        """
        Get replica set status (wraps rs.status()).

        Returns detailed status of all members including:
        - Member states (PRIMARY, SECONDARY, etc.)
        - Health status
        - Replication lag
        - Oplog position
        """
        pass

    def is_healthy(self) -> bool:
        """Check if replica set is healthy (all members up, primary exists)."""
        pass

    def get_primary(self) -> Optional['ReplicaSetMember']:
        """Get the current primary member."""
        pass

    def get_secondaries(self) -> List['ReplicaSetMember']:
        """Get all secondary members."""
        pass

    def get_arbiters(self) -> List['ReplicaSetMember']:
        """Get all arbiter members."""
        pass

    # ============================================
    # ELECTION & FAILOVER
    # (Based on rs.stepDown, rs.freeze)
    # ============================================

    def step_down_primary(
        self,
        step_down_secs: int = 60,
        secondary_catch_up_secs: int = 10
    ) -> 'OperationResult':
        """
        Step down current primary (wraps rs.stepDown()).

        Forces primary to become secondary and triggers election.

        Args:
            step_down_secs: Seconds to prevent re-election as primary
            secondary_catch_up_secs: Max time to wait for secondaries to sync
        """
        pass

    def freeze_member(
        self,
        member_host: str,
        freeze_secs: int
    ) -> 'OperationResult':
        """
        Prevent member from becoming primary (wraps rs.freeze()).

        Args:
            member_host: Member to freeze
            freeze_secs: Seconds to freeze (0 = unfreeze)
        """
        pass

    def force_election(self) -> 'OperationResult':
        """
        Force a new election by stepping down primary.
        Useful for testing failover.
        """
        pass

    # ============================================
    # REPLICATION MONITORING
    # (Based on oplog, rs.printReplicationInfo, etc.)
    # ============================================

    def get_replication_lag(self) -> Dict[str, float]:
        """
        Get replication lag for each member in seconds.

        Returns:
            Dict mapping member hostname to lag in seconds
        """
        pass

    def get_oplog_info(self) -> 'OplogInfo':
        """
        Get oplog information (wraps rs.printReplicationInfo()).

        Returns oplog size, time coverage, usage, etc.
        """
        pass

    def get_secondary_replication_info(self) -> Dict[str, Dict]:
        """
        Get detailed replication info for secondaries
        (wraps rs.printSecondaryReplicationInfo()).
        """
        pass

    # ============================================
    # MAINTENANCE OPERATIONS
    # (Based on replSetMaintenance, rs.syncFrom, etc.)
    # ============================================

    def enable_maintenance_mode(self, member_host: str) -> 'OperationResult':
        """
        Enable maintenance mode on a secondary (wraps replSetMaintenance).

        Puts member in RECOVERING state, prevents reads.
        """
        pass

    def disable_maintenance_mode(self, member_host: str) -> 'OperationResult':
        """
        Disable maintenance mode on a secondary.
        """
        pass

    def set_sync_source(
        self,
        member_host: str,
        source_host: str
    ) -> 'OperationResult':
        """
        Set which member a secondary syncs from (wraps rs.syncFrom()).

        Args:
            member_host: Secondary to configure
            source_host: Source to sync from (or empty string for automatic)
        """
        pass

    def resync_member(self, member_host: str) -> 'OperationResult':
        """
        Force a full resync of a member's data.
        Used when member falls too far behind oplog.
        """
        pass

    def resize_oplog(
        self,
        member_host: str,
        size_mb: int
    ) -> 'OperationResult':
        """
        Resize oplog on a member (wraps replSetResizeOplog).
        WiredTiger engine only.
        """
        pass

    # ============================================
    # ADMINISTRATION
    # ============================================

    def rolling_restart(self) -> 'OperationResult':
        """
        Perform rolling restart of all members.
        Secondaries first, then primary.
        """
        pass

    def rolling_upgrade(self, target_version: str) -> 'OperationResult':
        """
        Perform rolling upgrade to new MongoDB version.
        """
        pass

    def create_backup(
        self,
        backup_path: str,
        use_secondary: bool = True
    ) -> 'OperationResult':
        """
        Create backup of replica set.
        Preferentially uses secondary to avoid impacting primary.
        """
        pass

    # ============================================
    # ADVANCED OPERATIONS
    # ============================================

    def validate_configuration(self) -> List[str]:
        """
        Validate replica set configuration.
        Returns list of warnings/issues.
        """
        pass

    def check_election_quorum(self) -> bool:
        """Check if sufficient voting members exist for elections."""
        pass

    def get_election_history(self) -> List['ElectionEvent']:
        """Get recent election events from logs."""
        pass

    def diagnose_replication_issues(self) -> 'DiagnosticReport':
        """
        Run diagnostics on replication health.
        Checks lag, oplog, network connectivity, etc.
        """
        pass

    # ============================================
    # HELPER METHODS
    # ============================================

    def _execute_command(
        self,
        command: str,
        member: Optional[str] = None,
        database: str = "admin"
    ) -> Any:
        """Execute MongoDB command on specified member or primary."""
        pass

    def _wait_for_primary_election(self, timeout_secs: int = 30) -> bool:
        """Wait for a primary to be elected."""
        pass

    def _wait_for_member_state(
        self,
        member_host: str,
        target_state: 'MemberState',
        timeout_secs: int = 30
    ) -> bool:
        """Wait for member to reach target state."""
        pass
```

## Supporting Classes

### ReplicaSetSettings

```python
@dataclass
class ReplicaSetSettings:
    """Global replica set settings."""
    chaining_allowed: bool = True
    heartbeat_interval_millis: int = 2000
    heartbeat_timeout_secs: int = 10
    election_timeout_millis: int = 10000
    catchup_timeout_millis: int = -1
    write_concern_majority_journal_default: bool = True
```

### MemberConfig

```python
@dataclass
class MemberConfig:
    """Configuration for a single replica set member."""
    id: int
    host: str
    arbiter_only: bool = False
    priority: int = 1              # 0-1000 (0 = cannot be primary)
    votes: int = 1                 # 0 or 1
    hidden: bool = False           # Hidden from client reads
    delay_secs: int = 0            # Delayed member
    tags: Dict[str, str] = None    # Custom tags

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
```

### MemberState

```python
class MemberState(Enum):
    """MongoDB replica set member states."""
    STARTUP = 0
    PRIMARY = 1
    SECONDARY = 2
    RECOVERING = 3
    STARTUP2 = 5
    UNKNOWN = 6
    ARBITER = 7
    DOWN = 8
    ROLLBACK = 9
    REMOVED = 10
```

## Summary: MongoDB Official Commands Mapped to Class Methods

| MongoDB Command | ReplicaSet Method | Purpose |
|-----------------|-------------------|---------|
| `rs.initiate()` | `initiate()` | Initialize replica set |
| `rs.add()` | `add_member()` | Add member |
| `rs.remove()` | `remove_member()` | Remove member |
| `rs.addArb()` | `add_arbiter()` | Add arbiter |
| `rs.conf()` | `get_config()` | Get configuration |
| `rs.reconfig()` | `reconfigure()` | Update configuration |
| `rs.reconfigForPSASet()` | `reconfigure_psa()` | Safe PSA reconfiguration |
| `rs.status()` | `get_status()` | Get replica set status |
| `rs.stepDown()` | `step_down_primary()` | Step down primary |
| `rs.freeze()` | `freeze_member()` | Prevent election |
| `rs.syncFrom()` | `set_sync_source()` | Set sync source |
| `rs.printReplicationInfo()` | `get_oplog_info()` | Get oplog info |
| `rs.printSecondaryReplicationInfo()` | `get_secondary_replication_info()` | Get secondary replication info |
| `replSetMaintenance` | `enable_maintenance_mode()` | Enable maintenance |
| `replSetResizeOplog` | `resize_oplog()` | Resize oplog |
| `db.shutdownServer()` | `shutdown()` | Shutdown member |

## Lifecycle Example

```python
from gds_mongodb import ReplicaSet, MemberConfig

# Define replica set
replica_set = ReplicaSet(
    name="rs0",
    members=[
        MemberConfig(id=0, host="mongo1:27017", priority=2),
        MemberConfig(id=1, host="mongo2:27017", priority=1),
        MemberConfig(id=2, host="mongo3:27017", priority=1),
    ],
    platform="docker"
)

# Build
result = replica_set.build()
assert result.success

# Operate
status = replica_set.get_status()
primary = replica_set.get_primary()
lag = replica_set.get_replication_lag()

# Destroy
result = replica_set.destroy(force=False)
assert result.success
```

This design follows MongoDB's official terminology and includes all documented replica set operations.
