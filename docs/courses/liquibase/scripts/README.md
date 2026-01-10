# Liquibase Tutorial Scripts

This directory contains reusable scripts for the Liquibase tutorial series. Scripts are named descriptively to indicate their function, making them reusable across different tutorials.

## Script Naming Convention

Scripts use descriptive names that indicate their purpose:
- `setup_*` - Environment and project setup
- `start_*` - Starting services/containers
- `create_*` - Creating databases, schemas, objects
- `populate_*` - Adding sample data
- `generate_*` - Generating Liquibase artifacts
- `deploy_*` - Deploying changes to environments
- `validate_*` - Validation and verification
- `cleanup_*` - Cleanup and teardown

## Core Scripts

### Setup Scripts

| Script | Purpose | Used In |
|--------|---------|---------|
| `setup_liquibase_environment.sh` | Creates project directories, properties files, master changelog | Part 1, End-to-End |
| `start_mssql_containers.sh` | Starts SQL Server containers (dev/stg/prd) | Part 1, End-to-End |
| `create_orderdb_database.sh` | Creates `orderdb` database and `app` schema on all containers | Part 1, End-to-End |
| `populate_dev_database.sh` | Populates development with sample objects for baseline | Part 1, End-to-End |

### Liquibase Operations

| Script | Purpose | Used In |
|--------|---------|---------|
| `generate_liquibase_baseline.sh` | Generates baseline changelog from development database | Part 1, End-to-End |
| `deploy_liquibase_baseline.sh` | Deploys baseline to all environments (dev: sync, stg/prd: update) | Part 1, End-to-End |

### Helper Scripts

| Script | Purpose |
|--------|---------|
| `setup_tutorial.sh` | One-time setup: exports env vars, creates aliases, prompts for password |
| `setup_aliases.sh` | Creates shell aliases (`lb`, `sqlcmd-tutorial`, `cr`) |
| `lb.sh` | Wrapper for running Liquibase in Docker/Podman |
| `sqlcmd_tutorial.sh` | Wrapper for running sqlcmd against tutorial containers |
| `cr.sh` | Container runtime detection (docker/podman) |

### Cleanup Scripts

| Script | Purpose |
|--------|---------|
| `cleanup_liquibase_tutorial.sh` | Removes all tutorial containers, networks, and data |
| `cleanup_tutorial.sh` | Lightweight cleanup (containers only) |

## Usage Pattern

All scripts follow a consistent pattern:

1. **Check prerequisites** (environment variables, containers, files)
2. **Execute operation** with clear success/failure indicators
3. **Provide next steps** guidance

## Environment Variables

Scripts expect these environment variables:

- `LIQUIBASE_TUTORIAL_DIR` - Path to tutorial root (e.g., `/path/to/repo/docs/courses/liquibase`)
- `LIQUIBASE_TUTORIAL_DATA_DIR` - Path to project data (default: `/data/$USER/liquibase_tutorial`)
- `MSSQL_LIQUIBASE_TUTORIAL_PWD` - SQL Server password (prompted if not set)
- `MSSQL_DEV_PORT`, `MSSQL_STG_PORT`, `MSSQL_PRD_PORT` - Port overrides (defaults: 14331, 14332, 14333)

## Reusability Guidelines

1. **No hard-coded paths** - Use environment variables
2. **Container runtime detection** - Auto-detect Docker vs Podman
3. **Idempotent operations** - Scripts can be run multiple times safely
4. **Clear error messages** - Indicate what failed and how to fix
5. **Success indicators** - Use colored output (✓/✗) for quick feedback

## Integration with Tutorials

Scripts are referenced in tutorials using descriptive names:

```bash
# In tutorial documentation:
$LIQUIBASE_TUTORIAL_DIR/scripts/setup_liquibase_environment.sh
$LIQUIBASE_TUTORIAL_DIR/scripts/start_mssql_containers.sh
```

This makes it clear what each script does without needing to remember step numbers.
