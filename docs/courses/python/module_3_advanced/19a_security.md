# Security Best Practices

Security is not an afterthought—it must be built into your code from the start. This chapter covers essential security practices for Python developers, focusing on common vulnerabilities and how to prevent them.

## Why security matters

A single security vulnerability can:
- Expose sensitive user data (GDPR fines up to 4% of global revenue)
- Allow attackers to take control of your systems
- Damage your organization's reputation
- Result in legal liability

**The OWASP Top 10** lists the most critical web application security risks. Python developers commonly encounter:
1. Injection (SQL, command, etc.)
2. Broken authentication
3. Sensitive data exposure
4. Security misconfiguration
5. Insecure deserialization

## Input validation

Never trust user input. All external data must be validated before use.

### Allowlist validation

Validate against known good values (allowlist), not known bad values (blocklist):

```python
# BAD - Blocklist approach (easy to bypass)
def validate_username_bad(username: str) -> bool:
    dangerous_chars = ["<", ">", "'", '"', ";", "--"]
    for char in dangerous_chars:
        if char in username:
            return False
    return True

# GOOD - Allowlist approach
import re

def validate_username_good(username: str) -> bool:
    """Username must be 3-20 alphanumeric characters."""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

# Even better - Use a validation library
from pydantic import BaseModel, Field, field_validator

class UserInput(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
```

### Type coercion

Explicitly convert input to expected types:

```python
# BAD - Using string input directly
def get_user(user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD - Convert to int first
def get_user(user_id: str) -> dict:
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise ValueError("Invalid user ID")

    if user_id_int <= 0:
        raise ValueError("User ID must be positive")

    return db.query("SELECT * FROM users WHERE id = ?", (user_id_int,))
```

### Validate at boundaries

Validate input as early as possible, at system boundaries:

```mermaid
flowchart LR
    A[User Input] --> B[Validation Layer]
    B --> C{Valid?}
    C -->|Yes| D[Application Logic]
    C -->|No| E[Reject with Error]
    D --> F[Database/External Services]
```

## SQL injection prevention

SQL injection occurs when user input is incorporated into SQL queries without proper escaping.

### The vulnerability

```python
# VULNERABLE - String concatenation
def get_user_vulnerable(username: str):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# Attack: username = "' OR '1'='1"
# Query becomes: SELECT * FROM users WHERE username = '' OR '1'='1'
# Returns ALL users!

# Attack: username = "'; DROP TABLE users; --"
# Query becomes: SELECT * FROM users WHERE username = ''; DROP TABLE users; --'
# Deletes the entire table!
```

### Parameterized queries

Always use parameterized queries (prepared statements):

```python
import sqlite3

# SAFE - Parameterized query with sqlite3
def get_user_safe(username: str) -> dict | None:
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    # ? is the parameter placeholder for sqlite3
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)  # Parameters as tuple
    )

    return cursor.fetchone()

# SAFE - With psycopg (PostgreSQL)
import psycopg

def get_user_postgres(username: str) -> dict | None:
    with psycopg.connect("dbname=app") as conn:
        with conn.cursor() as cur:
            # %s is the placeholder for psycopg
            cur.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            return cur.fetchone()

# SAFE - With SQLAlchemy ORM
from sqlalchemy import select
from models import User

def get_user_sqlalchemy(session, username: str) -> User | None:
    # ORM queries are automatically parameterized
    stmt = select(User).where(User.username == username)
    return session.execute(stmt).scalar_one_or_none()
```

### Dynamic queries safely

When you need dynamic column or table names (which can't be parameterized):

```python
# DANGEROUS - Dynamic column names from user input
def sort_users(sort_column: str):
    query = f"SELECT * FROM users ORDER BY {sort_column}"  # SQL injection!
    return db.execute(query)

# SAFE - Allowlist valid column names
VALID_SORT_COLUMNS = {'username', 'email', 'created_at'}

def sort_users_safe(sort_column: str):
    if sort_column not in VALID_SORT_COLUMNS:
        raise ValueError(f"Invalid sort column: {sort_column}")

    query = f"SELECT * FROM users ORDER BY {sort_column}"
    return db.execute(query)
```

## Command injection prevention

Never pass user input directly to shell commands.

### The vulnerability

```python
import os
import subprocess

# VULNERABLE - Shell injection
def ping_host_vulnerable(hostname: str) -> str:
    return os.popen(f"ping -c 1 {hostname}").read()

# Attack: hostname = "google.com; cat /etc/passwd"
# Executes: ping -c 1 google.com; cat /etc/passwd
```

### Safe alternatives

```python
import subprocess
import shlex

# SAFE - Use subprocess with list arguments (no shell)
def ping_host_safe(hostname: str) -> str:
    # Validate hostname format
    import re
    if not re.match(r'^[a-zA-Z0-9.-]+$', hostname):
        raise ValueError("Invalid hostname")

    result = subprocess.run(
        ['ping', '-c', '1', hostname],  # List, not string
        capture_output=True,
        text=True,
        timeout=10
    )
    return result.stdout

# If you MUST use shell=True, escape properly
def run_command_escaped(user_input: str) -> str:
    # shlex.quote escapes the input for shell
    safe_input = shlex.quote(user_input)
    result = subprocess.run(
        f"echo {safe_input}",
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout
```

## Path traversal prevention

Prevent attackers from accessing files outside intended directories.

### The vulnerability

```python
# VULNERABLE - Path traversal
def read_file_vulnerable(filename: str) -> str:
    with open(f"/app/uploads/{filename}") as f:
        return f.read()

# Attack: filename = "../../../etc/passwd"
# Reads: /app/uploads/../../../etc/passwd = /etc/passwd
```

### Safe file handling

```python
from pathlib import Path
import os

UPLOAD_DIR = Path("/app/uploads").resolve()

def read_file_safe(filename: str) -> str:
    # Construct the full path
    requested_path = (UPLOAD_DIR / filename).resolve()

    # Verify it's still within the allowed directory
    if not requested_path.is_relative_to(UPLOAD_DIR):
        raise ValueError("Access denied: path traversal detected")

    if not requested_path.is_file():
        raise FileNotFoundError(f"File not found: {filename}")

    with open(requested_path) as f:
        return f.read()

# Even safer - use a whitelist of allowed files
ALLOWED_FILES = {'report.pdf', 'summary.txt', 'data.csv'}

def read_allowed_file(filename: str) -> str:
    if filename not in ALLOWED_FILES:
        raise ValueError(f"File not allowed: {filename}")

    filepath = UPLOAD_DIR / filename
    with open(filepath) as f:
        return f.read()
```

## Secrets management

Never hardcode secrets in your code.

### What NOT to do

```python
# NEVER DO THIS
API_KEY = "sk-1234567890abcdef"  # Hardcoded secret!
DATABASE_URL = "postgres://user:password@localhost/db"  # Credentials in code!

# NEVER commit .env files with real secrets
# NEVER log secrets
print(f"Connecting with key: {api_key}")  # Secret in logs!
```

### Environment variables

```python
import os

# Load from environment variables
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable not set")

# Or use python-dotenv for development
from dotenv import load_dotenv

load_dotenv()  # Loads from .env file
API_KEY = os.getenv("API_KEY")
```

### Secret managers

For production, use a dedicated secret manager:

```python
# HashiCorp Vault (using hvac library)
import hvac

def get_secret_from_vault(path: str) -> dict:
    client = hvac.Client(url=os.environ["VAULT_ADDR"])
    client.token = os.environ["VAULT_TOKEN"]

    secret = client.secrets.kv.v2.read_secret_version(path=path)
    return secret["data"]["data"]

# AWS Secrets Manager
import boto3

def get_secret_from_aws(secret_name: str) -> str:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return response["SecretString"]

# Azure Key Vault
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_secret_from_azure(vault_url: str, secret_name: str) -> str:
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    return client.get_secret(secret_name).value
```

### .gitignore essentials

```gitignore
# Never commit these
.env
.env.local
.env.*.local
*.pem
*.key
credentials.json
secrets.yaml
config/local.py
```

## Password handling

Never store passwords in plain text.

### Hashing passwords

```python
# Use bcrypt or argon2
import bcrypt

def hash_password(password: str) -> bytes:
    """Hash a password for storage."""
    salt = bcrypt.gensalt(rounds=12)  # Work factor of 12
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password: str, hashed: bytes) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Usage
hashed = hash_password("user_password")
# Store 'hashed' in database

# Later, verify
if verify_password("user_password", hashed):
    print("Password correct")
```

### Password requirements

```python
import re

def validate_password(password: str) -> tuple[bool, list[str]]:
    """Validate password meets security requirements."""
    errors = []

    if len(password) < 12:
        errors.append("Password must be at least 12 characters")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain uppercase letter")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain lowercase letter")

    if not re.search(r'\d', password):
        errors.append("Password must contain a digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain special character")

    return (len(errors) == 0, errors)
```

## Cryptography basics

Use established libraries, never implement your own crypto.

### Secure random numbers

```python
import secrets

# For tokens, passwords, etc.
token = secrets.token_hex(32)  # 64 character hex string
url_token = secrets.token_urlsafe(32)  # URL-safe base64

# For choosing from a list
choices = ['a', 'b', 'c', 'd']
secure_choice = secrets.choice(choices)

# For generating integers
secure_int = secrets.randbelow(100)  # 0-99

# DON'T use random module for security
import random
insecure_token = random.randint(0, 1000000)  # Predictable!
```

### Hashing data

```python
import hashlib

# For non-password data integrity
def hash_file(filepath: str) -> str:
    """Generate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

# Verify file integrity
expected_hash = "a1b2c3..."
actual_hash = hash_file("download.zip")
if actual_hash != expected_hash:
    raise ValueError("File integrity check failed")
```

### Encryption

```python
from cryptography.fernet import Fernet

# Generate a key (do this once, store securely)
key = Fernet.generate_key()

# Encrypt data
def encrypt_data(data: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data.encode('utf-8'))

# Decrypt data
def decrypt_data(encrypted: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted).decode('utf-8')

# Usage
encrypted = encrypt_data("sensitive information", key)
decrypted = decrypt_data(encrypted, key)
```

## Dependency security

Your dependencies can introduce vulnerabilities.

### Scanning for vulnerabilities

```bash
# pip-audit scans for known vulnerabilities
uv add --dev pip-audit
pip-audit

# Safety (alternative)
uv add --dev safety
safety check

# Bandit for static analysis
uv add --dev bandit
bandit -r src/
```

### Lock your dependencies

```bash
# Always use lockfiles for reproducible builds
uv lock

# Pin exact versions in production
# pyproject.toml
[project]
dependencies = [
    "requests==2.31.0",  # Exact version
    "pydantic>=2.0,<3.0",  # Version range
]
```

### Update regularly

```bash
# Check for updates
uv pip list --outdated

# Update with care (test after updating)
uv lock --upgrade-package requests
```

## Example from our code

The `gds_vault` package demonstrates secure secret handling:

```python
# python/gds_vault/src/gds_vault/client.py
import os
from functools import lru_cache

class VaultClient:
    """Secure client for HashiCorp Vault."""

    def __init__(self):
        self.vault_addr = os.environ.get("VAULT_ADDR")
        if not self.vault_addr:
            raise RuntimeError("VAULT_ADDR not configured")

        # Token from environment, never hardcoded
        self._token = os.environ.get("VAULT_TOKEN")

    @lru_cache(maxsize=100)
    def get_secret(self, path: str) -> dict:
        """Retrieve secret with caching."""
        # Validate path to prevent traversal
        if ".." in path or path.startswith("/"):
            raise ValueError("Invalid secret path")

        # Actual Vault API call...
        return self._fetch_from_vault(path)

    def _fetch_from_vault(self, path: str) -> dict:
        # Implementation uses parameterized requests
        pass
```

## Security checklist

**Input Handling**:
- [ ] All user input is validated (allowlist approach)
- [ ] Input types are explicitly converted
- [ ] Validation happens at system boundaries

**Database**:
- [ ] All queries use parameterized statements
- [ ] No string concatenation in SQL
- [ ] Database user has minimal required permissions

**Files & Commands**:
- [ ] File paths are validated against traversal
- [ ] Shell commands use subprocess with list arguments
- [ ] No user input in shell commands without validation

**Secrets**:
- [ ] No hardcoded credentials in code
- [ ] Secrets loaded from environment or secret manager
- [ ] .env files are gitignored
- [ ] Secrets are not logged

**Dependencies**:
- [ ] Dependencies are scanned for vulnerabilities
- [ ] Versions are locked
- [ ] Regular updates are applied

## Best practices summary

1. **Validate all input**: Use allowlists, not blocklists
2. **Parameterize queries**: Never concatenate SQL strings
3. **Avoid shell commands**: Use subprocess with list arguments
4. **Validate file paths**: Prevent path traversal attacks
5. **Never hardcode secrets**: Use environment variables or secret managers
6. **Hash passwords**: Use bcrypt or argon2, never plain text or MD5/SHA
7. **Use cryptography libraries**: Never implement your own crypto
8. **Scan dependencies**: Use pip-audit, safety, or bandit regularly
9. **Principle of least privilege**: Minimal permissions for all accounts
10. **Defense in depth**: Multiple layers of security controls

---

[← Back to Module 3](./README.md) | [Next: HTTP and Requests →](./19b_http_requests.md)
