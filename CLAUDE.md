# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build, Test, and Lint Commands

```bash
# Primary workflow commands (via Makefile)
make all              # Run lint, test, and build everything
make lint             # Run Ruff linter
make format           # Run Ruff formatter
make test             # Run Pytest across all test directories
make ci               # Run lint + test (CI checks)
make coverage         # Generate coverage report (HTML + terminal)
make pre-commit       # Run all pre-commit hooks
make clean            # Clean caches and build artifacts

# Run a single test file
PYTHONPATH=.:gds_database/src:gds_vault/src pytest tests/test_example.py -v

# Run tests for a specific package
cd gds_vault && pytest tests/ -v

# PowerShell tests
make test-pwsh        # Run Pester tests

# Dev container
make verify-devcontainer  # Run verification suite
make dev-shell            # Open shell in dev container
```

## Architecture Overview

### Monorepo Structure

This is a UV workspace monorepo with 13 Python packages (`gds_*`) sharing a common lockfile. Each package has a `src/` layout and can depend on others.

**Core abstraction pattern:**
- `gds_database` - Abstract base classes defining database connection interfaces
- `gds_postgres`, `gds_mssql`, `gds_mongodb` - Concrete implementations extending `gds_database`
- `gds_vault` - HashiCorp Vault client (authentication, secrets caching)
- `gds_snowflake` - Snowflake utilities used by monitoring tools

**Services (FastAPI-based):**
- `gds_snmp_receiver` - SNMP trap receiver with worker pipeline
- `gds_notification` - Alert ingestion service

**Supporting packages:**
- `gds_metrics` - OpenTelemetry/Prometheus metrics abstraction
- `gds_kafka` - Kafka producer/consumer clients
- `gds_liquibase` - Database change management integration
- `gds_benchmark`, `gds_hammerdb` - Performance testing frameworks

### PowerShell Modules

`PowerShell/Modules/` contains Windows automation modules (GDS.Logging, GDS.MSSQL.*, GDS.Security, etc.). Build with `PowerShell/BuildAllModules.ps1`.

### Documentation

Follows Diátaxis framework:
- `docs/tutorials/` - Learning-oriented (Liquibase, Kafka, Python OOP)
- `docs/how-to/` - Task-oriented guides
- `docs/explanation/` - Conceptual background
- `docs/reference/` - API and configuration docs

## Code Style

- **Python**: Ruff for linting and formatting (line-length 120, Python 3.9+, Google-style docstrings)
- **PowerShell**: PSScriptAnalyzer + Pester
- **Documentation**: Diátaxis structure, kebab-case filenames, sentence-case headings

Key standards documents:
- `docs/development/coding-standards/python-coding-standards.md`
- `docs/development/coding-standards/powershell-coding-standards.md`
- `docs/best-practices/documentation-standards.md`

## Liquibase Tutorial Testing

When modifying the Liquibase tutorial in `docs/courses/liquibase/`, ensure the corresponding test scripts are updated:

| Tutorial | Test Script |
|----------|-------------|
| `learning-paths/series-part1-baseline.md` | `scripts/test_part1_baseline.sh` |
| `learning-paths/series-part2-manual.md` | `scripts/test_part2_manual.sh` |

After making changes to a tutorial or its scripts, run the test to verify everything works:

```bash
cd docs/courses/liquibase/scripts
./test_part1_baseline.sh    # Test Part 1 only
./test_part2_manual.sh      # Test Part 2 (runs Part 1 first, or use --skip-part1)
```

The test script executes the same scripts as the tutorial - it should not contain duplicate validation logic.
