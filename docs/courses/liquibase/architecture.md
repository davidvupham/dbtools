# Liquibase Tutorial Architecture

## Container Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│                     Host Machine (Ubuntu/RHEL)                       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Podman/Docker                              │   │
│  │                                                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │   │
│  │  │  mssql_dev  │  │  mssql_stg  │  │  mssql_prd  │           │   │
│  │  │  Port 14331 │  │  Port 14332 │  │  Port 14333 │           │   │
│  │  │  orderdb    │  │  orderdb    │  │  orderdb    │           │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘           │   │
│  │         │                │                │                   │   │
│  │         └────────────────┼────────────────┘                   │   │
│  │                          │                                    │   │
│  │              slirp4netns networking                           │   │
│  │                          │                                    │   │
│  │                ┌─────────────────┐                            │   │
│  │                │    Liquibase    │                            │   │
│  │                │   (run-once)    │                            │   │
│  │                └─────────────────┘                            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              /data/$USER/liquibase_tutorial/                   │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────────────┐ │  │
│  │  │mssql_dev│ │mssql_stg│ │mssql_prd│ │      database/       │ │  │
│  │  │  data   │ │  data   │ │  data   │ │     changelog/       │ │  │
│  │  └─────────┘ └─────────┘ └─────────┘ │ ┌──────────────────┐ │ │  │
│  │                                       │ │ V0000__baseline  │ │ │  │
│  │  ┌──────────────────────────────────┐ │ │       .sql       │ │ │  │
│  │  │              env/                │ │ └──────────────────┘ │ │  │
│  │  │ liquibase.dev.properties         │ └──────────────────────┘ │  │
│  │  │ liquibase.stg.properties         │                          │  │
│  │  │ liquibase.prd.properties         │                          │  │
│  │  └──────────────────────────────────┘                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Deployment Flow

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    DEV      │────▶│   STAGING   │────▶│ PRODUCTION  │
│  mssql_dev  │     │  mssql_stg  │     │  mssql_prd  │
│  Port 14331 │     │  Port 14332 │     │  Port 14333 │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
  changelogSync         update              update
  (mark as done)     (apply changes)    (apply changes)
```

## Changelog Structure

```text
database/changelog/
├── changelog.xml          # Master changelog (includes all files)
├── baseline/
│   └── V0000__baseline.mssql.sql          # Initial state
└── changes/
    ├── V0001__add_orders.sql        # First change
    └── V0002__add_index.sql         # Second change
```

## Network Configuration

| Mode | Use Case | Connection String Host |
|------|----------|------------------------|
| slirp4netns | Container → Host | `host.containers.internal` |
| Bridge | Container → Container | Container hostname |
| Host | Cloud databases | Public DNS/IP |
