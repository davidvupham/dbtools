# GDS Database Package - Object-Oriented Design

**Document Version:** 1.0
**Date:** November 4, 2025
**Author:** Global Data Services Team

---

## Executive Summary

This document outlines a comprehensive design of the `gds_database` package to follow object-oriented best practices. The design introduces a **Database Object Model** that represents databases as first-class entities with attributes and operations, supporting multiple database types (Microsoft SQL Server, Snowflake, MongoDB, PostgreSQL, etc.) through a unified, extensible architecture.

### Key Design Goals

1. **Database as a Domain Entity**: Model databases as objects with attributes (name, size, collation, etc.) and operations (backup, restore, offline, etc.)
2. **Multi-Platform Support**: Unified interface supporting MSSQL, Snowflake, MongoDB, PostgreSQL, and future database types
3. **Strong OOP Principles**: Adherence to SOLID principles, proper abstraction, encapsulation, and polymorphism
4. **Separation of Concerns**: Clear distinction between connection management, database operations, and metadata
5. **Extensibility**: Easy addition of new database types and operations without modifying existing code
6. **Type Safety**: Full type hints and protocol support for compile-time checking

---

## Table of Contents

1. [Current Architecture Analysis](#1-current-architecture-analysis)
2. [Proposed Architecture](#2-proposed-architecture)
3. [Core Abstractions](#3-core-abstractions)
4. [Database Type Implementations](#4-database-type-implementations)
5. [Class Hierarchy](#5-class-hierarchy)
6. [Design Patterns](#6-design-patterns)
7. [API Design](#7-api-design)
8. [Migration Strategy](#8-migration-strategy)
9. [Implementation Plan](#9-implementation-plan)

---

## 1. Current Architecture Analysis

### 1.1 Strengths

- **Well-defined abstractions**: `DatabaseConnection`, `ConfigurableComponent`, `ResourceManager`
- **Strong type safety**: Comprehensive type hints throughout
- **Good separation**: Connection management separated from configuration
- **Async support**: Both sync and async patterns supported
- **Error handling**: Custom exceptions for different failure modes

### 1.2 Limitations

1. **No Database Domain Model**: Current design focuses on connections, not database entities
2. **Limited Metadata Support**: No standardized way to represent database attributes
3. **Operation-centric**: Lacks object-centric operations (backup, restore, etc.)
4. **Type-specific Logic**: Each implementation (MSSQL, Postgres) duplicates patterns
5. **No Database Object Lifecycle**: Missing create, alter, drop operations at database level

### 1.3 Gap Analysis

| Feature | Current State | Desired State |
|---------|--------------|---------------|
| Database as Object | ❌ Not represented | ✅ First-class entity |
| Database Attributes | ❌ No model | ✅ Rich attribute model |
| Database Operations | ❌ Query-only | ✅ Full CRUD + admin ops |
| Multi-type Support | ⚠️ Implicit | ✅ Explicit polymorphism |
| Metadata Management | ⚠️ Ad-hoc | ✅ Structured & unified |
| Type-specific Features | ❌ Scattered | ✅ Extensible system |

---

## 2. Proposed Architecture

### 2.1 Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│            (User code using gds_database)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Domain Model Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Database   │  │    Schema    │  │    Table     │      │
│  │   (Entity)   │  │   (Entity)   │  │   (Entity)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Operations & Services Layer                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Database   │  │   Metadata   │  │    Backup    │      │
│  │   Manager    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Database-Specific Implementations               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    MSSQL     │  │  Snowflake   │  │  PostgreSQL  │      │
│  │   Provider   │  │   Provider   │  │   Provider   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Connection Layer                           │
│            (Existing DatabaseConnection ABCs)                │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Core Concepts

1. **Database Entity**: Represents a database with attributes and operations
2. **Database Provider**: Platform-specific implementations (MSSQL, Snowflake, etc.)
3. **Operation Services**: Specialized services for backup, restore, monitoring, etc.
4. **Metadata Model**: Structured representation of database properties
5. **Database Manager**: Factory and lifecycle management

---

## 3. Core Abstractions

### 3.1 Database Entity (Domain Model)

```python
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
```

```python
class Database(ABC):
    """
    Abstract base class representing a database entity.

    A database is a first-class domain object with:
    - Attributes (metadata): name, size, collation, etc.
    - Operations: create, drop, backup, restore, etc.
    - State: online, offline, restoring, etc.
    """

    def __init__(
        self,
        name: str,
        connection: DatabaseConnection,
        metadata: Optional[DatabaseMetadata] = None
    ):
        self.name = name
        self.connection = connection
        self._metadata = metadata

    # ========== Metadata & Attributes ==========

    @abstractmethod
    def get_metadata(self) -> DatabaseMetadata:
        """Retrieve current database metadata."""
        pass

    @abstractmethod
    def refresh_metadata(self) -> None:
        """Refresh metadata from the database server."""
        pass

    @property
    def metadata(self) -> DatabaseMetadata:
        """Get cached metadata."""
        if self._metadata is None:
            self._metadata = self.get_metadata()
        return self._metadata

    # ========== Lifecycle Operations ==========

    @abstractmethod
    def exists(self) -> bool:
        """Check if database exists on the server."""
        pass

    @abstractmethod
    def create(self, **options) -> OperationResult:
        """Create the database."""
        pass

    @abstractmethod
    def drop(self, force: bool = False) -> OperationResult:
        """Drop the database."""
        pass

    # ========== State Management ==========

    @abstractmethod
    def get_state(self) -> DatabaseState:
        """Get current database state."""
        pass

    @abstractmethod
    def set_online(self) -> OperationResult:
        """Bring database online."""
        pass

    @abstractmethod
    def set_offline(self) -> OperationResult:
        """Take database offline."""
        pass

    # ========== Access Control ==========

    @abstractmethod
    def set_single_user_mode(self) -> OperationResult:
        """Set database to single-user mode."""
        pass

    @abstractmethod
    def set_multi_user_mode(self) -> OperationResult:
        """Set database to multi-user mode."""
        pass

    # ========== Backup & Restore ==========

    @abstractmethod
    def backup(
        self,
        backup_path: str,
        backup_type: BackupType = BackupType.FULL,
        **options
    ) -> OperationResult:
        """Backup the database."""
        pass

    @abstractmethod
    def restore(
        self,
        backup_path: str,
        **options
    ) -> OperationResult:
        """Restore the database from backup."""
        pass

    # ========== Schema & Objects ==========

    @abstractmethod
    def list_schemas(self) -> List[str]:
        """List all schemas in the database."""
        pass

    @abstractmethod
    def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """List all tables in the database."""
        pass

    # ========== Utility Methods ==========

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"

    def __str__(self) -> str:
        return self.name
```

### 3.2 Database Type Enumeration

```python
from enum import Enum

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
```

### 3.3 Database Provider (Strategy Pattern)

```python
class DatabaseProvider(ABC):
    """
    Abstract base class for database-specific implementations.

    Each database type (MSSQL, Snowflake, etc.) implements this
    interface to provide platform-specific functionality.
    """

    @property
    @abstractmethod
    def database_type(self) -> DatabaseType:
        """Get the database type this provider supports."""
        pass

    @abstractmethod
    def create_database(
        self,
        connection: DatabaseConnection,
        name: str,
        **options
    ) -> Database:
        """Create a Database instance for this provider."""
        pass

    @abstractmethod
    def supports_feature(self, feature: str) -> bool:
        """Check if a feature is supported by this provider."""
        pass

    @abstractmethod
    def get_server_metadata(
        self,
        connection: DatabaseConnection
    ) -> Dict[str, Any]:
        """Get server-level metadata."""
        pass
```

### 3.4 Database Manager (Factory Pattern)

```python
class DatabaseManager:
    """
    Factory and manager for database instances.

    Provides high-level API for working with databases across
    different platforms.
    """

    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self._provider = self._detect_provider()

    def _detect_provider(self) -> DatabaseProvider:
        """Detect database provider from connection."""
        # Implementation that detects database type
        pass

    def get_database(self, name: str) -> Database:
        """Get a Database instance."""
        return self._provider.create_database(self.connection, name)

    def list_databases(self) -> List[Database]:
        """List all databases on the server."""
        pass

    def create_database(self, name: str, **options) -> Database:
        """Create a new database."""
        pass

    def drop_database(self, name: str, force: bool = False) -> OperationResult:
        """Drop a database."""
        pass

    def database_exists(self, name: str) -> bool:
        """Check if a database exists."""
        pass
```

---

## 4. Database Type Implementations

### 4.1 Microsoft SQL Server

```python
@dataclass
class MSSQLDatabaseMetadata(DatabaseMetadata):
    """MSSQL-specific metadata."""
    recovery_model: Optional[str] = None
    compatibility_level: Optional[int] = None
    page_verify_option: Optional[str] = None
    is_auto_close_on: Optional[bool] = None
    is_auto_shrink_on: Optional[bool] = None

    # File groups
    filegroups: List[Dict[str, Any]] = field(default_factory=list)

    # Files
    data_files: List[Dict[str, Any]] = field(default_factory=list)
    log_files: List[Dict[str, Any]] = field(default_factory=list)

class MSSQLDatabase(Database):
    """Microsoft SQL Server database implementation."""

    def get_metadata(self) -> MSSQLDatabaseMetadata:
        """Get MSSQL-specific metadata."""
        query = """
        SELECT
            d.name,
            d.database_id,
            d.create_date,
            d.collation_name,
            d.state_desc,
            d.recovery_model_desc,
            d.compatibility_level,
            d.page_verify_option_desc,
            d.is_auto_close_on,
            d.is_auto_shrink_on,
            CAST(SUM(mf.size) * 8.0 / 1024 / 1024 AS DECIMAL(18,2)) AS size_gb
        FROM sys.databases d
        LEFT JOIN sys.master_files mf ON d.database_id = mf.database_id
        WHERE d.name = ?
        GROUP BY d.name, d.database_id, d.create_date, ...
        """
        # Execute query and build metadata object
        pass

    def create(self, **options) -> OperationResult:
        """
        Create MSSQL database.

        Supported options:
        - collation: Database collation
        - recovery_model: SIMPLE, FULL, BULK_LOGGED
        - containment: NONE, PARTIAL
        - filegroups: List of filegroup definitions
        - data_files: List of data file definitions
        - log_files: List of log file definitions
        """
        # Build CREATE DATABASE statement
        pass

    def backup(
        self,
        backup_path: str,
        backup_type: BackupType = BackupType.FULL,
        **options
    ) -> OperationResult:
        """
        Backup MSSQL database.

        Supported options:
        - compression: Enable backup compression
        - checksum: Perform checksum
        - init: Overwrite existing backup set
        - format: Format the media
        """
        # Build BACKUP DATABASE statement
        pass

    def set_recovery_model(self, model: str) -> OperationResult:
        """Set database recovery model (MSSQL-specific)."""
        pass

    def shrink(self, target_percent: Optional[int] = None) -> OperationResult:
        """Shrink database (MSSQL-specific)."""
        pass
```

### 4.2 Snowflake

```python
@dataclass
class SnowflakeDatabaseMetadata(DatabaseMetadata):
    """Snowflake-specific metadata."""
    is_transient: bool = False
    retention_time_days: Optional[int] = None
    comment: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)

class SnowflakeDatabase(Database):
    """Snowflake database implementation."""

    def get_metadata(self) -> SnowflakeDatabaseMetadata:
        """Get Snowflake-specific metadata."""
        query = """
        SELECT
            DATABASE_NAME,
            DATABASE_OWNER,
            IS_TRANSIENT,
            RETENTION_TIME,
            COMMENT,
            CREATED,
            LAST_ALTERED
        FROM SNOWFLAKE.INFORMATION_SCHEMA.DATABASES
        WHERE DATABASE_NAME = %s
        """
        pass

    def create(self, **options) -> OperationResult:
        """
        Create Snowflake database.

        Supported options:
        - transient: Create transient database
        - clone: Clone from existing database
        - time_travel_retention_days: Set retention period
        - data_retention_time_in_days: Set data retention
        - comment: Database comment
        """
        pass

    def backup(self, backup_path: str, **options) -> OperationResult:
        """
        Backup Snowflake database (uses cloning or time travel).

        Note: Snowflake doesn't use traditional backups.
        This creates a clone or manages time travel.
        """
        pass

    def clone(self, target_name: str, at_time: Optional[datetime] = None) -> OperationResult:
        """Clone database (Snowflake-specific)."""
        pass

    def set_retention_time(self, days: int) -> OperationResult:
        """Set time travel retention (Snowflake-specific)."""
        pass
```

### 4.3 PostgreSQL

```python
@dataclass
class PostgreSQLDatabaseMetadata(DatabaseMetadata):
    """PostgreSQL-specific metadata."""
    encoding: Optional[str] = None
    lc_collate: Optional[str] = None
    lc_ctype: Optional[str] = None
    tablespace: Optional[str] = None
    connection_limit: Optional[int] = None

class PostgreSQLDatabase(Database):
    """PostgreSQL database implementation."""

    def get_metadata(self) -> PostgreSQLDatabaseMetadata:
        """Get PostgreSQL-specific metadata."""
        query = """
        SELECT
            d.datname AS name,
            pg_catalog.pg_get_userbyid(d.datdba) AS owner,
            pg_catalog.pg_encoding_to_char(d.encoding) AS encoding,
            d.datcollate AS lc_collate,
            d.datctype AS lc_ctype,
            t.spcname AS tablespace,
            d.datconnlimit AS connection_limit,
            pg_catalog.pg_database_size(d.datname) AS size_bytes
        FROM pg_catalog.pg_database d
        LEFT JOIN pg_catalog.pg_tablespace t ON d.dattablespace = t.oid
        WHERE d.datname = %s
        """
        pass

    def create(self, **options) -> OperationResult:
        """
        Create PostgreSQL database.

        Supported options:
        - owner: Database owner
        - encoding: Character encoding
        - lc_collate: Collation order
        - lc_ctype: Character classification
        - tablespace: Default tablespace
        - template: Template database
        - connection_limit: Max connections
        """
        pass

    def backup(
        self,
        backup_path: str,
        backup_type: BackupType = BackupType.FULL,
        **options
    ) -> OperationResult:
        """
        Backup PostgreSQL database using pg_dump.

        Supported options:
        - format: custom, directory, tar, plain
        - compress: Compression level (0-9)
        - schema: Specific schema to backup
        - jobs: Number of parallel jobs
        """
        pass

    def vacuum(self, full: bool = False, analyze: bool = True) -> OperationResult:
        """Vacuum database (PostgreSQL-specific)."""
        pass
```

### 4.4 MongoDB

```python
@dataclass
class MongoDBDatabaseMetadata(DatabaseMetadata):
    """MongoDB-specific metadata."""
    collections_count: int = 0
    views_count: int = 0
    data_size: int = 0
    storage_size: int = 0
    indexes_count: int = 0
    index_size: int = 0

class MongoDBDatabase(Database):
    """MongoDB database implementation."""

    def get_metadata(self) -> MongoDBDatabaseMetadata:
        """Get MongoDB-specific metadata."""
        # Use db.stats() command
        pass

    def create(self, **options) -> OperationResult:
        """
        Create MongoDB database.

        Note: MongoDB creates databases implicitly.
        This ensures the database exists.
        """
        pass

    def backup(self, backup_path: str, **options) -> OperationResult:
        """
        Backup MongoDB database using mongodump.

        Supported options:
        - archive: Create archive file
        - gzip: Compress backup
        - oplog: Include oplog
        """
        pass

    def list_collections(self) -> List[str]:
        """List collections (MongoDB-specific)."""
        pass

    def get_profiling_level(self) -> int:
        """Get profiling level (MongoDB-specific)."""
        pass
```

---

## 5. Class Hierarchy

```
DatabaseConnection (existing ABC)
    ├── MSSQLConnection
    ├── SnowflakeConnection
    ├── PostgreSQLConnection
    └── MongoDBConnection

Database (new ABC)
    ├── MSSQLDatabase
    ├── SnowflakeDatabase
    ├── PostgreSQLDatabase
    └── MongoDBDatabase

DatabaseMetadata (new dataclass)
    ├── MSSQLDatabaseMetadata
    ├── SnowflakeDatabaseMetadata
    ├── PostgreSQLDatabaseMetadata
    └── MongoDBDatabaseMetadata

DatabaseProvider (new ABC)
    ├── MSSQLProvider
    ├── SnowflakeProvider
    ├── PostgreSQLProvider
    └── MongoDBProvider

DatabaseManager (new concrete class)

OperationResult (existing dataclass)
    └── [No changes needed]

# Enumerations
DatabaseType (new enum)
DatabaseState (new enum)
BackupType (new enum)
```

---

## 6. Design Patterns

### 6.1 Strategy Pattern
- **DatabaseProvider** acts as strategy interface
- Each database type provides specific implementation
- Enables runtime selection of database-specific behavior

### 6.2 Factory Pattern
- **DatabaseManager** serves as factory
- Creates appropriate Database instances based on provider
- Encapsulates object creation logic

### 6.3 Template Method Pattern
- **Database ABC** defines operation templates
- Subclasses implement specific steps
- Common validation and error handling in base class

### 6.4 Adapter Pattern
- Database classes adapt database-specific APIs
- Provides unified interface across platforms
- Isolates platform-specific details

### 6.5 Facade Pattern
- **DatabaseManager** provides simplified interface
- Hides complexity of provider detection and instantiation
- Single entry point for database operations

---

## 7. API Design

### 7.1 Simple Usage Examples

```python
# Example 1: Basic database operations
from gds_database import DatabaseManager
from gds_mssql import MSSQLConnection

# Connect and get database manager
conn = MSSQLConnection(server="localhost", database="master")
manager = DatabaseManager(conn)

# Get database instance
db = manager.get_database("MyDatabase")

# Check if exists
if db.exists():
    # Get metadata
    metadata = db.metadata
    print(f"Database: {metadata.name}")
    print(f"Size: {metadata.size_bytes / 1024 / 1024:.2f} MB")
    print(f"State: {metadata.state}")

    # Perform operations
    db.set_offline()
    db.backup("/backups/mydb.bak", BackupType.FULL)
    db.set_online()
```

```python
# Example 2: Create and configure database
from gds_database import DatabaseManager, BackupType
from gds_mssql import MSSQLConnection

conn = MSSQLConnection(server="localhost", database="master")
manager = DatabaseManager(conn)

# Create new database
result = manager.create_database(
    "MyNewDB",
    collation="SQL_Latin1_General_CP1_CI_AS",
    recovery_model="FULL",
    data_files=[
        {"name": "primary", "size_mb": 100, "growth_mb": 10}
    ],
    log_files=[
        {"name": "log", "size_mb": 50, "growth_mb": 10}
    ]
)

if result.is_success():
    db = manager.get_database("MyNewDB")
    print(f"Created: {db.metadata.name}")
```

```python
# Example 3: Multi-platform code
from gds_database import DatabaseManager

def backup_database(connection, db_name, backup_path):
    """Works with any database type."""
    manager = DatabaseManager(connection)
    db = manager.get_database(db_name)

    result = db.backup(backup_path)
    return result.is_success()

# Works with MSSQL
from gds_mssql import MSSQLConnection
mssql_conn = MSSQLConnection(server="localhost", database="master")
backup_database(mssql_conn, "MyDB", "/backups/mydb.bak")

# Works with PostgreSQL
from gds_postgres import PostgreSQLConnection
pg_conn = PostgreSQLConnection(host="localhost", database="postgres")
backup_database(pg_conn, "mydb", "/backups/mydb.dump")

# Works with Snowflake
from gds_snowflake import SnowflakeConnection
sf_conn = SnowflakeConnection(account="myaccount", database="MYDB")
backup_database(sf_conn, "MYDB", "MYDB_BACKUP")
```

### 7.2 Advanced Usage

```python
# Platform-specific features
from gds_database import DatabaseManager
from gds_mssql import MSSQLConnection, MSSQLDatabase

conn = MSSQLConnection(server="localhost", database="master")
manager = DatabaseManager(conn)

db = manager.get_database("MyDB")

# Type check for platform-specific operations
if isinstance(db, MSSQLDatabase):
    # MSSQL-specific operations
    db.set_recovery_model("FULL")
    db.shrink(target_percent=10)

    # Access MSSQL-specific metadata
    metadata = db.metadata
    print(f"Recovery Model: {metadata.recovery_model}")
    print(f"Page Verify: {metadata.page_verify_option}")
```

---

## 8. Migration Strategy

### 8.1 Backward Compatibility

- **Keep existing classes**: `DatabaseConnection`, `ConfigurableComponent`, etc.
- **Add new abstractions**: `Database`, `DatabaseProvider`, `DatabaseManager`
- **Deprecation period**: Mark old patterns as deprecated with warnings
- **Version 2.0**: Remove deprecated patterns in major version bump

### 8.2 Migration Path

**Phase 1: Add New Abstractions (v1.5.0)**
- Introduce `Database`, `DatabaseProvider`, `DatabaseManager`
- Implement for MSSQL and PostgreSQL
- Keep existing connection classes unchanged
- Add deprecation warnings to old patterns

**Phase 2: Update Implementations (v1.6.0)**
- Add Snowflake and MongoDB implementations
- Create migration guide
- Provide compatibility layer

**Phase 3: Full Migration (v2.0.0)**
- Remove deprecated patterns
- Make new architecture the standard
- Update all documentation

### 8.3 Breaking Changes

- Method signatures on connection classes remain unchanged
- New classes are additive, not replacing
- Minimal breaking changes for existing users

---

## 9. Implementation Plan

### 9.1 Phase 1: Core Framework (Week 1-2)

**Tasks:**
1. Create enumerations (`DatabaseType`, `DatabaseState`, `BackupType`)
2. Implement `DatabaseMetadata` dataclass
3. Create `Database` abstract base class
4. Implement `DatabaseProvider` abstract base class
5. Create `DatabaseManager` factory class
6. Write comprehensive unit tests

**Deliverables:**
- `gds_database/database.py` - Core database abstractions
- `gds_database/enums.py` - Enumerations
- `gds_database/metadata.py` - Metadata models
- `gds_database/provider.py` - Provider interface
- `gds_database/manager.py` - Manager implementation
- `tests/test_database.py` - Test suite

### 9.2 Phase 2: MSSQL Implementation (Week 3)

**Tasks:**
1. Create `MSSQLDatabaseMetadata` class
2. Implement `MSSQLDatabase` class
3. Implement `MSSQLProvider` class
4. Add MSSQL-specific operations
5. Write integration tests

**Deliverables:**
- `gds_mssql/database.py` - MSSQL database implementation
- `gds_mssql/provider.py` - MSSQL provider
- `tests/test_mssql_database.py` - Test suite
- Documentation updates

### 9.3 Phase 3: PostgreSQL Implementation (Week 4)

**Tasks:**
1. Create `PostgreSQLDatabaseMetadata` class
2. Implement `PostgreSQLDatabase` class
3. Implement `PostgreSQLProvider` class
4. Add PostgreSQL-specific operations
5. Write integration tests

**Deliverables:**
- `gds_postgres/database.py` - PostgreSQL database implementation
- `gds_postgres/provider.py` - PostgreSQL provider
- `tests/test_postgres_database.py` - Test suite

### 9.4 Phase 4: Snowflake Implementation (Week 5)

**Tasks:**
1. Create `SnowflakeDatabaseMetadata` class
2. Implement `SnowflakeDatabase` class
3. Implement `SnowflakeProvider` class
4. Add Snowflake-specific operations
5. Write integration tests

**Deliverables:**
- `gds_snowflake/database.py` - Snowflake database implementation
- `gds_snowflake/provider.py` - Snowflake provider
- `tests/test_snowflake_database.py` - Test suite

### 9.5 Phase 5: MongoDB Implementation (Week 6)

**Tasks:**
1. Create `MongoDBDatabaseMetadata` class
2. Implement `MongoDBDatabase` class
3. Implement `MongoDBProvider` class
4. Add MongoDB-specific operations
5. Write integration tests

**Deliverables:**
- `gds_mongodb/database.py` - MongoDB database implementation
- `gds_mongodb/provider.py` - MongoDB provider
- `tests/test_mongodb_database.py` - Test suite

### 9.6 Phase 6: Documentation & Examples (Week 7)

**Tasks:**
1. Update README files for all packages
2. Create migration guide
3. Write API documentation
4. Create usage examples
5. Update tutorials

**Deliverables:**
- Updated README.md files
- MIGRATION_GUIDE.md
- API_REFERENCE.md
- examples/ directory with samples
- Tutorial updates

---

## 10. Success Criteria

### 10.1 Technical Criteria

- ✅ All database types implement `Database` interface
- ✅ 100% type hint coverage
- ✅ >90% test coverage
- ✅ Zero linting errors (ruff)
- ✅ Zero mypy errors
- ✅ Successful pip installation
- ✅ All examples run without errors

### 10.2 Design Criteria

- ✅ SOLID principles followed
- ✅ Clear separation of concerns
- ✅ Minimal code duplication
- ✅ Platform-specific code properly isolated
- ✅ Easy to add new database types
- ✅ Backward compatible (where possible)

### 10.3 Documentation Criteria

- ✅ Complete API documentation
- ✅ Usage examples for all major operations
- ✅ Migration guide for existing users
- ✅ Architecture documentation
- ✅ Tutorial for each database type

---

## 11. High Availability Design

### 11.1 Overview

High availability (HA) features vary significantly across database platforms but share common concepts:
- **Replication**: Data synchronization across multiple nodes
- **Failover**: Automatic or manual promotion of secondary to primary
- **Monitoring**: Health checks and status monitoring
- **Recovery**: Restoration of failed nodes

### 11.2 HA Abstraction Design

#### 11.2.1 Core HA Abstractions

```python
from enum import Enum
from typing import Protocol, runtime_checkable

class HARole(str, Enum):
    """High availability node roles."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ARBITER = "arbiter"
    WITNESS = "witness"
    STANDBY = "standby"
    REPLICA = "replica"
    UNKNOWN = "unknown"

class HAState(str, Enum):
    """High availability states."""
    HEALTHY = "healthy"
    SYNCHRONIZING = "synchronizing"
    SYNCED = "synced"
    NOT_SYNCHRONIZED = "not_synchronized"
    SUSPENDED = "suspended"
    DISCONNECTED = "disconnected"
    RESOLVING = "resolving"
    FAILOVER_IN_PROGRESS = "failover_in_progress"
    UNKNOWN = "unknown"

class SyncMode(str, Enum):
    """Replication synchronization modes."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    SEMI_SYNCHRONOUS = "semi_synchronous"

@dataclass
class HANodeInfo:
    """Information about a node in an HA configuration."""
    node_name: str
    role: HARole
    state: HAState
    endpoint: str  # Host:Port or connection string
    lag_seconds: Optional[float] = None
    last_sync_time: Optional[datetime] = None
    is_healthy: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HAConfiguration:
    """High availability configuration information."""
    name: str
    type: str  # "replica_set", "availability_group", "replication", etc.
    nodes: List[HANodeInfo]
    sync_mode: SyncMode
    automatic_failover: bool
    created: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### 11.2.2 High Availability Protocol

```python
@runtime_checkable
class HighAvailabilityCapable(Protocol):
    """
    Protocol for databases that support high availability.

    This protocol defines the contract for HA operations.
    Not all databases support all operations.
    """

    def supports_high_availability(self) -> bool:
        """Check if database supports HA."""
        ...

    def get_ha_configuration(self) -> Optional[HAConfiguration]:
        """Get current HA configuration."""
        ...

    def get_ha_status(self) -> HAState:
        """Get current HA status."""
        ...

    def is_primary(self) -> bool:
        """Check if current node is primary."""
        ...

    def get_primary_node(self) -> Optional[HANodeInfo]:
        """Get primary node information."""
        ...

    def get_all_nodes(self) -> List[HANodeInfo]:
        """Get all nodes in HA configuration."""
        ...
```

#### 11.2.3 High Availability Manager

```python
class HighAvailabilityManager(ABC):
    """
    Abstract base class for managing high availability configurations.

    Each database type implements this with platform-specific HA features.
    """

    def __init__(self, database: Database):
        """
        Initialize HA manager.

        Args:
            database: Database instance to manage HA for
        """
        self.database = database
        self.connection = database.connection

    @abstractmethod
    def get_configuration(self) -> Optional[HAConfiguration]:
        """
        Get current HA configuration.

        Returns:
            HAConfiguration object or None if not configured
        """
        pass

    @abstractmethod
    def get_status(self) -> HAState:
        """Get current HA status."""
        pass

    @abstractmethod
    def get_all_nodes(self) -> List[HANodeInfo]:
        """Get all nodes in the HA configuration."""
        pass

    @abstractmethod
    def get_primary_node(self) -> Optional[HANodeInfo]:
        """Get the primary/master node."""
        pass

    @abstractmethod
    def monitor_lag(self) -> Dict[str, float]:
        """
        Monitor replication lag for all secondary nodes.

        Returns:
            Dictionary mapping node names to lag in seconds
        """
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if HA configuration is healthy."""
        pass

    # Optional operations (may not be supported by all platforms)

    def create_configuration(self, **options) -> OperationResult:
        """Create HA configuration."""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support create_configuration"
        )

    def add_node(self, node_config: Dict[str, Any]) -> OperationResult:
        """Add a node to HA configuration."""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support add_node"
        )

    def remove_node(self, node_name: str) -> OperationResult:
        """Remove a node from HA configuration."""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support remove_node"
        )

    def failover(
        self,
        target_node: Optional[str] = None,
        force: bool = False
    ) -> OperationResult:
        """
        Perform failover to another node.

        Args:
            target_node: Target node name (None for automatic selection)
            force: Force failover even if data loss may occur
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support failover"
        )

    def set_sync_mode(self, mode: SyncMode) -> OperationResult:
        """Set synchronization mode."""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support set_sync_mode"
        )
```

### 11.3 Platform-Specific Implementations

#### 11.3.1 MongoDB Replica Set

```python
class MongoDBReplicaSetManager(HighAvailabilityManager):
    """MongoDB Replica Set management."""

    def get_configuration(self) -> Optional[HAConfiguration]:
        """Get replica set configuration."""
        # Run rs.conf() command
        result = self.database.connection.execute_query({
            "replSetGetConfig": 1
        })

        if not result:
            return None

        config = result.get("config", {})
        members = config.get("members", [])

        nodes = []
        for member in members:
            # Get member status
            status = self._get_member_status(member["host"])

            node = HANodeInfo(
                node_name=member["host"],
                role=self._map_member_role(member, status),
                state=self._map_member_state(status),
                endpoint=member["host"],
                lag_seconds=status.get("lag"),
                is_healthy=status.get("health") == 1
            )
            nodes.append(node)

        return HAConfiguration(
            name=config.get("_id"),
            type="replica_set",
            nodes=nodes,
            sync_mode=SyncMode.ASYNCHRONOUS,
            automatic_failover=True
        )

    def get_status(self) -> HAState:
        """Get replica set status."""
        status = self.database.connection.execute_query({
            "replSetGetStatus": 1
        })

        if not status:
            return HAState.UNKNOWN

        set_state = status.get("myState")
        return self._map_set_state(set_state)

    def get_all_nodes(self) -> List[HANodeInfo]:
        """Get all replica set members."""
        config = self.get_configuration()
        return config.nodes if config else []

    def get_primary_node(self) -> Optional[HANodeInfo]:
        """Get primary node."""
        status = self.database.connection.execute_query({
            "replSetGetStatus": 1
        })

        if not status:
            return None

        members = status.get("members", [])
        for member in members:
            if member.get("stateStr") == "PRIMARY":
                return HANodeInfo(
                    node_name=member["name"],
                    role=HARole.PRIMARY,
                    state=HAState.HEALTHY,
                    endpoint=member["name"],
                    is_healthy=member.get("health") == 1
                )
        return None

    def monitor_lag(self) -> Dict[str, float]:
        """Monitor replication lag."""
        status = self.database.connection.execute_query({
            "replSetGetStatus": 1
        })

        lag_info = {}
        members = status.get("members", [])

        # Find primary optime
        primary_optime = None
        for member in members:
            if member.get("stateStr") == "PRIMARY":
                primary_optime = member.get("optimeDate")
                break

        if not primary_optime:
            return lag_info

        # Calculate lag for secondaries
        for member in members:
            if member.get("stateStr") == "SECONDARY":
                secondary_optime = member.get("optimeDate")
                if secondary_optime:
                    lag = (primary_optime - secondary_optime).total_seconds()
                    lag_info[member["name"]] = lag

        return lag_info

    def is_healthy(self) -> bool:
        """Check if replica set is healthy."""
        status = self.database.connection.execute_query({
            "replSetGetStatus": 1
        })

        if not status:
            return False

        members = status.get("members", [])

        # Check if we have a primary
        has_primary = any(m.get("stateStr") == "PRIMARY" for m in members)

        # Check if majority of members are healthy
        healthy_count = sum(1 for m in members if m.get("health") == 1)
        majority = len(members) // 2 + 1

        return has_primary and healthy_count >= majority

    def create_configuration(self, **options) -> OperationResult:
        """Initialize replica set."""
        config = {
            "_id": options.get("replica_set_name"),
            "members": options.get("members", [])
        }

        try:
            self.database.connection.execute_query({
                "replSetInitiate": config
            })
            return OperationResult.success_result(
                "Replica set initialized successfully"
            )
        except Exception as e:
            return OperationResult.failure_result(
                "Failed to initialize replica set",
                error=str(e)
            )

    def add_node(self, node_config: Dict[str, Any]) -> OperationResult:
        """Add member to replica set."""
        try:
            self.database.connection.execute_query({
                "replSetReconfig": {
                    "add": node_config
                }
            })
            return OperationResult.success_result(
                f"Added node {node_config.get('host')}"
            )
        except Exception as e:
            return OperationResult.failure_result(
                "Failed to add node",
                error=str(e)
            )

    def failover(
        self,
        target_node: Optional[str] = None,
        force: bool = False
    ) -> OperationResult:
        """Step down primary (triggers election)."""
        try:
            self.database.connection.execute_query({
                "replSetStepDown": 60,  # seconds
                "force": force
            })
            return OperationResult.success_result("Failover initiated")
        except Exception as e:
            return OperationResult.failure_result(
                "Failover failed",
                error=str(e)
            )
```

#### 11.3.2 SQL Server Availability Groups

```python
class MSSQLAvailabilityGroupManager(HighAvailabilityManager):
    """Microsoft SQL Server Availability Group management."""

    def get_configuration(self) -> Optional[HAConfiguration]:
        """Get availability group configuration."""
        query = """
        SELECT
            ag.name AS ag_name,
            ag.automated_backup_preference_desc,
            ag.failure_condition_level,
            ag.health_check_timeout,
            ar.replica_server_name,
            ar.availability_mode_desc,
            ar.failover_mode_desc,
            ar.endpoint_url,
            ars.role_desc,
            ars.connected_state_desc,
            ars.synchronization_health_desc,
            ars.last_connect_error_description
        FROM sys.availability_groups ag
        JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
        LEFT JOIN sys.dm_hadr_availability_replica_states ars
            ON ar.replica_id = ars.replica_id
        WHERE ag.name = ?
        """

        ag_name = self.database.metadata.additional_attributes.get(
            "availability_group_name"
        )

        if not ag_name:
            return None

        results = self.connection.execute_query(query, (ag_name,))

        if not results:
            return None

        nodes = []
        for row in results:
            node = HANodeInfo(
                node_name=row["replica_server_name"],
                role=self._map_role(row["role_desc"]),
                state=self._map_state(row["synchronization_health_desc"]),
                endpoint=row["endpoint_url"],
                is_healthy=row["connected_state_desc"] == "CONNECTED",
                metadata={
                    "availability_mode": row["availability_mode_desc"],
                    "failover_mode": row["failover_mode_desc"]
                }
            )
            nodes.append(node)

        # Determine sync mode from first node
        sync_mode = (
            SyncMode.SYNCHRONOUS
            if results[0]["availability_mode_desc"] == "SYNCHRONOUS_COMMIT"
            else SyncMode.ASYNCHRONOUS
        )

        return HAConfiguration(
            name=ag_name,
            type="availability_group",
            nodes=nodes,
            sync_mode=sync_mode,
            automatic_failover=results[0]["failover_mode_desc"] == "AUTOMATIC"
        )

    def get_status(self) -> HAState:
        """Get AG synchronization status."""
        query = """
        SELECT
            drs.synchronization_state_desc,
            drs.synchronization_health_desc
        FROM sys.dm_hadr_database_replica_states drs
        JOIN sys.databases db ON drs.database_id = db.database_id
        WHERE db.name = ?
        """

        results = self.connection.execute_query(
            query,
            (self.database.name,)
        )

        if not results:
            return HAState.UNKNOWN

        # Check if any replica is not synchronized
        for row in results:
            state = row["synchronization_state_desc"]
            if state == "NOT SYNCHRONIZING":
                return HAState.NOT_SYNCHRONIZED
            elif state == "SYNCHRONIZING":
                return HAState.SYNCHRONIZING

        return HAState.SYNCED

    def get_all_nodes(self) -> List[HANodeInfo]:
        """Get all replicas."""
        config = self.get_configuration()
        return config.nodes if config else []

    def get_primary_node(self) -> Optional[HANodeInfo]:
        """Get primary replica."""
        query = """
        SELECT
            ar.replica_server_name,
            ar.endpoint_url
        FROM sys.availability_groups ag
        JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
        JOIN sys.dm_hadr_availability_replica_states ars
            ON ar.replica_id = ars.replica_id
        WHERE ars.role_desc = 'PRIMARY'
        """

        results = self.connection.execute_query(query)

        if not results:
            return None

        row = results[0]
        return HANodeInfo(
            node_name=row["replica_server_name"],
            role=HARole.PRIMARY,
            state=HAState.HEALTHY,
            endpoint=row["endpoint_url"],
            is_healthy=True
        )

    def monitor_lag(self) -> Dict[str, float]:
        """Monitor replication lag."""
        query = """
        SELECT
            ar.replica_server_name,
            drs.log_send_queue_size,
            drs.redo_queue_size,
            drs.last_commit_time
        FROM sys.dm_hadr_database_replica_states drs
        JOIN sys.availability_replicas ar ON drs.replica_id = ar.replica_id
        JOIN sys.databases db ON drs.database_id = db.database_id
        WHERE db.name = ? AND ar.replica_server_name != @@SERVERNAME
        """

        results = self.connection.execute_query(
            query,
            (self.database.name,)
        )

        lag_info = {}
        for row in results:
            # Estimate lag based on queue sizes and last commit time
            queue_size = (
                row["log_send_queue_size"] + row["redo_queue_size"]
            )
            lag_info[row["replica_server_name"]] = queue_size / 1024.0

        return lag_info

    def is_healthy(self) -> bool:
        """Check if AG is healthy."""
        query = """
        SELECT
            COUNT(*) as replica_count,
            SUM(CASE WHEN ars.connected_state_desc = 'CONNECTED' THEN 1 ELSE 0 END) as connected_count,
            SUM(CASE WHEN ars.synchronization_health_desc = 'HEALTHY' THEN 1 ELSE 0 END) as healthy_count
        FROM sys.availability_replicas ar
        JOIN sys.dm_hadr_availability_replica_states ars
            ON ar.replica_id = ars.replica_id
        """

        results = self.connection.execute_query(query)

        if not results:
            return False

        row = results[0]
        return (
            row["connected_count"] == row["replica_count"] and
            row["healthy_count"] == row["replica_count"]
        )

    def failover(
        self,
        target_node: Optional[str] = None,
        force: bool = False
    ) -> OperationResult:
        """Failover to another replica."""
        ag_name = self.database.metadata.additional_attributes.get(
            "availability_group_name"
        )

        if not ag_name:
            return OperationResult.failure_result(
                "No availability group configured"
            )

        # Connect to target node if specified
        failover_query = f"""
        ALTER AVAILABILITY GROUP [{ag_name}]
        {"FORCE_FAILOVER_ALLOW_DATA_LOSS" if force else "FAILOVER"}
        """

        try:
            self.connection.execute_query(failover_query)
            return OperationResult.success_result(
                f"Failover of {ag_name} completed"
            )
        except Exception as e:
            return OperationResult.failure_result(
                "Failover failed",
                error=str(e)
            )
```

#### 11.3.3 PostgreSQL Replication

```python
class PostgreSQLReplicationManager(HighAvailabilityManager):
    """PostgreSQL Replication management (streaming/logical)."""

    def get_configuration(self) -> Optional[HAConfiguration]:
        """Get replication configuration."""
        # Check if this is primary or standby
        query = "SELECT pg_is_in_recovery()"
        result = self.connection.execute_query(query)
        is_standby = result[0][0] if result else False

        if is_standby:
            return self._get_standby_configuration()
        else:
            return self._get_primary_configuration()

    def _get_primary_configuration(self) -> Optional[HAConfiguration]:
        """Get configuration from primary server."""
        query = """
        SELECT
            client_addr,
            application_name,
            state,
            sync_state,
            sync_priority,
            replay_lag,
            write_lag,
            flush_lag
        FROM pg_stat_replication
        """

        results = self.connection.execute_query(query)

        if not results:
            return None

        nodes = [
            HANodeInfo(
                node_name="primary",
                role=HARole.PRIMARY,
                state=HAState.HEALTHY,
                endpoint=self.connection.config.get("host"),
                is_healthy=True
            )
        ]

        for row in results:
            node = HANodeInfo(
                node_name=row["application_name"],
                role=HARole.STANDBY,
                state=self._map_state(row["state"]),
                endpoint=row["client_addr"],
                lag_seconds=self._extract_lag(row["replay_lag"]),
                is_healthy=row["state"] == "streaming",
                metadata={
                    "sync_state": row["sync_state"],
                    "sync_priority": row["sync_priority"]
                }
            )
            nodes.append(node)

        # Check if synchronous replication is enabled
        sync_query = "SHOW synchronous_commit"
        sync_result = self.connection.execute_query(sync_query)
        sync_mode = (
            SyncMode.SYNCHRONOUS
            if sync_result and sync_result[0][0] in ("on", "remote_apply")
            else SyncMode.ASYNCHRONOUS
        )

        return HAConfiguration(
            name="postgresql_replication",
            type="streaming_replication",
            nodes=nodes,
            sync_mode=sync_mode,
            automatic_failover=False  # Requires external tool
        )

    def get_status(self) -> HAState:
        """Get replication status."""
        query = "SELECT pg_is_in_recovery()"
        result = self.connection.execute_query(query)
        is_standby = result[0][0] if result else False

        if is_standby:
            return HAState.SYNCED  # Standby is receiving

        # Check if replicas are connected
        query = "SELECT COUNT(*) FROM pg_stat_replication"
        result = self.connection.execute_query(query)
        replica_count = result[0][0] if result else 0

        return HAState.HEALTHY if replica_count > 0 else HAState.UNKNOWN

    def get_all_nodes(self) -> List[HANodeInfo]:
        """Get all nodes."""
        config = self.get_configuration()
        return config.nodes if config else []

    def get_primary_node(self) -> Optional[HANodeInfo]:
        """Get primary node."""
        query = "SELECT pg_is_in_recovery()"
        result = self.connection.execute_query(query)
        is_standby = result[0][0] if result else False

        if not is_standby:
            return HANodeInfo(
                node_name="primary",
                role=HARole.PRIMARY,
                state=HAState.HEALTHY,
                endpoint=self.connection.config.get("host"),
                is_healthy=True
            )

        # On standby, we don't have direct access to primary info
        return None

    def monitor_lag(self) -> Dict[str, float]:
        """Monitor replication lag."""
        query = """
        SELECT
            application_name,
            EXTRACT(EPOCH FROM replay_lag) as replay_lag_seconds
        FROM pg_stat_replication
        WHERE replay_lag IS NOT NULL
        """

        results = self.connection.execute_query(query)

        lag_info = {}
        for row in results:
            lag_info[row["application_name"]] = row["replay_lag_seconds"]

        return lag_info

    def is_healthy(self) -> bool:
        """Check if replication is healthy."""
        query = """
        SELECT COUNT(*) as total,
               SUM(CASE WHEN state = 'streaming' THEN 1 ELSE 0 END) as streaming
        FROM pg_stat_replication
        """

        results = self.connection.execute_query(query)

        if not results:
            return True  # No replicas configured, primary is healthy

        row = results[0]
        return row["total"] == row["streaming"]
```

#### 11.3.4 Snowflake Replication

```python
class SnowflakeReplicationManager(HighAvailabilityManager):
    """Snowflake Database Replication management."""

    def get_configuration(self) -> Optional[HAConfiguration]:
        """Get replication configuration."""
        query = """
        SHOW REPLICATION DATABASES LIKE %s
        """

        results = self.connection.execute_query_dict(
            query,
            (self.database.name,)
        )

        if not results:
            return None

        nodes = []
        primary_region = None

        for row in results:
            is_primary = row.get("is_primary", False)
            role = HARole.PRIMARY if is_primary else HARole.REPLICA

            if is_primary:
                primary_region = row.get("region")

            node = HANodeInfo(
                node_name=row.get("account_locator"),
                role=role,
                state=HAState.SYNCED,
                endpoint=row.get("account_locator"),
                is_healthy=True,
                metadata={
                    "region": row.get("region"),
                    "snowflake_region": row.get("snowflake_region"),
                    "organization_name": row.get("organization_name")
                }
            )
            nodes.append(node)

        return HAConfiguration(
            name=self.database.name,
            type="snowflake_replication",
            nodes=nodes,
            sync_mode=SyncMode.ASYNCHRONOUS,  # Snowflake uses async
            automatic_failover=False,  # Manual failover/promotion
            metadata={"primary_region": primary_region}
        )

    def get_status(self) -> HAState:
        """Get replication status."""
        # Check replication status
        query = """
        SELECT SYSTEM$GET_REPLICATION_STATUS(%s)
        """

        result = self.connection.execute_query(query, (self.database.name,))

        if result:
            status = result[0][0]
            # Parse JSON status
            return HAState.SYNCED if status else HAState.UNKNOWN

        return HAState.UNKNOWN

    def get_all_nodes(self) -> List[HANodeInfo]:
        """Get all replication nodes."""
        config = self.get_configuration()
        return config.nodes if config else []

    def get_primary_node(self) -> Optional[HANodeInfo]:
        """Get primary database."""
        config = self.get_configuration()
        if not config:
            return None

        for node in config.nodes:
            if node.role == HARole.PRIMARY:
                return node

        return None

    def monitor_lag(self) -> Dict[str, float]:
        """
        Monitor replication lag.

        Note: Snowflake doesn't expose real-time lag metrics.
        Returns empty dict.
        """
        return {}

    def is_healthy(self) -> bool:
        """Check if replication is healthy."""
        config = self.get_configuration()
        if not config:
            return True  # No replication configured

        # All nodes should be healthy
        return all(node.is_healthy for node in config.nodes)

    def create_configuration(self, **options) -> OperationResult:
        """Enable replication for database."""
        target_accounts = options.get("target_accounts", [])

        if not target_accounts:
            return OperationResult.failure_result(
                "Target accounts required"
            )

        try:
            # Enable replication
            query = f"""
            ALTER DATABASE {self.database.name}
            ENABLE REPLICATION TO ACCOUNTS {', '.join(target_accounts)}
            """

            self.connection.execute_query(query)

            return OperationResult.success_result(
                f"Replication enabled for {self.database.name}"
            )
        except Exception as e:
            return OperationResult.failure_result(
                "Failed to enable replication",
                error=str(e)
            )

    def failover(
        self,
        target_node: Optional[str] = None,
        force: bool = False
    ) -> OperationResult:
        """
        Failover/promote a secondary database.

        In Snowflake, this promotes a secondary database to primary.
        """
        if not target_node:
            return OperationResult.failure_result(
                "Target account required for Snowflake failover"
            )

        try:
            # Promote secondary to primary
            query = f"""
            ALTER DATABASE {self.database.name}
            ENABLE FAILOVER TO ACCOUNTS {target_node}
            """

            self.connection.execute_query(query)

            return OperationResult.success_result(
                f"Failover to {target_node} initiated"
            )
        except Exception as e:
            return OperationResult.failure_result(
                "Failover failed",
                error=str(e)
            )
```

### 11.4 Integration with Database Class

Update the `Database` abstract class to include HA support:

```python
class Database(ABC):
    """Abstract base class representing a database entity."""

    def __init__(
        self,
        name: str,
        connection: DatabaseConnection,
        metadata: Optional[DatabaseMetadata] = None
    ):
        self.name = name
        self.connection = connection
        self._metadata = metadata
        self._ha_manager: Optional[HighAvailabilityManager] = None

    # ... existing methods ...

    # ========== High Availability ==========

    @property
    def ha(self) -> Optional[HighAvailabilityManager]:
        """
        Get high availability manager for this database.

        Returns None if database type doesn't support HA.
        """
        if self._ha_manager is None:
            self._ha_manager = self._create_ha_manager()
        return self._ha_manager

    def _create_ha_manager(self) -> Optional[HighAvailabilityManager]:
        """
        Create platform-specific HA manager.

        Override in subclasses to provide HA support.
        """
        return None

    def supports_high_availability(self) -> bool:
        """Check if database supports high availability."""
        return self.ha is not None
```

### 11.5 Usage Examples

```python
# Example 1: Check HA status across different databases
from gds_database import DatabaseManager

def check_ha_status(connection, db_name):
    """Universal HA status check."""
    manager = DatabaseManager(connection)
    db = manager.get_database(db_name)

    if not db.supports_high_availability():
        print(f"{db_name}: HA not supported or not configured")
        return

    config = db.ha.get_configuration()
    if not config:
        print(f"{db_name}: No HA configuration found")
        return

    print(f"\n{db_name} HA Configuration:")
    print(f"  Type: {config.type}")
    print(f"  Sync Mode: {config.sync_mode}")
    print(f"  Auto Failover: {config.automatic_failover}")
    print(f"  Status: {db.ha.get_status()}")
    print(f"  Healthy: {db.ha.is_healthy()}")

    print("\n  Nodes:")
    for node in config.nodes:
        print(f"    - {node.node_name}")
        print(f"      Role: {node.role}")
        print(f"      State: {node.state}")
        print(f"      Healthy: {node.is_healthy}")
        if node.lag_seconds:
            print(f"      Lag: {node.lag_seconds:.2f}s")

# Works with MongoDB
from gds_mongodb import MongoDBConnection
mongo_conn = MongoDBConnection(host="localhost", database="admin")
check_ha_status(mongo_conn, "mydb")

# Works with SQL Server
from gds_mssql import MSSQLConnection
mssql_conn = MSSQLConnection(server="localhost", database="master")
check_ha_status(mssql_conn, "MyDatabase")

# Works with PostgreSQL
from gds_postgres import PostgreSQLConnection
pg_conn = PostgreSQLConnection(host="localhost", database="postgres")
check_ha_status(pg_conn, "mydb")

# Works with Snowflake
from gds_snowflake import SnowflakeConnection
sf_conn = SnowflakeConnection(account="myaccount", database="MYDB")
check_ha_status(sf_conn, "MYDB")
```

```python
# Example 2: Monitor replication lag
def monitor_replication_lag(connection, db_name, threshold_seconds=5.0):
    """Monitor and alert on replication lag."""
    manager = DatabaseManager(connection)
    db = manager.get_database(db_name)

    if not db.supports_high_availability():
        return

    lag_info = db.ha.monitor_lag()

    for node, lag in lag_info.items():
        if lag > threshold_seconds:
            print(f"WARNING: {node} is lagging by {lag:.2f}s")
        else:
            print(f"OK: {node} lag is {lag:.2f}s")
```

```python
# Example 3: Automated failover
def perform_failover(connection, db_name, target_node=None, force=False):
    """Perform database failover with platform-specific handling."""
    manager = DatabaseManager(connection)
    db = manager.get_database(db_name)

    if not db.supports_high_availability():
        print("Database doesn't support HA")
        return False

    # Check current health before failover
    if not db.ha.is_healthy() and not force:
        print("WARNING: HA configuration is not healthy")
        response = input("Force failover anyway? (yes/no): ")
        if response.lower() != "yes":
            return False

    # Get primary before failover
    primary = db.ha.get_primary_node()
    print(f"Current primary: {primary.node_name if primary else 'Unknown'}")

    # Perform failover
    result = db.ha.failover(target_node=target_node, force=force)

    if result.is_success():
        print(f"Failover successful: {result.message}")

        # Wait and verify new primary
        time.sleep(5)
        new_primary = db.ha.get_primary_node()
        print(f"New primary: {new_primary.node_name if new_primary else 'Unknown'}")
        return True
    else:
        print(f"Failover failed: {result.error}")
        return False
```

### 11.6 Benefits of This Design

1. **Abstraction**: Common HA interface across all database types
2. **Platform-Specific**: Each platform implements its native HA features
3. **Type Safety**: Proper enums and dataclasses for HA concepts
4. **Extensible**: Easy to add new HA features per platform
5. **Optional**: HA is optional; databases without HA return None
6. **Consistent API**: Same code works across platforms where applicable
7. **Feature Detection**: `supports_high_availability()` for capability checking

## 12. Future Enhancements

### 12.1 Additional Features

1. **Schema Management**: Add `Schema` class as domain entity
2. **Table Management**: Add `Table` class with operations
3. **Index Management**: Operations for index management
4. **User Management**: Database user and permission management
5. **Performance Monitoring**: Built-in performance metrics
6. **Migration Support**: Database schema migration tools

### 12.2 Additional Database Types

1. MySQL
2. Oracle
3. SQLite
4. Redis
5. Cassandra
6. DynamoDB

---

## Appendix A: File Structure

```
gds_database/
├── __init__.py
├── base.py              # Existing classes (kept)
├── database.py          # NEW: Database ABC
├── enums.py             # NEW: Enumerations
├── metadata.py          # NEW: Metadata models
├── provider.py          # NEW: Provider ABC
├── manager.py           # NEW: DatabaseManager
└── py.typed

gds_mssql/
├── __init__.py
├── connection.py        # Existing
├── database.py          # NEW: MSSQLDatabase
├── provider.py          # NEW: MSSQLProvider
└── metadata.py          # NEW: MSSQL metadata

gds_postgres/
├── __init__.py
├── connection.py        # Existing
├── database.py          # NEW: PostgreSQLDatabase
├── provider.py          # NEW: PostgreSQLProvider
└── metadata.py          # NEW: PostgreSQL metadata

gds_snowflake/
├── __init__.py
├── connection.py        # Existing
├── database.py          # NEW: SnowflakeDatabase (refactor existing)
├── provider.py          # NEW: SnowflakeProvider
└── metadata.py          # NEW: Snowflake metadata

gds_mongodb/             # NEW package
├── __init__.py
├── connection.py
├── database.py
├── provider.py
└── metadata.py
```

---

## Appendix B: SOLID Principles Application

### Single Responsibility Principle (SRP)
- `Database`: Manages database entity state and operations
- `DatabaseProvider`: Creates platform-specific instances
- `DatabaseManager`: Factory for database instances
- `DatabaseMetadata`: Holds database attributes
- Each class has one reason to change

### Open/Closed Principle (OCP)
- Open for extension: Add new database types by implementing interfaces
- Closed for modification: Core abstractions don't change
- New providers can be added without modifying existing code

### Liskov Substitution Principle (LSP)
- All `Database` subclasses can be used interchangeably
- Platform-specific methods are clearly marked
- Base interface operations work consistently across types

### Interface Segregation Principle (ISP)
- Multiple focused interfaces: `Database`, `DatabaseProvider`, `Connectable`
- Clients depend only on methods they use
- No fat interfaces with unused methods

### Dependency Inversion Principle (DIP)
- High-level `DatabaseManager` depends on abstract `DatabaseProvider`
- Platform implementations depend on abstract `Database` class
- Concrete classes instantiated through factories, not directly

---

## Document Approval

**Architecture Review:** Pending
**Technical Review:** Pending
**Implementation Start Date:** TBD

---

**End of Design Document**
