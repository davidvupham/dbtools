# Complete Beginner's Guide to gds_vault
## Learn Python Through HashiCorp Vault Integration

Welcome! This guide will teach you everything about the `gds_vault` package, starting from zero knowledge and building up to understanding every line of code.

---

## Table of Contents

1. [What Problem Does This Package Solve?](#what-problem-does-this-package-solve)
2. [Understanding the Architecture](#understanding-the-architecture)
3. [Core Concepts Explained](#core-concepts-explained)
4. [Module-by-Module Deep Dive](#module-by-module-deep-dive)
5. [Complete Usage Examples](#complete-usage-examples)
6. [Python Concepts Used](#python-concepts-used)
7. [Design Patterns Explained](#design-patterns-explained)
8. [Exercises and Practice](#exercises-and-practice)

---

## What Problem Does This Package Solve?

### The Problem: Secret Management

Imagine you're building an application that needs to:
- Connect to a database (needs password)
- Call an API (needs API key)
- Send emails (needs SMTP credentials)

**Bad Approach (Don't do this!):**
```python
# ❌ NEVER store secrets in code!
DATABASE_PASSWORD = "super_secret_123"
API_KEY = "abc-xyz-789"
SMTP_PASSWORD = "email_pass_456"
```

**Problems with this:**
- 😱 Anyone who sees your code sees all passwords
- 🔓 Passwords are committed to version control (git history forever!)
- 🔄 Changing passwords means changing code and redeploying
- 📝 No audit trail of who accessed what

### The Solution: HashiCorp Vault

**Vault is like a secure safe for your secrets:**
- 🔒 All secrets encrypted at rest
- 🎫 Only authenticated applications can access
- 📊 Complete audit log of all access
- 🔄 Secrets can be rotated without code changes

**How gds_vault helps:**
```python
# ✅ Good approach with gds_vault
from gds_vault import VaultClient

client = VaultClient()
secrets = client.get_secret("secret/data/myapp")

# Now use the secrets
db_password = secrets["database_password"]
api_key = secrets["api_key"]
```

---

## Understanding the Architecture

### High-Level Overview

The `gds_vault` package is organized into modules, each with a specific responsibility:

```
gds_vault/
├── base.py          # Abstract base classes (interfaces)
├── auth.py          # Authentication strategies
├── cache.py         # Caching implementations
├── retry.py         # Retry logic
├── exceptions.py    # Custom error types
├── client.py        # Main VaultClient class
└── __init__.py      # Package exports
```

### How Components Work Together

```
┌─────────────────────────────────────────────────┐
│                  VaultClient                    │
│  (Main class - coordinates everything)          │
└───────────┬─────────────────────────────────────┘
            │
            ├─── Uses ──► AuthStrategy (auth.py)
            │              ├─ AppRoleAuth
            │              ├─ TokenAuth
            │              └─ EnvironmentAuth
            │
            ├─── Uses ──► Cache (cache.py)
            │              ├─ SecretCache
            │              ├─ TTLCache
            │              └─ NoOpCache
            │
            ├─── Uses ──► RetryPolicy (retry.py)
            │              └─ retry_with_backoff
            │
            └─── Raises ──► Exceptions (exceptions.py)
                           ├─ VaultAuthError
                           ├─ VaultConnectionError
                           ├─ VaultSecretNotFoundError
                           └─ VaultPermissionError
```

**Why this structure?**
- **Separation of Concerns**: Each module has one clear job
- **Testability**: Each component can be tested independently
- **Flexibility**: You can swap implementations (e.g., different cache types)
- **Maintainability**: Changes in one module don't affect others

---

## Core Concepts Explained

### 1. Abstract Base Classes (base.py)

**What is it?**
An abstract base class (ABC) defines a "contract" - it says "any class that inherits from me MUST implement these methods."

**Why use it?**
- Ensures consistency across different implementations
- Makes code self-documenting
- Enables polymorphism (different implementations, same interface)

**Real-world analogy:**
Think of a "Vehicle" ABC. It says "all vehicles MUST have start(), stop(), and accelerate() methods." Then:
- Car implements these methods (turn key, press brake, press gas pedal)
- Boat implements these methods (start motor, drop anchor, push throttle)
- Bicycle implements these methods (start pedaling, use brakes, pedal faster)

All are vehicles, but each implements the methods differently!

**In gds_vault:**

```python
# base.py
class SecretProvider(ABC):
    """Defines what ALL secret providers must do."""
    
    @abstractmethod
    def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
        """Every secret provider MUST implement this."""
        pass
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Every secret provider MUST implement this."""
        pass
```

Then `VaultClient` inherits from `SecretProvider`, so it MUST implement these methods:

```python
# client.py
class VaultClient(SecretProvider):
    """Concrete implementation of SecretProvider."""
    
    def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
        # Implementation for Vault
        ...
    
    def authenticate(self) -> bool:
        # Implementation for Vault
        ...
```

**Benefits:**
- If someone creates `ConsulClient(SecretProvider)`, they know exactly what methods to implement
- Code that uses `SecretProvider` works with ANY implementation
- IDE gives autocomplete for required methods

### 2. Strategy Pattern (auth.py)

**What is it?**
The Strategy pattern lets you swap out different algorithms (strategies) without changing the code that uses them.

**Real-world analogy:**
You need to get to work. You have multiple strategies:
- Drive your car
- Take the bus
- Ride your bike
- Walk

You choose a strategy based on weather, time, distance, etc. But regardless of which you choose, the result is the same: you get to work.

**In gds_vault:**

```python
# Define the interface
class AuthStrategy(ABC):
    @abstractmethod
    def authenticate(self, vault_addr: str, timeout: int) -> tuple[str, float]:
        """All auth strategies must implement this."""
        pass

# Strategy 1: AppRole Authentication
class AppRoleAuth(AuthStrategy):
    def authenticate(self, vault_addr: str, timeout: int) -> tuple[str, float]:
        # Use role_id and secret_id
        ...

# Strategy 2: Token Authentication
class TokenAuth(AuthStrategy):
    def authenticate(self, vault_addr: str, timeout: int) -> tuple[str, float]:
        # Use existing token
        ...

# Strategy 3: Environment Authentication
class EnvironmentAuth(AuthStrategy):
    def authenticate(self, vault_addr: str, timeout: int) -> tuple[str, float]:
        # Read from environment variables
        ...
```

**Using the strategy:**

```python
# VaultClient doesn't care WHICH strategy you use!
# It just calls authenticate() and gets a token back

# Production: Use AppRole
auth = AppRoleAuth(role_id="xxx", secret_id="yyy")
client = VaultClient(auth=auth)

# Development: Use Token
auth = TokenAuth(token="hvs.ABC123")
client = VaultClient(auth=auth)

# Quick testing: Use Environment
auth = EnvironmentAuth()
client = VaultClient(auth=auth)
```

**Benefits:**
- Easy to add new authentication methods without changing VaultClient
- Each strategy is tested independently
- Users choose the best strategy for their use case

### 3. Composition Over Inheritance

**What is it?**
Instead of inheriting functionality, you "compose" objects by including them as attributes.

**Bad approach (inheritance):**
```python
class VaultClientWithCache(VaultClient):
    # Now we have caching
    pass

class VaultClientWithRetry(VaultClient):
    # Now we have retry
    pass

# What if I want BOTH cache AND retry?
# Do I need VaultClientWithCacheAndRetry???
# This gets messy fast!
```

**Good approach (composition):**
```python
class VaultClient:
    def __init__(self, auth, cache, retry_policy):
        # Compose by including these objects
        self._auth = auth              # Has-a auth strategy
        self._cache = cache            # Has-a cache
        self._retry_policy = retry_policy  # Has-a retry policy
```

**Benefits:**
- Mix and match features easily
- Each component is independent
- More flexible than inheritance

**In gds_vault:**
```python
# Mix different components!
client = VaultClient(
    auth=AppRoleAuth(...),        # Choose auth
    cache=TTLCache(...),           # Choose cache
    retry_policy=RetryPolicy(...)  # Choose retry
)

# Or use different combinations
client = VaultClient(
    auth=TokenAuth(...),
    cache=NoOpCache(),             # Disable caching
    retry_policy=RetryPolicy(max_retries=5)
)
```

### 4. Properties (@property)

**What is it?**
Properties make methods look like attributes. They provide controlled access to private data.

**Why use them?**
- Add validation when setting values
- Compute values on-the-fly
- Make read-only attributes
- Keep API clean and Pythonic

**Example:**

```python
class Person:
    def __init__(self, name):
        self._name = name  # Private attribute
        self._age = 0
    
    @property
    def name(self):
        """Get name - looks like an attribute!"""
        return self._name
    
    @property
    def age(self):
        """Get age."""
        return self._age
    
    @age.setter
    def age(self, value):
        """Set age with validation."""
        if value < 0:
            raise ValueError("Age cannot be negative")
        self._age = value

# Usage
person = Person("Alice")
print(person.name)     # Call method, looks like attribute!
person.age = 30        # Call setter with validation
person.age = -5        # Raises ValueError!
```

**In gds_vault:**

```python
class VaultClient:
    def __init__(self, vault_addr, timeout=10):
        self._vault_addr = vault_addr
        self._timeout = timeout
        self._token = None
    
    @property
    def vault_addr(self) -> str:
        """Get Vault address (read-only)."""
        return self._vault_addr
    
    @property
    def timeout(self) -> int:
        """Get timeout."""
        return self._timeout
    
    @timeout.setter
    def timeout(self, value: int) -> None:
        """Set timeout with validation."""
        if value <= 0:
            raise ValueError("Timeout must be positive")
        self._timeout = value
    
    @property
    def is_authenticated(self) -> bool:
        """Check if authenticated (computed property)."""
        return self._token is not None

# Usage
client = VaultClient("https://vault.example.com")
print(client.vault_addr)    # Read-only
print(client.timeout)       # Read value
client.timeout = 30         # Set with validation
client.timeout = -5         # Raises ValueError!
print(client.is_authenticated)  # Computed from _token
```

### 5. Context Managers (with statement)

**What is it?**
Context managers ensure resources are properly cleaned up, even if errors occur.

**Real-world analogy:**
When you borrow a book from the library:
1. Check out the book (setup)
2. Read it (use the resource)
3. Return the book (cleanup)

Even if you never finish reading, you MUST return the book!

**Without context manager:**
```python
file = open("data.txt")
try:
    data = file.read()
    process(data)
finally:
    file.close()  # Must remember to close!
```

**With context manager:**
```python
with open("data.txt") as file:
    data = file.read()
    process(data)
# File automatically closed, even if exception occurs!
```

**In gds_vault:**

```python
class VaultClient:
    def __enter__(self):
        """Called when entering 'with' block."""
        self.initialize()  # Setup
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'with' block."""
        self.cleanup()  # Cleanup
        return False

# Usage
with VaultClient() as client:
    secret = client.get_secret("secret/data/myapp")
    # Use the secret
# Client automatically cleaned up!
```

**Benefits:**
- No resource leaks
- Cleaner code
- Exceptions handled properly

---

## Module-by-Module Deep Dive

### Module 1: exceptions.py

**Purpose:** Define custom exception types for precise error handling.

**Why we need it:**
- Different errors need different handling
- Clear error messages
- Better debugging

**The Exception Hierarchy:**

```python
Exception (Python built-in)
    └── VaultError (base for all our errors)
            ├── VaultAuthError (authentication failed)
            ├── VaultConnectionError (network issues)
            ├── VaultSecretNotFoundError (secret doesn't exist)
            ├── VaultPermissionError (access denied)
            ├── VaultConfigurationError (invalid config)
            └── VaultCacheError (cache issues)
```

**Complete Code with Explanation:**

```python
"""
Exception classes for gds_vault package.

This module defines a hierarchy of exceptions for different error scenarios,
enabling precise error handling and better debugging.
"""


class VaultError(Exception):
    """
    Base exception for all Vault-related errors.
    
    This is the parent class for all custom exceptions in the package,
    allowing users to catch all package-specific errors with a single handler.
    
    Example:
        try:
            client.get_secret("secret/data/myapp")
        except VaultError as e:
            logger.error(f"Vault operation failed: {e}")
    """
    pass


class VaultAuthError(VaultError):
    """
    Exception raised for authentication failures.
    
    Raised when:
    - AppRole credentials are invalid
    - Token has expired or is invalid
    - Authentication endpoint is unreachable
    
    Example:
        try:
            client.authenticate()
        except VaultAuthError as e:
            logger.error(f"Authentication failed: {e}")
            # Maybe retry with different credentials
    """
    pass


class VaultConnectionError(VaultError):
    """
    Exception raised for network/connection errors.
    
    Raised when:
    - Vault server is unreachable
    - Network timeout occurs
    - DNS resolution fails
    
    Example:
        try:
            client.get_secret("secret/data/myapp")
        except VaultConnectionError as e:
            logger.error(f"Cannot connect to Vault: {e}")
            # Maybe retry or use cached value
    """
    pass


class VaultSecretNotFoundError(VaultError):
    """
    Exception raised when a secret is not found.
    
    Raised when:
    - Secret path does not exist
    - Secret has been deleted
    - Wrong secret path specified
    
    Example:
        try:
            secret = client.get_secret("secret/data/nonexistent")
        except VaultSecretNotFoundError as e:
            logger.error(f"Secret not found: {e}")
            # Maybe use default values
    """
    pass


class VaultPermissionError(VaultError):
    """
    Exception raised for permission/authorization errors.
    
    Raised when:
    - Token lacks required permissions
    - Policy denies access to secret
    - Token has been revoked
    
    Example:
        try:
            client.get_secret("secret/data/restricted")
        except VaultPermissionError as e:
            logger.error(f"Permission denied: {e}")
            # Maybe request access or notify admin
    """
    pass


class VaultConfigurationError(VaultError):
    """
    Exception raised for configuration errors.
    
    Raised when:
    - Required environment variables missing
    - Invalid Vault address format
    - Invalid configuration parameters
    
    Example:
        try:
            client = VaultClient(vault_addr="invalid")
        except VaultConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            # Check environment variables
    """
    pass


class VaultCacheError(VaultError):
    """
    Exception raised for cache-related errors.
    
    Raised when:
    - Cache size exceeded
    - Invalid cache operation
    - Cache corruption detected
    
    Example:
        try:
            cache.set("key", "value")
        except VaultCacheError as e:
            logger.error(f"Cache error: {e}")
            # Maybe clear cache
    """
    pass
```

**Using these exceptions:**

```python
from gds_vault import VaultClient, VaultAuthError, VaultSecretNotFoundError

client = VaultClient()

# Specific error handling
try:
    secret = client.get_secret("secret/data/myapp")
except VaultAuthError:
    print("Authentication failed - check credentials")
except VaultSecretNotFoundError:
    print("Secret doesn't exist - using default values")
    secret = {"password": "default"}
except VaultError as e:
    print(f"Other Vault error: {e}")

# Or catch all Vault errors
try:
    secret = client.get_secret("secret/data/myapp")
except VaultError as e:
    print(f"Vault operation failed: {e}")
    # Handle any Vault-related error
```

**Benefits:**
1. **Precise Error Handling**: Different errors, different responses
2. **Better Debugging**: Error type tells you what went wrong
3. **Cleaner Code**: No need to parse error messages
4. **Self-Documenting**: Exception names explain the error

---

### Module 2: base.py

**Purpose:** Define abstract base classes (interfaces) that establish contracts for implementations.

**Why we need it:**
- Ensures all implementations have required methods
- Enables polymorphism (different implementations, same interface)
- Makes code self-documenting
- Helps catch errors at development time

**Complete Code with Detailed Explanation:**

```python
"""
Base classes and interfaces for the gds_vault package.

This module provides abstract base classes and protocols that define
the contracts for secret providers, authentication strategies, caching,
and retry mechanisms.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol


# ============================================================================
# PART 1: SecretProvider Interface
# ============================================================================

class SecretProvider(ABC):
    """
    Abstract base class for secret providers.
    
    This defines the interface that all secret provider implementations
    must follow, enabling polymorphic usage and easy testing with mocks.
    
    Think of this as a blueprint that says:
    "Any class that provides secrets MUST have these methods."
    
    Example:
        class MySecretProvider(SecretProvider):
            def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
                # Implementation
                pass
            
            def authenticate(self) -> bool:
                # Implementation
                pass
            
            def is_authenticated(self) -> bool:
                # Implementation
                pass
    """
    
    @abstractmethod
    def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
        """
        Retrieve a secret from the provider.
        
        Args:
            path: Path to the secret
            **kwargs: Additional provider-specific options
        
        Returns:
            dict: Secret data as key-value pairs
        
        Raises:
            Exception: If secret retrieval fails
        """
        pass
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the secret provider.
        
        Returns:
            bool: True if authentication successful, False otherwise
        
        Raises:
            Exception: If authentication fails
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated with valid credentials.
        
        Returns:
            bool: True if authenticated with valid credentials
        """
        pass


# ============================================================================
# PART 2: AuthStrategy Interface
# ============================================================================

class AuthStrategy(ABC):
    """
    Abstract base class for authentication strategies.
    
    This enables the Strategy pattern for different authentication methods
    (AppRole, Token, Kubernetes, etc.) without modifying the client code.
    
    Why use this pattern?
    - VaultClient doesn't need to know HOW authentication works
    - Easy to add new authentication methods
    - Each strategy is independent and testable
    
    Example:
        class AppRoleAuth(AuthStrategy):
            def __init__(self, role_id: str, secret_id: str):
                self.role_id = role_id
                self.secret_id = secret_id
            
            def authenticate(self, vault_addr: str, timeout: int) -> tuple[str, float]:
                # Implementation returns (token, expiry_time)
                pass
    """
    
    @abstractmethod
    def authenticate(self, vault_addr: str, timeout: int) -> tuple[str, float]:
        """
        Authenticate and return token with expiry.
        
        Args:
            vault_addr: Vault server address
            timeout: Request timeout in seconds
        
        Returns:
            tuple: (token, expiry_timestamp)
                - token: Authentication token string
                - expiry_timestamp: Unix timestamp when token expires
        
        Raises:
            Exception: If authentication fails
        """
        pass


# ============================================================================
# PART 3: CacheProtocol
# ============================================================================

class CacheProtocol(Protocol):
    """
    Protocol for cache implementations.
    
    This uses Python's structural subtyping (Protocol) to define
    what methods a cache must implement without requiring inheritance.
    
    Protocol vs ABC:
    - Protocol: "Duck typing" - if it has these methods, it's a cache
    - ABC: Explicit inheritance required
    
    Example:
        class MyCache:  # No inheritance needed!
            def get(self, key: str) -> Optional[dict]:
                ...
            
            def set(self, key: str, value: dict) -> None:
                ...
            
            # As long as it has the right methods, it's a valid cache!
    """
    
    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get cached value by key."""
        ...
    
    def set(self, key: str, value: dict[str, Any]) -> None:
        """Set cached value for key."""
        ...
    
    def clear(self) -> None:
        """Clear all cached values."""
        ...
    
    def __len__(self) -> int:
        """Return number of cached items."""
        ...
    
    def __contains__(self, key: str) -> bool:
        """Check if key is in cache."""
        ...


# ============================================================================
# PART 4: ResourceManager Interface
# ============================================================================

class ResourceManager(ABC):
    """
    Abstract base class for resource management.
    
    Provides lifecycle management methods for resources that need
    initialization and cleanup (connections, file handles, etc.).
    
    This enables the "with" statement (context manager protocol).
    
    Example:
        class MyResource(ResourceManager):
            def initialize(self) -> None:
                print("Setting up resource")
                self.connection = create_connection()
            
            def cleanup(self) -> None:
                print("Cleaning up resource")
                self.connection.close()
        
        # Usage
        with MyResource() as resource:
            resource.do_work()
        # Cleanup happens automatically!
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize resources.
        
        Called when entering a context manager or when explicitly called.
        Use this to set up connections, open files, etc.
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        Called when exiting a context manager or when explicitly called.
        Use this to close connections, release locks, etc.
        """
        pass
    
    def __enter__(self):
        """
        Context manager entry.
        
        Called when using "with" statement:
            with VaultClient() as client:  # __enter__ called here
                ...
        """
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        
        Called when exiting "with" block:
            with VaultClient() as client:
                ...
            # __exit__ called here (even if exception occurred!)
        
        Args:
            exc_type: Exception type (if exception occurred)
            exc_val: Exception value
            exc_tb: Exception traceback
        
        Returns:
            False: Don't suppress exceptions
        """
        self.cleanup()
        return False  # Don't suppress exceptions


# ============================================================================
# PART 5: Configurable Interface
# ============================================================================

class Configurable(ABC):
    """
    Abstract base class for configurable components.
    
    Provides a standard interface for components that can be
    configured via dictionaries or key-value pairs.
    
    Example:
        class MyComponent(Configurable):
            def __init__(self):
                self._config = {}
            
            def get_config(self, key: str, default: Any = None) -> Any:
                return self._config.get(key, default)
            
            def set_config(self, key: str, value: Any) -> None:
                self._config[key] = value
            
            def get_all_config(self) -> dict[str, Any]:
                return self._config.copy()
    """
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        pass
    
    @abstractmethod
    def get_all_config(self) -> dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            dict: All configuration key-value pairs
        """
        pass
```

**How VaultClient uses these:**

```python
class VaultClient(SecretProvider, ResourceManager, Configurable):
    """
    VaultClient implements THREE interfaces!
    
    1. SecretProvider: Must implement get_secret(), authenticate(), is_authenticated()
    2. ResourceManager: Must implement initialize(), cleanup()
    3. Configurable: Must implement get_config(), set_config(), get_all_config()
    """
    
    # SecretProvider methods
    def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
        # Implementation
        ...
    
    def authenticate(self) -> bool:
        # Implementation
        ...
    
    def is_authenticated(self) -> bool:
        # Implementation
        ...
    
    # ResourceManager methods
    def initialize(self) -> None:
        # Implementation
        ...
    
    def cleanup(self) -> None:
        # Implementation
        ...
    
    # Configurable methods
    def get_config(self, key: str, default: Any = None) -> Any:
        # Implementation
        ...
    
    def set_config(self, key: str, value: Any) -> None:
        # Implementation
        ...
    
    def get_all_config(self) -> dict[str, Any]:
        # Implementation
        ...
```

**Benefits:**
1. **Contract Enforcement**: Python ensures all methods are implemented
2. **Documentation**: Interface clearly shows what's required
3. **Polymorphism**: Any `SecretProvider` works the same way
4. **Testing**: Easy to create mock implementations

---

### Module 3: auth.py

**Purpose:** Implement different authentication strategies for Vault.

**Why we need it:**
- Different environments need different auth methods
- Flexibility without changing client code
- Each strategy is independent and testable

**Complete Code with Detailed Explanation:**

```python
"""
Authentication strategies for HashiCorp Vault.

This module implements various authentication methods using the Strategy pattern,
allowing flexible authentication without modifying client code.
"""

import logging
import os
import time
from typing import Optional

import requests

from gds_vault.base import AuthStrategy
from gds_vault.exceptions import VaultAuthError

logger = logging.getLogger(__name__)


# ============================================================================
# Strategy 1: AppRole Authentication
# ============================================================================

class AppRoleAuth(AuthStrategy):
    """
    AppRole authentication strategy for HashiCorp Vault.
    
    AppRole is designed for machine authentication, making it ideal for
    servers, applications, and automation workflows.
    
    How AppRole works:
    1. Admin creates an AppRole with specific permissions
    2. App gets role_id (like username) and secret_id (like password)
    3. App uses these to authenticate and get a token
    4. Token is used for subsequent requests
    
    Args:
        role_id: AppRole role_id (or None to use VAULT_ROLE_ID env var)
        secret_id: AppRole secret_id (or None to use VAULT_SECRET_ID env var)
    
    Example:
        # Explicit credentials
        auth = AppRoleAuth(role_id="my-role-id", secret_id="my-secret-id")
        token, expiry = auth.authenticate("https://vault.example.com", timeout=10)
        
        # From environment
        auth = AppRoleAuth()  # Reads VAULT_ROLE_ID and VAULT_SECRET_ID
        token, expiry = auth.authenticate("https://vault.example.com", timeout=10)
    """
    
    def __init__(self, role_id: Optional[str] = None, secret_id: Optional[str] = None):
        """Initialize AppRole authentication."""
        # Try to get credentials from arguments or environment
        self.role_id = role_id or os.getenv("VAULT_ROLE_ID")
        self.secret_id = secret_id or os.getenv("VAULT_SECRET_ID")
        
        # Validate credentials are provided
        if not self.role_id or not self.secret_id:
            raise VaultAuthError(
                "AppRole credentials must be provided or set in "
                "VAULT_ROLE_ID and VAULT_SECRET_ID environment variables"
            )
    
    def authenticate(self, vault_addr: str, timeout: int) -> tuple[str, float]:
        """
        Authenticate with Vault using AppRole.
        
        This method:
        1. Sends role_id and secret_id to Vault's AppRole endpoint
        2. Receives a token if credentials are valid
        3. Calculates when the token will expire
        4. Returns token and expiry timestamp
        
        Args:
            vault_addr: Vault server address (e.g., "https://vault.example.com:8200")
            timeout: Request timeout in seconds
        
        Returns:
            tuple: (token, expiry_timestamp)
                - token: String token for subsequent requests
                - expiry_timestamp: Unix timestamp when token expires
        
        Raises:
            VaultAuthError: If authentication fails
        """
        logger.info("Authenticating with Vault using AppRole at %s", vault_addr)
        
        # Construct the AppRole login URL
        login_url = f"{vault_addr}/v1/auth/approle/login"
        
        # Prepare the login payload
        login_payload = {
            "role_id": self.role_id,
            "secret_id": self.secret_id
        }
        
        try:
            # Send authentication request
            resp = requests.post(login_url, json=login_payload, timeout=timeout)
        except requests.RequestException as e:
            logger.error("Network error during AppRole authentication: %s", e)
            raise VaultAuthError(f"Failed to connect to Vault: {e}") from e
        
        # Check if authentication succeeded
        if not resp.ok:
            logger.error(
                "AppRole authentication failed with status %s: %s",
                resp.status_code,
                resp.text
            )
            raise VaultAuthError(f"Vault AppRole login failed: {resp.text}")
        
        # Parse the response
        auth_data = resp.json()["auth"]
        token = auth_data["client_token"]
        
        # Calculate token expiry with 5-minute early refresh buffer
        # Why buffer? Ensures token doesn't expire mid-operation
        lease_duration = auth_data.get("lease_duration", 3600)  # Default 1 hour
        expiry = time.time() + lease_duration - 300  # Subtract 5 minutes
        
        logger.info(
            "Successfully authenticated with AppRole. Token valid for %ss",
            lease_duration
        )
        logger.debug("Token will expire at timestamp: %s", expiry)
        
        return token, expiry
    
    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        
        Used in debugger and for logging.
        Masks sensitive data!
        """
        role_id_masked = f"{self.role_id[:8]}..." if self.role_id else "None"
        return f"AppRoleAuth(role_id='{role_id_masked}')"
    
    def __str__(self) -> str:
        """
        User-friendly representation.
        
        Used in print() and str().
        """
        return "AppRole Authentication"


# ============================================================================
# Strategy 2: Token Authentication
# ============================================================================

class TokenAuth(AuthStrategy):
    """
    Direct token authentication strategy.
    
    Use this when you already have a Vault token (e.g., from environment
    or a previous authentication). The token is used directly without
    additional authentication.
    
    When to use:
    - Development/testing with a long-lived token
    - Using token from another authentication method
    - CI/CD pipeline with pre-generated token
    
    Args:
        token: Vault token
        ttl: Token time-to-live in seconds (default: 3600)
    
    Example:
        auth = TokenAuth(token="hvs.CAESIF...")
        token, expiry = auth.authenticate("https://vault.example.com", timeout=10)
    """
    
    def __init__(self, token: str, ttl: int = 3600):
        """Initialize token authentication."""
        if not token:
            raise VaultAuthError("Token must be provided")
        self.token = token
        self.ttl = ttl
    
    def authenticate(self, vault_addr: str, timeout: int) -> tuple[str, float]:
        """
        Return the provided token with calculated expiry.
        
        No actual authentication happens - just returns the token!
        
        Args:
            vault_addr: Vault server address (not used)
            timeout: Request timeout (not used)
        
        Returns:
            tuple: (token, expiry_timestamp)
        """
        logger.info("Using direct token authentication")
        expiry = time.time() + self.ttl - 300  # 5-minute early refresh
        return self.token, expiry
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        token_masked = f"{self.token[:8]}..." if self.token else "None"
        return f"TokenAuth(token='{token_masked}', ttl={self.ttl})"
    
    def __str__(self) -> str:
        """User-friendly representation."""
        return "Token Authentication"


# ============================================================================
# Strategy 3: Environment Authentication
# ============================================================================

class EnvironmentAuth(AuthStrategy):
    """
    Environment-based authentication strategy.
    
    Reads authentication details from environment variables:
    - Tries VAULT_TOKEN first
    - Falls back to AppRole (VAULT_ROLE_ID and VAULT_SECRET_ID)
    
    This is the "smart" strategy that figures out what to use
    based on what's available in the environment.
    
    Example:
        # Set environment
        os.environ["VAULT_TOKEN"] = "hvs.ABC123"
        
        # Use environment auth
        auth = EnvironmentAuth()
        token, expiry = auth.authenticate("https://vault.example.com", timeout=10)
    """
    
    def __init__(self):
        """Initialize environment authentication."""
        self._token_auth = None
        self._approle_auth = None
        
        # Check for token first
        vault_token = os.getenv("VAULT_TOKEN")
        if vault_token:
            self._token_auth = TokenAuth(token=vault_token)
            logger.debug("Using VAULT_TOKEN for authentication")
            return
        
        # Try AppRole
        role_id = os.getenv("VAULT_ROLE_ID")
        secret_id = os.getenv("VAULT_SECRET_ID")
        if role_id and secret_id:
            self._approle_auth = AppRoleAuth(role_id=role_id, secret_id=secret_id)
            logger.debug("Using AppRole for authentication")
            return
        
        # No credentials found
        raise VaultAuthError(
            "No credentials found in environment. Set either "
            "VAULT_TOKEN or (VAULT_ROLE_ID and VAULT_SECRET_ID)"
        )
    
    def authenticate(self, vault_addr: str, timeout: int) -> tuple[str, float]:
        """
        Authenticate using available environment credentials.
        
        Args:
            vault_addr: Vault server address
            timeout: Request timeout
        
        Returns:
            tuple: (token, expiry_timestamp)
        """
        if self._token_auth:
            return self._token_auth.authenticate(vault_addr, timeout)
        elif self._approle_auth:
            return self._approle_auth.authenticate(vault_addr, timeout)
        else:
            raise VaultAuthError("No authentication strategy available")
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        if self._token_auth:
            return f"EnvironmentAuth(using TokenAuth)"
        elif self._approle_auth:
            return f"EnvironmentAuth(using AppRoleAuth)"
        return "EnvironmentAuth(no strategy)"
    
    def __str__(self) -> str:
        """User-friendly representation."""
        return "Environment Authentication"
```

**Using authentication strategies:**

```python
from gds_vault import VaultClient, AppRoleAuth, TokenAuth, EnvironmentAuth

# Strategy 1: Production with AppRole
auth = AppRoleAuth(role_id="xxx", secret_id="yyy")
client = VaultClient(auth=auth)

# Strategy 2: Development with Token
auth = TokenAuth(token="hvs.ABC123")
client = VaultClient(auth=auth)

# Strategy 3: Let it figure out from environment
auth = EnvironmentAuth()
client = VaultClient(auth=auth)

# Strategy 4: Use default (reads from environment)
client = VaultClient()  # Uses AppRoleAuth with env vars
```

---

(Continued in next section due to length...)

### Module 4: cache.py

**Purpose:** Implement caching to reduce Vault API calls and improve performance.

**Why we need it:**
- Vault API calls are slow (network latency)
- Reduce load on Vault server
- Secrets don't change frequently
- Improve application performance

**Caching Strategies:**

1. **SecretCache**: Simple in-memory cache (no expiration)
2. **TTLCache**: Time-to-live cache (auto-expire)
3. **NoOpCache**: No caching (always fetch from Vault)

Let me continue creating this comprehensive guide:

