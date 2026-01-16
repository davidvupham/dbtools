"""
Final comprehensive tests for SnowflakeConnection class with proper mocking
"""

from unittest.mock import Mock, patch

import pytest

from gds_snowflake.connection import SnowflakeConnection


@pytest.fixture
def connection_params():
    """Fixture providing standard connection parameters for RSA auth"""
    return {"account": "test_account", "user": "test_user", "warehouse": "test_warehouse", "role": "test_role"}


@pytest.fixture
def mock_vault_disabled():
    """Fixture that completely bypasses Vault operations"""
    with patch("gds_snowflake.connection.get_secret_from_vault") as mock_vault:
        # Don't call vault at all by providing no vault_secret_path
        yield mock_vault


@pytest.fixture
def mock_vault_working():
    """Fixture providing working Vault operations"""
    with patch("gds_snowflake.connection.get_secret_from_vault") as mock_vault:
        mock_vault.return_value = {
            "private_key": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQkt",  # Proper base64
            "user": "vault_user",
        }
        yield mock_vault


@pytest.fixture
def mock_snowflake_connection():
    """Fixture providing a mocked Snowflake connection"""
    with patch("snowflake.connector.connect") as mock_connect:
        mock_conn = Mock()
        mock_conn.is_closed.return_value = False
        mock_conn.close = Mock()

        # Mock cursor - returned directly, not as context manager
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
        mock_cursor.fetchone.return_value = ("account_name", "user", "role", "warehouse", "database", "7.0.0", "region")
        mock_cursor.description = [("col1",), ("col2",)]
        mock_cursor.execute = Mock()
        mock_cursor.close = Mock()

        # Return cursor directly
        mock_conn.cursor.return_value = mock_cursor

        mock_connect.return_value = mock_conn
        yield mock_connect, mock_conn


class TestSnowflakeConnectionInit:
    """Tests for SnowflakeConnection initialization"""

    def test_init_minimal_params_no_vault(self, mock_vault_working):
        """Test initialization with minimal parameters and vault"""
        conn = SnowflakeConnection(account="test_account", user="test_user", vault_secret_path="secret/snowflake")

        assert conn.account == "test_account"
        assert conn.user == "test_user"
        assert conn.connection is None

    def test_init_with_vault_path(self, connection_params, mock_vault_working):
        """Test initialization with vault path"""
        params = connection_params.copy()
        params["vault_secret_path"] = "secret/snowflake"

        conn = SnowflakeConnection(**params)

        assert conn.account == params["account"]
        assert conn.user == params["user"]
        # vault_secret_path is not stored as an instance attribute


class TestSnowflakeConnectionConnect:
    """Tests for connection establishment"""

    def test_connect_success_with_vault(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test successful connection with vault"""
        _mock_connect, mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params["vault_secret_path"] = "secret/snowflake"

        conn = SnowflakeConnection(**params)
        result = conn.connect()

        assert result == mock_conn
        assert conn.connection == mock_conn
        mock_vault_working.assert_called_once()

    def test_connect_no_vault_no_private_key(self, connection_params, mock_vault_disabled):
        """Test connection fails without vault or private key"""
        # Exception is raised in __init__, not connect()
        with pytest.raises(RuntimeError, match="Vault secret path must be provided"):
            SnowflakeConnection(**connection_params)


class TestSnowflakeConnectionQueries:
    """Tests for query execution"""

    def test_execute_query(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test query execution"""
        _mock_connect, _mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params["vault_secret_path"] = "secret/snowflake"

        conn = SnowflakeConnection(**params)
        conn.connect()

        result = conn.execute_query("SELECT * FROM test_table")

        assert result == [("row1",), ("row2",)]

    def test_execute_query_dict(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test query execution returning dictionaries"""
        _mock_connect, mock_conn = mock_snowflake_connection

        # Create mock dict cursor
        mock_dict_cursor = Mock()
        mock_dict_cursor.fetchall.return_value = [{"col1": "row1", "col2": "row2"}]
        mock_dict_cursor.execute = Mock()
        mock_dict_cursor.close = Mock()

        # Make cursor() return dict cursor when called with DictCursor
        def cursor_factory(cursor_class=None):
            if cursor_class is not None:
                return mock_dict_cursor
            return mock_conn.cursor.return_value

        mock_conn.cursor.side_effect = cursor_factory

        params = connection_params.copy()
        params["vault_secret_path"] = "secret/snowflake"

        conn = SnowflakeConnection(**params)
        conn.connect()

        result = conn.execute_query_dict("SELECT col1, col2 FROM test")

        assert result == [{"col1": "row1", "col2": "row2"}]


class TestSnowflakeConnectionLifecycle:
    """Tests for connection lifecycle management"""

    def test_close_connection(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test connection closing"""
        _mock_connect, mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params["vault_secret_path"] = "secret/snowflake"

        conn = SnowflakeConnection(**params)
        conn.connect()
        conn.close()

        mock_conn.close.assert_called_once()
        # Connection object still exists after close, just closed
        assert conn.connection is not None

    def test_close_when_no_connection(self, connection_params, mock_vault_working):
        """Test closing when no connection exists"""
        params = connection_params.copy()
        params["vault_secret_path"] = "secret/snowflake"

        conn = SnowflakeConnection(**params)

        # Should not raise an exception
        conn.close()
        assert conn.connection is None

    def test_context_manager(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test context manager functionality"""
        _mock_connect, mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params["vault_secret_path"] = "secret/snowflake"

        with SnowflakeConnection(**params) as conn:
            assert conn.connection == mock_conn

        mock_conn.close.assert_called_once()


class TestSnowflakeConnectionAdvanced:
    """Advanced tests for better coverage"""

    def test_test_connectivity_success(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test connectivity testing success"""
        _mock_connect, _mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params["vault_secret_path"] = "secret/snowflake"

        conn = SnowflakeConnection(**params)

        result = conn.test_connectivity()

        assert result["success"] is True
        assert "response_time_ms" in result
        assert "account_info" in result

    @patch("os.environ.get")
    def test_environment_variable_defaults(self, mock_env_get, mock_vault_working):
        """Test environment variable defaults"""

        def env_side_effect(key, default=None):
            env_vars = {
                "SNOWFLAKE_USER": "env_user",
                "VAULT_NAMESPACE": "env_namespace",
                "VAULT_SECRET_PATH": "env_secret_path",
            }
            return env_vars.get(key, default)

        mock_env_get.side_effect = env_side_effect

        conn = SnowflakeConnection(account="test_account", vault_secret_path="env_secret_path")

        assert conn.user == "env_user"
        assert conn.vault_namespace == "env_namespace"
        # vault_secret_path is not stored as an instance attribute
