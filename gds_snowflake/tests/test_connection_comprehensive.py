"""
Comprehensive connection module tests for 10/10 coverage
"""

import os
from unittest.mock import Mock, patch

import pytest

from gds_snowflake.connection import SnowflakeConnection


@pytest.fixture
def mock_vault_success():
    """Mock successful Vault operations"""
    with patch("gds_snowflake.connection.get_secret_from_vault") as mock_vault:
        mock_vault.return_value = {
            "private_key": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0t",
            "user": "vault_user",
        }
        yield mock_vault


@pytest.fixture
def mock_snowflake_connect():
    """Mock Snowflake connector"""
    with patch("snowflake.connector.connect") as mock_connect:
        mock_conn = Mock()
        mock_conn.is_closed.return_value = False
        mock_conn.close = Mock()

        # Mock cursor - returned directly from cursor() call, not as context manager
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [("test_result",)]
        mock_cursor.fetchone.return_value = (
            "test_account",
            "us-west-2",
            "test_user",
        )
        mock_cursor.description = [("column1",), ("column2",)]
        mock_cursor.execute = Mock()
        mock_cursor.close = Mock()

        # Return cursor directly (not wrapped in context manager)
        mock_conn.cursor.return_value = mock_cursor

        mock_connect.return_value = mock_conn
        yield mock_connect, mock_conn, mock_cursor


class TestSnowflakeConnectionInitialization:
    """Test connection initialization and configuration"""

    def test_init_minimal_params(self):
        """Test initialization with minimal parameters"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("gds_snowflake.connection.get_secret_from_vault", return_value={"private_key": "test_key"}):
                conn = SnowflakeConnection(
                    account="test_account",
                    user="test_user",
                    vault_secret_path="secret/snowflake",
                )

                assert conn.account == "test_account"
                assert conn.user == "test_user"
                assert conn.private_key == "test_key"
                assert conn.connection is None

    def test_init_with_environment_variables(self):
        """Test initialization using environment variables"""
        env_vars = {
            "SNOWFLAKE_USER": "env_user",
            "VAULT_NAMESPACE": "env_namespace",
            "VAULT_SECRET_PATH": "env_secret_path",
            "VAULT_MOUNT_POINT": "env_mount",
            "VAULT_ROLE_ID": "env_role_id",
            "VAULT_SECRET_ID": "env_secret_id",
            "VAULT_ADDR": "env_vault_addr",
        }

        with patch.dict(os.environ, env_vars):
            with patch("gds_snowflake.connection.get_secret_from_vault", return_value={"private_key": "test_key"}):
                conn = SnowflakeConnection(account="test_account")

                assert conn.user == "env_user"
                assert conn.vault_namespace == "env_namespace"

    def test_init_with_vault_configuration(self, mock_vault_success):
        """Test initialization with Vault configuration"""
        conn = SnowflakeConnection(
            account="test_account",
            vault_secret_path="secret/snowflake",
            vault_namespace="production",
            warehouse="test_warehouse",
            database="test_db",
            role="test_role",
        )

        assert conn.vault_namespace == "production"
        assert conn.warehouse == "test_warehouse"
        assert conn.database == "test_db"
        assert conn.role == "test_role"

    def test_init_vault_error_handling(self):
        """Test Vault error handling during initialization"""
        with patch(
            "gds_snowflake.connection.get_secret_from_vault"
        ) as mock_vault:
            mock_vault.side_effect = Exception("Vault connection failed")

            with pytest.raises(
                RuntimeError,
                match="Snowflake private key could not be retrieved",
            ):
                SnowflakeConnection(
                    account="test_account",
                    vault_secret_path="secret/snowflake",
                )

    def test_init_missing_private_key_in_vault(self):
        """Test handling when private key is missing from Vault response"""
        with patch(
            "gds_snowflake.connection.get_secret_from_vault"
        ) as mock_vault:
            mock_vault.return_value = {
                "user": "vault_user"
            }  # Missing private_key

            with pytest.raises(
                RuntimeError,
                match="Snowflake private key could not be retrieved",
            ):
                SnowflakeConnection(
                    account="test_account",
                    vault_secret_path="secret/snowflake",
                )


class TestSnowflakeConnectionConnectivity:
    """Test connection establishment and management"""

    def test_connect_success(self, mock_vault_success, mock_snowflake_connect):
        """Test successful connection"""
        mock_connect, mock_conn, _ = mock_snowflake_connect

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )

        result = conn.connect()

        assert result == mock_conn
        assert conn.connection == mock_conn
        mock_connect.assert_called_once()
        mock_vault_success.assert_called_once()

    def test_connect_with_all_parameters(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test connection with all parameters"""
        mock_connect, mock_conn, _ = mock_snowflake_connect

        conn = SnowflakeConnection(
            account="test_account",
            vault_secret_path="secret/snowflake",
            warehouse="test_warehouse",
            database="test_db",
            role="test_role",
        )

        conn.connect()

        # Verify all parameters were passed to snowflake.connector.connect
        call_kwargs = mock_connect.call_args[1]
        assert call_kwargs["account"] == "test_account"
        assert call_kwargs["warehouse"] == "test_warehouse"
        assert call_kwargs["database"] == "test_db"
        assert call_kwargs["role"] == "test_role"

    def test_connect_failure(self, mock_vault_success):
        """Test connection failure handling"""
        with patch("snowflake.connector.connect") as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            conn = SnowflakeConnection(
                account="test_account", vault_secret_path="secret/snowflake"
            )

            with pytest.raises(Exception, match="Connection failed"):
                conn.connect()

    def test_get_connection_existing(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test get_connection with existing connection"""
        mock_connect, mock_conn, _ = mock_snowflake_connect
        mock_conn.is_closed.return_value = False

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )
        conn.connect()

        # Reset mock to test get_connection doesn't call connect again
        mock_connect.reset_mock()

        result = conn.get_connection()

        assert result == mock_conn
        mock_connect.assert_not_called()  # Should not reconnect

    def test_get_connection_auto_reconnect(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test get_connection with auto-reconnect"""
        mock_connect, mock_conn, _ = mock_snowflake_connect

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )
        conn.connection = mock_conn

        # Simulate closed connection
        mock_conn.is_closed.return_value = True

        result = conn.get_connection()

        assert result == mock_conn
        # Should have called connect again
        mock_connect.assert_called()

    def test_close_connection(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test connection closing"""
        mock_connect, mock_conn, _ = mock_snowflake_connect

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )
        conn.connect()
        conn.close()

        mock_conn.close.assert_called_once()
        # Connection object still exists but is closed
        assert conn.connection is not None

    def test_close_no_connection(self, mock_vault_success):
        """Test closing when no connection exists"""
        conn = SnowflakeConnection(
            account="test_account", user="test_user", vault_secret_path="secret/snowflake"
        )

        # Should not raise an exception
        conn.close()
        assert conn.connection is None


class TestSnowflakeConnectionQueries:
    """Test query execution functionality"""

    def test_execute_query_success(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test successful query execution"""
        mock_connect, mock_conn, mock_cursor = mock_snowflake_connect
        mock_cursor.fetchall.return_value = [
            ("row1", "val1"),
            ("row2", "val2"),
        ]

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )
        conn.connect()

        result = conn.execute_query("SELECT * FROM test_table")

        assert result == [("row1", "val1"), ("row2", "val2")]
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM test_table"
        )

    def test_execute_query_with_params(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test query execution with parameters"""
        mock_connect, mock_conn, mock_cursor = mock_snowflake_connect
        mock_cursor.fetchall.return_value = [("filtered_result",)]

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )
        conn.connect()

        params = ("test_value", 123)
        result = conn.execute_query(
            "SELECT * FROM test WHERE col1 = %s AND col2 = %s", params
        )

        assert result == [("filtered_result",)]
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM test WHERE col1 = %s AND col2 = %s", params
        )

    def test_execute_query_error_handling(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test query execution error handling"""
        mock_connect, mock_conn, mock_cursor = mock_snowflake_connect
        mock_cursor.execute.side_effect = Exception("Query failed")

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )
        conn.connect()

        # Should raise exception on error
        with pytest.raises(Exception, match="Query failed"):
            conn.execute_query("INVALID SQL")

    def test_execute_query_dict_success(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test successful dictionary query execution"""
        mock_connect, mock_conn, mock_cursor = mock_snowflake_connect
        
        # Create a separate mock for DictCursor that returns dicts
        mock_dict_cursor = Mock()
        mock_dict_cursor.fetchall.return_value = [
            {"col1": "val1", "col2": "val2"},
            {"col1": "val3", "col2": "val4"},
        ]
        mock_dict_cursor.execute = Mock()
        mock_dict_cursor.close = Mock()
        
        # Make cursor() return the dict cursor when called with DictCursor
        def cursor_factory(cursor_class=None):
            if cursor_class is not None:
                return mock_dict_cursor
            return mock_cursor
        mock_conn.cursor.side_effect = cursor_factory

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )
        conn.connect()

        result = conn.execute_query_dict("SELECT col1, col2 FROM test")

        expected = [
            {"col1": "val1", "col2": "val2"},
            {"col1": "val3", "col2": "val4"},
        ]
        assert result == expected

    def test_execute_query_dict_error_handling(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test dictionary query execution error handling"""
        mock_connect, mock_conn, mock_cursor = mock_snowflake_connect
        
        # Create mock dict cursor that raises exception
        mock_dict_cursor = Mock()
        mock_dict_cursor.execute.side_effect = Exception("Query failed")
        mock_dict_cursor.close = Mock()
        
        def cursor_factory(cursor_class=None):
            if cursor_class is not None:
                return mock_dict_cursor
            return mock_cursor
        mock_conn.cursor.side_effect = cursor_factory

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )
        conn.connect()

        # Should raise exception on error
        with pytest.raises(Exception, match="Query failed"):
            conn.execute_query_dict("INVALID SQL")


class TestSnowflakeConnectionAdvanced:
    """Test advanced connection functionality"""

    def test_test_connectivity_success(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test successful connectivity test"""
        mock_connect, mock_conn, mock_cursor = mock_snowflake_connect
        # Return tuple with 7 values matching CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_VERSION(), CURRENT_REGION()
        mock_cursor.fetchone.return_value = (
            "test_account",  # account_name
            "test_user",  # current_user
            "test_role",  # current_role
            "test_warehouse",  # current_warehouse
            "test_database",  # current_database
            "7.0.0",  # snowflake_version
            "us-west-2",  # region
        )

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )

        result = conn.test_connectivity()

        assert result["success"] is True
        assert "response_time_ms" in result
        assert result["account_info"]["account_name"] == "test_account"
        assert result["account_info"]["region"] == "us-west-2"
        assert result["account_info"]["current_user"] == "test_user"

    def test_test_connectivity_timeout(self, mock_vault_success):
        """Test connectivity test with timeout"""
        with patch("snowflake.connector.connect") as mock_connect:
            mock_connect.side_effect = Exception("Connection timeout")

            conn = SnowflakeConnection(
                account="test_account", vault_secret_path="secret/snowflake"
            )

            result = conn.test_connectivity(timeout_seconds=1)

            assert result["success"] is False
            assert "error" in result
            assert "Connection timeout" in result["error"]

    def test_switch_account(self, mock_vault_success, mock_snowflake_connect):
        """Test account switching functionality"""
        mock_connect, mock_conn, _ = mock_snowflake_connect

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )
        conn.connect()

        original_connection = conn.connection
        assert conn.account == "test_account"

        # Switch account
        new_conn = conn.switch_account("new_account")

        assert conn.account == "new_account"
        assert new_conn == mock_conn
        # Should have closed old connection and created new one
        original_connection.close.assert_called_once()

    def test_context_manager(self, mock_vault_success, mock_snowflake_connect):
        """Test context manager functionality"""
        mock_connect, mock_conn, _ = mock_snowflake_connect

        with SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        ) as conn:
            assert conn.connection == mock_conn
            assert conn.account == "test_account"

        # Should have closed connection when exiting context
        mock_conn.close.assert_called_once()

    def test_context_manager_with_exception(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test context manager with exception handling"""
        mock_connect, mock_conn, _ = mock_snowflake_connect

        try:
            with SnowflakeConnection(
                account="test_account", vault_secret_path="secret/snowflake"
            ) as conn:
                assert conn.connection == mock_conn
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected

        # Should still close connection even when exception occurs
        mock_conn.close.assert_called_once()


class TestSnowflakeConnectionEdgeCases:
    """Test edge cases and error conditions"""

    def test_no_vault_path_no_private_key(self):
        """Test error when neither vault path nor private key provided"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                RuntimeError, match="Vault secret path must be provided"
            ):
                SnowflakeConnection(
                    account="test_account", user="test_user"
                )

    def test_repr_method(self, mock_vault_success):
        """Test string representation"""
        conn = SnowflakeConnection(
            account="test_account", user="test_user", vault_secret_path="secret/snowflake"
        )

        repr_str = repr(conn)
        assert "SnowflakeConnection" in repr_str
        # Default repr includes object type and memory address
        assert "0x" in repr_str

    def test_multiple_connections(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test handling multiple connection attempts"""
        mock_connect, mock_conn, _ = mock_snowflake_connect

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )

        # Connect multiple times
        conn1 = conn.connect()
        conn2 = conn.connect()

        # Should return the same connection instance
        assert conn1 == conn2
        assert conn.connection == mock_conn

    def test_connection_state_tracking(
        self, mock_vault_success, mock_snowflake_connect
    ):
        """Test connection state tracking"""
        mock_connect, mock_conn, _ = mock_snowflake_connect

        conn = SnowflakeConnection(
            account="test_account", vault_secret_path="secret/snowflake"
        )

        # Initially no connection
        assert conn.connection is None

        # After connecting
        conn.connect()
        assert conn.connection is not None
        assert conn.connection == mock_conn

        # After closing - connection object still exists but is closed
        conn.close()
        assert conn.connection is not None
        mock_conn.close.assert_called_once()
