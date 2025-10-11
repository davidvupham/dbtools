"""
Test suite for PostgreSQL connection implementation.
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

from gds_database import ConfigurationError, ConnectionError, QueryError

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
            'password': 'testpass',
            'sslmode': 'require',
            'application_name': 'unit-test',
        }
        mock_psycopg2.reset_mock()
        mock_psycopg2.connect.side_effect = None

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

    def test_initialization_with_kwargs(self):
        """Test initialization with supplementary kwargs."""
        conn = PostgreSQLConnection(
            host='localhost',
            database='testdb',
            user='testuser',
            options='-c search_path=public'
        )

        self.assertEqual(conn.config['options'], '-c search_path=public')

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

    def test_connect_success(self):
        """Test successful database connection."""
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection

        conn = PostgreSQLConnection(config=self.config)
        result = conn.connect()

        self.assertEqual(result, mock_connection)
        self.assertEqual(conn.connection, mock_connection)
        mock_psycopg2.connect.assert_called_once_with(
            host='localhost',
            port=5432,
            database='testdb',
            user='testuser',
            password='testpass',
            connect_timeout=30,
            sslmode='require',
            application_name='unit-test'
        )

    def test_connect_failure(self):
        """Test connection failure handling."""
        mock_psycopg2.connect.side_effect = mock_psycopg2.Error("Connection failed")
        self.addCleanup(lambda: setattr(mock_psycopg2.connect, 'side_effect', None))

        conn = PostgreSQLConnection(config=self.config)

        with self.assertRaises(ConnectionError):
            conn.connect()

    def test_connect_returns_existing_connection(self):
        """Connection should return existing handle when already connected."""
        conn = PostgreSQLConnection(config=self.config)
        existing_connection = Mock()
        conn.connection = existing_connection
        conn.is_connected = Mock(return_value=True)

        result = conn.connect()

        self.assertIs(result, existing_connection)
        conn.is_connected.assert_called_once()

    def test_build_connection_parameters_does_not_mutate_config(self):
        """Ensure helper copies configuration values."""
        conn = PostgreSQLConnection(config=self.config)
        params = conn._build_connection_parameters()

        self.assertIn('host', params)
        self.assertIn('host', conn.config)
        params['host'] = 'mutated'
        self.assertEqual(conn.config['host'], 'localhost')

    def test_connect_respects_autocommit_flag(self):
        """Verify autocommit flag is applied after connection."""
        config = dict(self.config)
        config['autocommit'] = True

        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection

        conn = PostgreSQLConnection(config=config)
        conn.connect()

        self.assertTrue(mock_connection.autocommit)

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

    def test_disconnect_handles_close_error(self):
        """Disconnect should swallow errors from cursor/connection close."""
        conn = PostgreSQLConnection(config=self.config)
        broken_cursor = Mock()
        broken_cursor.close.side_effect = mock_psycopg2.Error("cursor error")
        conn._cursor = broken_cursor

        broken_connection = Mock()
        broken_connection.close.side_effect = mock_psycopg2.Error("close error")
        conn.connection = broken_connection

        conn.disconnect()

        broken_cursor.close.assert_called_once()
        broken_connection.close.assert_called_once()
        self.assertIsNone(conn.connection)
        self.assertIsNone(conn._cursor)

    def test_is_connected_true(self):
        """Test is_connected when connection is active."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_connection.closed = 0
        mock_connection.poll = Mock()

        conn.connection = mock_connection

        self.assertTrue(conn.is_connected())

    def test_is_connected_false(self):
        """Test is_connected when not connected."""
        conn = PostgreSQLConnection(config=self.config)
        self.assertFalse(conn.is_connected())

    def test_is_connected_handles_poll_failure(self):
        """Poll errors should mark connection as inactive."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_connection.closed = 0
        mock_connection.poll.side_effect = mock_psycopg2.Error("poll error")

        conn.connection = mock_connection

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
        mock_cursor.close.assert_called_once()
        self.assertIsNone(conn._cursor)

    def test_execute_query_closes_existing_cursor_before_new_query(self):
        """Existing cursor should be closed before running new SELECT."""
        conn = PostgreSQLConnection(config=self.config)
        conn.connection = Mock()
        conn.is_connected = Mock(return_value=True)
        conn._cursor = Mock()
        conn.close_active_cursor = Mock()

        new_cursor = Mock()
        new_cursor.description = [('id',)]
        new_cursor.fetchall.return_value = [(1,)]
        conn.connection.cursor.return_value = new_cursor

        conn.execute_query("SELECT 1")

        conn.close_active_cursor.assert_called_once()
        new_cursor.close.assert_called_once()
        self.assertIsNone(conn._cursor)

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
        mock_cursor.close.assert_called_once()
        self.assertIsNone(conn._cursor)

    def test_execute_query_not_connected(self):
        """Test executing query when not connected."""
        conn = PostgreSQLConnection(config=self.config)

        with self.assertRaises(ConnectionError):
            conn.execute_query("SELECT 1")

    def test_execute_query_dict(self):
        """Test executing query with dictionary results."""
        conn = PostgreSQLConnection(config=self.config)
        # Mock is_connected and execute_query
        conn.is_connected = Mock(return_value=True)
        conn.execute_query = Mock(return_value=[{'id': 1, 'name': 'test'}])

        results = conn.execute_query_dict("SELECT * FROM users")

        conn.execute_query.assert_called_once_with("SELECT * FROM users", None, return_dict=True)
        self.assertEqual(results, [{'id': 1, 'name': 'test'}])

    def test_execute_query_streaming_returns_open_cursor(self):
        """Ensure fetch_all=False leaves cursor open for caller."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_cursor = Mock()

        conn.connection = mock_connection
        conn.is_connected = Mock(return_value=True)
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.description = [('id',)]

        cursor = conn.execute_query("SELECT 1", fetch_all=False)

        self.assertIs(cursor, mock_cursor)
        self.assertIs(conn._cursor, mock_cursor)

    def test_execute_query_return_dict(self):
        """SELECT with return_dict should convert results to dicts."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_cursor = Mock()

        conn.connection = mock_connection
        conn.is_connected = Mock(return_value=True)
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.description = [('id',)]
        mock_cursor.fetchall.return_value = [{'id': 1}]

        results = conn.execute_query("SELECT id FROM users", return_dict=True)

        self.assertEqual(results, [{'id': 1}])
        mock_connection.cursor.assert_called_once_with(
            cursor_factory=mock_psycopg2.extras.RealDictCursor
        )
        mock_cursor.close.assert_called_once()
        self.assertIsNone(conn._cursor)

    def test_execute_query_raises_query_error(self):
        """Database errors should surface as QueryError."""
        conn = PostgreSQLConnection(config=self.config)
        conn.connection = Mock()
        conn.is_connected = Mock(return_value=True)
        conn.connection.cursor.side_effect = mock_psycopg2.Error("boom")

        with self.assertRaises(QueryError):
            conn.execute_query("SELECT 1")

    def test_close_active_cursor_closes_tracked_cursor(self):
        """close_active_cursor should shut down any tracked cursor."""
        conn = PostgreSQLConnection(config=self.config)
        mock_cursor = Mock()
        conn._cursor = mock_cursor

        conn.close_active_cursor()

        mock_cursor.close.assert_called_once()
        self.assertIsNone(conn._cursor)

    def test_close_active_cursor_handles_close_error(self):
        """Cursor close errors should be swallowed."""
        conn = PostgreSQLConnection(config=self.config)
        mock_cursor = Mock()
        mock_cursor.close.side_effect = mock_psycopg2.Error("close failure")
        conn._cursor = mock_cursor

        conn.close_active_cursor()

        mock_cursor.close.assert_called_once()
        self.assertIsNone(conn._cursor)

    def test_get_connection_info(self):
        """Test getting connection information."""
        conn = PostgreSQLConnection(config=self.config)

        info = conn.get_connection_info()

        expected_keys = {'database_type', 'host', 'port', 'database', 'user', 'connected'}
        self.assertEqual(set(info.keys()), expected_keys)
        self.assertEqual(info['database_type'], 'postgresql')
        self.assertEqual(info['host'], 'localhost')
        self.assertEqual(info['database'], 'testdb')

    def test_get_connection_info_includes_metadata(self):
        """Active connection should populate server metadata."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_connection.closed = 0
        mock_connection.poll = Mock()
        mock_connection.server_version = '15.4'
        mock_connection.protocol_version = 3
        mock_connection.autocommit = False
        mock_connection.encoding = 'UTF8'

        conn.connection = mock_connection

        info = conn.get_connection_info()

        self.assertEqual(info['server_version'], '15.4')
        self.assertEqual(info['protocol_version'], 3)
        self.assertIn('autocommit', info)
        self.assertEqual(info['encoding'], 'UTF8')

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

    def test_initialize_and_cleanup_delegate(self):
        """Resource manager helpers should delegate to connect/disconnect."""
        conn = PostgreSQLConnection(config=self.config)
        conn.connect = Mock()
        conn.disconnect = Mock()

        conn.initialize()
        conn.connect.assert_called_once()

        conn.cleanup()
        conn.disconnect.assert_called_once()

    def test_is_initialized_delegates_to_is_connected(self):
        """is_initialized should mirror is_connected."""
        conn = PostgreSQLConnection(config=self.config)
        conn.is_connected = Mock(return_value=True)

        self.assertTrue(conn.is_initialized())
        conn.is_connected.assert_called_once()

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

    def test_begin_transaction_not_connected(self):
        """begin_transaction should raise when disconnected."""
        conn = PostgreSQLConnection(config=self.config)
        conn.is_connected = Mock(return_value=False)

        with self.assertRaises(ConnectionError):
            conn.begin_transaction()

    def test_begin_transaction_logs_when_autocommit_disabled(self):
        """Ensure begin_transaction executes silently when autocommit is False."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_connection.autocommit = False
        conn.connection = mock_connection
        conn.is_connected = Mock(return_value=True)

        conn.begin_transaction()

    def test_commit_error_raises_query_error(self):
        """Commit failures should raise QueryError."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_connection.commit.side_effect = mock_psycopg2.Error("commit error")
        conn.connection = mock_connection
        conn.is_connected = Mock(return_value=True)

        with self.assertRaises(QueryError):
            conn.commit()

    def test_rollback_error_raises_query_error(self):
        """Rollback failures should raise QueryError."""
        conn = PostgreSQLConnection(config=self.config)
        mock_connection = Mock()
        mock_connection.rollback.side_effect = mock_psycopg2.Error("rollback error")
        conn.connection = mock_connection
        conn.is_connected = Mock(return_value=True)

        with self.assertRaises(QueryError):
            conn.rollback()

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
