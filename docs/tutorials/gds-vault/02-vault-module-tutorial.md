# Vault Module Tutorial - Beginner's Guide

## Understanding HashiCorp Vault Integration

This tutorial explains the `gds_vault` module, which connects to HashiCorp Vault to securely retrieve secrets like passwords and API keys.

---

## Table of Contents

1. [What is Vault?](#what-is-vault)
2. [Module Overview](#module-overview)
3. [The VaultClient Class](#the-vaultclient-class)
4. [Retry Logic and Resilience](#retry-logic-and-resilience)
5. [Step-by-Step Code Walkthrough](#step-by-step-code-walkthrough)
6. [Usage Examples](#usage-examples)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## What is Vault?

### The Problem

Applications need secrets (passwords, API keys, certificates) but storing them in code is dangerous:

```python
# ❌ BAD - Never do this!
password = "my_secret_password_123"
api_key = "abc123xyz789"
```

### The Solution: HashiCorp Vault

Vault is a secure storage system for secrets. Think of it as a high-security safe for your passwords:

- **Centralized**: All secrets in one place
- **Secure**: Encrypted storage
- **Audited**: Tracks who accessed what and when
- **Dynamic**: Can rotate secrets automatically

### How It Works

```
1. Your Application → 2. Authenticate with Vault → 3. Get Secret → 4. Use Secret
       |                     (Prove who you are)      (Retrieve password)    (Connect to DB)
```

---

## Module Overview

### File Structure

```
gds_vault/
├── gds_vault/
│   ├── __init__.py          # Package initialization
│   ├── vault.py             # Main module (we'll study this)
│   └── tests.py             # Basic integration tests
├── tests/
│   └── test_vault_client.py # Unit tests
└── examples/
    └── vault_client_example.py  # Usage examples
```

### Main Components

1. **VaultError** - Custom exception for Vault operations
2. **retry_with_backoff()** - Decorator for automatic retries
3. **VaultClient** - Main class to interact with Vault
4. **get_secret_from_vault()** - Simple function to get secrets

---

## The VaultClient Class

### What Does It Do?

VaultClient manages connections to Vault and retrieves secrets. It's like a smart assistant that:
- Logs into Vault for you
- Remembers your login (caching)
- Tries again if something fails (retry)
- Keeps track of everything (logging)

### Basic Usage

```python
from gds_vault.vault import VaultClient

# Create a client
client = VaultClient(
    vault_addr="https://vault.example.com:8200",
    role_id="your-role-id",
    secret_id="your-secret-id"
)

# Get a secret
secret_data = client.get_secret("secret/data/myapp")

# Access the password
password = secret_data["password"]
```

---

## Step-by-Step Code Walkthrough

### Part 1: Custom Exception

```python
class VaultError(Exception):
    """Exception raised for Vault operation errors."""
```

**What's happening?**
- Creates a custom exception type
- When Vault operations fail, we raise this specific error
- Makes it easy to catch Vault-specific problems

**Example:**
```python
try:
    secret = client.get_secret("secret/path")
except VaultError as e:
    print(f"Vault error occurred: {e}")
```

---

### Part 2: The Retry Decorator

```python
def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 32.0,
    backoff_factor: float = 2.0,
    retriable_exceptions: tuple = (requests.RequestException,)
) -> Callable:
```

**What's happening?**

This is a **decorator** that makes functions automatically retry when they fail.

**Parameters Explained:**

- `max_retries=3` → Try up to 3 times
- `initial_delay=1.0` → Wait 1 second before first retry
- `max_delay=32.0` → Never wait more than 32 seconds
- `backoff_factor=2.0` → Double the wait time each retry
- `retriable_exceptions` → Which errors should trigger a retry

**The Exponential Backoff Pattern:**

```
Attempt 1: Fails → Wait 1 second
Attempt 2: Fails → Wait 2 seconds (1 * 2)
Attempt 3: Fails → Wait 4 seconds (2 * 2)
Attempt 4: Fails → Wait 8 seconds (4 * 2)
...and so on...
```

**Why Use This?**

When a server is temporarily overloaded, waiting a bit before retrying gives it time to recover. Exponential backoff prevents overwhelming the server with too many retries.

**Example:**

```python
@retry_with_backoff(max_retries=3, initial_delay=1.0)
def fetch_data_from_vault():
    """This function will retry up to 3 times if it fails."""
    response = requests.get("https://vault.example.com/data")
    return response.json()
```

**The Decorator Code Explained:**

```python
def wrapper(*args, **kwargs):
    """Inner function that adds retry logic."""
    last_exception = None
    delay = initial_delay

    # Try max_retries times
    for attempt in range(max_retries):
        try:
            # Try to run the original function
            return func(*args, **kwargs)
        except retriable_exceptions as e:
            last_exception = e

            # On last attempt, give up
            if attempt == max_retries:
                logger.error(
                    "%s failed after %s retries: %s",
                    func.__name__,
                    max_retries,
                    e
                )
                raise

            # Wait before retrying (exponential backoff)
            current_delay = min(delay, max_delay)
            logger.warning(
                "%s attempt %s failed: %s. Retrying in %.1fs...",
                func.__name__,
                attempt + 1,
                e,
                current_delay
            )
            time.sleep(current_delay)
            delay *= backoff_factor  # Double the delay

    # If we get here, something went wrong
    raise last_exception
```

---

### Part 3: The VaultClient Class

#### Initialization

```python
class VaultClient:
    def __init__(
        self,
        vault_addr: Optional[str] = None,
        role_id: Optional[str] = None,
        secret_id: Optional[str] = None,
        timeout: int = 10
    ):
```

**What's happening?**

When you create a VaultClient, it:
1. Gets connection details (from parameters or environment variables)
2. Validates that required information is provided
3. Initializes caches for tokens and secrets
4. Sets up logging

**Parameters:**

- `vault_addr` → Vault server URL (e.g., "https://vault.example.com:8200")
- `role_id` → Your application's role ID (like a username)
- `secret_id` → Your application's secret ID (like a password)
- `timeout` → How long to wait for Vault to respond (seconds)

**The Code:**

```python
# Get Vault address (from parameter or environment variable)
self.vault_addr = vault_addr or os.getenv("VAULT_ADDR")
if not self.vault_addr:
    raise VaultError(
        "Vault address must be provided or set in VAULT_ADDR"
    )

# Get credentials
self.role_id = role_id or os.getenv("VAULT_ROLE_ID")
self.secret_id = secret_id or os.getenv("VAULT_SECRET_ID")

if not self.role_id or not self.secret_id:
    raise VaultError(
        "VAULT_ROLE_ID and VAULT_SECRET_ID must be provided"
    )

# Initialize caching variables
self._token: Optional[str] = None  # Store login token
self._token_expiry: Optional[float] = None  # When token expires
self._secret_cache: Dict[str, Dict[str, Any]] = {}  # Cache secrets
self.timeout = timeout
```

**Key Concepts:**

1. **`or` operator**: `vault_addr or os.getenv("VAULT_ADDR")`
   - If vault_addr is provided, use it
   - Otherwise, get it from environment variable

2. **Validation**: Checks that required parameters exist

3. **Caching**: Stores tokens and secrets to avoid repeated requests

---

#### Context Manager Support

```python
def __enter__(self):
    """Context manager entry."""
    logger.debug("Entering VaultClient context manager")
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit - clear cached token and secrets."""
    if exc_type:
        logger.error(
            "Exiting VaultClient context with exception: %s: %s",
            exc_type.__name__,
            exc_val
        )
    else:
        logger.debug("Exiting VaultClient context manager")

    # Clean up
    self.clear_cache()
    return False
```

**What's happening?**

This allows you to use VaultClient with the `with` statement:

```python
with VaultClient(vault_addr="...") as client:
    secret = client.get_secret("secret/path")
    # Do stuff with secret
# Automatically cleans up when done!
```

**Benefits:**
- Automatic cleanup (clears caches)
- Ensures resources are released
- Logs errors if they occur

---

#### Authentication Method

```python
@retry_with_backoff(max_retries=3, initial_delay=1.0)
def _authenticate(self) -> str:
    """
    Authenticate with Vault using AppRole and return a client token.

    Returns:
        str: Client token

    Raises:
        VaultError: If authentication fails
    """
    logger.info("Authenticating with Vault at %s", self.vault_addr)

    # Construct login URL
    login_url = f"{self.vault_addr}/v1/auth/approle/login"

    # Prepare credentials
    login_payload = {
        "role_id": self.role_id,
        "secret_id": self.secret_id
    }

    try:
        # Send authentication request
        resp = requests.post(
            login_url,
            json=login_payload,
            timeout=self.timeout
        )
    except requests.RequestException as e:
        logger.error("Network error connecting to Vault: %s", e)
        raise VaultError(f"Failed to connect to Vault: {e}") from e

    # Check if authentication succeeded
    if not resp.ok:
        logger.error(
            "Vault AppRole login failed with status %s: %s",
            resp.status_code,
            resp.text
        )
        raise VaultError(f"Vault AppRole login failed: {resp.text}")

    # Extract token from response
    auth_data = resp.json()["auth"]
    self._token = auth_data["client_token"]

    # Calculate token expiry (lease_duration - 5 minutes safety buffer)
    lease_duration = auth_data.get("lease_duration", 3600)
    self._token_expiry = time.time() + lease_duration - 300

    logger.info(
        "Successfully authenticated with Vault. Token valid for %ss",
        lease_duration
    )
    logger.debug("Token will be refreshed at %s", self._token_expiry)

    return self._token
```

**Step-by-Step Breakdown:**

1. **Decorator**: `@retry_with_backoff` → Retries if network fails

2. **Log the attempt**: So you know when authentication happens

3. **Build the URL**: Vault's AppRole login endpoint

4. **Prepare credentials**: Role ID and Secret ID

5. **Send HTTP POST request**:
   ```python
   resp = requests.post(login_url, json=login_payload, timeout=10)
   ```

6. **Handle network errors**: Wrap in try-except

7. **Check response**: If not OK (200), raise error

8. **Extract token**: Get the authentication token from response

9. **Calculate expiry**: Set when to refresh (with 5-minute buffer)

10. **Cache token**: Store for reuse

**Example Flow:**

```
1. VaultClient._authenticate()
   ↓
2. POST to https://vault.com:8200/v1/auth/approle/login
   ↓
3. Send: {"role_id": "...", "secret_id": "..."}
   ↓
4. Receive: {"auth": {"client_token": "s.abc123...", "lease_duration": 3600}}
   ↓
5. Store token and expiry time
   ↓
6. Return token
```

---

#### Getting Secrets

```python
@retry_with_backoff(max_retries=3, initial_delay=1.0)
def get_secret(
    self,
    secret_path: str,
    version: Optional[int] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Retrieve a secret from Vault.

    Args:
        secret_path: Path to the secret (e.g., 'secret/data/myapp')
        version: Specific version to retrieve (optional)
        use_cache: Whether to use cached secrets (default: True)

    Returns:
        dict: Secret data

    Raises:
        VaultError: If secret fetch fails
    """
```

**Parameters Explained:**

- `secret_path` → Where the secret is stored in Vault
- `version` → Get a specific version (Vault keeps history)
- `use_cache` → Speed up by using cached secrets

**The Code:**

```python
# Create cache key
cache_key = f"{secret_path}:v{version}" if version else secret_path

# Check cache first
if use_cache and cache_key in self._secret_cache:
    logger.debug("Cache hit for secret: %s", secret_path)
    return self._secret_cache[cache_key]

logger.info("Fetching secret from Vault: %s", secret_path)
if version:
    logger.debug("Requesting specific version: %s", version)

# Get valid token (will authenticate if needed)
token = self._get_token()

# Build URL
secret_url = f"{self.vault_addr}/v1/{secret_path}"
headers = {"X-Vault-Token": token}
params = {"version": version} if version else None

try:
    # Fetch the secret
    resp = requests.get(
        secret_url,
        headers=headers,
        params=params,
        timeout=self.timeout
    )
except requests.RequestException as e:
    logger.error("Network error fetching secret %s: %s", secret_path, e)
    raise VaultError(f"Failed to connect to Vault: {e}") from e

# Check response
if not resp.ok:
    logger.error(
        "Failed to fetch secret %s (status %s): %s",
        secret_path,
        resp.status_code,
        resp.text
    )
    raise VaultError(f"Vault secret fetch failed: {resp.text}")

# Parse response (handle both KV v1 and v2)
data = resp.json()

if "data" in data and "data" in data["data"]:
    # KV v2 format
    secret_data = data["data"]["data"]
    logger.debug("Successfully fetched KV v2 secret: %s", secret_path)
elif "data" in data:
    # KV v1 format
    secret_data = data["data"]
    logger.debug("Successfully fetched KV v1 secret: %s", secret_path)
else:
    logger.error(
        "Unexpected response format for secret %s: %s",
        secret_path,
        list(data.keys())
    )
    raise VaultError("Secret data not found in Vault response")

# Cache the secret
if use_cache:
    self._secret_cache[cache_key] = secret_data
    logger.debug("Cached secret: %s", cache_key)

return secret_data
```

**Flow Diagram:**

```
get_secret("secret/data/myapp")
    ↓
Check cache → Found? → Return cached data
    ↓ Not found
Get authentication token
    ↓
Build request URL
    ↓
Send GET request with token
    ↓
Receive response
    ↓
Parse JSON response
    ↓
Extract secret data
    ↓
Cache for next time
    ↓
Return secret data
```

---

## Usage Examples

### Example 1: Basic Usage

```python
from gds_vault.vault import VaultClient

# Create client
client = VaultClient(
    vault_addr="https://vault.example.com:8200",
    role_id="my-app-role",
    secret_id="my-app-secret"
)

# Get a secret
secret = client.get_secret("secret/data/database")

# Use the secret
db_password = secret["password"]
db_username = secret["username"]

print(f"Connecting to database as {db_username}")
```

### Example 2: Using Environment Variables

```bash
# Set environment variables
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_ROLE_ID="my-app-role"
export VAULT_SECRET_ID="my-app-secret"
```

```python
from gds_vault.vault import VaultClient

# Client automatically reads from environment
client = VaultClient()

# Get secret
secret = client.get_secret("secret/data/api-keys")
api_key = secret["api_key"]
```

### Example 3: Using Context Manager

```python
from gds_vault.vault import VaultClient

with VaultClient() as client:
    # Get multiple secrets
    db_secret = client.get_secret("secret/data/database")
    api_secret = client.get_secret("secret/data/api")

    # Use secrets
    connect_to_db(db_secret["password"])
    call_api(api_secret["api_key"])

# Automatically cleans up when done
```

### Example 4: Simple Function (No Class)

```python
from gds_vault.vault import get_secret_from_vault

# One-line secret retrieval
secret = get_secret_from_vault("secret/data/myapp")
password = secret["password"]
```

---

## Common Patterns

### Pattern 1: Retry on Failure

The module automatically retries failed operations:

```python
# This will retry up to 3 times if network fails
client = VaultClient()
secret = client.get_secret("secret/data/myapp")  # Automatic retry!
```

### Pattern 2: Token Caching

Tokens are cached to avoid re-authenticating:

```python
client = VaultClient()

# First call: Authenticates with Vault
secret1 = client.get_secret("secret/data/app1")

# Second call: Reuses token (no re-authentication!)
secret2 = client.get_secret("secret/data/app2")
```

### Pattern 3: Secret Caching

Secrets are cached to avoid repeated fetches:

```python
client = VaultClient()

# First call: Fetches from Vault
secret = client.get_secret("secret/data/myapp")

# Second call: Returns cached version (instant!)
secret_again = client.get_secret("secret/data/myapp")

# Force fresh fetch
secret_fresh = client.get_secret("secret/data/myapp", use_cache=False)
```

### Pattern 4: Error Handling

```python
from gds_vault.vault import VaultClient, VaultError

try:
    client = VaultClient()
    secret = client.get_secret("secret/data/myapp")
except VaultError as e:
    print(f"Vault error: {e}")
    # Handle error (use default values, exit, etc.)
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Troubleshooting

### Error: "Vault address must be provided"

**Problem:** VaultClient can't find the Vault server address.

**Solution:**
```python
# Option 1: Pass directly
client = VaultClient(vault_addr="https://vault.example.com:8200")

# Option 2: Set environment variable
export VAULT_ADDR="https://vault.example.com:8200"
```

### Error: "VAULT_ROLE_ID and VAULT_SECRET_ID must be provided"

**Problem:** Missing authentication credentials.

**Solution:**
```bash
export VAULT_ROLE_ID="your-role-id"
export VAULT_SECRET_ID="your-secret-id"
```

### Error: "Failed to connect to Vault"

**Problem:** Network issues or Vault is down.

**Solutions:**
1. Check network connectivity
2. Verify Vault URL is correct
3. Check if Vault server is running
4. Check firewall rules

### Error: "Vault AppRole login failed"

**Problem:** Invalid credentials.

**Solutions:**
1. Verify role_id is correct
2. Verify secret_id is correct
3. Check if AppRole is enabled in Vault
4. Verify permissions

### Slow Performance

**Problem:** Too many Vault requests.

**Solutions:**
1. Use caching (enabled by default)
2. Reuse VaultClient instance
3. Batch secret retrievals together

---

## Key Takeaways

1. **VaultClient** manages secure access to secrets
2. **Automatic retry** handles temporary failures
3. **Caching** improves performance
4. **Logging** helps debug issues
5. **Context managers** ensure cleanup
6. **Environment variables** keep config flexible

---

## Practice Exercise

Try creating a script that:
1. Connects to Vault using environment variables
2. Retrieves a database secret
3. Handles errors gracefully
4. Logs all operations

```python
import logging
from gds_vault.vault import VaultClient, VaultError

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_database_credentials():
    """Retrieve database credentials from Vault."""
    try:
        # Your code here
        pass
    except VaultError as e:
        # Your error handling here
        pass

if __name__ == "__main__":
    get_database_credentials()
```

---

## Next Tutorial

Ready to learn about Snowflake connections? Continue to:
**[Connection Module Tutorial](03_CONNECTION_MODULE_TUTORIAL.md)**

---

## Additional Resources

- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [Vault AppRole Auth Method](https://www.vaultproject.io/docs/auth/approle)
- [Python Requests Library](https://requests.readthedocs.io/)
