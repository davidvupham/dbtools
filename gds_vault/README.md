
# gds-vault

`gds-vault` is a production-ready Python package for retrieving secrets from HashiCorp Vault using AppRole authentication. It is designed for secure, programmatic access to secrets in CI/CD pipelines, microservices, and automation scripts.

## Features

- **AppRole authentication** using environment variables: `VAULT_ROLE_ID`, `VAULT_SECRET_ID`
- **Vault address** from `VAULT_ADDR` environment variable
- **Supports both KV v1 and v2** secret engines with auto-detection
- **Token caching** with automatic refresh (5-minute early renewal)
- **Secret caching** for improved performance
- **Automatic retry logic** with exponential backoff for resilience
- **Production logging** for debugging and monitoring
- **Simple dual API**: Functional API and class-based API
- **Context manager support** for automatic resource cleanup
- **No external dependencies** except `requests`

## Requirements

- Python 3.7+
- HashiCorp Vault server (AppRole auth enabled)

## Usage

1. **Set environment variables** (or pass values directly):
	- `VAULT_ROLE_ID`: Your Vault AppRole role_id
	- `VAULT_SECRET_ID`: Your Vault AppRole secret_id
	- `VAULT_ADDR`: Vault server address (e.g. `https://vault.example.com`)

2. **Fetch a secret:**

```python
from gds_vault.vault import get_secret_from_vault

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

You can build and install `gds-vault` as a standalone package using pip and standard Python tools.

### 1. Install directly from source (Development Mode)

```bash
cd /path/to/gds_vault
pip install -e .
```

### 2. Install directly from source (Normal Install)

```bash
cd /path/to/gds_vault
pip install .
```

### 3. Build a distributable package

First, ensure you have `build` installed:

```bash
pip install build
```

Then build the package:

```bash
cd /path/to/gds_vault
python -m build
```

This creates both `.tar.gz` (source distribution) and `.whl` (wheel) files in the `dist/` directory.

Install the built wheel:

```bash
pip install dist/gds_vault-0.1.0-py3-none-any.whl
```

### 4. Legacy build method

```bash
cd /path/to/gds_vault
python setup.py sdist bdist_wheel
pip install dist/gds_vault-0.1.0-py3-none-any.whl
```

## Advanced Features

### Class-Based API with Token Caching

For multiple secret retrievals, use `VaultClient` to cache the authentication token:

```python
from gds_vault import VaultClient

# Create client (authenticates once)
client = VaultClient()

# Fetch multiple secrets using the same token
secret1 = client.get_secret('secret/data/app1')
secret2 = client.get_secret('secret/data/app2')
secret3 = client.get_secret('secret/data/app3')

# Check cache info
print(client.get_cache_info())
```

### Context Manager for Automatic Cleanup

```python
from gds_vault import VaultClient

# Automatically clears cache on exit
with VaultClient() as client:
    secret = client.get_secret('secret/data/myapp')
    # Use secret...
# Cache automatically cleared here
```

### Logging for Production Debugging

Enable logging to track operations and troubleshoot issues:

```python
import logging
from gds_vault import VaultClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

**Log output example:**
```
2025-10-03 10:15:23 - gds_vault.vault - INFO - Authenticating with Vault at https://vault.example.com
2025-10-03 10:15:24 - gds_vault.vault - INFO - Successfully authenticated with Vault. Token valid for 3600s
2025-10-03 10:15:24 - gds_vault.vault - INFO - Fetching secret from Vault: secret/data/myapp
```

### Automatic Retry with Exponential Backoff

Network operations automatically retry on transient failures:

```
WARNING: get_secret attempt 1 failed: Connection timeout. Retrying in 1.0s...
WARNING: get_secret attempt 2 failed: Connection timeout. Retrying in 2.0s...
INFO: Successfully fetched KV v2 secret: secret/data/myapp
```

**Retry configuration:**
- Max retries: 3
- Initial delay: 1.0s
- Backoff factor: 2.0 (exponential)
- Handles: Connection timeouts, network errors, rate limiting

## Documentation

- **[LOGGING_AND_RETRY_GUIDE.md](LOGGING_AND_RETRY_GUIDE.md)** - Comprehensive guide to logging and retry features (500+ lines)
- **[LOGGING_AND_RETRY_IMPLEMENTATION.md](LOGGING_AND_RETRY_IMPLEMENTATION.md)** - Implementation details and technical summary
- **[examples/logging_retry_example.py](examples/logging_retry_example.py)** - Working examples

## Testing

### Run all tests

Using pytest (recommended):

```bash
cd /path/to/gds_vault
pip install pytest pytest-cov
pytest -v
```

Using the test runner:

```bash
cd /path/to/gds_vault
python run_tests.py
```

Using unittest directly:

```bash
cd /path/to/gds_vault
python -m unittest discover -s tests -v
```

### Run with coverage

```bash
pytest --cov=gds_vault --cov-report=term-missing tests/
```

**Current test coverage:** 96% (108/112 statements)

## License
MIT
