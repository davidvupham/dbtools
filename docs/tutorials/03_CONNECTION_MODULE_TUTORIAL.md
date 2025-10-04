# Connection Module Tutorial - Beginner's Guide

## Understanding Snowflake Database Connections

This tutorial explains the `gds_snowflake.connection` module, which manages connections to Snowflake databases securely using Vault for credential storage.

---

## Table of Contents

1. [What is Snowflake?](#what-is-snowflake)
2. [Module Overview](#module-overview)
3. [The SnowflakeConnection Class](#the-snowflakeconnection-class)
4. [Authentication Methods](#authentication-methods)
5. [Step-by-Step Code Walkthrough](#step-by-step-code-walkthrough)
6. [Usage Examples](#usage-examples)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## What is Snowflake?

### Snowflake is a Cloud Data Warehouse

Think of Snowflake as a massive spreadsheet in the cloud that can:
- Store huge amounts of data
- Run complex queries very fast
- Scale automatically
- Share data securely

### Why Do We Need a Connection Module?

To access Snowflake, we need to:
1. **Authenticate** (prove who we are)
2. **Connect** (establish a connection)
3. **Execute queries** (get data)
4. **Handle errors** (deal with problems)

This module handles all of that!

---

## Module Overview

### File: `gds_snowflake/connection.py`

This file contains the `SnowflakeConnection` class that:
- Connects to Snowflake using RSA key authentication
- Retrieves credentials from Vault
- Tests connectivity
- Executes queries
- Manages connections

### Key Dependencies

```python
import snowflake.connector  # Official Snowflake Python driver
from gds_vault.vault import get_secret_from_vault  # Get credentials
```

---

## The SnowflakeConnection Class

### What Does It Do?

SnowflakeConnection is like a bridge between your application and Snowflake:

```
Your App → SnowflakeConnection → Vault (get key) → Snowflake (connect)
```

### Basic Structure

```python
class SnowflakeConnection:
    """
    Manages Snowflake database connections using RSA key pair
    authentication.
    """
    
    def __init__(self, account, user=None, ...):
        """Initialize connection parameters."""
        
    def connect(self):
        """Establish connection to Snowflake."""
        
    def execute_query(self, query):
        """Run a SQL query."""
        
    def close(self):
        """Close the connection."""
```

---

## Authentication Methods

### RSA Key Pair Authentication

This module uses RSA key pair authentication (more secure than passwords):

```
┌─────────────┐         ┌─────────┐         ┌───────────┐
│  Your App   │  ────>  │  Vault  │  ────>  │ Snowflake │
└─────────────┘         └─────────┘         └───────────┘
      │                       │                     │
      │  "Give me the key"   │                     │
      │ ──────────────────>  │                     │
      │                       │                     │
      │  Returns private key │                     │
      │ <──────────────────  │                     │
      │                       │                     │
      │  "Here's my signed token"                  │
      │ ───────────────────────────────────────>  │
      │                       │                     │
      │            "Access granted"                │
      │ <─────────────────────────────────────────│
```

**Benefits:**
- More secure than passwords
- Keys can be rotated
- No password in config files

---

## Step-by-Step Code Walkthrough

### Part 1: Initialization

```python
def __init__(
    self,
    account: str,
    user: Optional[str] = None,
    warehouse: Optional[str] = None,
    role: Optional[str] = None,
    database: Optional[str] = None,
    vault_namespace: Optional[str] = None,
    vault_secret_path: Optional[str] = None,
    vault_mount_point: Optional[str] = None,
    vault_role_id: Optional[str] = None,
    vault_secret_id: Optional[str] = None,
    vault_addr: Optional[str] = None,
):
```

**Parameters Explained:**

**Snowflake Parameters:**
- `account` → Your Snowflake account identifier (e.g., "xy12345.us-east-1")
- `user` → Snowflake username (optional, can come from env)
- `warehouse` → Virtual warehouse to use for queries
- `role` → User role for permissions
- `database` → Default database to use

**Vault Parameters:**
- `vault_addr` → Vault server URL
- `vault_namespace` → Vault namespace (for multi-tenancy)
- `vault_secret_path` → Where the RSA key is stored
- `vault_role_id` → Vault authentication role ID
- `vault_secret_id` → Vault authentication secret ID
- `vault_mount_point` → Vault mount point (default: "secret")

**The Code:**

```python
# Store Snowflake parameters
self.account = account
self.user = user or os.getenv("SNOWFLAKE_USER")
self.warehouse = warehouse
self.role = role
self.database = database

# Store Vault parameters (with defaults from environment)
self.vault_namespace = vault_namespace or os.getenv("VAULT_NAMESPACE")
self.vault_secret_path = vault_secret_path or os.getenv(
    "VAULT_SECRET_PATH",
    f"secret/data/{self.account}"
)
self.vault_mount_point = vault_mount_point or os.getenv(
    "VAULT_MOUNT_POINT",
    "secret"
)
self.vault_role_id = vault_role_id or os.getenv("VAULT_ROLE_ID")
self.vault_secret_id = vault_secret_id or os.getenv("VAULT_SECRET_ID")
self.vault_addr = vault_addr or os.getenv("VAULT_ADDR")

# Connection object (starts as None)
self.connection = None

logger.info("SnowflakeConnection initialized for account: %s", self.account)
```

**Key Concepts:**

1. **Flexible Configuration**: Parameters can come from:
   - Direct arguments
   - Environment variables
   - Default values

2. **`or` operator chains**: 
   ```python
   user or os.getenv("SNOWFLAKE_USER")
   ```
   - If `user` is provided, use it
   - Otherwise, get from environment variable

3. **Default path construction**:
   ```python
   f"secret/data/{self.account}"
   ```
   - Creates a default Vault path based on account name

---

### Part 2: Fetching Credentials from Vault

```python
def _get_private_key_from_vault(self) -> str:
    """
    Fetch the RSA private key from Vault.
    
    Returns:
        str: PEM-encoded RSA private key
        
    Raises:
        Exception: If unable to retrieve the key
    """
    logger.info("Fetching private key from Vault: %s", self.vault_secret_path)
    
    try:
        # Get secret from Vault
        secret_data = get_secret_from_vault(
            secret_path=self.vault_secret_path,
            vault_addr=self.vault_addr
        )
        
        # Extract the private key
        private_key_pem = secret_data.get("private_key")
        
        if not private_key_pem:
            raise Exception(
                f"Private key not found in Vault secret at {self.vault_secret_path}"
            )
        
        logger.debug("Successfully retrieved private key from Vault")
        return private_key_pem
        
    except Exception as e:
        logger.error("Failed to retrieve private key from Vault: %s", str(e))
        raise Exception(f"Unable to get private key from Vault: {e}")
```

**Step-by-Step:**

1. **Log the attempt**: Track what's happening

2. **Call Vault function**: 
   ```python
   secret_data = get_secret_from_vault(secret_path, vault_addr)
   ```

3. **Extract the key**:
   ```python
   private_key_pem = secret_data.get("private_key")
   ```
   - The secret is a dictionary
   - We want the "private_key" field

4. **Validate**: Check that the key exists

5. **Error handling**: Catch and log any problems

**Example Secret in Vault:**

```json
{
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvg...\n-----END PRIVATE KEY-----",
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIj...\n-----END PUBLIC KEY-----",
  "user": "snowflake_user"
}
```

---

### Part 3: Connecting to Snowflake

```python
def connect(self):
    """
    Establish a connection to Snowflake using RSA key pair authentication.
    
    Returns:
        snowflake.connector.connection.SnowflakeConnection: Active connection
        
    Raises:
        Exception: If connection fails
    """
    logger.info("Connecting to Snowflake account: %s", self.account)
    
    try:
        # Get the private key from Vault
        private_key_pem = self._get_private_key_from_vault()
        
        # Parse the PEM-encoded key
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization
        
        p_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        
        # Convert to DER format (required by Snowflake connector)
        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Build connection parameters
        connection_params = {
            "account": self.account,
            "user": self.user,
            "private_key": pkb,
        }
        
        # Add optional parameters
        if self.warehouse:
            connection_params["warehouse"] = self.warehouse
        if self.role:
            connection_params["role"] = self.role
        if self.database:
            connection_params["database"] = self.database
        
        # Establish connection
        logger.debug("Attempting Snowflake connection with parameters: %s", 
                    {k: v for k, v in connection_params.items() if k != "private_key"})
        
        self.connection = snowflake.connector.connect(**connection_params)
        
        logger.info("Successfully connected to Snowflake account: %s", self.account)
        return self.connection
        
    except Exception as e:
        logger.error("Failed to connect to Snowflake: %s", str(e))
        raise Exception(f"Snowflake connection failed: {e}")
```

**Step-by-Step Breakdown:**

1. **Get private key from Vault**:
   ```python
   private_key_pem = self._get_private_key_from_vault()
   ```

2. **Parse the PEM format**:
   - PEM is a text format for keys (starts with "-----BEGIN PRIVATE KEY-----")
   - We need to convert it to a Python key object

3. **Convert to DER format**:
   - Snowflake requires DER format (binary)
   - Convert using cryptography library

4. **Build connection parameters**:
   ```python
   connection_params = {
       "account": self.account,
       "user": self.user,
       "private_key": pkb,  # DER format key
   }
   ```

5. **Add optional parameters**: If provided

6. **Connect**:
   ```python
   self.connection = snowflake.connector.connect(**connection_params)
   ```
   - `**connection_params` unpacks the dictionary into keyword arguments

7. **Return connection**: Ready to use!

---

### Part 4: Testing Connectivity

```python
def test_connectivity(self, timeout: int = 30) -> Dict[str, Any]:
    """
    Test connectivity to Snowflake with detailed diagnostics.
    
    Args:
        timeout: Maximum time to wait for connection (seconds)
        
    Returns:
        dict: Test results with success status and details
    """
    import time
    from datetime import datetime
    
    result = {
        'success': False,
        'account': self.account,
        'user': self.user,
        'timestamp': datetime.now().isoformat(),
        'account_info': {},
        'error': None
    }
    
    test_connection = None
    start_time = time.time()
    
    try:
        # Create a test connection
        logger.info("Testing connectivity to Snowflake account: %s", self.account)
        
        private_key_pem = self._get_private_key_from_vault()
        
        # Parse and convert key
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization
        
        p_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        
        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Connect with timeout
        connection_params = {
            "account": self.account,
            "user": self.user,
            "private_key": pkb,
            "login_timeout": timeout,
            "network_timeout": timeout,
        }
        
        if self.warehouse:
            connection_params["warehouse"] = self.warehouse
        if self.role:
            connection_params["role"] = self.role
        
        test_connection = snowflake.connector.connect(**connection_params)
        
        # Run a simple test query
        cursor = test_connection.cursor()
        cursor.execute("SELECT CURRENT_VERSION(), CURRENT_ACCOUNT(), CURRENT_USER()")
        row = cursor.fetchone()
        cursor.close()
        
        # Store account information
        result['account_info'] = {
            'version': row[0],
            'account_name': row[1],
            'user': row[2]
        }
        
        result['success'] = True
        
        end_time = time.time()
        result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
        
        logger.info(
            "Connectivity test successful for %s (response time: %sms)",
            self.account,
            result['response_time_ms']
        )
        
    except Exception as e:
        end_time = time.time()
        result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
        result['error'] = str(e)
        logger.error(
            "Connectivity test failed for %s: %s (response time: %sms)",
            self.account,
            str(e),
            result['response_time_ms']
        )
    finally:
        # Clean up test connection
        if test_connection and not test_connection.is_closed():
            try:
                test_connection.close()
                logger.info("Closed connection to Snowflake account: %s", self.account)
            except Exception as e:
                logger.warning("Error closing test connection: %s", str(e))
    
    return result
```

**What This Does:**

1. **Creates a test result dictionary**: Stores all test information

2. **Times the operation**: Measures how long it takes

3. **Connects to Snowflake**: Just like `connect()` but with timeout

4. **Runs a test query**:
   ```sql
   SELECT CURRENT_VERSION(), CURRENT_ACCOUNT(), CURRENT_USER()
   ```
   - Gets Snowflake version
   - Gets account name
   - Gets current user

5. **Records results**: Success/failure, timing, account info

6. **Cleans up**: Always closes test connection (in `finally` block)

**Example Result:**

```python
{
    'success': True,
    'account': 'xy12345.us-east-1',
    'user': 'snowflake_admin',
    'timestamp': '2025-10-04T10:30:00',
    'response_time_ms': 1523.45,
    'account_info': {
        'version': '7.14.0',
        'account_name': 'MY_ACCOUNT',
        'user': 'SNOWFLAKE_ADMIN'
    },
    'error': None
}
```

---

### Part 5: Executing Queries

```python
def execute_query(
    self,
    query: str,
    params: Optional[tuple] = None
) -> list:
    """
    Execute a SQL query and return results.
    
    Args:
        query: SQL query to execute
        params: Optional query parameters for parameterized queries
        
    Returns:
        list: Query results as list of tuples
    """
    if not self.connection or self.connection.is_closed():
        logger.warning("No active connection, connecting now...")
        self.connect()
    
    logger.debug("Executing query: %s", query[:100])  # Log first 100 chars
    
    try:
        cursor = self.connection.cursor()
        
        # Execute with or without parameters
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        cursor.close()
        
        logger.info("Query executed successfully, returned %s rows", len(results))
        return results
        
    except Exception as e:
        logger.error("Query execution failed: %s", str(e))
        raise
```

**How It Works:**

1. **Check connection**: Make sure we're connected

2. **Create cursor**: A cursor executes queries

3. **Execute query**:
   - With parameters (safe from SQL injection): `cursor.execute(query, params)`
   - Without parameters: `cursor.execute(query)`

4. **Fetch results**: Get all rows

5. **Close cursor**: Clean up

6. **Return results**: List of tuples

**Example Usage:**

```python
# Simple query
results = conn.execute_query("SELECT * FROM users LIMIT 10")
for row in results:
    print(row)

# Parameterized query (safe!)
results = conn.execute_query(
    "SELECT * FROM users WHERE age > %s",
    (25,)  # Tuple of parameters
)
```

---

## Usage Examples

### Example 1: Basic Connection

```python
from gds_snowflake import SnowflakeConnection

# Create connection
conn = SnowflakeConnection(
    account="xy12345.us-east-1",
    user="my_user",
    warehouse="COMPUTE_WH",
    role="ACCOUNTADMIN"
)

# Connect
conn.connect()

# Run query
results = conn.execute_query("SELECT CURRENT_VERSION()")
print(results)

# Close when done
conn.close()
```

### Example 2: Using Environment Variables

```bash
# Set environment variables
export SNOWFLAKE_USER="my_user"
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_ROLE_ID="app-role-id"
export VAULT_SECRET_ID="app-secret-id"
```

```python
from gds_snowflake import SnowflakeConnection

# Connection reads from environment
conn = SnowflakeConnection(account="xy12345.us-east-1")
conn.connect()

# Use connection
results = conn.execute_query("SELECT COUNT(*) FROM my_table")
print(f"Total rows: {results[0][0]}")

conn.close()
```

### Example 3: Testing Connectivity

```python
from gds_snowflake import SnowflakeConnection

conn = SnowflakeConnection(account="xy12345.us-east-1")

# Test before doing real work
test_result = conn.test_connectivity(timeout=30)

if test_result['success']:
    print(f"✓ Connected successfully!")
    print(f"  Account: {test_result['account_info']['account_name']}")
    print(f"  User: {test_result['account_info']['user']}")
    print(f"  Response time: {test_result['response_time_ms']}ms")
else:
    print(f"✗ Connection failed: {test_result['error']}")
```

### Example 4: Context Manager Pattern

```python
from gds_snowflake import SnowflakeConnection

# Automatically closes connection when done
conn = SnowflakeConnection(account="xy12345.us-east-1")
conn.connect()

try:
    # Do work
    results = conn.execute_query("SELECT * FROM my_table")
    process_results(results)
finally:
    # Always close
    conn.close()
```

### Example 5: Dictionary Results

```python
from gds_snowflake import SnowflakeConnection

conn = SnowflakeConnection(account="xy12345.us-east-1")
conn.connect()

# Get results as list of dictionaries
results = conn.execute_query_dict("SELECT id, name, email FROM users LIMIT 5")

for row in results:
    print(f"User: {row['NAME']} ({row['EMAIL']})")
    # Note: Column names are uppercase in Snowflake!

conn.close()
```

---

## Common Patterns

### Pattern 1: Connection Pooling

```python
# Create connection once, reuse many times
conn = SnowflakeConnection(account="xy12345.us-east-1")
conn.connect()

# Run multiple queries
users = conn.execute_query("SELECT * FROM users")
orders = conn.execute_query("SELECT * FROM orders")
products = conn.execute_query("SELECT * FROM products")

# Close when all done
conn.close()
```

### Pattern 2: Error Handling

```python
from gds_snowflake import SnowflakeConnection

conn = SnowflakeConnection(account="xy12345.us-east-1")

try:
    conn.connect()
    results = conn.execute_query("SELECT * FROM my_table")
except Exception as e:
    print(f"Error: {e}")
    # Handle error (retry, alert, etc.)
finally:
    if conn.connection:
        conn.close()
```

### Pattern 3: Safe Query Parameters

```python
# BAD - Vulnerable to SQL injection!
user_id = "123 OR 1=1"  # Malicious input
query = f"SELECT * FROM users WHERE id = {user_id}"
results = conn.execute_query(query)  # DANGEROUS!

# GOOD - Use parameterized queries
user_id = "123 OR 1=1"
query = "SELECT * FROM users WHERE id = %s"
results = conn.execute_query(query, (user_id,))  # SAFE!
```

### Pattern 4: Account Switching

```python
# Connect to primary account
primary_conn = SnowflakeConnection(account="primary-account")
primary_conn.connect()

# Do work...
data = primary_conn.execute_query("SELECT * FROM source_table")

# Switch to secondary account
secondary_conn = SnowflakeConnection(account="secondary-account")
secondary_conn.connect()

# Use both connections
secondary_conn.execute_query("INSERT INTO target_table VALUES ...")

# Close both
primary_conn.close()
secondary_conn.close()
```

---

## Troubleshooting

### Error: "Private key not found in Vault"

**Problem:** The secret doesn't contain "private_key" field.

**Solution:** Check Vault secret format:
```bash
vault kv get secret/data/your-account
```

Should contain:
```json
{
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "user": "snowflake_user"
}
```

### Error: "Unable to get private key from Vault"

**Problem:** Vault connection failed.

**Solutions:**
1. Check `VAULT_ADDR` environment variable
2. Verify `VAULT_ROLE_ID` and `VAULT_SECRET_ID`
3. Check network connectivity to Vault
4. Verify Vault permissions

### Error: "Snowflake connection failed"

**Problem:** Can't connect to Snowflake.

**Solutions:**
1. Verify account identifier is correct
2. Check user has proper permissions
3. Verify private key matches public key in Snowflake
4. Check network connectivity
5. Verify warehouse exists and is accessible

### Error: "Programming Error: SQL compilation error"

**Problem:** Invalid SQL query.

**Solutions:**
1. Check SQL syntax
2. Verify table/column names exist
3. Check permissions on objects
4. Test query in Snowflake UI first

### Slow Query Performance

**Problem:** Queries take too long.

**Solutions:**
1. Use appropriate warehouse size
2. Add WHERE clauses to filter data
3. Create appropriate indexes
4. Check query execution plan
5. Consider result caching

---

## Key Takeaways

1. **SnowflakeConnection** manages secure database connections
2. **RSA key authentication** is more secure than passwords
3. **Vault integration** keeps credentials secure
4. **Parameterized queries** prevent SQL injection
5. **Error handling** is essential for production code
6. **Connection pooling** improves performance

---

## Practice Exercise

Create a script that:
1. Connects to Snowflake
2. Tests connectivity
3. Runs a query
4. Handles errors
5. Logs everything

```python
import logging
from gds_snowflake import SnowflakeConnection

logging.basicConfig(level=logging.INFO)

def main():
    """Connect to Snowflake and run a test query."""
    conn = None
    try:
        # Your code here
        pass
    except Exception as e:
        # Your error handling here
        pass
    finally:
        # Your cleanup here
        pass

if __name__ == "__main__":
    main()
```

---

## Next Tutorial

Ready to learn about replication monitoring? Continue to:
**[Replication Module Tutorial](04_REPLICATION_MODULE_TUTORIAL.md)**

---

## Additional Resources

- [Snowflake Python Connector](https://docs.snowflake.com/en/user-guide/python-connector.html)
- [Snowflake Key Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth.html)
- [RSA Encryption Explained](https://simple.wikipedia.org/wiki/RSA_algorithm)
