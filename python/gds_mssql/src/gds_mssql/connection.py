"""
Microsoft SQL Server database connection implementation.

This module provides a concrete implementation of the DatabaseConnection
interface for Microsoft SQL Server databases using pyodbc.
"""

import logging
from typing import Any, Optional

import pyodbc
from gds_database import (
    ConfigurableComponent,
    ConfigurationError,
    DatabaseConnection,
    QueryError,
    ResourceManager,
)
from gds_database import (
    DatabaseConnectionError as ConnectionError,
)

logger = logging.getLogger(__name__)


class MSSQLConnection(DatabaseConnection, ConfigurableComponent, ResourceManager):
    """
    Microsoft SQL Server database connection implementation.

    Provides a complete implementation of the DatabaseConnection interface
    for Microsoft SQL Server databases using pyodbc. Supports both
    username/password and Kerberos authentication.

    Examples:
        # Using username/password authentication
        conn = MSSQLConnection(
            server='localhost',
            database='mydb',
            user='myuser',
            password='mypassword'
        )

        # Using Kerberos authentication
        conn = MSSQLConnection(
            server='localhost',
            database='mydb',
            authentication='kerberos'
        )

        # Using configuration dictionary
        config = {
            'server': 'localhost',
            'database': 'mydb',
            'user': 'myuser',
            'password': 'mypassword',
            'driver': 'ODBC Driver 18 for SQL Server',
            'connection_timeout': 30
        }
        conn = MSSQLConnection(config=config)

        # Using as context manager
        with MSSQLConnection(server='localhost', database='mydb') as conn:
            results = conn.execute_query("SELECT * FROM users")
    """

    def __init__(
        self,
        server: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        authentication: Optional[str] = None,
        driver: Optional[str] = None,
        port: Optional[int] = None,
        config: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize MSSQL connection.

        Args:
            server: SQL Server instance name or IP address
            database: Database name
            user: Username for authentication (not used with Kerberos)
            password: Password for authentication (not used with Kerberos)
            authentication: Authentication method ('kerberos' or None for username/password)
            driver: ODBC driver name (default: 'ODBC Driver 18 for SQL Server')
            port: SQL Server port (default: 1433)
            config: Configuration dictionary
            **kwargs: Additional pyodbc connection parameters
        """
        # Build configuration from parameters
        conn_config: dict[str, Any] = dict(config) if config else {}

        if server is not None:
            conn_config["server"] = server
        if database is not None:
            conn_config["database"] = database
        if user is not None:
            conn_config["user"] = user
        if password is not None:
            conn_config["password"] = password
        if authentication is not None:
            conn_config["authentication"] = authentication
        if driver is not None:
            conn_config["driver"] = driver
        if port is not None:
            conn_config["port"] = port

        # Add any additional parameters
        if kwargs:
            conn_config.update(kwargs)

        # Set defaults
        conn_config.setdefault("driver", "ODBC Driver 18 for SQL Server")
        conn_config.setdefault("port", 1433)
        conn_config.setdefault("connection_timeout", 30)
        # None means username/password
        conn_config.setdefault("authentication", None)

        # Initialize parent classes
        ConfigurableComponent.__init__(self, conn_config)

        # Connection state
        self.connection: Optional[pyodbc.Connection] = None
        self._cursor: Optional[pyodbc.Cursor] = None

    def validate_config(self) -> bool:
        """
        Validate MSSQL connection configuration.

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If required configuration is missing or invalid
        """
        required_fields = ["server", "database"]
        missing_fields = [field for field in required_fields if not self.config.get(field)]

        if missing_fields:
            raise ConfigurationError(f"Missing required configuration fields: {missing_fields}")

        auth_method = self.config.get("authentication")
        if auth_method == "kerberos":
            # For Kerberos, user/password should not be provided
            if self.config.get("user") or self.config.get("password"):
                raise ConfigurationError("User/password should not be provided with Kerberos authentication")
        # For username/password, user is required
        elif not self.config.get("user"):
            raise ConfigurationError("Username is required for username/password authentication")

        # Validate port is a number
        port = self.config.get("port")
        if port and not isinstance(port, int):
            try:
                self.config["port"] = int(port)
            except ValueError as err:
                raise ConfigurationError(f"Invalid port number: {port}") from err

        return True

    def connect(self) -> pyodbc.Connection:
        """
        Establish connection to Microsoft SQL Server database.

        Returns:
            pyodbc connection object

        Raises:
            ConnectionError: If connection cannot be established
        """
        if self.is_connected():
            logger.info("Already connected to SQL Server database")
            return self.connection

        try:
            conn_string = self._build_connection_string()

            logger.info(
                "Connecting to SQL Server database: %s/%s on %s",
                self.config.get("database"),
                self.config.get("user", "Kerberos"),
                self.config.get("server"),
            )

            # Establish connection
            self.connection = pyodbc.connect(conn_string, timeout=self.config.get("connection_timeout", 30))

            logger.info("Successfully connected to SQL Server database")
            return self.connection

        except pyodbc.Error as e:
            error_msg = f"Failed to connect to SQL Server database: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

    def disconnect(self) -> None:
        """
        Close SQL Server database connection.

        Properly closes cursor and connection, handling any errors gracefully.
        """
        try:
            if self._cursor:
                self._close_cursor(self._cursor)

            if self.connection:
                self.connection.close()
                logger.info("Disconnected from SQL Server database")

        except pyodbc.Error as e:
            logger.warning("Error during disconnect: %s", e)
        finally:
            self._cursor = None
            self.connection = None

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_all: bool = True,
        return_dict: bool = False,
    ) -> list[Any]:
        """
        Execute a query and return results.

        Args:
            query: SQL query string to execute
            params: Optional parameters for parameterized queries
            fetch_all: If True, fetch all results. If False, returns cursor
            return_dict: If True, return results as dictionaries

        Returns:
            List of query results

        Raises:
            ConnectionError: If not connected to database
            QueryError: If query execution fails
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to SQL Server database")

        try:
            # Clean up any lingering cursor before creating a new one
            if self._cursor and fetch_all:
                self.close_active_cursor()

            # Create cursor
            cursor = self.connection.cursor()
            self._cursor = cursor

            logger.debug(
                "Executing query: %s",
                query[:100] + "..." if len(query) > 100 else query,
            )

            # Execute query
            cursor.execute(query, params or ())

            # Handle different query types
            if cursor.description is None:
                # Non-SELECT query (INSERT, UPDATE, DELETE, etc.)
                affected_rows = cursor.rowcount
                logger.debug("Query affected %d rows", affected_rows)
                self._close_cursor(cursor)
                self._cursor = None
                return [{"affected_rows": affected_rows}]

            # SELECT query - fetch results
            if fetch_all:
                if return_dict:
                    # Get column names
                    columns = [column[0] for column in cursor.description]
                    results = []
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                else:
                    results = cursor.fetchall()

                logger.debug("Query returned %d rows", len(results))
                self._close_cursor(cursor)
                self._cursor = None
                return results
            # Return cursor for manual fetching
            logger.debug("Returning open cursor for manual fetching")
            return cursor

        except pyodbc.Error as e:
            error_msg = f"Query execution failed: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def execute_query_dict(self, query: str, params: Optional[tuple] = None) -> list[dict[str, Any]]:
        """
        Execute query and return results as dictionaries.

        Convenience method that calls execute_query with return_dict=True.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            List of dictionaries representing query results
        """
        return self.execute_query(query, params, return_dict=True)

    def is_connected(self) -> bool:
        """
        Check if connection is active.

        Returns:
            True if connection is active and usable, False otherwise
        """
        conn = self.connection
        if not conn:
            return False

        try:
            # Try to execute a simple query to test connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except pyodbc.Error:
            return False

    def get_connection_info(self) -> dict[str, Any]:
        """
        Get connection information.

        Returns:
            Dictionary containing connection metadata
        """
        info = {
            "database_type": "mssql",
            "server": self.config.get("server"),
            "port": self.config.get("port"),
            "database": self.config.get("database"),
            "user": self.config.get("user"),
            "authentication": self.config.get("authentication", "username/password"),
            "driver": self.config.get("driver"),
            "connected": self.is_connected(),
        }

        if self.connection:
            try:
                # Get SQL Server version
                cursor = self.connection.cursor()
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                cursor.close()
                info["server_version"] = version
            except pyodbc.Error:
                pass

        return info

    def begin_transaction(self) -> None:
        """Begin a new transaction."""
        if not self.is_connected():
            raise ConnectionError("Not connected to database")

        # pyodbc handles transactions automatically
        logger.debug("Transaction started")

    def commit(self) -> None:
        """Commit current transaction."""
        if not self.is_connected():
            raise ConnectionError("Not connected to database")

        try:
            self.connection.commit()
            logger.debug("Transaction committed")
        except pyodbc.Error as e:
            error_msg = f"Failed to commit transaction: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def rollback(self) -> None:
        """Rollback current transaction."""
        if not self.is_connected():
            raise ConnectionError("Not connected to database")

        try:
            self.connection.rollback()
            logger.debug("Transaction rolled back")
        except pyodbc.Error as e:
            error_msg = f"Failed to rollback transaction: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_table_names(self, schema: str = "dbo") -> list[str]:
        """
        Get list of table names in specified schema.

        Args:
            schema: Schema name (default: 'dbo')

        Returns:
            List of table names
        """
        query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = ? AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """

        results = self.execute_query(query, (schema,))
        return [row[0] for row in results]

    def get_column_info(self, table_name: str, schema: str = "dbo") -> list[dict[str, Any]]:
        """
        Get column information for specified table.

        Args:
            table_name: Name of the table
            schema: Schema name (default: 'dbo')

        Returns:
            List of dictionaries containing column information
        """
        query = """
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            ORDINAL_POSITION
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ? AND TABLE_SCHEMA = ?
        ORDER BY ORDINAL_POSITION
        """

        return self.execute_query_dict(query, (table_name, schema))

    # ResourceManager implementation
    def initialize(self) -> None:
        """Initialize resources (establish connection)."""
        self.connect()

    def cleanup(self) -> None:
        """Clean up resources (close connection)."""
        self.disconnect()

    def is_initialized(self) -> bool:
        """Check if resources are initialized (connected)."""
        return self.is_connected()

    def close_active_cursor(self) -> None:
        """Close the currently tracked cursor if it is still open."""
        if self._cursor:
            self._close_cursor(self._cursor)
            self._cursor = None

    def _build_connection_string(self) -> str:
        """Build pyodbc connection string."""
        config = self.config
        conn_parts = []

        # Driver
        driver = config.get("driver", "ODBC Driver 18 for SQL Server")
        conn_parts.append(f"DRIVER={{{driver}}}")

        # Server and port
        server = config["server"]
        port = config.get("port", 1433)
        if port != 1433:
            server = f"{server},{port}"
        conn_parts.append(f"SERVER={server}")

        # Database
        conn_parts.append(f"DATABASE={config['database']}")

        # Authentication
        auth_method = config.get("authentication")
        if auth_method == "kerberos":
            conn_parts.append("Trusted_Connection=yes")
        else:
            # Username/password
            user = config.get("user")
            password = config.get("password")
            if user:
                conn_parts.append(f"UID={user}")
            if password:
                conn_parts.append(f"PWD={password}")

        # Connection timeout
        timeout = config.get("connection_timeout", 30)
        conn_parts.append(f"Connection Timeout={timeout}")

        return ";".join(conn_parts)

    def _close_cursor(self, cursor: pyodbc.Cursor) -> None:
        """Safely close a pyodbc cursor."""
        try:
            cursor.close()
            logger.debug("Cursor closed")
        except pyodbc.Error as exc:
            logger.debug("Failed to close cursor cleanly: %s", exc)
