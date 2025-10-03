"""
Pytest version of gds_snowflake.connection tests
Can be run with: pytest tests/test_connection_pytest.py
"""

import pytest
from unittest.mock import Mock, patch
import snowflake.connector
from gds_snowflake.connection import SnowflakeConnection


@pytest.fixture
def connection_params():
    """Fixture providing standard connection parameters"""
    return {
        'account': 'test_account',
        'user': 'test_user',
        'password': 'test_password',
        'warehouse': 'test_warehouse',
        'role': 'test_role'
    }


@pytest.fixture
def mock_snowflake_connection():
    """Fixture providing a mocked Snowflake connection"""
    with patch('snowflake.connector.connect') as mock_connect:
        mock_conn = Mock()
        mock_conn.is_closed.return_value = False
        mock_connect.return_value = mock_conn
        yield mock_connect, mock_conn


class TestSnowflakeConnectionInit:
    """Tests for SnowflakeConnection initialization"""
    
    def test_init_with_all_params(self, connection_params):
        """Test initialization with all parameters"""
        conn = SnowflakeConnection(**connection_params)
        
        assert conn.account == connection_params['account']
        assert conn.user == connection_params['user']
        assert conn.password == connection_params['password']
        assert conn.warehouse == connection_params['warehouse']
        assert conn.role == connection_params['role']
        assert conn.connection is None
        
    def test_init_minimal_params(self):
        """Test initialization with minimal parameters"""
        conn = SnowflakeConnection(
            account='test_account',
            user='test_user',
            password='test_password'
        )
        
        assert conn.account == 'test_account'
        assert conn.warehouse is None
        assert conn.role is None


class TestSnowflakeConnectionConnect:
    """Tests for connection establishment"""
    
    def test_connect_success(self, connection_params, mock_snowflake_connection):
        """Test successful connection"""
        mock_connect, mock_conn = mock_snowflake_connection
        
        conn = SnowflakeConnection(**connection_params)
        result = conn.connect()
        
        assert result == mock_conn
        assert conn.connection == mock_conn
        mock_connect.assert_called_once()
        
    def test_connect_with_warehouse_and_role(self, connection_params, mock_snowflake_connection):
        """Test connection includes warehouse and role"""
        mock_connect, mock_conn = mock_snowflake_connection
        
        conn = SnowflakeConnection(**connection_params)
        conn.connect()
        
        call_args = mock_connect.call_args[1]
        assert call_args['warehouse'] == connection_params['warehouse']
        assert call_args['role'] == connection_params['role']
        
    def test_connect_failure(self, connection_params):
        """Test connection failure handling"""
        with patch('snowflake.connector.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            conn = SnowflakeConnection(**connection_params)
            
            with pytest.raises(Exception, match="Connection failed"):
                conn.connect()


class TestSnowflakeConnectionQueries:
    """Tests for query execution"""
    
    def test_execute_query(self, connection_params):
        """Test executing a SQL query"""
        with patch('snowflake.connector.connect') as mock_connect:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [('result1',), ('result2',)]
            
            mock_conn = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.is_closed.return_value = False
            mock_connect.return_value = mock_conn
            
            conn = SnowflakeConnection(**connection_params)
            conn.connection = mock_conn
            
            results = conn.execute_query("SELECT * FROM table")
            
            assert len(results) == 2
            assert results[0] == ('result1',)
            mock_cursor.execute.assert_called_once_with("SELECT * FROM table")
            
    def test_execute_query_with_params(self, connection_params):
        """Test executing query with parameters"""
        with patch('snowflake.connector.connect') as mock_connect:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [('result',)]
            
            mock_conn = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.is_closed.return_value = False
            mock_connect.return_value = mock_conn
            
            conn = SnowflakeConnection(**connection_params)
            conn.connection = mock_conn
            
            results = conn.execute_query(
                "SELECT * FROM table WHERE id = ?",
                params=(123,)
            )
            
            mock_cursor.execute.assert_called_once_with(
                "SELECT * FROM table WHERE id = ?",
                (123,)
            )
            
    def test_execute_query_dict(self, connection_params):
        """Test executing query returning dictionaries"""
        with patch('snowflake.connector.connect') as mock_connect:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [
                {'col1': 'val1'},
                {'col1': 'val2'}
            ]
            
            mock_conn = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.is_closed.return_value = False
            mock_connect.return_value = mock_conn
            
            conn = SnowflakeConnection(**connection_params)
            conn.connection = mock_conn
            
            results = conn.execute_query_dict("SELECT * FROM table")
            
            assert len(results) == 2
            mock_conn.cursor.assert_called_once_with(snowflake.connector.DictCursor)


class TestSnowflakeConnectionLifecycle:
    """Tests for connection lifecycle management"""
    
    def test_close_connection(self, connection_params):
        """Test closing an open connection"""
        mock_conn = Mock()
        mock_conn.is_closed.return_value = False
        
        conn = SnowflakeConnection(**connection_params)
        conn.connection = mock_conn
        
        conn.close()
        
        mock_conn.close.assert_called_once()
        
    def test_close_when_no_connection(self, connection_params):
        """Test closing when no connection exists"""
        conn = SnowflakeConnection(**connection_params)
        conn.close()  # Should not raise an error
        
    def test_context_manager(self, connection_params, mock_snowflake_connection):
        """Test using as context manager"""
        mock_connect, mock_conn = mock_snowflake_connection
        
        with SnowflakeConnection(**connection_params) as conn:
            assert conn.connection == mock_conn
        
        mock_conn.close.assert_called_once()
        
    def test_switch_account(self, connection_params, mock_snowflake_connection):
        """Test switching to a different account"""
        mock_connect, mock_conn = mock_snowflake_connection
        mock_conn2 = Mock()
        mock_connect.side_effect = [mock_conn, mock_conn2]
        
        conn = SnowflakeConnection(**connection_params)
        conn.connect()
        
        result = conn.switch_account('new_account')
        
        assert conn.account == 'new_account'
        assert result == mock_conn2
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
