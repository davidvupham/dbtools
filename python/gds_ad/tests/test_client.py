"""Test suite for Active Directory client."""

from unittest.mock import MagicMock, patch

import pytest
from gds_ad import ActiveDirectoryClient
from gds_ad.auth import SimpleBindAuth
from gds_ad.exceptions import ADConfigurationError, ADObjectNotFoundError
from gds_ad.models import ADGroup


class TestActiveDirectoryClientInit:
    """Tests for ActiveDirectoryClient initialization."""

    def test_init_with_username_password(self, sample_ad_config):
        """Test initialization with username and password."""
        client = ActiveDirectoryClient(**sample_ad_config)

        assert client.server_address == "ldap://dc.example.com"
        assert client.base_dn == "DC=example,DC=com"
        assert isinstance(client._auth, SimpleBindAuth)
        assert not client.is_connected

    def test_init_with_auth_strategy(self, sample_ad_config):
        """Test initialization with auth strategy."""
        auth = SimpleBindAuth(username="test", password="pass")
        client = ActiveDirectoryClient(
            server=sample_ad_config["server"],
            base_dn=sample_ad_config["base_dn"],
            auth=auth,
        )

        assert client._auth is auth

    def test_init_without_auth_raises_error(self, sample_ad_config):
        """Test initialization without auth raises error."""
        with pytest.raises(ADConfigurationError) as exc_info:
            ActiveDirectoryClient(
                server=sample_ad_config["server"],
                base_dn=sample_ad_config["base_dn"],
            )

        assert "auth" in str(exc_info.value).lower() or "username" in str(exc_info.value).lower()

    def test_init_detects_ssl_from_url(self, sample_ad_config):
        """Test SSL detection from URL."""
        client_ldap = ActiveDirectoryClient(
            server="ldap://dc.example.com",
            base_dn=sample_ad_config["base_dn"],
            username=sample_ad_config["username"],
            password=sample_ad_config["password"],
        )
        assert client_ldap._use_ssl is False

        client_ldaps = ActiveDirectoryClient(
            server="ldaps://dc.example.com",
            base_dn=sample_ad_config["base_dn"],
            username=sample_ad_config["username"],
            password=sample_ad_config["password"],
        )
        assert client_ldaps._use_ssl is True


class TestActiveDirectoryClientConnection:
    """Tests for connection management."""

    @patch("ldap3.Connection")
    @patch("gds_ad.client.Server")
    def test_connect_success(self, mock_server_class, mock_conn_class, sample_ad_config, mock_ldap_connection):
        """Test successful connection."""
        mock_conn_class.return_value = mock_ldap_connection
        mock_ldap_connection.bind.return_value = True

        client = ActiveDirectoryClient(**sample_ad_config)
        client.connect()

        assert client.is_connected
        mock_server_class.assert_called_once()

    @patch("ldap3.Connection")
    @patch("gds_ad.client.Server")
    def test_context_manager(self, mock_server_class, mock_conn_class, sample_ad_config, mock_ldap_connection):
        """Test context manager connects and disconnects."""
        mock_conn_class.return_value = mock_ldap_connection
        mock_ldap_connection.bind.return_value = True

        with ActiveDirectoryClient(**sample_ad_config) as client:
            assert client.is_connected

        mock_ldap_connection.unbind.assert_called_once()


class TestGetUserGroupMembership:
    """Tests for get_user_group_membership method."""

    @patch("ldap3.Connection")
    @patch("gds_ad.client.Server")
    def test_get_all_groups(
        self, mock_server_class, mock_conn_class, sample_ad_config, mock_ldap_connection, mock_ldap_entry, sample_group_entries
    ):
        """Test getting all groups for a user."""
        mock_conn_class.return_value = mock_ldap_connection
        mock_ldap_connection.bind.return_value = True

        # Create mock entries
        entries = [mock_ldap_entry(g["dn"], g["attributes"]) for g in sample_group_entries]

        # First search returns user, subsequent searches return groups
        user_entry = mock_ldap_entry(
            "CN=John Doe,OU=Users,DC=example,DC=com",
            {"sAMAccountName": ["jdoe"], "distinguishedName": ["CN=John Doe,OU=Users,DC=example,DC=com"]},
        )

        call_count = [0]

        def search_side_effect(*args, **kwargs):
            if call_count[0] == 0:
                mock_ldap_connection.entries = [user_entry]
            else:
                mock_ldap_connection.entries = entries
            call_count[0] += 1

        mock_ldap_connection.search = MagicMock(side_effect=search_side_effect)

        with ActiveDirectoryClient(**sample_ad_config) as client:
            groups = client.get_user_group_membership("jdoe")

        assert len(groups) == 3
        assert all(isinstance(g, ADGroup) for g in groups)

    @patch("ldap3.Connection")
    @patch("gds_ad.client.Server")
    def test_get_groups_with_filter(
        self, mock_server_class, mock_conn_class, sample_ad_config, mock_ldap_connection, mock_ldap_entry, sample_group_entries
    ):
        """Test getting groups with wildcard filter."""
        mock_conn_class.return_value = mock_ldap_connection
        mock_ldap_connection.bind.return_value = True

        # Create mock entries
        entries = [mock_ldap_entry(g["dn"], g["attributes"]) for g in sample_group_entries]

        user_entry = mock_ldap_entry(
            "CN=John Doe,OU=Users,DC=example,DC=com",
            {"sAMAccountName": ["jdoe"], "distinguishedName": ["CN=John Doe,OU=Users,DC=example,DC=com"]},
        )

        call_count = [0]

        def search_side_effect(*args, **kwargs):
            if call_count[0] == 0:
                mock_ldap_connection.entries = [user_entry]
            else:
                mock_ldap_connection.entries = entries
            call_count[0] += 1

        mock_ldap_connection.search = MagicMock(side_effect=search_side_effect)

        with ActiveDirectoryClient(**sample_ad_config) as client:
            groups = client.get_user_group_membership("jdoe", filter="SQL*")

        # Should only return SQL_Admin and SQL_Reader
        assert len(groups) == 2
        assert all(g.name.startswith("SQL") for g in groups)

    @patch("ldap3.Connection")
    @patch("gds_ad.client.Server")
    def test_user_not_found(self, mock_server_class, mock_conn_class, sample_ad_config, mock_ldap_connection):
        """Test error when user is not found."""
        mock_conn_class.return_value = mock_ldap_connection
        mock_ldap_connection.bind.return_value = True
        mock_ldap_connection.entries = []

        with pytest.raises(ADObjectNotFoundError) as exc_info:
            with ActiveDirectoryClient(**sample_ad_config) as client:
                client.get_user_group_membership("nonexistent")

        assert "nonexistent" in str(exc_info.value)


class TestRemoveUserGroupMembership:
    """Tests for remove_user_group_membership method."""

    @patch("ldap3.Connection")
    @patch("gds_ad.client.Server")
    def test_remove_single_group(self, mock_server_class, mock_conn_class, sample_ad_config, mock_ldap_connection, mock_ldap_entry):
        """Test removing user from a single group."""
        mock_conn_class.return_value = mock_ldap_connection
        mock_ldap_connection.bind.return_value = True
        mock_ldap_connection.result = {"result": 0, "description": "success"}

        user_entry = mock_ldap_entry(
            "CN=John Doe,OU=Users,DC=example,DC=com",
            {"sAMAccountName": ["jdoe"], "distinguishedName": ["CN=John Doe,OU=Users,DC=example,DC=com"]},
        )
        group_entry = mock_ldap_entry(
            "CN=SQL_Admin,OU=Groups,DC=example,DC=com",
            {"distinguishedName": ["CN=SQL_Admin,OU=Groups,DC=example,DC=com"]},
        )

        call_count = [0]

        def search_side_effect(*args, **kwargs):
            if call_count[0] == 0:
                mock_ldap_connection.entries = [user_entry]
            else:
                mock_ldap_connection.entries = [group_entry]
            call_count[0] += 1

        mock_ldap_connection.search = MagicMock(side_effect=search_side_effect)

        with ActiveDirectoryClient(**sample_ad_config) as client:
            result = client.remove_user_group_membership("jdoe", "SQL_Admin")

        assert result["SQL_Admin"] is True
        mock_ldap_connection.modify.assert_called_once()

    @patch("ldap3.Connection")
    @patch("gds_ad.client.Server")
    def test_remove_multiple_groups(self, mock_server_class, mock_conn_class, sample_ad_config, mock_ldap_connection, mock_ldap_entry):
        """Test removing user from multiple groups."""
        mock_conn_class.return_value = mock_ldap_connection
        mock_ldap_connection.bind.return_value = True
        mock_ldap_connection.result = {"result": 0, "description": "success"}

        user_entry = mock_ldap_entry(
            "CN=John Doe,OU=Users,DC=example,DC=com",
            {"sAMAccountName": ["jdoe"], "distinguishedName": ["CN=John Doe,OU=Users,DC=example,DC=com"]},
        )
        group1_entry = mock_ldap_entry(
            "CN=SQL_Admin,OU=Groups,DC=example,DC=com",
            {"distinguishedName": ["CN=SQL_Admin,OU=Groups,DC=example,DC=com"]},
        )
        group2_entry = mock_ldap_entry(
            "CN=SQL_Reader,OU=Groups,DC=example,DC=com",
            {"distinguishedName": ["CN=SQL_Reader,OU=Groups,DC=example,DC=com"]},
        )

        call_count = [0]

        def search_side_effect(*args, **kwargs):
            if call_count[0] == 0:
                mock_ldap_connection.entries = [user_entry]
            elif call_count[0] == 1:
                mock_ldap_connection.entries = [group1_entry]
            else:
                mock_ldap_connection.entries = [group2_entry]
            call_count[0] += 1

        mock_ldap_connection.search = MagicMock(side_effect=search_side_effect)

        with ActiveDirectoryClient(**sample_ad_config) as client:
            result = client.remove_user_group_membership("jdoe", ["SQL_Admin", "SQL_Reader"])

        assert result["SQL_Admin"] is True
        assert result["SQL_Reader"] is True
        assert mock_ldap_connection.modify.call_count == 2

    @patch("ldap3.Connection")
    @patch("gds_ad.client.Server")
    def test_remove_with_adgroup_objects(
        self, mock_server_class, mock_conn_class, sample_ad_config, mock_ldap_connection, mock_ldap_entry
    ):
        """Test removing user from groups using ADGroup objects."""
        mock_conn_class.return_value = mock_ldap_connection
        mock_ldap_connection.bind.return_value = True
        mock_ldap_connection.result = {"result": 0, "description": "success"}

        user_entry = mock_ldap_entry(
            "CN=John Doe,OU=Users,DC=example,DC=com",
            {"sAMAccountName": ["jdoe"], "distinguishedName": ["CN=John Doe,OU=Users,DC=example,DC=com"]},
        )

        mock_ldap_connection.search = MagicMock()
        mock_ldap_connection.entries = [user_entry]

        groups = [
            ADGroup(name="SQL_Admin", distinguished_name="CN=SQL_Admin,OU=Groups,DC=example,DC=com"),
        ]

        with ActiveDirectoryClient(**sample_ad_config) as client:
            result = client.remove_user_group_membership("jdoe", groups)

        assert result["CN=SQL_Admin,OU=Groups,DC=example,DC=com"] is True


class TestClientHelpers:
    """Tests for client helper methods."""

    def test_escape_ldap_filter(self):
        """Test LDAP filter escaping."""
        assert ActiveDirectoryClient._escape_ldap_filter("test") == "test"
        assert ActiveDirectoryClient._escape_ldap_filter("test*") == r"test\2a"
        assert ActiveDirectoryClient._escape_ldap_filter("(test)") == r"\28test\29"
        assert ActiveDirectoryClient._escape_ldap_filter("a\\b") == r"a\5cb"

    def test_wildcard_to_ldap(self):
        """Test PowerShell wildcard to LDAP conversion."""
        assert ActiveDirectoryClient._wildcard_to_ldap("SQL*") == "SQL*"
        assert ActiveDirectoryClient._wildcard_to_ldap("*Admin*") == "*Admin*"
        assert ActiveDirectoryClient._wildcard_to_ldap("SQL?") == "SQL*"  # ? becomes *

    def test_match_wildcard(self):
        """Test wildcard matching."""
        assert ActiveDirectoryClient._match_wildcard("SQL_Admin", "SQL*") is True
        assert ActiveDirectoryClient._match_wildcard("HR_Admin", "SQL*") is False
        assert ActiveDirectoryClient._match_wildcard("SQL_Admin", "*Admin*") is True
        assert ActiveDirectoryClient._match_wildcard("sql_admin", "SQL*") is True  # Case insensitive


class TestClientMagicMethods:
    """Tests for client magic methods."""

    def test_repr(self, sample_ad_config):
        """Test __repr__ method."""
        client = ActiveDirectoryClient(**sample_ad_config)
        repr_str = repr(client)

        assert "ActiveDirectoryClient" in repr_str
        assert "ldap://dc.example.com" in repr_str
        assert "not connected" in repr_str

    def test_str(self, sample_ad_config):
        """Test __str__ method."""
        client = ActiveDirectoryClient(**sample_ad_config)
        str_repr = str(client)

        assert "AD Client" in str_repr
        assert "dc.example.com" in str_repr

    def test_bool_not_connected(self, sample_ad_config):
        """Test __bool__ when not connected."""
        client = ActiveDirectoryClient(**sample_ad_config)
        assert bool(client) is False

    @patch("ldap3.Connection")
    @patch("gds_ad.client.Server")
    def test_bool_connected(self, mock_server_class, mock_conn_class, sample_ad_config, mock_ldap_connection):
        """Test __bool__ when connected."""
        mock_conn_class.return_value = mock_ldap_connection
        mock_ldap_connection.bind.return_value = True

        with ActiveDirectoryClient(**sample_ad_config) as client:
            assert bool(client) is True
