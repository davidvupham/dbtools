"""
Unit tests for SnowflakeConnection class with RSA authentication
"""

from unittest.mock import Mock, patch

import pytest

from gds_snowflake.connection import SnowflakeConnection


@pytest.fixture
def connection_params():
    """Fixture providing standard connection parameters for RSA auth"""
    return {
        "account": "test_account",
        "user": "test_user",
        "vault_secret_path": "secret/snowflake",
        "vault_mount_point": "kv-v2",
        "warehouse": "test_warehouse",
        "role": "test_role",
    }


@pytest.fixture
def mock_snowflake_connection():
    """Fixture providing a mocked Snowflake connection"""
    with patch("snowflake.connector.connect") as mock_connect:
        mock_conn = Mock()
        mock_conn.is_closed.return_value = False
        mock_connect.return_value = mock_conn
        yield mock_connect, mock_conn


@pytest.fixture
def mock_vault():
    """Fixture for mocking Vault operations"""
    with patch("gds_snowflake.connection.get_secret_from_vault") as mock_vault:
        mock_vault.return_value = {
            "private_key": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQkt",  # Valid base64
            "user": "vault_user",
        }
        yield mock_vault


class TestSnowflakeConnectionInit:
    """Tests for SnowflakeConnection initialization"""

    def test_init_with_all_params(self, connection_params, mock_vault):
        """Test initialization with all parameters"""
        conn = SnowflakeConnection(**connection_params)

        assert conn.account == connection_params["account"]
        assert conn.user == connection_params["user"]
        # vault_secret_path is not stored as an instance attribute
        assert conn.warehouse == connection_params["warehouse"]
        assert conn.role == connection_params["role"]
        assert conn.connection is None

    def test_init_minimal_params(self, mock_vault):
        """Test initialization with minimal parameters"""
        conn = SnowflakeConnection(account="test_account", user="test_user", vault_secret_path="secret/snowflake")

        assert conn.account == "test_account"
        assert conn.user == "test_user"
        assert conn.connection is None


class TestSnowflakeConnectionConnect:
    """Tests for connection establishment"""

    def test_connect_success(self, connection_params, mock_snowflake_connection, mock_vault):
        """Test successful connection"""
        _mock_connect, mock_conn = mock_snowflake_connection

        conn = SnowflakeConnection(**connection_params)
        result = conn.connect()

        assert result == mock_conn
        assert conn.connection == mock_conn
        mock_vault.assert_called_once()

    def test_connect_with_warehouse_and_role(self, connection_params, mock_snowflake_connection, mock_vault):
        """Test connection with warehouse and role"""
        mock_connect, _mock_conn = mock_snowflake_connection

        conn = SnowflakeConnection(**connection_params)
        conn.connect()

        # Verify connection was called with correct parameters
        mock_connect.assert_called_once()
        call_args = mock_connect.call_args[1]
        assert call_args["account"] == connection_params["account"]
        assert call_args["user"] == connection_params["user"]
        assert call_args["warehouse"] == connection_params["warehouse"]
        assert call_args["role"] == connection_params["role"]

    def test_connect_failure(self, connection_params, mock_vault):
        """Test connection failure"""
        with patch("snowflake.connector.connect", side_effect=Exception("Connection failed")):
            conn = SnowflakeConnection(**connection_params)

            with pytest.raises(Exception):
                conn.connect()


class TestSnowflakeConnectionQueries:
    """Tests for query execution"""

    def test_execute_query(self, connection_params, mock_snowflake_connection, mock_vault):
        """Test query execution"""
        _mock_connect, mock_conn = mock_snowflake_connection
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
        mock_cursor.execute = Mock()
        mock_cursor.close = Mock()
        # Return cursor directly, not as context manager
        mock_conn.cursor.return_value = mock_cursor

        conn = SnowflakeConnection(**connection_params)
        conn.connect()

        result = conn.execute_query("SELECT * FROM test_table")

        assert result == [("row1",), ("row2",)]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table")

    def test_execute_query_with_params(self, connection_params, mock_snowflake_connection, mock_vault):
        """Test query execution with parameters"""
        _mock_connect, mock_conn = mock_snowflake_connection
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [("result",)]
        mock_cursor.execute = Mock()
        mock_cursor.close = Mock()
        # Return cursor directly, not as context manager
        mock_conn.cursor.return_value = mock_cursor

        conn = SnowflakeConnection(**connection_params)
        conn.connect()

        result = conn.execute_query("SELECT * FROM test WHERE id = %s", ("123",))

        assert result == [("result",)]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test WHERE id = %s", ("123",))

    def test_execute_query_dict(self, connection_params, mock_snowflake_connection, mock_vault):
        """Test query execution returning dictionaries"""
        _mock_connect, mock_conn = mock_snowflake_connection

        # Mock regular cursor
        mock_cursor = Mock()
        mock_cursor.execute = Mock()
        mock_cursor.close = Mock()

        # Mock dict cursor
        mock_dict_cursor = Mock()
        mock_dict_cursor.fetchall.return_value = [{"col1": "val1", "col2": "val2"}]
        mock_dict_cursor.execute = Mock()
        mock_dict_cursor.close = Mock()

        # Return dict cursor when DictCursor is passed
        def cursor_factory(cursor_class=None):
            if cursor_class is not None:
                return mock_dict_cursor
            return mock_cursor

        mock_conn.cursor.side_effect = cursor_factory

        conn = SnowflakeConnection(**connection_params)
        conn.connect()

        result = conn.execute_query_dict("SELECT col1, col2 FROM test")

        assert result == [{"col1": "val1", "col2": "val2"}]


class TestSnowflakeConnectionLifecycle:
    """Tests for connection lifecycle management"""

    def test_close_connection(self, connection_params, mock_snowflake_connection, mock_vault):
        """Test connection closing"""
        _mock_connect, mock_conn = mock_snowflake_connection

        conn = SnowflakeConnection(**connection_params)
        conn.connect()
        conn.close()

        mock_conn.close.assert_called_once()
        # Connection object still exists after close
        assert conn.connection is not None

    def test_close_when_no_connection(self, connection_params, mock_vault):
        """Test closing when no connection exists"""
        conn = SnowflakeConnection(**connection_params)

        # Should not raise an exception
        conn.close()
        assert conn.connection is None

    def test_context_manager(self, connection_params, mock_snowflake_connection, mock_vault):
        """Test context manager functionality"""
        _mock_connect, mock_conn = mock_snowflake_connection

        with SnowflakeConnection(**connection_params) as conn:
            assert conn.connection == mock_conn

        mock_conn.close.assert_called_once()

    def test_switch_account(self, connection_params, mock_snowflake_connection, mock_vault):
        """Test account switching"""
        _mock_connect, _mock_conn = mock_snowflake_connection

        conn = SnowflakeConnection(**connection_params)

        original_account = conn.account
        conn.switch_account("new_account")

        assert conn.account == "new_account"
        assert conn.account != original_account
        # Connection is set after switch_account calls connect()
        assert conn.connection is not None
