
# gds-hvault

`gds-hvault` is a minimal Python package for retrieving secrets from HashiCorp Vault using AppRole authentication. It is designed for secure, programmatic access to secrets in CI/CD pipelines, microservices, and automation scripts.

## Features

- **AppRole login** using environment variables: `HVAULT_ROLE_ID`, `HVAULT_SECRET_ID`
- **Vault address** from `HVAULT_ADDR` or `VAULT_ADDR`
- **Supports both KV v1 and v2** secret engines
- **Simple API**: `get_secret_from_vault(secret_path)`
- **No external dependencies** except `requests`

## Requirements

- Python 3.7+
- HashiCorp Vault server (AppRole auth enabled)

## Usage

1. **Set environment variables** (or pass values directly):
	- `HVAULT_ROLE_ID`: Your Vault AppRole role_id
	- `HVAULT_SECRET_ID`: Your Vault AppRole secret_id
	- `HVAULT_ADDR` or `VAULT_ADDR`: Vault server address (e.g. `https://vault.example.com`)

2. **Fetch a secret:**

```python
from gds_hvault.vault import get_secret_from_vault

# Example: fetch secret at 'secret/data/myapp' (KV v2)
secret = get_secret_from_vault('secret/data/myapp')
print(secret['password'])
```

## API

### `get_secret_from_vault(secret_path: str, vault_addr: str = None) -> dict`

- `secret_path`: Path to the secret in Vault (e.g., `'secret/data/myapp'` for KV v2, `'secret/myapp'` for KV v1)
- `vault_addr`: (optional) Override Vault address
- **Returns:** Secret data as a dictionary
- **Raises:** `VaultError` on failure

## How to Build and Install

You can build and install `gds-hvault` as a standalone package using pip and standard Python tools.

### 1. Install directly from source (Development Mode)

```bash
cd /path/to/gds_hvault
pip install -e .
```

### 2. Install directly from source (Normal Install)

```bash
cd /path/to/gds_hvault
pip install .
```

### 3. Build a distributable package

First, ensure you have `build` installed:

```bash
pip install build
```

Then build the package:

```bash
cd /path/to/gds_hvault
python -m build
```

This creates both `.tar.gz` (source distribution) and `.whl` (wheel) files in the `dist/` directory.

Install the built wheel:

```bash
pip install dist/gds_hvault-0.1.0-py3-none-any.whl
```

### 4. Legacy build method

```bash
cd /path/to/gds_hvault
python setup.py sdist bdist_wheel
pip install dist/gds_hvault-0.1.0-py3-none-any.whl
```

## Testing

### Run all tests

Using the test runner:

```bash
cd /path/to/gds_hvault
python run_tests.py
```

Using unittest directly:

```bash
cd /path/to/gds_hvault
python -m unittest discover -s tests -v
```

Using pytest (if installed):

```bash
cd /path/to/gds_hvault
pip install pytest
pytest
```

### Run specific test file

```bash
python -m unittest tests.test_vault
```

### Run with coverage

```bash
pip install coverage
coverage run -m unittest discover -s tests
coverage report
coverage html  # Generate HTML coverage report
```

## License
MIT
