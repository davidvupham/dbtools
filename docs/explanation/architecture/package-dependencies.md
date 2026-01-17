# Package dependencies

This document visualizes the internal dependencies between Python packages in the dbtools monorepo.

## Dependency diagram

```
                            ┌─────────────────┐
                            │   gds_metrics   │
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │    gds_kafka    │
                            └─────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE LAYER                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                            ┌─────────────────┐
                            │  gds_database   │  (Abstract Base)
                            └────────┬────────┘
                                     │
           ┌────────────┬────────────┼────────────┬────────────┐
           │            │            │            │            │
           ▼            ▼            ▼            ▼            ▼
    ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
    │gds_postgres│ │ gds_mssql │ │gds_mongodb│ │gds_snowflake│ │    ...    │
    └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘
           │            │            │
           └────────────┴────────────┘
                        │
                        ▼
                ┌─────────────────┐
                │  gds_liquibase  │  (Uses multiple DB implementations)
                └─────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                            BENCHMARKING LAYER                                │
└─────────────────────────────────────────────────────────────────────────────┘

                            ┌─────────────────┐
                            │  gds_benchmark  │  (Abstract Base)
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  gds_hammerdb   │
                            └─────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                           STANDALONE PACKAGES                                │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌───────────┐  ┌───────────────┐  ┌──────────────────┐  ┌───────────┐
    │ gds_vault │  │gds_notification│  │ gds_snmp_receiver│  │ gds_certs │
    └───────────┘  └───────────────┘  └──────────────────┘  └───────────┘
```

## Dependency matrix

| Package | Depends On |
|---------|------------|
| `gds_database` | - (base package) |
| `gds_postgres` | `gds_database` |
| `gds_mssql` | `gds_database` |
| `gds_mongodb` | `gds_database` |
| `gds_snowflake` | `gds_database` |
| `gds_liquibase` | `gds_database`, `gds_postgres`, `gds_mssql`, `gds_mongodb` |
| `gds_benchmark` | - (base package) |
| `gds_hammerdb` | `gds_benchmark` |
| `gds_metrics` | - (standalone) |
| `gds_kafka` | `gds_metrics` |
| `gds_vault` | - (standalone) |
| `gds_certs` | - (standalone) |
| `gds_notification` | - (standalone) |
| `gds_snmp_receiver` | - (standalone) |

## Package categories

### Core abstractions

These packages define interfaces that other packages implement:

- **gds_database**: Abstract base classes for database connections
- **gds_benchmark**: Abstract interfaces for benchmarking tools

### Database implementations

Concrete implementations of the database abstraction:

- **gds_postgres**: PostgreSQL with psycopg2
- **gds_mssql**: SQL Server with pyodbc
- **gds_mongodb**: MongoDB with pymongo
- **gds_snowflake**: Snowflake utilities

### Integration packages

Packages that integrate multiple components:

- **gds_liquibase**: Database change management across multiple databases
- **gds_hammerdb**: HammerDB integration using benchmark abstractions
- **gds_kafka**: Kafka with metrics integration

### Standalone packages

Independent packages with no internal dependencies:

- **gds_vault**: HashiCorp Vault client
- **gds_certs**: Certificate management
- **gds_metrics**: Metrics collection
- **gds_notification**: Alert ingestion
- **gds_snmp_receiver**: SNMP trap receiver

## Adding new packages

When creating a new package:

1. Determine if it should extend an existing abstraction
2. Add workspace dependency in `pyproject.toml`:
   ```toml
   [project]
   dependencies = ["gds-database>=1.0.0"]

   [tool.uv.sources]
   gds-database = { workspace = true }
   ```
3. Update this documentation
4. Consider impact on build order in CI
