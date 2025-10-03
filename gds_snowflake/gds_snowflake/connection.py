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
                vault_namespace: Vault namespace (optional, for multi-tenant Vault)
                vault_secret_path: Path to secret in Vault
                    (e.g., 'namespace/data/snowflake')
                vault_mount_point: Vault mount point (e.g., 'secret')
                vault_role_id: Vault AppRole role_id
                    (optional, defaults to HVAULT_ROLE_ID env)
                vault_secret_id: Vault AppRole secret_id
                    (optional, defaults to HVAULT_SECRET_ID env)
                vault_addr: Vault address (optional, defaults to HVAULT_ADDR env)
        """
        self.account = account
        self.user = user or os.getenv("SNOWFLAKE_USER")
        self.warehouse = warehouse
        self.role = role
        self.database = database
        self.connection = None

        # Vault namespace: parameter > env > None
        self.vault_namespace = vault_namespace or os.getenv("HVAULT_NAMESPACE")

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
                logger.info("Snowflake private key loaded from Vault: %s", secret_path)
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
                f"Connecting to Snowflake account: {self.account} as user: "
                f"{self.user}"
            )
            self.connection = snowflake.connector.connect(**connection_params)
            logger.info("Successfully connected to Snowflake account: %s", self.account)
            return self.connection
        except Exception as e:
            logger.error(
                f"Failed to connect to Snowflake account {self.account}: " f"{str(e)}"
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
