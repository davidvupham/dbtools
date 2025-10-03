"""
Unit tests for gds_snowflake.connection module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import snowflake.connector
from gds_snowflake.connection import SnowflakeConnection


class TestSnowflakeConnection(unittest.TestCase):
    """Test cases for SnowflakeConnection class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.account = 'test_account'
        self.user = 'test_user'
        self.password = 'test_password'
        self.warehouse = 'test_warehouse'
        self.role = 'test_role'
        self.database = 'test_database'
        
    def test_init(self):
        """Test SnowflakeConnection initialization"""
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password,
            warehouse=self.warehouse,
            role=self.role,
            database=self.database
        )
        
        self.assertEqual(conn.account, self.account)
        self.assertEqual(conn.user, self.user)
        self.assertEqual(conn.password, self.password)
        self.assertEqual(conn.warehouse, self.warehouse)
        self.assertEqual(conn.role, self.role)
        self.assertEqual(conn.database, self.database)
        self.assertIsNone(conn.connection)
        
    def test_init_minimal(self):
        """Test SnowflakeConnection with minimal parameters"""
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        
        self.assertEqual(conn.account, self.account)
        self.assertEqual(conn.user, self.user)
        self.assertEqual(conn.password, self.password)
        self.assertIsNone(conn.warehouse)
        self.assertIsNone(conn.role)
        self.assertIsNone(conn.database)
        
    @patch('snowflake.connector.connect')
    def test_connect_success(self, mock_connect):
        """Test successful connection"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        
        result = conn.connect()
        
        mock_connect.assert_called_once_with(
            account=self.account,
            user=self.user,
            password=self.password
        )
        self.assertEqual(result, mock_connection)
        self.assertEqual(conn.connection, mock_connection)
        
    @patch('snowflake.connector.connect')
    def test_connect_with_warehouse_and_role(self, mock_connect):
        """Test connection with warehouse and role"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password,
            warehouse=self.warehouse,
            role=self.role
        )
        
        conn.connect()
        
        mock_connect.assert_called_once_with(
            account=self.account,
            user=self.user,
            password=self.password,
            warehouse=self.warehouse,
            role=self.role
        )
        
    @patch('snowflake.connector.connect')
    def test_connect_failure(self, mock_connect):
        """Test connection failure"""
        mock_connect.side_effect = Exception("Connection failed")
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        
        with self.assertRaises(Exception) as context:
            conn.connect()
        
        self.assertIn("Connection failed", str(context.exception))
        
    @patch('snowflake.connector.connect')
    def test_get_connection_when_none(self, mock_connect):
        """Test get_connection when connection is None"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        
        result = conn.get_connection()
        
        self.assertEqual(result, mock_connection)
        mock_connect.assert_called_once()
        
    @patch('snowflake.connector.connect')
    def test_get_connection_when_closed(self, mock_connect):
        """Test get_connection when connection is closed"""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = True
        mock_connect.return_value = mock_connection
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        conn.connection = mock_connection
        
        result = conn.get_connection()
        
        self.assertEqual(result, mock_connection)
        # Should reconnect because connection was closed
        self.assertEqual(mock_connect.call_count, 1)
        
    @patch('snowflake.connector.connect')
    def test_get_connection_when_open(self, mock_connect):
        """Test get_connection when connection is already open"""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        conn.connection = mock_connection
        
        result = conn.get_connection()
        
        self.assertEqual(result, mock_connection)
        # Should not reconnect
        mock_connect.assert_not_called()
        
    def test_close_connection(self):
        """Test closing connection"""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = False
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        conn.connection = mock_connection
        
        conn.close()
        
        mock_connection.close.assert_called_once()
        
    def test_close_when_no_connection(self):
        """Test closing when no connection exists"""
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        
        # Should not raise an error
        conn.close()
        
    def test_close_when_already_closed(self):
        """Test closing when connection already closed"""
        mock_connection = Mock()
        mock_connection.is_closed.return_value = True
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        conn.connection = mock_connection
        
        conn.close()
        
        # Should not call close on already closed connection
        mock_connection.close.assert_not_called()
        
    @patch('snowflake.connector.connect')
    def test_execute_query(self, mock_connect):
        """Test executing a query"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [('result1',), ('result2',)]
        
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        mock_connect.return_value = mock_connection
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        conn.connection = mock_connection
        
        results = conn.execute_query("SELECT * FROM table")
        
        mock_cursor.execute.assert_called_once_with("SELECT * FROM table")
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()
        self.assertEqual(results, [('result1',), ('result2',)])
        
    @patch('snowflake.connector.connect')
    def test_execute_query_with_params(self, mock_connect):
        """Test executing a query with parameters"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [('result',)]
        
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        mock_connect.return_value = mock_connection
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        conn.connection = mock_connection
        
        results = conn.execute_query(
            "SELECT * FROM table WHERE id = ?",
            params=(123,)
        )
        
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM table WHERE id = ?",
            (123,)
        )
        self.assertEqual(results, [('result',)])
        
    @patch('snowflake.connector.connect')
    def test_execute_query_dict(self, mock_connect):
        """Test executing a query returning dictionaries"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'col1': 'val1', 'col2': 'val2'},
            {'col1': 'val3', 'col2': 'val4'}
        ]
        
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        mock_connect.return_value = mock_connection
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        conn.connection = mock_connection
        
        results = conn.execute_query_dict("SELECT * FROM table")
        
        # Verify DictCursor was requested
        mock_connection.cursor.assert_called_once_with(snowflake.connector.DictCursor)
        mock_cursor.execute.assert_called_once_with("SELECT * FROM table")
        self.assertEqual(len(results), 2)
        
    @patch('snowflake.connector.connect')
    def test_execute_query_failure(self, mock_connect):
        """Test query execution failure"""
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Query failed")
        
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_closed.return_value = False
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        conn.connection = mock_connection
        
        with self.assertRaises(Exception) as context:
            conn.execute_query("SELECT * FROM table")
        
        self.assertIn("Query failed", str(context.exception))
        
    @patch('snowflake.connector.connect')
    def test_switch_account(self, mock_connect):
        """Test switching to a different account"""
        mock_connection1 = Mock()
        mock_connection2 = Mock()
        mock_connect.side_effect = [mock_connection1, mock_connection2]
        
        conn = SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        )
        conn.connect()
        
        new_account = 'new_account'
        result = conn.switch_account(new_account)
        
        # Should close old connection
        mock_connection1.close.assert_called_once()
        
        # Should connect to new account
        self.assertEqual(conn.account, new_account)
        self.assertEqual(result, mock_connection2)
        self.assertEqual(mock_connect.call_count, 2)
        
    @patch('snowflake.connector.connect')
    def test_context_manager(self, mock_connect):
        """Test using SnowflakeConnection as context manager"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        with SnowflakeConnection(
            account=self.account,
            user=self.user,
            password=self.password
        ) as conn:
            self.assertEqual(conn.connection, mock_connection)
        
        # Should have connected and closed
        mock_connect.assert_called_once()
        mock_connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
