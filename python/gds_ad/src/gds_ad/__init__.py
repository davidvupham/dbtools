"""
gds-ad: Active Directory integration library for GDS services.

This package provides a modern, Pythonic interface to Active Directory
for common operations like querying user group memberships and managing
group members.

Example:
    from gds_ad import ActiveDirectoryClient

    client = ActiveDirectoryClient(
        server="ldap://dc.example.com",
        base_dn="DC=example,DC=com",
        username="MYDOMAIN\\\\admin",
        password="secret123"
    )

    with client:
        # Get user's SQL-related groups
        groups = client.get_user_group_membership("jdoe", filter="SQL*")
        for group in groups:
            print(f"{group.name}")

        # Remove user from a group
        client.remove_user_group_membership("jdoe", ["SQL_Admin"])
"""

# Authentication strategies
from gds_ad.auth import AuthStrategy, EnvironmentAuth, KerberosAuth, SimpleBindAuth

# Main client and convenience function
from gds_ad.client import ActiveDirectoryClient, get_user_groups

# Exceptions
from gds_ad.exceptions import (
    ActiveDirectoryError,
    ADAuthenticationError,
    ADConfigurationError,
    ADConnectionError,
    ADModificationError,
    ADObjectNotFoundError,
    ADSearchError,
)

# Models
from gds_ad.models import ADGroup, ADUser, GroupCategory, GroupScope

__version__ = "1.0.0"

__all__ = [
    "ADAuthenticationError",
    "ADConfigurationError",
    "ADConnectionError",
    "ADGroup",
    "ADModificationError",
    "ADObjectNotFoundError",
    "ADSearchError",
    "ADUser",
    "ActiveDirectoryClient",
    "ActiveDirectoryError",
    "AuthStrategy",
    "EnvironmentAuth",
    "GroupCategory",
    "GroupScope",
    "KerberosAuth",
    "SimpleBindAuth",
    "get_user_groups",
]
