"""Test suite for authentication strategies."""

from unittest.mock import MagicMock, patch

import pytest
from gds_ad.auth import EnvironmentAuth, KerberosAuth, SimpleBindAuth
from gds_ad.exceptions import ADAuthenticationError, ADConfigurationError


class TestSimpleBindAuth:
    """Tests for SimpleBindAuth strategy."""

    def test_init(self):
        """Test SimpleBindAuth initialization."""
        auth = SimpleBindAuth(username="admin", password="secret")

        assert auth.username == "admin"
        assert auth.password == "secret"

    @patch("ldap3.Connection")
    def test_authenticate_success(self, mock_conn_class):
        """Test successful authentication."""
        mock_conn = MagicMock()
        mock_conn.bind.return_value = True
        mock_conn_class.return_value = mock_conn

        auth = SimpleBindAuth(username="admin", password="secret")
        mock_server = MagicMock()

        conn = auth.authenticate(mock_server)

        assert conn is mock_conn
        mock_conn.bind.assert_called_once()

    @patch("ldap3.Connection")
    def test_authenticate_failure(self, mock_conn_class):
        """Test authentication failure."""
        mock_conn = MagicMock()
        mock_conn.bind.return_value = False
        mock_conn.result = {"description": "Invalid credentials"}
        mock_conn_class.return_value = mock_conn

        auth = SimpleBindAuth(username="admin", password="wrong")
        mock_server = MagicMock()

        with pytest.raises(ADAuthenticationError) as exc_info:
            auth.authenticate(mock_server)

        assert "Simple bind failed" in str(exc_info.value)


class TestEnvironmentAuth:
    """Tests for EnvironmentAuth strategy."""

    def test_init_with_env_vars(self, monkeypatch):
        """Test EnvironmentAuth with environment variables set."""
        monkeypatch.setenv("AD_USERNAME", "env_admin")
        monkeypatch.setenv("AD_PASSWORD", "env_secret")

        auth = EnvironmentAuth()

        assert auth.username == "env_admin"
        assert auth.password == "env_secret"

    def test_init_missing_username(self, monkeypatch):
        """Test EnvironmentAuth with missing username."""
        monkeypatch.delenv("AD_USERNAME", raising=False)
        monkeypatch.setenv("AD_PASSWORD", "secret")

        with pytest.raises(ADConfigurationError) as exc_info:
            EnvironmentAuth()

        assert "AD_USERNAME" in str(exc_info.value)

    def test_init_missing_password(self, monkeypatch):
        """Test EnvironmentAuth with missing password."""
        monkeypatch.setenv("AD_USERNAME", "admin")
        monkeypatch.delenv("AD_PASSWORD", raising=False)

        with pytest.raises(ADConfigurationError) as exc_info:
            EnvironmentAuth()

        assert "AD_PASSWORD" in str(exc_info.value)

    def test_init_missing_both(self, monkeypatch):
        """Test EnvironmentAuth with both vars missing."""
        monkeypatch.delenv("AD_USERNAME", raising=False)
        monkeypatch.delenv("AD_PASSWORD", raising=False)

        with pytest.raises(ADConfigurationError):
            EnvironmentAuth()


class TestKerberosAuth:
    """Tests for KerberosAuth strategy."""

    def test_init_default(self):
        """Test KerberosAuth with default principal."""
        auth = KerberosAuth()
        assert auth.principal is None

    def test_init_with_principal(self):
        """Test KerberosAuth with explicit principal."""
        auth = KerberosAuth(principal="user@REALM.COM")
        assert auth.principal == "user@REALM.COM"

    @patch("ldap3.Connection")
    def test_authenticate_success(self, mock_conn_class):
        """Test successful Kerberos authentication."""
        mock_conn = MagicMock()
        mock_conn.bind.return_value = True
        mock_conn_class.return_value = mock_conn

        auth = KerberosAuth()
        mock_server = MagicMock()

        conn = auth.authenticate(mock_server)

        assert conn is mock_conn
        mock_conn.bind.assert_called_once()

    @patch("ldap3.Connection")
    def test_authenticate_failure(self, mock_conn_class):
        """Test Kerberos authentication failure."""
        mock_conn = MagicMock()
        mock_conn.bind.return_value = False
        mock_conn.result = {"description": "Kerberos failed"}
        mock_conn_class.return_value = mock_conn

        auth = KerberosAuth()
        mock_server = MagicMock()

        with pytest.raises(ADAuthenticationError) as exc_info:
            auth.authenticate(mock_server)

        assert "Kerberos" in str(exc_info.value)
