"""
Test suite for PostgreSQL connection implementation.
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

from gds_database import ConfigurationError, ConnectionError

# Mock psycopg2 to avoid import errors in test environment
mock_psycopg2 = MagicMock()
mock_psycopg2.Error = Exception
mock_psycopg2.extensions = MagicMock()
mock_psycopg2.extras = MagicMock()

with patch.dict('sys.modules', {'psycopg2': mock_psycopg2, 'psycopg2.extras': mock_psycopg2.extras}):
    from gds_postgres import PostgreSQLConnection


class TestPostgreSQLConnection(unittest.TestCase):
    """Test PostgreSQL connection implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'testdb',
            'user': 'testuser',
            'password': 'testpass'
        }

    def test_initialization_with_parameters(self):
        """Test initialization with individual parameters."""
        conn = PostgreSQLConnection(
            host='localhost',
            port=5432,
            database='testdb',
            user='testuser',
            password='testpass'
        )

        self.assertEqual(conn.config['host'], 'localhost')
        self.assertEqual(conn.config['port'], 5432)
        self.assertEqual(conn.config['database'], 'testdb')
        self.assertEqual(conn.config['user'], 'testuser')
        self.assertEqual(conn.config['password'], 'testpass')

    def test_initialization_with_config(self):
        """Test initialization with configuration dictionary."""
        conn = PostgreSQLConnection(config=self.config)

        self.assertEqual(conn.config['host'], 'localhost')
        self.assertEqual(conn.config['database'], 'testdb')

    def test_initialization_with_connection_url(self):
        """Test initialization with connection URL."""
        url = 'postgresql://testuser:testpass@localhost:5432/testdb'
        conn = PostgreSQLConnection(connection_url=url)

        self.assertEqual(conn.config['host'], 'localhost')
        self.assertEqual(conn.config['port'], 5432)
        self.assertEqual(conn.config['database'], 'testdb')
        self.assertEqual(conn.config['user'], 'testuser')
        self.assertEqual(conn.config['password'], 'testpass')

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        conn = PostgreSQLConnection(config=self.config)
        self.assertTrue(conn.validate_config())

    def test_validate_config_missing_required(self):
        """Test configuration validation with missing required fields."""
        invalid_config = {'host': 'localhost'}

        with self.assertRaises(ConfigurationError):
            PostgreSQLConnection(config=invalid_config)

    def test_validate_config_invalid_port(self):
        """Test configuration validation with invalid port."""
        invalid_config = self.config.copy()
        invalid_config['port'] = 'invalid'

        with self.assertRaises(ConfigurationError):
            PostgreSQLConnection(config=invalid_config)

    @patch('gds_postgres.connection.psycopg2.connect')
    def test_connect_success(self, mock_connect):
        """Test successful database connection."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        conn = PostgreSQLConnection(config=self.config)
        result = conn.connect()

        self.assertEqual(result, mock_connection)
        self.assertEqual(conn.connection, mock_connection)
        mock_connect.assert_called_once()

    @patch('gds_postgres.connection.psycopg2.connect')
    def test_connect_failure(self, mock_connect):
        """Test connection failure handling."""
        mock_connect.side_effect = mock_psycopg2.Error("Connection failed")

        conn = PostgreSQLConnection(config=self.config)

        with self.assertRaises(ConnectionError):
            conn.connect()

    def test_disconnect(self):
        """Test database disconnection."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_cursor = Mock()

        conn.connection = mock_connection
        conn._cursor = mock_cursor

        conn.disconnect()

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
        self.assertIsNone(conn.connection)
        self.assertIsNone(conn._cursor)

    def test_is_connected_true(self):
        """Test is_connected when connection is active."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_cursor = Mock()

        # Mock successful connection test
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1,)

        conn.connection = mock_connection

        self.assertTrue(conn.is_connected())

    def test_is_connected_false(self):
        """Test is_connected when not connected."""
        conn = PostgreSQLConnection(config=self.config)
        self.assertFalse(conn.is_connected())

    def test_execute_query_select(self):
        """Test executing SELECT query."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_cursor = Mock()

        # Mock connection and cursor
        conn.connection = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.description = [('id',), ('name',)]  # Simulate SELECT query
        mock_cursor.fetchall.return_value = [(1, 'test'), (2, 'test2')]

        # Mock is_connected to return True
        conn.is_connected = Mock(return_value=True)

        results = conn.execute_query("SELECT * FROM users")

        mock_cursor.execute.assert_called_once_with("SELECT * FROM users", None)
        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(results, [(1, 'test'), (2, 'test2')])

    def test_execute_query_insert(self):
        """Test executing INSERT query."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_cursor = Mock()

        # Mock connection and cursor for INSERT (no description)
        conn.connection = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.description = None  # Simulate INSERT/UPDATE/DELETE
        mock_cursor.rowcount = 1

        # Mock is_connected to return True
        conn.is_connected = Mock(return_value=True)

        results = conn.execute_query("INSERT INTO users VALUES (%s, %s)", ('test', 'user'))

        mock_cursor.execute.assert_called_once_with("INSERT INTO users VALUES (%s, %s)", ('test', 'user'))
        self.assertEqual(results, [{'affected_rows': 1}])

    def test_execute_query_not_connected(self):
        """Test executing query when not connected."""
        conn = PostgreSQLConnection(config=self.config)

        with self.assertRaises(ConnectionError):
            conn.execute_query("SELECT 1")

    def test_execute_query_dict(self):
        """Test executing query with dictionary results."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()

        # Mock is_connected and execute_query
        conn.is_connected = Mock(return_value=True)
        conn.execute_query = Mock(return_value=[{'id': 1, 'name': 'test'}])

        results = conn.execute_query_dict("SELECT * FROM users")

        conn.execute_query.assert_called_once_with("SELECT * FROM users", None, return_dict=True)
        self.assertEqual(results, [{'id': 1, 'name': 'test'}])

    def test_get_connection_info(self):
        """Test getting connection information."""
        conn = PostgreSQLConnection(config=self.config)

        info = conn.get_connection_info()

        expected_keys = {'database_type', 'host', 'port', 'database', 'user', 'connected'}
        self.assertEqual(set(info.keys()), expected_keys)
        self.assertEqual(info['database_type'], 'postgresql')
        self.assertEqual(info['host'], 'localhost')
        self.assertEqual(info['database'], 'testdb')

    def test_context_manager(self):
        """Test using connection as context manager."""
        conn = PostgreSQLConnection(config=self.config)

        # Mock the ResourceManager methods
        conn.initialize = Mock()
        conn.cleanup = Mock()

        with conn as context_conn:
            self.assertEqual(context_conn, conn)
            conn.initialize.assert_called_once()

        conn.cleanup.assert_called_once()

    def test_transaction_methods(self):
        """Test transaction management methods."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_connection.autocommit = False

        conn.connection = mock_connection
        conn.is_connected = Mock(return_value=True)

        # Test commit
        conn.commit()
        mock_connection.commit.assert_called_once()

        # Test rollback
        conn.rollback()
        mock_connection.rollback.assert_called_once()

    def test_get_table_names(self):
        """Test getting table names."""
        conn = PostgreSQLConnection(config=self.config)

        # Mock execute_query to return table names
        conn.execute_query = Mock(return_value=[('users',), ('products',), ('orders',)])

        tables = conn.get_table_names()

        conn.execute_query.assert_called_once()
        self.assertEqual(tables, ['users', 'products', 'orders'])

    def test_get_column_info(self):
        """Test getting column information."""
        conn = PostgreSQLConnection(config=self.config)

        # Mock execute_query_dict to return column info
        expected_columns = [
            {'column_name': 'id', 'data_type': 'integer', 'is_nullable': 'NO'},
            {'column_name': 'name', 'data_type': 'varchar', 'is_nullable': 'YES'}
        ]
        conn.execute_query_dict = Mock(return_value=expected_columns)

        columns = conn.get_column_info('users')

        conn.execute_query_dict.assert_called_once()
        self.assertEqual(columns, expected_columns)


if __name__ == '__main__':
    unittest.main()
