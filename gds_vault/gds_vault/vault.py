import os
import time
import logging
import requests
from typing import Optional, Dict, Any, Callable
from functools import wraps

# Configure module logger
logger = logging.getLogger(__name__)


class VaultError(Exception):
    """Exception raised for Vault operation errors."""
    pass


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 32.0,
    backoff_factor: float = 2.0,
    retriable_exceptions: tuple = (requests.RequestException,)
) -> Callable:
    """
    Decorator that retries a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for exponential backoff (typically 2.0)
        retriable_exceptions: Tuple of exceptions that trigger a retry
    
    Returns:
        Decorated function that retries on failure
    
    Example:
        @retry_with_backoff(max_retries=3, initial_delay=1.0)
        def fetch_data():
            return requests.get('https://api.example.com/data')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retriable_exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} "
                            f"retries: {e}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    current_delay = min(delay, max_delay)
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    time.sleep(current_delay)
                    delay *= backoff_factor
            
            raise last_exception
        
        return wrapper
    return decorator


class VaultClient:
    """
    Vault client with token caching and connection reuse.
    
    Use this class when fetching multiple secrets to avoid re-authenticating
    for each request. The client caches the authentication token and reuses
    it for subsequent requests.
    
    Example:
        client = VaultClient()
        secret1 = client.get_secret('secret/data/app1')
        secret2 = client.get_secret('secret/data/app2')
        secret3 = client.get_secret('secret/data/app3')
    
    Context manager usage:
        with VaultClient() as client:
            secret = client.get_secret('secret/data/myapp')
    """
    
    def __init__(
        self,
        vault_addr: Optional[str] = None,
        role_id: Optional[str] = None,
        secret_id: Optional[str] = None,
        timeout: int = 10,
    ):
        """
        Initialize Vault client.
        
        Args:
            vault_addr: Vault server address (overrides VAULT_ADDR env var)
            role_id: AppRole role_id (overrides VAULT_ROLE_ID env var)
            secret_id: AppRole secret_id (overrides VAULT_SECRET_ID env var)
            timeout: Request timeout in seconds
        
        Raises:
            VaultError: If required credentials are not provided
        """
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR")
        if not self.vault_addr:
            raise VaultError(
                "Vault address must be provided or set in VAULT_ADDR environment variable"
            )
        
        self.role_id = role_id or os.getenv("VAULT_ROLE_ID")
        self.secret_id = secret_id or os.getenv("VAULT_SECRET_ID")
        
        if not self.role_id or not self.secret_id:
            raise VaultError(
                "VAULT_ROLE_ID and VAULT_SECRET_ID must be provided or set in environment"
            )
        
        self.timeout = timeout
        self._token: Optional[str] = None
        self._token_expiry: Optional[float] = None
        self._secret_cache: Dict[str, Dict[str, Any]] = {}
    
    def __enter__(self):
        """Context manager entry."""
        logger.debug("Entering VaultClient context manager")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clear cached token and secrets."""
        if exc_type:
            logger.error(
                f"Exiting VaultClient context with exception: "
                f"{exc_type.__name__}: {exc_val}"
            )
        else:
            logger.debug("Exiting VaultClient context manager")
        self.clear_cache()
        return False
    
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def authenticate(self) -> str:
        """
        Authenticate with Vault using AppRole and cache the token.
        
        Returns:
            str: Client token
        
        Raises:
            VaultError: If authentication fails
        """
        logger.info(f"Authenticating with Vault at {self.vault_addr}")
        login_url = f"{self.vault_addr}/v1/auth/approle/login"
        login_payload = {"role_id": self.role_id, "secret_id": self.secret_id}
        
        try:
            resp = requests.post(login_url, json=login_payload, timeout=self.timeout)
        except requests.RequestException as e:
            logger.error(f"Network error connecting to Vault: {e}")
            raise VaultError(f"Failed to connect to Vault: {e}")
        
        if not resp.ok:
            logger.error(
                f"Vault AppRole login failed with status {resp.status_code}: "
                f"{resp.text}"
            )
            raise VaultError(f"Vault AppRole login failed: {resp.text}")
        
        auth_data = resp.json()["auth"]
        self._token = auth_data["client_token"]
        
        # Cache token with expiry (use lease_duration, default to 1 hour)
        lease_duration = auth_data.get("lease_duration", 3600)
        self._token_expiry = time.time() + lease_duration - 300
        
        logger.info(
            f"Successfully authenticated with Vault. "
            f"Token valid for {lease_duration}s"
        )
        logger.debug(f"Token will be refreshed at {self._token_expiry}")
        
        return self._token
    
    def _get_token(self) -> str:
        """
        Get valid token, re-authenticating if necessary.
        
        Returns:
            str: Valid client token
        """
        if self._token is None or (
            self._token_expiry and time.time() >= self._token_expiry
        ):
            self.authenticate()
        return self._token
    
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def get_secret(
        self,
        secret_path: str,
        use_cache: bool = True,
        version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve a secret from Vault.
        
        Args:
            secret_path: Path to the secret (e.g., 'secret/data/myapp')
            use_cache: If True, return cached secret if available
            version: Specific version to retrieve (KV v2 only)
        
        Returns:
            dict: Secret data
        
        Raises:
            VaultError: If secret fetch fails
        """
        cache_key = f"{secret_path}:v{version}" if version else secret_path
        
        # Check cache first
        if use_cache and cache_key in self._secret_cache:
            logger.debug(f"Cache hit for secret: {secret_path}")
            return self._secret_cache[cache_key]
        
        logger.info(f"Fetching secret from Vault: {secret_path}")
        if version:
            logger.debug(f"Requesting specific version: {version}")
        
        token = self._get_token()
        secret_url = f"{self.vault_addr}/v1/{secret_path}"
        headers = {"X-Vault-Token": token}
        params = {"version": version} if version else None
        
        try:
            resp = requests.get(
                secret_url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
        except requests.RequestException as e:
            logger.error(f"Network error fetching secret {secret_path}: {e}")
            raise VaultError(f"Failed to connect to Vault: {e}")
        
        if not resp.ok:
            logger.error(
                f"Failed to fetch secret {secret_path} "
                f"(status {resp.status_code}): {resp.text}"
            )
            raise VaultError(f"Vault secret fetch failed: {resp.text}")
        
        data = resp.json()
        
        # Support both KV v1 and v2
        if "data" in data and "data" in data["data"]:
            # KV v2
            secret_data = data["data"]["data"]
            logger.debug(f"Successfully fetched KV v2 secret: {secret_path}")
        elif "data" in data:
            # KV v1
            secret_data = data["data"]
            logger.debug(f"Successfully fetched KV v1 secret: {secret_path}")
        else:
            logger.error(
                f"Unexpected response format for secret {secret_path}: "
                f"{list(data.keys())}"
            )
            raise VaultError("Secret data not found in Vault response")
        
        # Cache the secret
        if use_cache:
            self._secret_cache[cache_key] = secret_data
            logger.debug(f"Cached secret: {cache_key}")
        
        return secret_data
    
    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def list_secrets(self, path: str) -> list:
        """
        List secrets at the given path.
        
        Args:
            path: Path to list (e.g., 'secret/metadata/myapp')
        
        Returns:
            list: List of secret names
        
        Raises:
            VaultError: If list operation fails
        """
        logger.info(f"Listing secrets at path: {path}")
        token = self._get_token()
        list_url = f"{self.vault_addr}/v1/{path}"
        headers = {"X-Vault-Token": token}
        
        try:
            resp = requests.request(
                "LIST",
                list_url,
                headers=headers,
                timeout=self.timeout
            )
        except requests.RequestException as e:
            logger.error(f"Network error listing secrets at {path}: {e}")
            raise VaultError(f"Failed to connect to Vault: {e}")
        
        if not resp.ok:
            logger.error(
                f"Failed to list secrets at {path} "
                f"(status {resp.status_code}): {resp.text}"
            )
            raise VaultError(f"Vault list operation failed: {resp.text}")
        
        data = resp.json()
        keys = data.get("data", {}).get("keys", [])
        logger.info(f"Found {len(keys)} secrets at {path}")
        logger.debug(f"Secret keys: {keys}")
        return keys
    
    def clear_cache(self):
        """Clear cached token and secrets."""
        cached_count = len(self._secret_cache)
        self._token = None
        self._token_expiry = None
        self._secret_cache.clear()
        logger.info(f"Cleared cache (removed {cached_count} secrets)")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached data.
        
        Returns:
            dict: Cache statistics
        """
        return {
            "has_token": self._token is not None,
            "token_valid": self._token is not None and (
                self._token_expiry is None or time.time() < self._token_expiry
            ),
            "cached_secrets_count": len(self._secret_cache),
            "cached_secret_paths": list(self._secret_cache.keys()),
        }


@retry_with_backoff(max_retries=3, initial_delay=1.0)
def get_secret_from_vault(secret_path: str, vault_addr: str = None) -> dict:
    """
    Retrieve a secret from HashiCorp Vault using AppRole authentication.
    Expects VAULT_ROLE_ID and VAULT_SECRET_ID in environment variables.
    Optionally, VAULT_ADDR for Vault address.

    Args:
        secret_path: Path to the secret in Vault (e.g., 'secret/data/myapp')
        vault_addr: Vault address (overrides env if provided)
    Returns:
        dict: Secret data
    Raises:
        VaultError: On failure to authenticate or fetch secret
    """
    logger.info(f"Fetching secret using functional API: {secret_path}")
    
    role_id = os.getenv("VAULT_ROLE_ID")
    secret_id = os.getenv("VAULT_SECRET_ID")
    if not role_id or not secret_id:
        logger.error("VAULT_ROLE_ID and VAULT_SECRET_ID not found in environment")
        raise VaultError(
            "VAULT_ROLE_ID and VAULT_SECRET_ID must be set in environment"
        )

    vault_addr = vault_addr or os.getenv("VAULT_ADDR")
    if not vault_addr:
        logger.error("VAULT_ADDR not found in environment")
        raise VaultError("Vault address must be set in VAULT_ADDR")

    logger.debug(f"Authenticating with Vault at {vault_addr}")
    
    # Step 1: Login with AppRole
    login_url = f"{vault_addr}/v1/auth/approle/login"
    login_payload = {"role_id": role_id, "secret_id": secret_id}
    
    try:
        resp = requests.post(login_url, json=login_payload, timeout=10)
    except requests.RequestException as e:
        logger.error(f"Network error during authentication: {e}")
        raise VaultError(f"Failed to connect to Vault: {e}")
    
    if not resp.ok:
        logger.error(
            f"AppRole login failed (status {resp.status_code}): {resp.text}"
        )
        raise VaultError(f"Vault AppRole login failed: {resp.text}")
    
    client_token = resp.json()["auth"]["client_token"]
    logger.debug("Successfully authenticated with Vault")

    # Step 2: Read secret
    secret_url = f"{vault_addr}/v1/{secret_path}"
    headers = {"X-Vault-Token": client_token}
    
    try:
        resp = requests.get(secret_url, headers=headers, timeout=10)
    except requests.RequestException as e:
        logger.error(f"Network error fetching secret {secret_path}: {e}")
        raise VaultError(f"Failed to connect to Vault: {e}")
    
    if not resp.ok:
        logger.error(
            f"Failed to fetch secret {secret_path} "
            f"(status {resp.status_code}): {resp.text}"
        )
        raise VaultError(f"Vault secret fetch failed: {resp.text}")
    
    data = resp.json()
    
    # Support both v1 and v2 kv
    if "data" in data and "data" in data["data"]:
        # kv v2
        logger.debug(f"Successfully fetched KV v2 secret: {secret_path}")
        return data["data"]["data"]
    elif "data" in data:
        # kv v1
        logger.debug(f"Successfully fetched KV v1 secret: {secret_path}")
        return data["data"]
    else:
        logger.error(
            f"Unexpected response format for secret {secret_path}: "
            f"{list(data.keys())}"
        )
        raise VaultError("Secret data not found in Vault response")
