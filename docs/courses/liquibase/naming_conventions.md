# Liquibase Naming Conventions

## File Naming

### Changelog Files

| Pattern                        | Example                        | Description                   |
|--------------------------------|-------------------------------|--------------------------------|
| `V<number>__<description>.<dbtype>.sql` | `V0000__baseline.mssql.sql` | Version-prefixed Formatted SQL |

**Rules:**

- Version number: Zero-padded 4 digits (V0000, V0001, etc.)
- Separator: Double underscore (`__`)
- Description: lowercase_with_underscores
- Database type: `mssql`, `postgresql`, `h2`, etc. (required for Liquibase Formatted SQL generation)
- Extension: `.sql`

**Examples:**

```text
V0000__baseline.mssql.sql
V0001__add_orders_table.mssql.sql
V0002__create_customer_index.mssql.sql
```

## Container Naming

| Pattern               | Examples                             |
|-----------------------|--------------------------------------|
| `mssql_<env>`         | `mssql_dev`, `mssql_stg`, `mssql_prd` |
| `liquibase_<purpose>` | `liquibase_tutorial`                 |

## Environment Names

| Full | Short | Port |
| ------ | ------- | ------ |
| development | dev | 14331 |
| staging | stg | 14332 |
| production | prd | 14333 |

## Property Files

| Pattern | Example |
|---------|---------|
| `liquibase.mssql_<env>.properties` | `liquibase.mssql_dev.properties` |

## Network Naming

| Pattern | Example |
|:-------------------|:-----------------------------|
| `<project>_network` | `liquibase_tutorial_network` |

## Directory Naming

| Pattern | Example |
|---------|---------|
| `/data/$USER/<project>` | `/data/$USER/liquibase_tutorial` |
| `platform/mssql/database/orderdb/changelog/baseline` | Baseline changelogs |
| `platform/mssql/database/orderdb/changelog/changes` | Incremental changes |
| `platform/mssql/database/orderdb/env/` | Environment property files |

## General Conventions

1. **Use underscores** (`_`) not hyphens (`-`) for multi-word names
2. **Use lowercase** for all file and directory names
3. **Version numbers** start at 0000 and increment sequentially
4. **Environment abbreviations** use 3 letters (dev, stg, prd)
