# Replication Architecture - Platform Differences

## Overview

Different database platforms implement replication at different levels of abstraction. This design document clarifies where replication lives in each platform and how the OOP design accommodates these differences.

---

## Replication Levels by Platform

### Engine-Level Replication (Instance-Wide)

Replication scope: **Entire database server/cluster**
All databases are replicated together as a unit.

#### MongoDB - Replica Sets ✅

```
┌─────────────────────────────────────┐
│     MongoDBEngine (Instance)        │
│  ┌───────────────────────────────┐  │
│  │      Replica Set              │  │
│  │  ┌─────────┬─────────┬──────┐ │  │
│  │  │Primary  │Secondary│Sec   │ │  │
│  │  └─────────┴─────────┴──────┘ │  │
│  └───────────────────────────────┘  │
│     ↓           ↓           ↓       │
│  [db1, db2]  [db1, db2]  [db1, db2] │ ← ALL databases replicated
└─────────────────────────────────────┘
```

**Key Points:**
- Replica set is an **engine property**
- All databases in instance are replicated together
- Cannot selectively replicate individual databases

**OOP Design:**
```python
class MongoDBEngine(DatabaseEngine):
    @property
    def replica_set(self) -> Optional[ReplicaSet]:
        """Replica set managing this entire engine"""
        pass

    def get_replication_status(self) -> ReplicationStatus:
        """Returns replica set status for entire instance"""
        if self.replica_set:
            return self.replica_set.get_status()
        return ReplicationStatus(enabled=False, ...)
```

#### PostgreSQL - Streaming Replication (Physical)

```
┌────────────────────────────────────────┐
│  PostgreSQLEngine (Instance)           │
│  ┌──────────────────────────────────┐  │
│  │  Streaming Replication           │  │
│  │  ┌────────┬────────┬─────────┐   │  │
│  │  │Primary │Standby1│Standby2 │   │  │
│  │  └────────┴────────┴─────────┘   │  │
│  └──────────────────────────────────┘  │
│     ↓         ↓         ↓              │
│  [db1,db2] [db1,db2] [db1,db2]         │ ← ALL databases replicated
└────────────────────────────────────────┘
```

**OOP Design:**
```python
class PostgreSQLEngine(DatabaseEngine):
    @property
    def streaming_replication(self) -> Optional[StreamingReplication]:
        """Physical replication at instance level"""
        pass
```

---

### Database-Level Replication (Selective)

Replication scope: **Individual databases or groups of databases**
Each database can have independent replication configuration.

#### MSSQL - Always On Availability Groups

```
┌───────────────────────────────────────────┐
│       MSSQLEngine (Instance)              │
│  ┌─────────┬─────────┬─────────┐          │
│  │  db1    │  db2    │  db3    │          │
│  │   ↓     │   ↓     │   X     │          │
│  │  AG1    │  AG2    │ (none)  │          │
│  └─────────┴─────────┴─────────┘          │
│     ↓         ↓                            │
│  [Primary,  [Primary,                      │
│   Sec1,     Sec1]                          │
│   Sec2]                                    │
└───────────────────────────────────────────┘
```

**Key Points:**
- Availability Group is a **database property**
- Each database independently configured
- db1, db2 have AGs; db3 does not

**OOP Design:**
```python
class MSSQLDatabase(Database):
    @property
    def availability_group(self) -> Optional[AvailabilityGroup]:
        """Availability group for THIS database"""
        pass

    def get_replication_status(self) -> ReplicationStatus:
        """Returns AG status for this specific database"""
        if self.availability_group:
            return self.availability_group.get_status()
        return ReplicationStatus(enabled=False, ...)
```

#### Snowflake - Failover Groups

```
┌───────────────────────────────────────────┐
│    SnowflakeEngine (Account)              │
│  ┌─────────┬─────────┬─────────┐          │
│  │  db1    │  db2    │  db3    │          │
│  │   ↓     │   ↓     │   X     │          │
│  │  FG1    │  FG1    │ (none)  │          │
│  └─────────┴─────────┴─────────┘          │
│     ↓                                      │
│  [Primary Region → Secondary Region]      │
└───────────────────────────────────────────┘
```

**Key Points:**
- Failover Group is a **database property**
- Multiple databases can share a failover group
- Selective replication per database

**OOP Design:**
```python
class SnowflakeDatabase(Database):
    @property
    def failover_group(self) -> Optional[FailoverGroup]:
        """Failover group for THIS database"""
        pass

    def get_replication_status(self) -> ReplicationStatus:
        """Returns failover group status for this database"""
        if self.failover_group:
            return self.failover_group.get_status()
        return ReplicationStatus(enabled=False, ...)
```

#### PostgreSQL - Logical Replication (Per-Database)

```
┌────────────────────────────────────────┐
│  PostgreSQLEngine (Instance)           │
│  ┌─────────┬─────────┬─────────┐        │
│  │  db1    │  db2    │  db3    │        │
│  │   ↓     │   X     │   ↓     │        │
│  │  Pub/Sub│ (none)  │ Pub/Sub │        │
│  └─────────┴─────────┴─────────┘        │
└────────────────────────────────────────┘
```

**OOP Design:**
```python
class PostgreSQLDatabase(Database):
    @property
    def logical_replication(self) -> Optional[LogicalReplication]:
        """Logical replication for THIS database"""
        pass
```

---

## OOP Design Pattern

### Abstract Base Classes

Both `DatabaseEngine` and `Database` have `get_replication_status()`:

```python
class DatabaseEngine(ABC):
    @abstractmethod
    def get_replication_status(self) -> ReplicationStatus:
        """
        Get engine-level replication status.

        Returns disabled status if platform uses database-level replication.
        """
        pass

class Database(ABC):
    @abstractmethod
    def get_replication_status(self) -> ReplicationStatus:
        """
        Get database-level replication status.

        Returns disabled status if platform uses engine-level replication.
        """
        pass
```

### Implementation Matrix

| Platform | Engine.get_replication_status() | Database.get_replication_status() |
|----------|----------------------------------|-----------------------------------|
| **MongoDB** | ✅ Returns replica set status | ❌ Returns disabled (not applicable) |
| **MSSQL** | ❌ Returns disabled (not applicable) | ✅ Returns AG status |
| **Snowflake** | ❌ Returns disabled (not applicable) | ✅ Returns failover group status |
| **PostgreSQL** | ✅ Returns streaming replication | ✅ Returns logical replication (both!) |

### Code Examples

#### MongoDB (Engine-Level)

```python
# Replication at engine level
mongo_engine = MongoDBEngine(connection)
engine_status = mongo_engine.get_replication_status()  # ✅ Replica set status

# Database level - not applicable
mongo_db = mongo_engine.get_database("mydb")
db_status = mongo_db.get_replication_status()  # ❌ Returns disabled
```

#### MSSQL (Database-Level)

```python
# Engine level - not applicable
mssql_engine = MSSQLEngine(connection)
engine_status = mssql_engine.get_replication_status()  # ❌ Returns disabled

# Replication at database level
mssql_db = mssql_engine.get_database("mydb")
db_status = mssql_db.get_replication_status()  # ✅ AG status
ag = mssql_db.availability_group  # Access AG directly
```

#### PostgreSQL (Both Levels!)

```python
# Engine level - streaming replication
pg_engine = PostgreSQLEngine(connection)
engine_status = pg_engine.get_replication_status()  # ✅ Streaming status

# Database level - logical replication
pg_db = pg_engine.get_database("mydb")
db_status = pg_db.get_replication_status()  # ✅ Logical replication status
```

---

## Platform-Specific HA/DR Objects

### MongoDB
```python
class ReplicaSet:
    """Engine-level HA/DR"""
    name: str
    members: List[ReplicaSetMember]

    def build() -> OperationResult
    def destroy() -> OperationResult
    def get_status() -> ReplicaSetStatus
    def add_member(...) -> OperationResult
    def step_down_primary(...) -> OperationResult
```

### MSSQL
```python
class AvailabilityGroup:
    """Database-level HA/DR"""
    name: str
    databases: List[str]
    replicas: List[AvailabilityReplica]

    def create() -> OperationResult
    def drop() -> OperationResult
    def get_status() -> AGStatus
    def add_database(...) -> OperationResult
    def failover(...) -> OperationResult
```

### Snowflake
```python
class FailoverGroup:
    """Database-level HA/DR"""
    name: str
    databases: List[str]
    source_account: str
    target_accounts: List[str]

    def create() -> OperationResult
    def drop() -> OperationResult
    def get_status() -> FailoverGroupStatus
    def failover(...) -> OperationResult
```

---

## Summary

✅ **Engine-Level Replication** (MongoDB, PostgreSQL streaming)
- All databases replicated together
- HA/DR object is property of `DatabaseEngine`
- `engine.get_replication_status()` returns actual status

✅ **Database-Level Replication** (MSSQL, Snowflake, PostgreSQL logical)
- Selective per-database replication
- HA/DR object is property of `Database`
- `database.get_replication_status()` returns actual status

✅ **Flexible Design**
- Both ABCs have `get_replication_status()`
- Implementations return appropriate status or "disabled"
- Platform-specific HA/DR objects as properties
- Supports platforms with both levels (PostgreSQL)
