# GDS Database Build Guide

## Overview

This guide explains how to install, build, test, and package the `gds_database` library. Whether you're a user wanting to install it, or a developer wanting to contribute, this guide has you covered.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Development Setup](#development-setup)
4. [Building the Package](#building-the-package)
5. [Running Tests](#running-tests)
6. [Code Quality Checks](#code-quality-checks)
7. [Creating a Release](#creating-a-release)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need

Before starting, ensure you have:

1. **Python 3.9 or higher**
   ```bash
   # Check your Python version
   python --version
   # Should show: Python 3.9.x or higher
   ```

2. **pip** (Python package installer)
   ```bash
   # Check pip version
   pip --version
   ```

3. **Git** (for cloning the repository)
   ```bash
   # Check Git version
   git --version
   ```

### Optional but Recommended

- **Virtual environment tool** (`venv`, `virtualenv`, or `conda`)
- **Text editor or IDE** (VS Code, PyCharm, etc.)

---

## Installation

### For Users

If you just want to use the library:

#### Option 1: Install from PyPI (when published)
```bash
pip install gds-database
```

#### Option 2: Install from Source
```bash
# Clone the repository
git clone https://github.com/davidvupham/dbtools.git
cd dbtools/gds_database

# Install the package
pip install .
```

#### Option 3: Install in Editable Mode (for development)
```bash
# Install so changes to source code are immediately available
pip install -e .
```

### Verify Installation

```bash
# Try importing in Python
python -c "from gds_database import DatabaseConnection; print('Success!')"
```

---

## Development Setup

### Step 1: Clone the Repository

```bash
# Clone the entire dbtools repository
git clone https://github.com/davidvupham/dbtools.git

# Navigate to the gds_database directory
cd dbtools/gds_database
```

### Step 2: Create a Virtual Environment

**Why use a virtual environment?**
- Isolates project dependencies
- Prevents conflicts with other projects
- Makes dependencies reproducible

#### Using `venv` (built into Python)

```bash
# Create virtual environment
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

#### Using `conda`

```bash
# Create conda environment
conda create -n gds-db python=3.9

# Activate it
conda activate gds-db
```

### Step 3: Install Development Dependencies

```bash
# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"

# This installs:
# - The gds_database package (editable)
# - pytest (for testing)
# - pytest-cov (for coverage)
# - black (for formatting)
# - ruff (for linting)
# - mypy (for type checking)
```

### Step 4: Verify Setup

```bash
# Check that tools are installed
pytest --version
ruff --version
mypy --version

# Run tests to ensure everything works
pytest tests/
```

**Expected output:**
```
===== test session starts =====
...
35 passed in 7.14s
```

---

## Building the Package

### Understanding Python Package Building

A Python package consists of:
- **Source code** (`gds_database/*.py`)
- **Metadata** (`pyproject.toml`, `setup.py`)
- **Documentation** (`README.md`, `docs/`)
- **Tests** (`tests/`)

We build it into distributable formats:
- **Wheel** (`.whl`) - Binary distribution (faster to install)
- **Source Distribution** (`.tar.gz`) - Source code archive

### Build Commands

#### Using build (Recommended)

```bash
# Install build tool
pip install build

# Build the package
python -m build

# This creates dist/ directory with:
# - gds_database-1.0.0-py3-none-any.whl
# - gds_database-1.0.0.tar.gz
```

#### Using setup.py (Legacy)

```bash
# Build wheel
python setup.py bdist_wheel

# Build source distribution
python setup.py sdist

# Build both
python setup.py sdist bdist_wheel
```

### Build Output

```bash
# Check what was built
ls -la dist/

# Output:
# gds_database-1.0.0-py3-none-any.whl  (wheel format)
# gds_database-1.0.0.tar.gz            (source format)
```

### Installing Your Local Build

```bash
# Install the wheel you just built
pip install dist/gds_database-1.0.0-py3-none-any.whl

# Or install from source distribution
pip install dist/gds_database-1.0.0.tar.gz
```

---

## Running Tests

### Quick Test Run

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_base.py

# Run specific test class
pytest tests/test_base.py::TestDatabaseConnection

# Run specific test method
pytest tests/test_base.py::TestDatabaseConnection::test_complete_implementation
```

### Test with Coverage

```bash
# Run tests with coverage report
pytest tests/ --cov=gds_database --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=gds_database --cov-report=html

# Open the report in browser
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Understanding Coverage Output

```
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
gds_database/__init__.py       3      0   100%
gds_database/base.py         162      0   100%
--------------------------------------------------------
TOTAL                        165      0   100%
```

- **Stmts**: Total statements (lines of code)
- **Miss**: Missed statements (not tested)
- **Cover**: Coverage percentage
- **Missing**: Line numbers not covered

**Goal**: 100% coverage! ✅

### Test Options

```bash
# Stop at first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s

# Run only failed tests from last run
pytest tests/ --lf

# Run tests in parallel (faster)
pip install pytest-xdist
pytest tests/ -n auto
```

---

## Code Quality Checks

### Linting with Ruff

**What is linting?**
Checking code for style issues, potential bugs, and anti-patterns.

```bash
# Check all code
ruff check gds_database/ tests/

# Auto-fix issues
ruff check --fix gds_database/ tests/

# Check specific file
ruff check gds_database/base.py
```

**Common ruff checks:**
- Unused imports
- Undefined variables
- Line too long
- Missing docstrings
- Code complexity

### Type Checking with mypy

**What is type checking?**
Verifying that types (int, str, list, etc.) are used correctly.

```bash
# Check types
mypy gds_database/

# Strict mode (recommended)
mypy --strict gds_database/
```

**Example mypy error:**
```python
def add(a: int, b: int) -> int:
    return a + b

result = add("hello", "world")  # ❌ mypy error
# Argument 1 to "add" has incompatible type "str"; expected "int"
```

### Formatting with black

**What is formatting?**
Automatically formatting code to follow consistent style.

```bash
# Check if code needs formatting
black --check gds_database/ tests/

# Format code
black gds_database/ tests/

# Show what would change (don't modify)
black --diff gds_database/
```

### Running All Checks

```bash
# Comprehensive check script
echo "=== RUFF CHECK ==="
ruff check gds_database/ tests/

echo "=== TYPE CHECK ==="
mypy gds_database/

echo "=== FORMAT CHECK ==="
black --check gds_database/ tests/

echo "=== TESTS ==="
pytest tests/ --cov=gds_database --cov-report=term

# If all pass, you're ready to commit! ✅
```

### Pre-commit Hooks

Automatically run checks before each commit:

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Now checks run automatically on git commit
# To run manually:
pre-commit run --all-files
```

---

## Creating a Release

### Version Numbering

We use **Semantic Versioning** (semver):

```
MAJOR.MINOR.PATCH
  1  .  0  .  0

MAJOR: Breaking changes (incompatible API changes)
MINOR: New features (backward-compatible)
PATCH: Bug fixes (backward-compatible)
```

Examples:
- `1.0.0` → `1.0.1` - Bug fix
- `1.0.1` → `1.1.0` - New feature added
- `1.1.0` → `2.0.0` - Breaking change

### Release Checklist

#### 1. Update Version Number

Edit `pyproject.toml`:
```toml
[project]
name = "gds-database"
version = "1.1.0"  # Update this
```

Edit `gds_database/__init__.py`:
```python
__version__ = "1.1.0"  # Update this
```

#### 2. Update Changelog

Create/update `CHANGELOG.md`:
```markdown
# Changelog

## [1.1.0] - 2025-11-03

### Added
- Async support with AsyncDatabaseConnection
- Connection pooling with ConnectionPool
- Transaction support with TransactionalConnection

### Fixed
- Type annotations for Python 3.9+

### Changed
- Improved error messages
```

#### 3. Run All Quality Checks

```bash
# Ensure everything passes
ruff check gds_database/ tests/
mypy gds_database/
pytest tests/ --cov=gds_database
```

#### 4. Build the Package

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build new packages
python -m build
```

#### 5. Test the Build Locally

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate

# Install from the wheel
pip install dist/gds_database-1.1.0-py3-none-any.whl

# Test import
python -c "import gds_database; print(gds_database.__version__)"
# Should print: 1.1.0

# Deactivate and remove
deactivate
rm -rf test-env
```

#### 6. Create Git Tag

```bash
# Commit changes
git add .
git commit -m "Release version 1.1.0"

# Create tag
git tag -a v1.1.0 -m "Version 1.1.0: Add async support and connection pooling"

# Push commits and tags
git push origin main
git push origin v1.1.0
```

#### 7. Publish to PyPI

```bash
# Install twine (for uploading)
pip install twine

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ gds-database

# If successful, upload to real PyPI
twine upload dist/*
```

### Publishing to GitHub Releases

1. Go to https://github.com/davidvupham/dbtools/releases
2. Click "Draft a new release"
3. Choose tag: `v1.1.0`
4. Title: "Release 1.1.0"
5. Description: Copy from CHANGELOG.md
6. Attach built files: `dist/*.whl`, `dist/*.tar.gz`
7. Click "Publish release"

---

## Troubleshooting

### Common Issues

#### 1. Import Error After Installation

**Problem:**
```python
>>> import gds_database
ModuleNotFoundError: No module named 'gds_database'
```

**Solutions:**
```bash
# Ensure you're in the right environment
which python  # Should show venv/conda path

# Reinstall
pip uninstall gds-database
pip install -e .

# Check installation
pip show gds-database
```

#### 2. Tests Failing

**Problem:**
```
tests/test_base.py::TestDatabaseConnection::test_complete_implementation FAILED
```

**Solutions:**
```bash
# Run with verbose output to see details
pytest tests/ -v -s

# Run just the failing test
pytest tests/test_base.py::TestDatabaseConnection::test_complete_implementation -v

# Check if dependencies are installed
pip install -e ".[dev]"
```

#### 3. Type Checking Errors

**Problem:**
```
gds_database/base.py:100: error: Missing return statement
```

**Solutions:**
```bash
# Check which Python version mypy is using
mypy --version

# Ensure pyproject.toml has correct Python version
# [tool.mypy]
# python_version = "3.9"

# Install type stubs if needed
pip install types-all
```

#### 4. Coverage Not 100%

**Problem:**
```
TOTAL                        165      5    97%
```

**Solutions:**
```bash
# See which lines are missing
pytest tests/ --cov=gds_database --cov-report=term-missing

# Check HTML report for details
pytest tests/ --cov=gds_database --cov-report=html
open htmlcov/index.html

# Write tests for missing lines
# Or use # pragma: no cover for unreachable code
```

#### 5. Build Fails

**Problem:**
```
ERROR: Failed building wheel for gds-database
```

**Solutions:**
```bash
# Update pip and build tools
pip install --upgrade pip setuptools wheel build

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Try building again
python -m build

# Check pyproject.toml syntax
python -c "import tomli; tomli.load(open('pyproject.toml', 'rb'))"
```

#### 6. Virtual Environment Issues

**Problem:**
```bash
# Commands not found after activation
pytest: command not found
```

**Solutions:**
```bash
# Deactivate and recreate environment
deactivate
rm -rf venv/
python -m venv venv
source venv/bin/activate

# Reinstall everything
pip install -e ".[dev]"
```

### Getting Help

If you're still stuck:

1. **Check the logs**: Most tools provide detailed error messages
2. **Search existing issues**: https://github.com/davidvupham/dbtools/issues
3. **Ask for help**: Create a new issue with:
   - What you tried
   - Full error message
   - Your environment (`python --version`, OS, etc.)

---

## Development Workflow

### Typical Development Cycle

```bash
# 1. Create feature branch
git checkout -b feature/add-sqlite-support

# 2. Make changes
vim gds_database/sqlite.py

# 3. Add tests
vim tests/test_sqlite.py

# 4. Run tests locally
pytest tests/ -v

# 5. Check code quality
ruff check gds_database/ tests/
mypy gds_database/
black gds_database/ tests/

# 6. Commit changes
git add .
git commit -m "feat: Add SQLite support"

# 7. Push and create pull request
git push origin feature/add-sqlite-support
# Then create PR on GitHub

# 8. After PR is merged, delete branch
git checkout main
git pull origin main
git branch -d feature/add-sqlite-support
```

### Quick Commands Reference

```bash
# Development
pip install -e ".[dev]"          # Install for development
pytest tests/ -v                  # Run tests
pytest tests/ --cov=gds_database  # Run with coverage
ruff check gds_database/          # Lint code
mypy gds_database/                # Type check
black gds_database/               # Format code

# Building
python -m build                   # Build package
pip install dist/*.whl            # Install built package

# Releasing
git tag -a v1.0.0 -m "Release"    # Tag release
twine upload dist/*               # Upload to PyPI

# Cleanup
rm -rf dist/ build/ *.egg-info    # Remove build artifacts
rm -rf htmlcov/ .coverage          # Remove coverage files
rm -rf .pytest_cache/              # Remove pytest cache
find . -type d -name __pycache__ -exec rm -rf {} +  # Remove Python cache
```

---

## Summary

You now know how to:

✅ Install gds_database for use or development
✅ Set up a development environment
✅ Build the package
✅ Run tests with coverage
✅ Check code quality
✅ Create and publish releases
✅ Troubleshoot common issues

**Next Steps:**
- Read [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for contribution guidelines
- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the design
- Start building your first database implementation!
