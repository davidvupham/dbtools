"""Pytest configuration and shared fixtures for gds_ad tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_ldap_connection():
    """Create a mock LDAP connection for testing."""
    mock = MagicMock()
    mock.bound = True
    mock.bind = MagicMock(return_value=True)
    mock.unbind = MagicMock()
    mock.search = MagicMock()
    mock.modify = MagicMock()
    mock.result = {"result": 0, "description": "success"}
    mock.entries = []
    return mock


@pytest.fixture
def mock_ldap_server():
    """Create a mock LDAP server for testing."""
    mock = MagicMock()
    return mock


@pytest.fixture
def sample_ad_config() -> dict:
    """Return sample Active Directory configuration for testing."""
    return {
        "server": "ldap://dc.example.com",
        "base_dn": "DC=example,DC=com",
        "username": "EXAMPLE\\admin",
        "password": "testpass123",
    }


@pytest.fixture
def sample_user_entry() -> dict:
    """Return a sample LDAP user entry."""
    return {
        "dn": "CN=John Doe,OU=Users,DC=example,DC=com",
        "attributes": {
            "sAMAccountName": ["jdoe"],
            "distinguishedName": ["CN=John Doe,OU=Users,DC=example,DC=com"],
            "displayName": ["John Doe"],
            "mail": ["jdoe@example.com"],
            "userAccountControl": [512],  # Normal account, enabled
        },
    }


@pytest.fixture
def sample_group_entries() -> list[dict]:
    """Return sample LDAP group entries."""
    return [
        {
            "dn": "CN=SQL_Admin,OU=Groups,DC=example,DC=com",
            "attributes": {
                "cn": ["SQL_Admin"],
                "sAMAccountName": ["SQL_Admin"],
                "distinguishedName": ["CN=SQL_Admin,OU=Groups,DC=example,DC=com"],
                "groupType": [-2147483646],  # Security group, global scope
                "description": ["SQL Server Administrators"],
            },
        },
        {
            "dn": "CN=SQL_Reader,OU=Groups,DC=example,DC=com",
            "attributes": {
                "cn": ["SQL_Reader"],
                "sAMAccountName": ["SQL_Reader"],
                "distinguishedName": ["CN=SQL_Reader,OU=Groups,DC=example,DC=com"],
                "groupType": [-2147483646],
                "description": ["SQL Server Readers"],
            },
        },
        {
            "dn": "CN=HR_Users,OU=Groups,DC=example,DC=com",
            "attributes": {
                "cn": ["HR_Users"],
                "sAMAccountName": ["HR_Users"],
                "distinguishedName": ["CN=HR_Users,OU=Groups,DC=example,DC=com"],
                "groupType": [-2147483646],
                "description": ["HR Department Users"],
            },
        },
    ]


@pytest.fixture
def mock_ldap_entry():
    """Create a factory for mock LDAP entries."""

    def _create_entry(dn: str, attributes: dict):
        entry = MagicMock()
        entry.entry_dn = dn
        entry.entry_attributes_as_dict = attributes
        return entry

    return _create_entry
