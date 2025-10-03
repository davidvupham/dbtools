# Package Comparison: gds_hvault vs gds_snowflake

## Overview

This document compares the two packages in the repository and explains their structural differences.

## gds_hvault

**Purpose**: A minimal, single-purpose utility package for retrieving secrets from HashiCorp Vault using AppRole authentication.

**Scope**: Narrow - focused only on Vault secret retrieval

**Structure**:
```
gds_hvault/
├── README.md
├── pyproject.toml
├── setup.py
├── setup.cfg
├── tests/
│   └── test_vault.py
└── gds_hvault/
    ├── __init__.py
    ├── vault.py
    └── tests.py (deprecated - moved to tests/)
```

**Key Features**:
- AppRole authentication
- KV v1 and v2 secret engine support
- Simple API with one main function
- Minimal dependencies (only `requests`)

## gds_snowflake

**Purpose**: A comprehensive library for interacting with Snowflake, handling connection management and replication monitoring.

**Scope**: Broad - multiple responsibilities and features

**Structure**:
```
gds_snowflake/
├── LICENSE
├── MANIFEST.in
├── README.md
├── pyproject.toml
├── pytest.ini
├── run_tests.py
├── setup.py
├── test_modules.py
├── gds_snowflake/
│   ├── __init__.py
│   ├── connection.py
│   ├── replication.py
│   └── py.typed
├── tests/
│   ├── __init__.py
│   ├── test_connection_pytest.py
│   ├── test_monitor_integration.py
│   ├── test_snowflake_connection.py
│   └── test_snowflake_replication.py
└── gds_snowflake.egg-info/
```

**Key Features**:
- Connection management with Vault integration
- Replication and failover group monitoring
- Multiple modules and classes
- Type hints (`py.typed`)
- Comprehensive test suite
- Build and distribution tooling

## Why More Files in gds_snowflake?

### 1. **Complexity and Scope**
- `gds_snowflake` handles multiple concerns: connections, replication, failover groups
- `gds_hvault` does one thing: fetch secrets

### 2. **Testing Infrastructure**
- `gds_snowflake`: Full pytest setup with multiple test files, `pytest.ini`, test runners
- `gds_hvault`: Simpler testing needs

### 3. **Distribution Files**
- `gds_snowflake`: `MANIFEST.in` (includes non-Python files), `LICENSE`, `.gitignore`
- `gds_hvault`: Basic packaging files only

### 4. **Type Annotations**
- `gds_snowflake`: `py.typed` marker for type checking support
- `gds_hvault`: No formal type checking declaration

### 5. **Build Artifacts**
- `gds_snowflake`: `.egg-info/` directory from installations
- Both have similar packaging setup

## Recommendations for gds_hvault

To bring `gds_hvault` closer to the maturity of `gds_snowflake`:

1. **Add Missing Files**:
   - `LICENSE` file
   - `MANIFEST.in` for package data
   - `pytest.ini` for test configuration
   - `.gitignore` for version control

2. **Enhance Testing**:
   - Move from simple tests to pytest
   - Add integration tests
   - Add coverage reporting

3. **Add Type Hints**:
   - Include `py.typed` marker
   - Add type annotations to all functions

4. **Documentation**:
   - API reference
   - Usage examples
   - Contributing guidelines

5. **Additional Features** (see ENHANCEMENTS.md)
