# ADR-004: Database abstraction layer design

## Status

Accepted

## Context

The project requires connections to multiple database systems:
- PostgreSQL
- SQL Server (MSSQL)
- MongoDB
- Snowflake

Each database has different connection patterns, authentication methods, and query interfaces. Without abstraction, code becomes tightly coupled to specific databases.

Options considered:

1. **No abstraction**: Use each database's native driver directly
2. **SQLAlchemy only**: Use SQLAlchemy for all SQL databases
3. **Custom abstraction**: Build a thin abstraction layer
4. **Full ORM**: Build a complete object-relational mapping

## Decision

We implement a **layered abstraction** with:

1. **Abstract base classes** (`gds_database`): Define interfaces for connection, execution, and metadata
2. **Concrete implementations**: Database-specific packages that extend the base classes
3. **Optional ORM support**: SQLAlchemy integration where appropriate

Package structure:
```
python/
├── gds_database/    # Abstract interfaces
├── gds_postgres/    # PostgreSQL implementation
├── gds_mssql/       # SQL Server implementation
├── gds_mongodb/     # MongoDB implementation
└── gds_snowflake/   # Snowflake utilities
```

## Consequences

### Benefits

- **Consistent interface**: All database connections follow the same patterns
- **Substitutability**: Can switch implementations without changing application code
- **Testability**: Easy to mock database connections for testing
- **Separation of concerns**: Connection logic isolated from business logic
- **Gradual adoption**: Can use native drivers where abstraction adds no value

### Trade-offs

- **Additional layer**: Slight overhead compared to direct driver use
- **Maintenance burden**: Must maintain both base classes and implementations
- **Feature parity**: Some database-specific features may not fit the abstraction

### Design principles

1. **Open-Closed Principle**: Base classes are open for extension, closed for modification
2. **Dependency Inversion**: Application code depends on abstractions, not concrete implementations
3. **Composition over inheritance**: Prefer composition for optional features

### Example usage

```python
from gds_postgres import PostgresConnection

# Concrete implementation follows abstract interface
conn = PostgresConnection(
    host="localhost",
    database="mydb",
    user="user"
)

# Common interface across all implementations
with conn.connect() as session:
    result = session.execute("SELECT 1")
```

### Related documentation

- [Database Instance OO Design](../../design-records/database-instance-oo-design.md)
- [Database Platform OO Design](../../design-records/database-platform-oo-design.md)
