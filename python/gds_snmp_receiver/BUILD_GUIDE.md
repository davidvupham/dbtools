# Building gds_snmp_receiver Package

This document explains how the `gds_snmp_receiver` package is structured for distribution and how to build installable packages.

## Package Structure

The package follows standard Python packaging conventions with a **src-layout** structure:

```
gds_snmp_receiver/              # Package root
├── gds_snmp_receiver/          # Python package directory
│   ├── __init__.py            # Package initialization
│   ├── core.py                # SNMPReceiver class
│   └── receiver.py            # CLI entry point
├── setup.py                    # Build configuration (legacy)
├── pyproject.toml              # Build configuration (modern)
├── MANIFEST.in                 # File inclusion rules
├── LICENSE                     # MIT License
├── README.md                   # Package documentation
└── requirements.txt            # Runtime dependencies
```

## Build Configuration Files

### pyproject.toml (Modern Standard)

Primary build configuration using PEP 518/621 standards:

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "gds-snmp-receiver"
version = "0.1.0"
dependencies = [
    "pysnmp>=4.4.12",
    "pika>=1.3.0",
]

[project.scripts]
gds-snmp-receiver = "gds_snmp_receiver.receiver:main"
```

**Key Features:**
- Package name: `gds-snmp-receiver` (PyPI name)
- Module name: `gds_snmp_receiver` (import name)
- CLI tool: `gds-snmp-receiver` command installed globally
- Python 3.9+ required

### setup.py (Backward Compatibility)

Provides compatibility with older build tools:
- Uses `setuptools.find_packages()` to discover modules
- Declares dependencies in `install_requires`
- Defines console script entry point
- Reads README.md for long description

### MANIFEST.in

Controls which files are included in source distribution:

```
include README.md LICENSE requirements.txt
include *.md                     # Include all documentation
exclude Dockerfile               # Exclude Docker files
exclude docker-compose.yml
recursive-exclude tests *        # Exclude test files
recursive-exclude tools *        # Exclude E2E tools
```

## Building the Package

### Prerequisites

```bash
# Install build tools
pip install build twine
```

### Build Commands

```bash
# Build both source distribution (.tar.gz) and wheel (.whl)
python -m build

# Build only wheel
python -m build --wheel

# Build only source distribution
python -m build --sdist
```

### Output

Build artifacts are created in `dist/`:

```
dist/
├── gds_snmp_receiver-0.1.0-py3-none-any.whl    # Wheel (16 KB)
└── gds_snmp_receiver-0.1.0.tar.gz              # Source (44 KB)
```

**Wheel filename breakdown:**
- `gds_snmp_receiver` - Package name
- `0.1.0` - Version
- `py3` - Python 3 compatible
- `none` - No ABI requirements
- `any` - Works on any platform

## Installing the Package

### From Wheel (Recommended)

```bash
pip install dist/gds_snmp_receiver-0.1.0-py3-none-any.whl
```

### From Source Distribution

```bash
pip install dist/gds_snmp_receiver-0.1.0.tar.gz
```

### Development Mode (Editable Install)

```bash
# Install in editable mode (changes to code take effect immediately)
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

### From PyPI (Once Published)

```bash
pip install gds-snmp-receiver
```

## Verifying Installation

### CLI Tool

```bash
# Verify command is available
gds-snmp-receiver --help

# Run receiver
gds-snmp-receiver --host 0.0.0.0 --port 9162
```

### Python Import

```python
# Verify module can be imported
from gds_snmp_receiver import SNMPReceiver

# Create instance
receiver = SNMPReceiver(
    listen_host="0.0.0.0",
    listen_port=9162,
    rabbit_url="amqp://guest:guest@localhost:5672/",
    queue_name="alerts"
)

# Run receiver
receiver.run()
```

### Check Installation

```bash
# Show installed package info
pip show gds-snmp-receiver

# List installed files
pip show -f gds-snmp-receiver
```

## Publishing to PyPI

### Test PyPI (for testing)

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Install from Test PyPI to verify
pip install --index-url https://test.pypi.org/simple/ gds-snmp-receiver
```

### Production PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Install from PyPI
pip install gds-snmp-receiver
```

**Note:** You need PyPI credentials configured in `~/.pypirc` or passed via command line.

## Version Management

Version is defined in two places (must be kept in sync):

1. `pyproject.toml`: `version = "0.1.0"`
2. `setup.py`: `version="0.1.0"`

**Recommended:** Use a tool like `bump2version` to manage versions automatically.

## Development Workflow

1. **Make changes** to code in `gds_snmp_receiver/`
2. **Test changes** locally:
   ```bash
   pip install -e .
   gds-snmp-receiver --help
   ```
3. **Run tests**:
   ```bash
   pytest tests/
   docker compose -f docker-compose.e2e.yml up  # E2E test
   ```
4. **Update version** in `pyproject.toml` and `setup.py`
5. **Build package**:
   ```bash
   python -m build
   ```
6. **Test installation**:
   ```bash
   pip install dist/gds_snmp_receiver-*.whl
   ```
7. **Publish** to PyPI (if ready)

## Troubleshooting

### "package directory does not exist"

**Cause:** Python files are not in a subdirectory matching the package name.

**Solution:** Ensure structure is:
```
gds_snmp_receiver/           # Root
└── gds_snmp_receiver/       # Package (must match name)
    ├── __init__.py
    ├── core.py
    └── receiver.py
```

### "entry point not found"

**Cause:** Entry point function doesn't exist or has wrong signature.

**Solution:** Verify `receiver.py` has `main()` function:
```python
def main(argv: Optional[list[str]] = None) -> None:
    # CLI implementation
```

### CLI tool not available after install

**Cause:** Script not installed in PATH or wrong entry point.

**Solution:**
1. Verify entry point in `pyproject.toml`:
   ```toml
   [project.scripts]
   gds-snmp-receiver = "gds_snmp_receiver.receiver:main"
   ```
2. Check pip installation succeeded without errors
3. Verify PATH includes pip's script directory

## Best Practices

1. **Always build in clean environment** to avoid including dev files
2. **Test wheel installation** before publishing
3. **Use semantic versioning** (MAJOR.MINOR.PATCH)
4. **Update changelog** with each version
5. **Tag releases** in git: `git tag v0.1.0`
6. **Sign releases** with GPG for security (optional)

## Package Metadata

Defined in `pyproject.toml`:

- **Name:** `gds-snmp-receiver` (PyPI name with hyphen)
- **Import Name:** `gds_snmp_receiver` (Python module with underscore)
- **Version:** `0.1.0`
- **License:** MIT
- **Python:** >= 3.9
- **Dependencies:** `pysnmp>=4.4.12`, `pika>=1.3.0`
- **Classifiers:** Beta status, monitoring tools, Python 3.9-3.12

## Files Included in Distribution

### Source Distribution (.tar.gz)
- All Python source files
- Documentation (*.md files)
- LICENSE
- requirements.txt
- pyproject.toml, setup.py, MANIFEST.in
- Excludes: Docker files, tests, tools, __pycache__

### Wheel (.whl)
- Python bytecode (.pyc files)
- Package metadata
- Entry point scripts
- Much smaller than source distribution

## Summary

The `gds_snmp_receiver` package is now:

- ✅ **Installable** via `pip install`
- ✅ **Distributable** as wheel or source distribution
- ✅ **CLI-ready** with `gds-snmp-receiver` command
- ✅ **Importable** as `from gds_snmp_receiver import SNMPReceiver`
- ✅ **Publishable** to PyPI
- ✅ **Well-structured** following Python packaging standards

Build artifacts available in `dist/`:
- `gds_snmp_receiver-0.1.0-py3-none-any.whl` (16 KB) - **Use this for installation**
- `gds_snmp_receiver-0.1.0.tar.gz` (44 KB) - Source distribution
