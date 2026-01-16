# Building and Deploying gds_snowflake

This guide explains how to build, install, test, and deploy the `gds_snowflake` package.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Building the Package](#building-the-package)
- [Installation Methods](#installation-methods)
- [Running Tests](#running-tests)
- [Code Quality](#code-quality)
- [Deployment to PyPI](#deployment-to-pypi)
- [Versioning](#versioning)

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- git (for version control)

## Local Development

### 1. Clone the Repository

```bash
git clone <repository-url>
cd gds_snowflake
```

### 2. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

Development dependencies include:
- pytest (testing framework)
- pytest-cov (code coverage)
- pytest-mock (mocking support)
- black (code formatting)
- flake8 (linting)
- mypy (type checking)
- build (package building)
- twine (PyPI publishing)

### 3. Install in Editable Mode

For active development, install the package in editable mode:

```bash
pip install -e .
```

This allows you to make changes to the code and see them reflected immediately without reinstalling.

## Building the Package

### 1. Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info
```

### 2. Build the Package

```bash
python -m build
```

This creates two distribution formats in the `dist/` directory:
- **Source distribution** (`.tar.gz`): Contains source code
- **Wheel distribution** (`.whl`): Pre-built package for faster installation

Example output:
```
dist/
├── gds_snowflake-0.1.0-py3-none-any.whl
└── gds_snowflake-0.1.0.tar.gz
```

### 3. Verify the Build

List the contents of the wheel:

```bash
unzip -l dist/gds_snowflake-*.whl
```

Check package metadata:

```bash
python -m build --help
pip show gds_snowflake  # if installed
```

## Installation Methods

### Method 1: Install from Local Build

Install the built package locally:

```bash
pip install dist/gds_snowflake-*.whl
```

Or from source distribution:

```bash
pip install dist/gds_snowflake-*.tar.gz
```

### Method 2: Install Directly from Source

```bash
pip install .
```

### Method 3: Editable Installation (Development)

```bash
pip install -e .
```

This is recommended for development as changes are immediately reflected.

### Method 4: Install from PyPI (After Deployment)

```bash
pip install gds-snowflake
```

### Method 5: Install from Git Repository

```bash
pip install git+<repository-url>
```

### Uninstalling

```bash
pip uninstall gds-snowflake
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_connection.py
pytest tests/test_database.py
pytest tests/test_table.py
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
pytest --cov=gds_snowflake --cov-report=html --cov-report=term
```

View the HTML coverage report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Specific Test

```bash
pytest tests/test_database.py::TestSnowflakeDatabase::test_get_databases
```

### Run Tests Matching Pattern

```bash
pytest -k "database"  # Run tests with "database" in the name
```

## Code Quality

### Format Code with Black

```bash
# Format entire project
black gds_snowflake tests --line-length=120

# Check without modifying
black gds_snowflake tests --check --line-length=120
```

### Lint with Flake8

```bash
# Check for code style issues
flake8 gds_snowflake tests --max-line-length=120 --extend-ignore=E203,W503
```

### Type Check with mypy

```bash
mypy gds_snowflake --ignore-missing-imports
```

### Run All Quality Checks

```bash
# Format
black gds_snowflake tests --line-length=120

# Lint
flake8 gds_snowflake tests --max-line-length=120 --extend-ignore=E203,W503

# Type check
mypy gds_snowflake --ignore-missing-imports

# Test
pytest --cov=gds_snowflake
```

## Deployment to PyPI

### 1. Create PyPI Account

1. Register at [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. Verify your email address
3. (Optional) Register at [https://test.pypi.org/](https://test.pypi.org/) for testing

### 2. Configure API Token

Create an API token for authentication:

1. Go to [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
2. Create a new token with project scope
3. Save the token securely

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Your PyPI token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgENd...  # Your TestPyPI token
```

Set permissions:

```bash
chmod 600 ~/.pypirc
```

### 3. Test Deployment (TestPyPI)

```bash
# Build the package
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ gds-snowflake
```

### 4. Deploy to PyPI

```bash
# Build clean distributions
rm -rf dist/ build/ *.egg-info
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Or use shorthand
twine upload dist/*
```

### 5. Verify Deployment

Check your package on PyPI:
- [https://pypi.org/project/gds-snowflake/](https://pypi.org/project/gds-snowflake/)

Install and test:

```bash
pip install gds-snowflake
python -c "from gds_snowflake import SnowflakeConnection; print('Success!')"
```

### 6. Update Deployment

To release a new version:

1. Update version in `setup.py` or `pyproject.toml`
2. Update `CHANGELOG.md` (if you have one)
3. Commit changes
4. Create a git tag:
   ```bash
   git tag -a v0.1.1 -m "Release version 0.1.1"
   git push origin v0.1.1
   ```
5. Build and upload:
   ```bash
   rm -rf dist/ build/ *.egg-info
   python -m build
   twine upload dist/*
   ```

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Add functionality (backwards-compatible)
- **PATCH** version: Bug fixes (backwards-compatible)

Version format: `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)

### Updating Version

Edit `setup.py`:

```python
setup(
    name="gds-snowflake",
    version="0.2.0",  # Update this
    ...
)
```

Or edit `pyproject.toml`:

```toml
[project]
name = "gds-snowflake"
version = "0.2.0"  # Update this
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e .
        pip install -r requirements-dev.txt
    - name: Run tests
      run: pytest --cov=gds_snowflake
    - name: Check formatting
      run: black gds_snowflake tests --check --line-length=120
    - name: Lint
      run: flake8 gds_snowflake tests --max-line-length=120
```

## Troubleshooting

### Build Errors

**Issue**: `ModuleNotFoundError: No module named 'build'`

**Solution**:
```bash
pip install build
```

### Upload Errors

**Issue**: `403 Forbidden` when uploading to PyPI

**Solution**:
- Verify your API token is correct
- Ensure the package name isn't already taken
- Check that you have upload permissions

**Issue**: `400 Bad Request: File already exists`

**Solution**:
- You cannot overwrite an existing version on PyPI
- Increment the version number and rebuild

### Import Errors After Installation

**Issue**: `ImportError: cannot import name 'SnowflakeConnection'`

**Solution**:
```bash
# Reinstall the package
pip uninstall gds-snowflake
pip install gds-snowflake

# Or in editable mode
pip install -e .
```

## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
