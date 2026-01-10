# Validation Directory

This directory contains all validation scripts, reports, and logs for the Liquibase tutorial series.

## Directory Structure

```
validation/
├── README.md                    # This file
├── scripts/                     # Validation scripts
│   ├── cleanup_validation.sh
│   ├── validate_tutorial_full.sh
│   ├── validate_tutorial_part2.sh
│   ├── validate_part3_cicd.sh
│   ├── validate_tutorial.sh
│   └── validate_step*.sh        # Individual step validation scripts
├── reports/                     # Validation reports
│   ├── part1/                   # Part 1 (Baseline) validation reports
│   ├── part2/                   # Part 2 (Manual Lifecycle) validation reports
│   ├── part3/                   # Part 3 (CI/CD) validation reports
│   └── general/                 # General validation reports
└── logs/                        # Validation execution logs
    ├── tutorial_validation_*.log
    └── part3_validation_*.log
```

## Organization Principles

This directory follows best practices for test/validation organization:

1. **Separation by Type**: Scripts, reports, and logs are in separate directories
2. **Separation by Part**: Reports are organized by tutorial part for easy navigation
3. **Clear Documentation**: README files explain structure and usage
4. **Easy Navigation**: Logical grouping makes it easy to find specific files

## Validation Scripts

All validation scripts are located in `scripts/`:

### Main Validation Scripts

- **`scripts/validate_tutorial_full.sh`** - Complete end-to-end validation for Part 1 tutorial
  - Executes all tutorial steps
  - Validates each step
  - Generates comprehensive reports
  - Includes automatic cleanup (pre and post)

- **`scripts/validate_tutorial_part2.sh`** - Validation for Part 2 (Manual Lifecycle)

- **`scripts/validate_part3_cicd.sh`** - Validation for Part 3 (CI/CD)

- **`scripts/cleanup_validation.sh`** - Cleanup script for validation runs
  - Removes containers and networks
  - Cleans up resources
  - Supports non-interactive mode

### Validation Scripts

- **`scripts/validate_orderdb_database.sh`** - Validates database creation
- **`scripts/validate_dev_populate.sh`** - Validates dev population
- **`scripts/validate_liquibase_properties.sh`** - Validates properties files
- **`scripts/validate_liquibase_baseline.sh`** - Validates baseline generation
- **`scripts/validate_liquibase_deploy.sh`** - Validates baseline deployment

## Reports

Reports are organized by tutorial part in `reports/`:

### Part 1 Reports (`reports/part1/`)

- `tutorial_validation_report.md` - Main validation report
- `FINAL_VALIDATION_REPORT.md` - Final validation results
- `EXECUTION_VALIDATION_REPORT.md` - Execution validation results
- `CLEANUP_INTEGRATION_SUMMARY.md` - Cleanup integration documentation
- `CLEANUP_COMPLETE.md` - Cleanup completion summary
- `VALIDATION_SUMMARY.md` - Quick validation summary
- Timestamped validation reports

### Part 2 Reports (`reports/part2/`)

- `part2_validation_report.md` - Part 2 validation report
- `part2_validation_summary.md` - Part 2 validation summary
- Related validation documents

### Part 3 Reports (`reports/part3/`)

- `part3_comprehensive_validation_report.md` - Comprehensive Part 3 report
- `part3_validation_summary.md` - Part 3 validation summary
- `part3_validation_report_*.md` - Timestamped Part 3 reports
- `part3_issues_*.md` - Part 3 issue tracking reports

### General Reports (`reports/general/`)

- `validation_report.md` - General validation report
- `requirements_validation_report.md` - Requirements validation

## Logs

All validation execution logs are stored in `logs/`:

- `tutorial_validation_*.log` - Part 1 validation logs
- `part3_validation_*.log` - Part 3 validation logs

Logs are timestamped for easy identification and are preserved for review and debugging.

## Usage

### Running Full Validation

```bash
export LIQUIBASE_TUTORIAL_DIR="/path/to/repo/docs/courses/liquibase"
export MSSQL_LIQUIBASE_TUTORIAL_PWD="YourPassword123!"
bash "$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_tutorial_full.sh"
```

### Running Part 2 Validation

```bash
bash "$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_tutorial_part2.sh"
```

### Running Part 3 Validation

```bash
bash "$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_part3_cicd.sh"
```

### Running Cleanup

```bash
bash "$LIQUIBASE_TUTORIAL_DIR/validation/scripts/cleanup_validation.sh"
```

### Running Validation Scripts

```bash
bash "$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_orderdb_database.sh"
bash "$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_dev_populate.sh"
bash "$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_liquibase_properties.sh"
bash "$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_liquibase_baseline.sh"
bash "$LIQUIBASE_TUTORIAL_DIR/validation/scripts/validate_liquibase_deploy.sh"
```

## Best Practices

1. **Run cleanup before validation** - Ensures clean environment
2. **Review logs after validation** - Check `logs/` directory for execution details
3. **Check reports** - Review reports in `reports/` for validation results
4. **Keep logs for debugging** - Logs are preserved for troubleshooting
5. **Organize by part** - Reports are organized by tutorial part for easy navigation

## File Naming Conventions

- **Scripts**: `validate_*.sh`, `cleanup_*.sh`
- **Reports**: `*_validation_report.md`, `*_summary.md`
- **Logs**: `*_validation_YYYYMMDD_HHMMSS.log`

## Notes

- Validation scripts automatically clean up before and after execution
- Log files are preserved for review
- Reports are generated with timestamps for tracking
- All scripts support non-interactive execution
- Scripts reference paths relative to `$LIQUIBASE_TUTORIAL_DIR`

---

**Last Updated:** 2026-01-09
