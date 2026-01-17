# Scripts & Utilities

This directory contains various utility scripts for development, testing, database management, and infrastructure troubleshooting within the **dbtools** project.

## Directory structure

| Directory | Purpose |
|-----------|---------|
| [`build/`](./build/) | Build and packaging scripts |
| [`development/`](./development/) | Development environment and tooling scripts |
| [`operations/`](./operations/) | Operational and database management scripts |
| [`validation/`](./validation/) | Verification and validation scripts |

## Content overview

### Build scripts (`build/`)

| Script | Description |
|--------|-------------|
| [`build_container_image.sh`](./build/build_container_image.sh) | Builds container images for the project |
| [`lint.sh`](./build/lint.sh) | Wrapper for `ruff` to lint (check), format, and fix code issues |

### Development scripts (`development/`)

| Script | Description |
|--------|-------------|
| [`add_test_docstrings.py`](./development/add_test_docstrings.py) | Bulk-adds minimal docstrings to `pytest` test functions |
| [`set_prompt.sh`](./development/set_prompt.sh) | Sets up a colorful, informative bash prompt with OS detection |
| [`devcontainer/`](./development/devcontainer/) | Dev container helper scripts |

### Operations scripts (`operations/`)

| Script | Description |
|--------|-------------|
| [`fix-liquibase-baseline.py`](./operations/fix-liquibase-baseline.py) | Fixes and enhances Liquibase XML baseline files for SQL Server |
| [`diagnose_vault_approle.py`](./operations/diagnose_vault_approle.py) | Diagnostic tool for troubleshooting Vault AppRole authentication |
| [`prompt_mssql_password.sh`](./operations/prompt_mssql_password.sh) | Securely prompts for and sets the `MSSQL_SA_PASSWORD` env var |
| [`generate_synthetic_metrics.py`](./operations/generate_synthetic_metrics.py) | Generates fake metric data for testing monitoring pipelines |
| [`compare_directories.sh`](./operations/compare_directories.sh) | Compares directory contents |
| [`new-weekly-status.ps1`](./operations/new-weekly-status.ps1) | Creates weekly status reports |
| [`Merge-ToPfx.ps1`](./operations/Merge-ToPfx.ps1) | Merges certificate files to PFX format |
| [`Sign-GDSModule.ps1`](./operations/Sign-GDSModule.ps1) | Signs PowerShell modules |

### Validation scripts (`validation/`)

| Script | Description |
|--------|-------------|
| [`validate_links.py`](./validation/validate_links.py) | Validates links in documentation |
| [`validate_oop_docs.py`](./validation/validate_oop_docs.py) | Validates Python code blocks in markdown tutorials |
| [`verify_devcontainer.sh`](./validation/verify_devcontainer.sh) | Verifies dev container configuration |
| [`verify_sqlserver.sh`](./validation/verify_sqlserver.sh) | Verifies SQL Server connectivity |
| [`verify_pyodbc.sh`](./validation/verify_pyodbc.sh) | Verifies Python ODBC driver installation |

---

## Usage details

### Build scripts

#### `lint.sh`

A convenient wrapper around `ruff`.

```bash
./scripts/build/lint.sh           # Check for errors
./scripts/build/lint.sh --fix     # Auto-fix errors
./scripts/build/lint.sh --format  # Format code
./scripts/build/lint.sh --watch   # Watch mode for continuous checking
```

### Development scripts

#### `add_test_docstrings.py`

Automatically adds one-line docstrings to test functions (starting with `test_`) in `gds_*/tests` directories. Useful for enforcing linting rules about missing docstrings.

```bash
python scripts/development/add_test_docstrings.py
```

#### `set_prompt.sh`

Configures a colorful, informative bash prompt that displays:
- OS type (ubuntu/redhat/linux) at the beginning
- Current date
- Username and hostname
- Current working directory

```bash
# Source it to apply to current shell
. scripts/development/set_prompt.sh

# Or add to your ~/.bashrc to make it permanent
echo '. ~/src/dbtools/scripts/development/set_prompt.sh' >> ~/.bashrc
source ~/.bashrc
```

### Operations scripts

#### `fix-liquibase-baseline.py`

Corrects common issues in generated Liquibase baseline files, such as missing schema attributes, and can extract stored procedures from a live DB.

* **Documentation**: [See detailed README](./operations/README-fix-liquibase-baseline.md)

```bash
python scripts/operations/fix-liquibase-baseline.py --baseline-file path/to/baseline.xml --schema app
```

#### `prompt_mssql_password.sh`

Sets the critical `MSSQL_SA_PASSWORD` environment variable required for many other scripts and tests. It enforces complexity requirements.

```bash
# Source it to apply variables to current shell
. scripts/operations/prompt_mssql_password.sh
```

#### `diagnose_vault_approle.py`

If your application can't authenticate with Vault, run this tool. It checks env vars, connectivity, and attempts a login, providing specific advice on failure.

```bash
export VAULT_ADDR=...
export VAULT_ROLE_ID=...
export VAULT_SECRET_ID=...
python scripts/operations/diagnose_vault_approle.py
```

#### `generate_synthetic_metrics.py`

Generates stream of synthetic events. Useful for testing Kafka consumers or other metric ingestion pipelines.

```bash
# Print to stdout
python scripts/operations/generate_synthetic_metrics.py --metric-name cpu_usage --rate 2

# Write to Kafka
python scripts/operations/generate_synthetic_metrics.py --metric-name request_errors \
  --kafka-bootstrap localhost:9092 --kafka-topic metrics
```

### Validation scripts

#### `validate_oop_docs.py`

Ensures that code examples in the OOP tutorial markdown files are valid and runnable.

```bash
python scripts/validation/validate_oop_docs.py
```

#### `verify_sqlserver.sh` / `verify_pyodbc.sh`

Run these to verify your environment is correctly set up to talk to SQL Server.

```bash
./scripts/validation/verify_sqlserver.sh
```
