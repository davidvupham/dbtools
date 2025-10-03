"""
Snowflake Connection Module

This module handles Snowflake database connections and connection management.
"""

import snowflake.connector
import logging
from typing import Optional
import os

try:
    from gds_hvault.vault import get_secret_from_vault, VaultError
except ImportError:
    get_secret_from_vault = None
    VaultError = Exception

logger = logging.getLogger(__name__)


class SnowflakeConnection:
    """
    Manages Snowflake database connections using RSA key pair
    authentication.
    """

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
        """
        Initialize Snowflake connection parameters using RSA private key
        from Vault.

            Args:
                account: Snowflake account name
                warehouse: Optional warehouse name
                role: Optional role name
                database: Optional database name
                vault_namespace: Vault namespace (optional, defaults to VAULT_NAMESPACE env)
                vault_secret_path: Path to secret in Vault (optional, defaults to VAULT_SECRET_PATH env)
                    (e.g., 'namespace/data/snowflake')
                vault_mount_point: Vault mount point (optional, defaults to VAULT_MOUNT_POINT env)
                vault_role_id: Vault AppRole role_id (optional, defaults to VAULT_ROLE_ID env)
                vault_secret_id: Vault AppRole secret_id (optional, defaults to VAULT_SECRET_ID env)
                vault_addr: Vault address (optional, defaults to VAULT_ADDR env)
        """
        self.account = account
        self.user = user or os.getenv("SNOWFLAKE_USER")
        self.warehouse = warehouse
        self.role = role
        self.database = database
        self.connection = None

        # Vault configuration: parameter > env > None
        self.vault_namespace = vault_namespace or os.getenv("VAULT_NAMESPACE")
        vault_secret_path = vault_secret_path or os.getenv("VAULT_SECRET_PATH")
        vault_mount_point = vault_mount_point or os.getenv("VAULT_MOUNT_POINT")
        vault_role_id = vault_role_id or os.getenv("VAULT_ROLE_ID")
        vault_secret_id = vault_secret_id or os.getenv("VAULT_SECRET_ID")
        vault_addr = vault_addr or os.getenv("VAULT_ADDR")

        # Fetch RSA private key from Vault
        self.private_key = None
        if get_secret_from_vault and vault_secret_path:
            try:
                secret_path = vault_secret_path
                if self.vault_namespace:
                    secret_path = f"{self.vault_namespace}/{secret_path}"
                if vault_mount_point:
                    secret_path = f"{vault_mount_point}/{secret_path}"
                vault_kwargs = {}
                if vault_addr:
                    vault_kwargs["vault_addr"] = vault_addr
                if vault_role_id:
                    os.environ["HVAULT_ROLE_ID"] = vault_role_id
                if vault_secret_id:
                    os.environ["HVAULT_SECRET_ID"] = vault_secret_id
                secret = get_secret_from_vault(secret_path, **vault_kwargs)
                self.private_key = secret.get("private_key")
                if not self.private_key:
                    raise VaultError("private_key not found in Vault secret")
                logger.info(
                    "Snowflake private key loaded from Vault: %s", secret_path
                )
            except VaultError as e:
                logger.error("Vault error: %s", e)
                raise RuntimeError(
                    "Snowflake private key could not be retrieved from Vault."
                ) from e
        else:
            raise RuntimeError(
                "Vault secret path must be provided to retrieve private key."
            )

    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """
        Establish connection to Snowflake using key pair authentication.
        Returns:
            Snowflake connection object
        Raises:
            Exception: If connection fails
        """
        try:
            connection_params = {
                "account": self.account,
                "user": self.user,
                "private_key": self.private_key,
            }
            if self.warehouse:
                connection_params["warehouse"] = self.warehouse
            if self.role:
                connection_params["role"] = self.role
            if self.database:
                connection_params["database"] = self.database
            logger.info(
                "Connecting to Snowflake account: %s as user: %s",
                self.account, self.user
            )
            self.connection = snowflake.connector.connect(**connection_params)
            logger.info("Successfully connected to Snowflake account: %s", self.account)
            return self.connection
        except Exception as e:
            logger.error(
                "Failed to connect to Snowflake account %s: %s",
                self.account, str(e)
            )
            raise

    def get_connection(self) -> snowflake.connector.SnowflakeConnection:
        """
        Get the current connection, establishing one if needed.

        Returns:
            Snowflake connection object
        """
        if self.connection is None or self.connection.is_closed():
            self.connect()
        return self.connection

    def test_connectivity(self, timeout_seconds: int = 30) -> dict:
        """
        Test connectivity to Snowflake account with comprehensive diagnostics.
        
        Args:
            timeout_seconds: Connection timeout in seconds
            
        Returns:
            Dictionary with connectivity test results:
            {
                'success': bool,
                'response_time_ms': float,
                'account_info': dict,
                'error': str (if failed),
                'timestamp': str
            }
        """
        import time
        from datetime import datetime
        
        start_time = time.time()
        result = {
            'success': False,
            'response_time_ms': 0,
            'account_info': {},
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Test basic connectivity with a lightweight query
            test_connection = None
            connection_params = {
                "account": self.account,
                "user": self.user,
                "private_key": self.private_key,
                "login_timeout": timeout_seconds,
                "network_timeout": timeout_seconds
            }
            
            if self.warehouse:
                connection_params["warehouse"] = self.warehouse
            if self.role:
                connection_params["role"] = self.role
            if self.database:
                connection_params["database"] = self.database
                
            logger.info(
                "Testing connectivity to Snowflake account: %s", self.account
            )
            
            # Create test connection
            test_connection = snowflake.connector.connect(**connection_params)
            
            # Execute lightweight diagnostic queries
            cursor = test_connection.cursor()
            
            # Test 1: Basic connectivity with SELECT 1
            cursor.execute("SELECT 1 as connectivity_test")
            cursor.fetchone()
            
            # Test 2: Get account information
            cursor.execute("""
                SELECT 
                    CURRENT_ACCOUNT() as account_name,
                    CURRENT_USER() as current_user,
                    CURRENT_ROLE() as current_role,
                    CURRENT_WAREHOUSE() as current_warehouse,
                    CURRENT_DATABASE() as current_database,
                    CURRENT_VERSION() as snowflake_version,
                    CURRENT_REGION() as region
            """)
            
            account_info = cursor.fetchone()
            if account_info:
                result['account_info'] = {
                    'account_name': account_info[0],
                    'current_user': account_info[1],
                    'current_role': account_info[2],
                    'current_warehouse': account_info[3],
                    'current_database': account_info[4],
                    'snowflake_version': account_info[5],
                    'region': account_info[6]
                }
            
            cursor.close()
            result['success'] = True
            
            end_time = time.time()
            result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
            
            logger.info(
                f"Connectivity test successful for {self.account} "
                f"(response time: {result['response_time_ms']}ms)"
            )
            
        except Exception as e:
            end_time = time.time()
            result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
            result['error'] = str(e)
            logger.error(
                f"Connectivity test failed for {self.account}: {str(e)} "
                f"(response time: {result['response_time_ms']}ms)"
            )
        finally:
            # Clean up test connection
            if test_connection and not test_connection.is_closed():
                try:
                    test_connection.close()
                except Exception as e:
                    logger.warning(f"Error closing test connection: {str(e)}")
                    
        return result

    def close(self):
        """Close the Snowflake connection if open."""
        if self.connection and not self.connection.is_closed():
            try:
                self.connection.close()
                logger.info("Closed connection to Snowflake account: %s", self.account)
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of result rows

        Raises:
            Exception: If query execution fails
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            results = cursor.fetchall()
            cursor.close()
            return results

        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(f"Query: {query}")
            raise

    def execute_query_dict(self, query: str, params: Optional[tuple] = None) -> list:
        """
        Execute a SQL query and return results as list of dictionaries.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of result dictionaries

        Raises:
            Exception: If query execution fails
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor(snowflake.connector.DictCursor)

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            results = cursor.fetchall()
            cursor.close()
            return results

        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(f"Query: {query}")
            raise

    def switch_account(
        self, new_account: str
    ) -> snowflake.connector.SnowflakeConnection:
        """
        Switch to a different Snowflake account.

        Args:
            new_account: New account name to connect to

        Returns:
            New Snowflake connection object
        """
        logger.info(f"Switching from account {self.account} to {new_account}")
        self.close()
        self.account = new_account
        return self.connect()

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
