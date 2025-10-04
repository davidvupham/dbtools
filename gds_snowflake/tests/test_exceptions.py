"""
Comprehensive tests for custom exception classes
"""

import pytest
from gds_snowflake.exceptions import (
    SnowflakeConnectionError,
    SnowflakeQueryError,
    VaultAuthenticationError,
    VaultSecretError,
    SnowflakeConfigurationError,
)


class TestSnowflakeConnectionError:
    """Tests for SnowflakeConnectionError"""

    def test_init_with_message_only(self):
        """Test exception with message only"""
        error = SnowflakeConnectionError("Connection failed")

        assert str(error) == "Connection failed"
        assert error.account is None

    def test_init_with_message_and_account(self):
        """Test exception with message and account"""
        error = SnowflakeConnectionError(
            "Connection failed", account="test_account"
        )

        assert str(error) == "Connection failed"
        assert error.account == "test_account"

    def test_inheritance(self):
        """Test that SnowflakeConnectionError inherits from Exception"""
        error = SnowflakeConnectionError("test")
        assert isinstance(error, Exception)

    def test_raise_and_catch(self):
        """Test raising and catching the exception"""
        with pytest.raises(SnowflakeConnectionError) as exc_info:
            raise SnowflakeConnectionError(
                "Test connection error", account="test_account"
            )

        assert "Test connection error" in str(exc_info.value)
        assert exc_info.value.account == "test_account"


class TestSnowflakeQueryError:
    """Tests for SnowflakeQueryError"""

    def test_init_with_message_only(self):
        """Test exception with message only"""
        error = SnowflakeQueryError("Query failed")

        assert str(error) == "Query failed"
        assert error.query is None

    def test_init_with_message_and_query(self):
        """Test exception with message and query"""
        query = "SELECT * FROM nonexistent_table"
        error = SnowflakeQueryError("Query failed", query=query)

        assert str(error) == "Query failed"
        assert error.query == query

    def test_inheritance(self):
        """Test that SnowflakeQueryError inherits from Exception"""
        error = SnowflakeQueryError("test")
        assert isinstance(error, Exception)

    def test_raise_and_catch(self):
        """Test raising and catching the exception"""
        test_query = "SELECT * FROM invalid_table"

        with pytest.raises(SnowflakeQueryError) as exc_info:
            raise SnowflakeQueryError(
                "Query execution failed", query=test_query
            )

        assert "Query execution failed" in str(exc_info.value)
        assert exc_info.value.query == test_query


class TestVaultAuthenticationError:
    """Tests for VaultAuthenticationError"""

    def test_init_with_message_only(self):
        """Test exception with message only"""
        error = VaultAuthenticationError("Authentication failed")

        assert str(error) == "Authentication failed"
        assert error.vault_addr is None

    def test_init_with_message_and_vault_addr(self):
        """Test exception with message and vault address"""
        vault_addr = "https://vault.example.com"
        error = VaultAuthenticationError(
            "Authentication failed", vault_addr=vault_addr
        )

        assert str(error) == "Authentication failed"
        assert error.vault_addr == vault_addr

    def test_inheritance(self):
        """Test that VaultAuthenticationError inherits from Exception"""
        error = VaultAuthenticationError("test")
        assert isinstance(error, Exception)

    def test_raise_and_catch(self):
        """Test raising and catching the exception"""
        vault_addr = "https://vault.test.com"

        with pytest.raises(VaultAuthenticationError) as exc_info:
            raise VaultAuthenticationError(
                "Vault authentication failed", vault_addr=vault_addr
            )

        assert "Vault authentication failed" in str(exc_info.value)
        assert exc_info.value.vault_addr == vault_addr


class TestVaultSecretError:
    """Tests for VaultSecretError"""

    def test_init_with_message_only(self):
        """Test exception with message only"""
        error = VaultSecretError("Secret not found")

        assert str(error) == "Secret not found"
        assert error.secret_path is None

    def test_init_with_message_and_secret_path(self):
        """Test exception with message and secret path"""
        secret_path = "secret/snowflake/prod"
        error = VaultSecretError("Secret not found", secret_path=secret_path)

        assert str(error) == "Secret not found"
        assert error.secret_path == secret_path

    def test_inheritance(self):
        """Test that VaultSecretError inherits from Exception"""
        error = VaultSecretError("test")
        assert isinstance(error, Exception)

    def test_raise_and_catch(self):
        """Test raising and catching the exception"""
        secret_path = "secret/missing/path"

        with pytest.raises(VaultSecretError) as exc_info:
            raise VaultSecretError(
                "Secret retrieval failed", secret_path=secret_path
            )

        assert "Secret retrieval failed" in str(exc_info.value)
        assert exc_info.value.secret_path == secret_path


class TestSnowflakeConfigurationError:
    """Tests for SnowflakeConfigurationError"""

    def test_init_with_message_only(self):
        """Test exception with message only"""
        error = SnowflakeConfigurationError("Invalid configuration")

        assert str(error) == "Invalid configuration"
        assert error.parameter is None

    def test_init_with_message_and_parameter(self):
        """Test exception with message and parameter"""
        parameter = "account"
        error = SnowflakeConfigurationError(
            "Invalid configuration", parameter=parameter
        )

        assert str(error) == "Invalid configuration"
        assert error.parameter == parameter

    def test_inheritance(self):
        """Test that SnowflakeConfigurationError inherits from Exception"""
        error = SnowflakeConfigurationError("test")
        assert isinstance(error, Exception)

    def test_raise_and_catch(self):
        """Test raising and catching the exception"""
        parameter = "warehouse"

        with pytest.raises(SnowflakeConfigurationError) as exc_info:
            raise SnowflakeConfigurationError(
                "Configuration parameter missing", parameter=parameter
            )

        assert "Configuration parameter missing" in str(exc_info.value)
        assert exc_info.value.parameter == parameter


class TestExceptionInteroperability:
    """Tests for exception interoperability and edge cases"""

    def test_all_exceptions_are_exceptions(self):
        """Test that all custom exceptions are proper Exception subclasses"""
        exceptions = [
            SnowflakeConnectionError("test"),
            SnowflakeQueryError("test"),
            VaultAuthenticationError("test"),
            VaultSecretError("test"),
            SnowflakeConfigurationError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, Exception)
            assert hasattr(exc, "__str__")
            assert hasattr(exc, "args")

    def test_exception_chaining(self):
        """Test exception chaining works correctly"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise SnowflakeConnectionError(
                    "Connection failed due to configuration"
                ) from e
        except SnowflakeConnectionError as exc:
            assert exc.__cause__ is not None
            assert isinstance(exc.__cause__, ValueError)
            assert str(exc.__cause__) == "Original error"

    def test_empty_message_handling(self):
        """Test handling of empty messages"""
        error = SnowflakeConnectionError("")
        assert str(error) == ""
        assert error.account is None

    def test_none_message_handling(self):
        """Test handling of None as message"""
        # This should work since Exception handles None gracefully
        error = SnowflakeConnectionError(None)
        assert str(error) == "None"

    def test_unicode_message_handling(self):
        """Test handling of unicode messages"""
        unicode_msg = "Connection failed: ❌ 数据库连接失败"
        error = SnowflakeConnectionError(unicode_msg, account="测试账户")

        assert unicode_msg in str(error)
        assert error.account == "测试账户"
