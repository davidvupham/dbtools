# Scripts & Utilities

This directory contains various utility scripts for development, testing, database management, and infrastructure troubleshooting within the **dbtools** project.

## 📂 Content Overview

| Script | Category | Description |
|--------|----------|-------------|
| [`lint.sh`](./lint.sh) | Dev / Quality | Wrapper for `ruff` to lint (check), format, and fix code issues. |
| [`generate_synthetic_metrics.py`](./generate_synthetic_metrics.py) | Monitoring | Generates fake metric data (CPU, error rates) for testing monitoring pipelines. |
| [`diagnose_vault_approle.py`](./diagnose_vault_approle.py) | Vault | Diagnostic tool for troubleshooting Vault AppRole authentication (403/404 errors). |
| [`fix-liquibase-baseline.py`](./fix-liquibase-baseline.py) | Database / Liquibase | Fixes and enhances Liquibase XML baseline files for SQL Server. |
| [`prompt_mssql_password.sh`](./prompt_mssql_password.sh) | Database | Securely prompts for and sets the `MSSQL_SA_PASSWORD` env var. |
| [`verify_sqlserver.sh`](./verify_sqlserver.sh) | Database | Verifies SQL Server connectivity via `sqlcmd` and `pyodbc`. |
| [`verify_pyodbc.sh`](./verify_pyodbc.sh) | Database | specific verification for Python ODBC driver installation and configuration. |
| [`add_test_docstrings.py`](./add_test_docstrings.py) | Dev / Docs | Bulk-adds minimal docstrings to `pytest` test functions. |
| [`validate_oop_docs.py`](./validate_oop_docs.py) | Docs | Validates Python code blocks in markdown tutorials by executing them. |
| [`set_prompt.sh`](./set_prompt.sh) | Shell Config | Sets up a colorful, informative bash prompt with OS detection (ubuntu/redhat/linux). |

---

## 🛠️ Usage Details

### Development & Quality Assurance

#### `lint.sh`

A convenient wrapper around `ruff`.

```bash
./scripts/lint.sh           # Check for errors
./scripts/lint.sh --fix     # Auto-fix errors
./scripts/lint.sh --format  # Format code
./scripts/lint.sh --watch   # Watch mode for continuous checking
```

#### `add_test_docstrings.py`

Automatically adds one-line docstrings to test functions (starting with `test_`) in `gds_*/tests` directories. Useful for enforcing linting rules about missing docstrings.

```bash
python scripts/add_test_docstrings.py
```

#### `validate_oop_docs.py`

Ensures that code examples in the OOP tutorial markdown files are valid and runnable.

```bash
python scripts/validate_oop_docs.py
```

### Database Utilities

#### `fix-liquibase-baseline.py`

Corrects common issues in generated Liquibase baseline files, such as missing schema attributes, and can extract stored procedures from a live DB.

* **Documentation**: [See detailed README](./README-fix-liquibase-baseline.md)

```bash
python scripts/fix-liquibase-baseline.py --baseline-file path/to/baseline.xml --schema app
```

#### `prompt_mssql_password.sh`

Sets the critical `MSSQL_SA_PASSWORD` environment variable required for many other scripts and tests. It enforces complexity requirements.

```bash
# Source it to apply variables to current shell
. scripts/prompt_mssql_password.sh
```

#### `verify_sqlserver.sh` / `verify_pyodbc.sh`

Run these to verify your environment is correctly set up to talk to SQL Server.

```bash
./scripts/verify_sqlserver.sh
```

### Infrastructure & Monitoring

#### `generate_synthetic_metrics.py`

Generates stream of synthetic events. Useful for testing Kafka consumers or other metric ingestion pipelines.

```bash
# Print to stdout
python scripts/generate_synthetic_metrics.py --metric-name cpu_usage --rate 2

# Write to Kafka
python scripts/generate_synthetic_metrics.py --metric-name request_errors \
  --kafka-bootstrap localhost:9092 --kafka-topic metrics
```

#### `diagnose_vault_approle.py`

If your application can't authenticate with Vault, run this tool. It checks env vars, connectivity, and attempts a login, providing specific advice on failure.

```bash
export VAULT_ADDR=...
export VAULT_ROLE_ID=...
export VAULT_SECRET_ID=...
python scripts/diagnose_vault_approle.py
```

### Shell Configuration

#### `set_prompt.sh`

Configures a colorful, informative bash prompt that displays:
- OS type (ubuntu/redhat/linux) at the beginning
- Current date
- Username and hostname
- Current working directory

The prompt uses best-practice color coding for readability and visual hierarchy. OS detection runs once at shell startup for efficiency.

```bash
# Source it to apply to current shell
. scripts/set_prompt.sh

# Or add to your ~/.bashrc to make it permanent
echo '. ~/src/dbtools/scripts/set_prompt.sh' >> ~/.bashrc
source ~/.bashrc
```
