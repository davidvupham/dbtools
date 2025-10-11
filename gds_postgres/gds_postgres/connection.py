"""
PostgreSQL database connection implementation.

This module provides a concrete implementation of the DatabaseConnection
interface for PostgreSQL databases using psycopg2.
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras
from gds_database import (
    ConfigurableComponent,
    ConfigurationError,
    ConnectionError,
    DatabaseConnection,
    QueryError,
    ResourceManager,
)

logger = logging.getLogger(__name__)


class PostgreSQLConnection(DatabaseConnection, ConfigurableComponent, ResourceManager):
    """
    PostgreSQL database connection implementation.
    
    Provides a complete implementation of the DatabaseConnection interface
    for PostgreSQL databases using psycopg2. Supports both individual
    connection parameters and connection URL formats.
    
    Examples:
        # Using individual parameters
        conn = PostgreSQLConnection(
            host='localhost',
            port=5432,
            database='mydb',
            user='myuser',
            password='mypassword'
        )
        
        # Using connection URL
        conn = PostgreSQLConnection(
            connection_url='postgresql://user:pass@localhost:5432/mydb'
        )
        
        # Using configuration dictionary
        config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'mydb',
            'user': 'myuser',
            'password': 'mypassword',
            'autocommit': True,
            'connect_timeout': 30
        }
        conn = PostgreSQLConnection(config=config)
        
        # Using as context manager
        with PostgreSQLConnection(host='localhost', database='mydb') as conn:
            results = conn.execute_query("SELECT * FROM users")
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        connection_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize PostgreSQL connection.
        
        Args:
            host: PostgreSQL server host
            port: PostgreSQL server port (default: 5432)
            database: Database name
            user: Username for authentication
            password: Password for authentication
            connection_url: Complete connection URL (overrides individual params)
            config: Configuration dictionary
            **kwargs: Additional psycopg2 connection parameters
        """
        # Build configuration from parameters
        conn_config = config or {}

        if connection_url:
            # Parse connection URL
            parsed = urlparse(connection_url)
            conn_config.update({
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'database': parsed.path.lstrip('/'),
                'user': parsed.username,
                'password': parsed.password,
            })
        else:
            # Use individual parameters
            if host:
                conn_config['host'] = host
            if port:
                conn_config['port'] = port
            if database:
                conn_config['database'] = database
            if user:
                conn_config['user'] = user
            if password:
                conn_config['password'] = password

        # Add any additional parameters
        conn_config.update(kwargs)

        # Set defaults
        conn_config.setdefault('port', 5432)
        conn_config.setdefault('connect_timeout', 30)
        conn_config.setdefault('autocommit', False)

        # Initialize parent classes
        ConfigurableComponent.__init__(self, conn_config)

        # Connection state
        self.connection: Optional[psycopg2.extensions.connection] = None
        self._cursor: Optional[psycopg2.extensions.cursor] = None

    def validate_config(self) -> bool:
        """
        Validate PostgreSQL connection configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigurationError: If required configuration is missing
        """
        required_fields = ['host', 'database', 'user']
        missing_fields = [field for field in required_fields if not self.config.get(field)]

        if missing_fields:
            raise ConfigurationError(f"Missing required configuration fields: {missing_fields}")

        # Validate port is a number
        port = self.config.get('port')
        if port and not isinstance(port, int):
            try:
                self.config['port'] = int(port)
            except ValueError as err:
                raise ConfigurationError(f"Invalid port number: {port}") from err

        return True

    def connect(self) -> psycopg2.extensions.connection:
        """
        Establish connection to PostgreSQL database.
        
        Returns:
            psycopg2 connection object
            
        Raises:
            ConnectionError: If connection cannot be established
        """
        if self.is_connected():
            logger.info("Already connected to PostgreSQL database")
            return self.connection

        try:
            # Extract connection parameters
            conn_params = {
                'host': self.config['host'],
                'port': self.config['port'],
                'database': self.config['database'],
                'user': self.config['user'],
            }

            # Add optional parameters
            if self.config.get('password'):
                conn_params['password'] = self.config['password']
            if self.config.get('connect_timeout'):
                conn_params['connect_timeout'] = self.config['connect_timeout']

            logger.info(
                "Connecting to PostgreSQL database: %s@%s:%s/%s",
                conn_params['user'],
                conn_params['host'],
                conn_params['port'],
                conn_params['database']
            )

            # Establish connection
            self.connection = psycopg2.connect(**conn_params)

            # Set autocommit mode if configured
            if self.config.get('autocommit', False):
                self.connection.autocommit = True

            logger.info("Successfully connected to PostgreSQL database")
            return self.connection

        except psycopg2.Error as e:
            error_msg = f"Failed to connect to PostgreSQL database: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

    def disconnect(self) -> None:
        """
        Close PostgreSQL database connection.
        
        Properly closes cursor and connection, handling any errors gracefully.
        """
        try:
            if self._cursor:
                self._cursor.close()
                self._cursor = None
                logger.debug("Cursor closed")

            if self.connection:
                self.connection.close()
                self.connection = None
                logger.info("Disconnected from PostgreSQL database")

        except psycopg2.Error as e:
            logger.warning("Error during disconnect: %s", e)

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_all: bool = True,
        return_dict: bool = False
    ) -> List[Any]:
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
            raise ConnectionError("Not connected to PostgreSQL database")

        try:
            # Create cursor with appropriate row factory
            if return_dict:
                cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            else:
                cursor = self.connection.cursor()

            logger.debug("Executing query: %s", query[:100] + "..." if len(query) > 100 else query)

            # Execute query
            cursor.execute(query, params)

            # Handle different query types
            if cursor.description is None:
                # Non-SELECT query (INSERT, UPDATE, DELETE, etc.)
                affected_rows = cursor.rowcount
                logger.debug("Query affected %d rows", affected_rows)
                cursor.close()
                return [{'affected_rows': affected_rows}]

            # SELECT query - fetch results
            if fetch_all:
                results = cursor.fetchall()
                logger.debug("Query returned %d rows", len(results))
                cursor.close()

                # Convert RealDictRow to regular dict if needed
                if return_dict and results:
                    return [dict(row) for row in results]
                return results
            else:
                # Return cursor for manual fetching
                return cursor

        except psycopg2.Error as e:
            error_msg = f"Query execution failed: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def execute_query_dict(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
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
        if not self.connection:
            return False

        try:
            # Test connection with a simple query
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except (psycopg2.Error, AttributeError):
            return False

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information.
        
        Returns:
            Dictionary containing connection metadata
        """
        info = {
            'database_type': 'postgresql',
            'host': self.config.get('host'),
            'port': self.config.get('port'),
            'database': self.config.get('database'),
            'user': self.config.get('user'),
            'connected': self.is_connected(),
        }

        if self.connection:
            try:
                info.update({
                    'server_version': self.connection.server_version,
                    'protocol_version': self.connection.protocol_version,
                    'autocommit': self.connection.autocommit,
                    'encoding': self.connection.encoding,
                })
            except (psycopg2.Error, AttributeError):
                pass

        return info

    def begin_transaction(self) -> None:
        """Begin a new transaction (only if not in autocommit mode)."""
        if not self.is_connected():
            raise ConnectionError("Not connected to database")

        if not self.connection.autocommit:
            # psycopg2 automatically begins transactions
            logger.debug("Transaction started")

    def commit(self) -> None:
        """Commit current transaction."""
        if not self.is_connected():
            raise ConnectionError("Not connected to database")

        try:
            self.connection.commit()
            logger.debug("Transaction committed")
        except psycopg2.Error as e:
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
        except psycopg2.Error as e:
            error_msg = f"Failed to rollback transaction: {e}"
            logger.error(error_msg)
            raise QueryError(error_msg) from e

    def get_table_names(self, schema: str = 'public') -> List[str]:
        """
        Get list of table names in specified schema.
        
        Args:
            schema: Schema name (default: 'public')
            
        Returns:
            List of table names
        """
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """

        results = self.execute_query(query, (schema,))
        return [row[0] for row in results]

    def get_column_info(self, table_name: str, schema: str = 'public') -> List[Dict[str, Any]]:
        """
        Get column information for specified table.
        
        Args:
            table_name: Name of the table
            schema: Schema name (default: 'public')
            
        Returns:
            List of dictionaries containing column information
        """
        query = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            ordinal_position
        FROM information_schema.columns
        WHERE table_name = %s AND table_schema = %s
        ORDER BY ordinal_position
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
