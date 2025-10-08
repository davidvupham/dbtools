"""
Additional tests to improve connection module coverage
"""

import os
from unittest.mock import Mock, patch

import pytest

from gds_snowflake.connection import SnowflakeConnection


class TestSnowflakeConnectionCoverage:
    """Additional tests for better coverage"""

    @patch('gds_snowflake.connection.get_secret_from_vault')
    def test_vault_integration_success(self, mock_vault):
        """Test successful Vault integration"""
        mock_vault.return_value = {
            'private_key': 'test_private_key',
            'user': 'vault_user'
        }

        conn = SnowflakeConnection(
            account='test_account',
            vault_secret_path='secret/snowflake'
        )

        # Trigger vault call by accessing private key
        with patch('snowflake.connector.connect') as mock_connect:
            mock_connect.return_value = Mock()
            conn.connect()

        mock_vault.assert_called_once()

    @patch('gds_snowflake.connection.get_secret_from_vault')
    def test_vault_missing_private_key(self, mock_vault):
        """Test Vault response missing private key"""
        mock_vault.return_value = {'user': 'vault_user'}  # Missing private_key

        # Exception is raised in __init__, not in connect()
        with pytest.raises(RuntimeError, match="Snowflake private key could not be retrieved from Vault"):
            SnowflakeConnection(
                account='test_account',
                vault_secret_path='secret/snowflake'
            )

    @patch('gds_snowflake.connection.get_secret_from_vault')
    def test_environment_variable_defaults(self, mock_vault):
        """Test environment variable defaults"""
        mock_vault.return_value = {'private_key': 'key', 'user': 'env_user'}
        with patch.dict(os.environ, {
            'SNOWFLAKE_USER': 'env_user',
            'VAULT_NAMESPACE': 'env_namespace',
            'VAULT_SECRET_PATH': 'env_secret_path'
        }):
            conn = SnowflakeConnection(account='test_account', vault_secret_path='env_secret_path')

            assert conn.user == 'env_user'
            assert conn.vault_namespace == 'env_namespace'
            # vault_secret_path is not stored as an instance attribute

    @patch('snowflake.connector.connect')
    @patch('gds_snowflake.connection.get_secret_from_vault')
    def test_get_connection_auto_reconnect(self, mock_vault, mock_connect):
        """Test get_connection with auto-reconnect"""
        mock_vault.return_value = {'private_key': 'key', 'user': 'user'}
        mock_conn = Mock()
        mock_conn.is_closed.return_value = True  # Connection is closed
        mock_connect.return_value = mock_conn

        conn = SnowflakeConnection(account='test_account', vault_secret_path='secret/snowflake')
        conn.connection = mock_conn

        # Should auto-reconnect
        result = conn.get_connection()

        assert result == mock_conn
        assert mock_connect.call_count == 1  # Reconnected

    @patch('snowflake.connector.connect')
    @patch('gds_snowflake.connection.get_secret_from_vault')
    def test_test_connectivity_success(self, mock_vault, mock_connect):
        """Test connectivity testing success"""
        mock_vault.return_value = {'private_key': 'key', 'user': 'user'}
        mock_conn = Mock()
        mock_cursor = Mock()
        # Return tuple with 7 values for CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_VERSION(), CURRENT_REGION()
        mock_cursor.fetchone.return_value = ('account_name', 'user', 'role', 'warehouse', 'database', '7.0.0', 'region')
        mock_cursor.execute = Mock()
        mock_cursor.close = Mock()
        # Return cursor directly, not as context manager
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        conn = SnowflakeConnection(account='test_account', vault_secret_path='secret/snowflake')

        result = conn.test_connectivity()

        assert result['success'] is True
        assert 'response_time_ms' in result
        assert 'account_info' in result

    @patch('snowflake.connector.connect')
    @patch('gds_snowflake.connection.get_secret_from_vault')
    def test_test_connectivity_timeout(self, mock_vault, mock_connect):
        """Test connectivity testing with timeout"""
        mock_vault.return_value = {'private_key': 'key', 'user': 'user'}
        mock_connect.side_effect = Exception("Connection timeout")

        conn = SnowflakeConnection(account='test_account', vault_secret_path='secret/snowflake')

        result = conn.test_connectivity(timeout_seconds=1)

        assert result['success'] is False
        assert 'error' in result

    @patch('snowflake.connector.connect')
    @patch('gds_snowflake.connection.get_secret_from_vault')
    def test_execute_query_error_handling(self, mock_vault, mock_connect):
        """Test query execution error handling"""
        mock_vault.return_value = {'private_key': 'key', 'user': 'user'}
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_cursor.close = Mock()
        # Return cursor directly, not as context manager
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        conn = SnowflakeConnection(account='test_account', vault_secret_path='secret/snowflake')
        conn.connect()

        # Should raise exception, not return empty list
        with pytest.raises(Exception, match="Query failed"):
            conn.execute_query("INVALID SQL")
