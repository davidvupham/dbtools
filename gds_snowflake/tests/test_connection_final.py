"""
Final comprehensive tests for SnowflakeConnection class with proper mocking
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from gds_snowflake.connection import SnowflakeConnection


@pytest.fixture
def connection_params():
    """Fixture providing standard connection parameters for RSA auth"""
    return {
        'account': 'test_account',
        'user': 'test_user',
        'warehouse': 'test_warehouse',
        'role': 'test_role'
    }


@pytest.fixture
def mock_vault_disabled():
    """Fixture that completely bypasses Vault operations"""
    with patch('gds_snowflake.connection.get_secret_from_vault') as mock_vault:
        # Don't call vault at all by providing no vault_secret_path
        yield mock_vault


@pytest.fixture
def mock_vault_working():
    """Fixture providing working Vault operations"""
    with patch('gds_snowflake.connection.get_secret_from_vault') as mock_vault:
        mock_vault.return_value = {
            'private_key': 'LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQkt', # Proper base64
            'user': 'vault_user'
        }
        yield mock_vault


@pytest.fixture
def mock_snowflake_connection():
    """Fixture providing a mocked Snowflake connection"""
    with patch('snowflake.connector.connect') as mock_connect:
        mock_conn = Mock()
        mock_conn.is_closed.return_value = False
        mock_conn.close = Mock()

        # Properly mock cursor context manager
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [('row1',), ('row2',)]
        mock_cursor.fetchone.return_value = ('test_account', 'region', 'user')
        mock_cursor.description = [('col1',), ('col2',)]

        # Create proper context manager
        cursor_context = MagicMock()
        cursor_context.__enter__.return_value = mock_cursor
        cursor_context.__exit__.return_value = None
        mock_conn.cursor.return_value = cursor_context

        mock_connect.return_value = mock_conn
        yield mock_connect, mock_conn


class TestSnowflakeConnectionInit:
    """Tests for SnowflakeConnection initialization"""

    @patch('os.environ.get')
    def test_init_minimal_params_no_vault(self, mock_env_get, mock_vault_disabled):
        """Test initialization with minimal parameters and no vault"""
        mock_env_get.return_value = None  # No environment variables

        conn = SnowflakeConnection(
            account='test_account',
            user='test_user'
        )

        assert conn.account == 'test_account'
        assert conn.user == 'test_user'
        assert conn.connection is None

    def test_init_with_vault_path(self, connection_params, mock_vault_working):
        """Test initialization with vault path"""
        params = connection_params.copy()
        params['vault_secret_path'] = 'secret/snowflake'

        conn = SnowflakeConnection(**params)

        assert conn.account == params['account']
        assert conn.user == params['user']
        assert conn.vault_secret_path == params['vault_secret_path']


class TestSnowflakeConnectionConnect:
    """Tests for connection establishment"""

    def test_connect_success_with_vault(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test successful connection with vault"""
        mock_connect, mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params['vault_secret_path'] = 'secret/snowflake'

        conn = SnowflakeConnection(**params)
        result = conn.connect()

        assert result == mock_conn
        assert conn.connection == mock_conn
        mock_vault_working.assert_called_once()

    @patch('os.environ.get')
    def test_connect_no_vault_no_private_key(self, mock_env_get, connection_params, mock_vault_disabled):
        """Test connection fails without vault or private key"""
        mock_env_get.return_value = None

        conn = SnowflakeConnection(**connection_params)

        with pytest.raises(RuntimeError, match="Vault secret path must be provided"):
            conn.connect()


class TestSnowflakeConnectionQueries:
    """Tests for query execution"""

    def test_execute_query(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test query execution"""
        mock_connect, mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params['vault_secret_path'] = 'secret/snowflake'

        conn = SnowflakeConnection(**params)
        conn.connect()

        result = conn.execute_query("SELECT * FROM test_table")

        assert result == [('row1',), ('row2',)]

    def test_execute_query_dict(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test query execution returning dictionaries"""
        mock_connect, mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params['vault_secret_path'] = 'secret/snowflake'

        conn = SnowflakeConnection(**params)
        conn.connect()

        result = conn.execute_query_dict("SELECT col1, col2 FROM test")

        assert result == [{'col1': 'row1', 'col2': 'row2'}]


class TestSnowflakeConnectionLifecycle:
    """Tests for connection lifecycle management"""

    def test_close_connection(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test connection closing"""
        mock_connect, mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params['vault_secret_path'] = 'secret/snowflake'

        conn = SnowflakeConnection(**params)
        conn.connect()
        conn.close()

        mock_conn.close.assert_called_once()
        assert conn.connection is None

    @patch('os.environ.get')
    def test_close_when_no_connection(self, mock_env_get, connection_params, mock_vault_disabled):
        """Test closing when no connection exists"""
        mock_env_get.return_value = None

        conn = SnowflakeConnection(**connection_params)

        # Should not raise an exception
        conn.close()
        assert conn.connection is None

    def test_context_manager(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test context manager functionality"""
        mock_connect, mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params['vault_secret_path'] = 'secret/snowflake'

        with SnowflakeConnection(**params) as conn:
            assert conn.connection == mock_conn

        mock_conn.close.assert_called_once()


class TestSnowflakeConnectionAdvanced:
    """Advanced tests for better coverage"""

    def test_test_connectivity_success(self, connection_params, mock_snowflake_connection, mock_vault_working):
        """Test connectivity testing success"""
        mock_connect, mock_conn = mock_snowflake_connection

        params = connection_params.copy()
        params['vault_secret_path'] = 'secret/snowflake'

        conn = SnowflakeConnection(**params)

        result = conn.test_connectivity()

        assert result['success'] is True
        assert 'response_time_ms' in result
        assert 'account_info' in result

    @patch('os.environ.get')
    def test_environment_variable_defaults(self, mock_env_get, mock_vault_disabled):
        """Test environment variable defaults"""
        def env_side_effect(key, default=None):
            env_vars = {
                'SNOWFLAKE_USER': 'env_user',
                'VAULT_NAMESPACE': 'env_namespace',
                'VAULT_SECRET_PATH': 'env_secret_path'
            }
            return env_vars.get(key, default)

        mock_env_get.side_effect = env_side_effect

        conn = SnowflakeConnection(account='test_account')

        assert conn.user == 'env_user'
        assert conn.vault_namespace == 'env_namespace'
        assert conn.vault_secret_path == 'env_secret_path'
