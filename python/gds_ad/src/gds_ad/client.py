"""
Active Directory client for user and group management.

This module provides the main client class for interacting with Active Directory,
supporting operations like querying user group memberships and modifying group members.
"""

import fnmatch
import logging
from typing import Optional, Union

from ldap3 import ALL, SUBTREE, Server

from gds_ad.auth import AuthStrategy, SimpleBindAuth
from gds_ad.exceptions import (
    ADConfigurationError,
    ADConnectionError,
    ADModificationError,
    ADObjectNotFoundError,
    ADSearchError,
)
from gds_ad.models import ADGroup, ADUser

logger = logging.getLogger(__name__)


class ActiveDirectoryClient:
    """
    Client for Active Directory operations.

    Provides methods for querying and modifying Active Directory objects,
    including user group memberships.

    Features:
        - Multiple authentication strategies (Simple Bind, Kerberos)
        - TLS/SSL support
        - Wildcard filtering (PowerShell-style)
        - Context manager support

    Args:
        server: LDAP server address (e.g., "ldap://dc.example.com" or "ldaps://dc.example.com:636").
        base_dn: Base distinguished name for searches (e.g., "DC=example,DC=com").
        auth: Authentication strategy. Defaults to SimpleBindAuth if username/password provided.
        username: Bind username (alternative to auth parameter).
        password: Bind password (alternative to auth parameter).
        use_ssl: Whether to use SSL/TLS. Auto-detected from server URL if not specified.
        connect_timeout: Connection timeout in seconds.

    Example:
        # Basic usage with username/password
        client = ActiveDirectoryClient(
            server="ldap://dc.example.com",
            base_dn="DC=example,DC=com",
            username="MYDOMAIN\\\\admin",
            password="secret123"
        )

        with client:
            groups = client.get_user_group_membership("jdoe", filter="SQL*")
            for group in groups:
                print(f"{group.name}: {group.distinguished_name}")

        # Using auth strategy
        from gds_ad.auth import KerberosAuth
        client = ActiveDirectoryClient(
            server="ldap://dc.example.com",
            base_dn="DC=example,DC=com",
            auth=KerberosAuth()
        )
    """

    # LDAP filter for security groups (groupType bit 0x80000000)
    SECURITY_GROUP_FILTER = "(groupType:1.2.840.113556.1.4.803:=2147483648)"

    def __init__(
        self,
        server: str,
        base_dn: str,
        auth: Optional[AuthStrategy] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: Optional[bool] = None,
        connect_timeout: int = 10,
    ):
        """Initialize the Active Directory client."""
        self._server_address = server
        self._base_dn = base_dn
        self._connect_timeout = connect_timeout

        # Determine SSL usage
        if use_ssl is None:
            self._use_ssl = server.lower().startswith("ldaps://")
        else:
            self._use_ssl = use_ssl

        # Set up authentication
        if auth is not None:
            self._auth = auth
        elif username and password:
            self._auth = SimpleBindAuth(username=username, password=password)
        else:
            raise ADConfigurationError("Either 'auth' strategy or 'username'/'password' must be provided")

        # Connection state
        self._server: Optional[Server] = None
        self._connection = None
        self._connected = False

        logger.debug("ActiveDirectoryClient initialized for server: %s", server)

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def server_address(self) -> str:
        """LDAP server address."""
        return self._server_address

    @property
    def base_dn(self) -> str:
        """Base distinguished name for searches."""
        return self._base_dn

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to AD."""
        return self._connected and self._connection is not None and self._connection.bound

    # ========================================================================
    # Connection management
    # ========================================================================

    def connect(self) -> None:
        """
        Establish connection to Active Directory.

        Raises:
            ADConnectionError: If connection fails.
            ADAuthenticationError: If authentication fails.
        """
        if self.is_connected:
            logger.debug("Already connected to AD")
            return

        try:
            logger.info("Connecting to AD server: %s", self._server_address)

            self._server = Server(
                self._server_address,
                use_ssl=self._use_ssl,
                get_info=ALL,
                connect_timeout=self._connect_timeout,
            )

            self._connection = self._auth.authenticate(self._server)
            self._connected = True

            logger.info("Successfully connected to AD")

        except Exception as e:
            self._connected = False
            if "authentication" in str(e).lower() or "bind" in str(e).lower():
                raise  # Re-raise ADAuthenticationError
            raise ADConnectionError(f"Failed to connect to AD server {self._server_address}: {e}") from e

    def disconnect(self) -> None:
        """Close the connection to Active Directory."""
        if self._connection:
            try:
                self._connection.unbind()
            except Exception as e:
                logger.warning("Error during disconnect: %s", e)
            finally:
                self._connection = None
                self._connected = False
                logger.info("Disconnected from AD")

    def __enter__(self) -> "ActiveDirectoryClient":
        """Context manager entry - connect to AD."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - disconnect from AD."""
        self.disconnect()

    # ========================================================================
    # User group membership operations
    # ========================================================================

    def get_user_group_membership(
        self,
        username: str,
        filter: Optional[str] = None,
        security_only: bool = True,
    ) -> list[ADGroup]:
        """
        Get the groups a user is a member of.

        Equivalent to PowerShell's Get-GdsUserGroupMembership.

        Args:
            username: The user's SAM account name (e.g., "jdoe").
            filter: Optional wildcard filter for group names (e.g., "SQL*").
                   Uses PowerShell-style wildcards (* and ?).
            security_only: If True, only return Security groups (not Distribution).
                          Default is True to match PowerShell behavior.

        Returns:
            list[ADGroup]: List of groups the user is a member of.

        Raises:
            ADObjectNotFoundError: If the user is not found.
            ADSearchError: If the search fails.

        Example:
            # Get all security groups for a user
            groups = client.get_user_group_membership("jdoe")

            # Get only SQL-related groups
            groups = client.get_user_group_membership("jdoe", filter="SQL*")
        """
        self._ensure_connected()

        # First, find the user
        user = self._find_user(username)
        if not user:
            raise ADObjectNotFoundError(f"User not found: {username}")

        # Get the user's memberOf attribute
        user_dn = user.distinguished_name
        logger.debug("Getting group membership for user: %s", user_dn)

        # Search for groups where the user is a member
        # Using memberOf from user object is more efficient than searching all groups
        search_filter = f"(&(objectClass=group)(member={self._escape_ldap_filter(user_dn)}))"

        if security_only:
            search_filter = f"(&{search_filter}{self.SECURITY_GROUP_FILTER})"

        try:
            self._connection.search(
                search_base=self._base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=["cn", "sAMAccountName", "distinguishedName", "groupType", "description"],
            )
        except Exception as e:
            raise ADSearchError(f"Failed to search for user groups: {e}") from e

        groups = []
        for entry in self._connection.entries:
            group = ADGroup.from_ldap_entry(entry.entry_attributes_as_dict | {"dn": entry.entry_dn})

            # Apply name filter if specified
            if filter is None or self._match_wildcard(group.name, filter):
                groups.append(group)

        logger.info("Found %d groups for user %s (filter: %s)", len(groups), username, filter or "*")
        return groups

    def remove_user_group_membership(
        self,
        username: str,
        groups: Union[str, list[str], ADGroup, list[ADGroup]],
    ) -> dict[str, bool]:
        """
        Remove a user from one or more groups.

        Equivalent to PowerShell's Remove-GdsUserGroupMembership.

        Args:
            username: The user's SAM account name (e.g., "jdoe").
            groups: Group(s) to remove the user from. Can be:
                   - A single group name (str)
                   - A list of group names
                   - An ADGroup object
                   - A list of ADGroup objects

        Returns:
            dict[str, bool]: Dictionary mapping group names to success status.

        Raises:
            ADObjectNotFoundError: If the user is not found.
            ADModificationError: If all removals fail.

        Example:
            # Remove from a single group
            result = client.remove_user_group_membership("jdoe", "SQL_Admin")

            # Remove from multiple groups
            result = client.remove_user_group_membership("jdoe", ["SQL_Admin", "SQL_Reader"])

            # Remove from groups returned by get_user_group_membership
            sql_groups = client.get_user_group_membership("jdoe", filter="SQL*")
            result = client.remove_user_group_membership("jdoe", sql_groups)
        """
        self._ensure_connected()

        # Find the user
        user = self._find_user(username)
        if not user:
            raise ADObjectNotFoundError(f"User not found: {username}")

        # Normalize groups to list of names/DNs
        group_list = self._normalize_groups(groups)

        results: dict[str, bool] = {}
        errors: list[str] = []

        for group_identifier in group_list:
            group_dn = self._resolve_group_dn(group_identifier)
            if not group_dn:
                logger.warning("Group not found: %s", group_identifier)
                results[group_identifier] = False
                errors.append(f"Group not found: {group_identifier}")
                continue

            try:
                # Remove user from group using modify operation
                from ldap3 import MODIFY_DELETE

                self._connection.modify(group_dn, {"member": [(MODIFY_DELETE, [user.distinguished_name])]})

                if self._connection.result["result"] == 0:
                    logger.info("Removed user %s from group %s", username, group_identifier)
                    results[group_identifier] = True
                else:
                    error_msg = self._connection.result.get("description", "Unknown error")
                    logger.error("Failed to remove user %s from group %s: %s", username, group_identifier, error_msg)
                    results[group_identifier] = False
                    errors.append(f"Failed to remove from {group_identifier}: {error_msg}")

            except Exception as e:
                logger.error("Error removing user %s from group %s: %s", username, group_identifier, e)
                results[group_identifier] = False
                errors.append(f"Error removing from {group_identifier}: {e}")

        # If all operations failed, raise an exception
        if errors and not any(results.values()):
            raise ADModificationError(f"Failed to remove user '{username}' from all groups: {'; '.join(errors)}")

        return results

    # ========================================================================
    # Search operations
    # ========================================================================

    def search_users(self, filter: str = "*", attributes: Optional[list[str]] = None) -> list[ADUser]:
        """
        Search for users in Active Directory.

        Args:
            filter: Wildcard filter for user names (e.g., "j*" for names starting with 'j').
            attributes: Additional attributes to retrieve.

        Returns:
            list[ADUser]: List of matching users.
        """
        self._ensure_connected()

        ldap_filter = f"(&(objectClass=user)(objectCategory=person)(sAMAccountName={self._wildcard_to_ldap(filter)}))"

        default_attrs = ["sAMAccountName", "distinguishedName", "displayName", "mail", "userAccountControl"]
        search_attrs = list(set(default_attrs + (attributes or [])))

        try:
            self._connection.search(
                search_base=self._base_dn,
                search_filter=ldap_filter,
                search_scope=SUBTREE,
                attributes=search_attrs,
            )
        except Exception as e:
            raise ADSearchError(f"User search failed: {e}") from e

        users = []
        for entry in self._connection.entries:
            users.append(ADUser.from_ldap_entry(entry.entry_attributes_as_dict | {"dn": entry.entry_dn}))

        logger.info("Found %d users matching filter: %s", len(users), filter)
        return users

    def search_groups(self, filter: str = "*", security_only: bool = True) -> list[ADGroup]:
        """
        Search for groups in Active Directory.

        Args:
            filter: Wildcard filter for group names.
            security_only: If True, only return Security groups.

        Returns:
            list[ADGroup]: List of matching groups.
        """
        self._ensure_connected()

        ldap_filter = f"(&(objectClass=group)(cn={self._wildcard_to_ldap(filter)}))"
        if security_only:
            ldap_filter = f"(&{ldap_filter}{self.SECURITY_GROUP_FILTER})"

        try:
            self._connection.search(
                search_base=self._base_dn,
                search_filter=ldap_filter,
                search_scope=SUBTREE,
                attributes=["cn", "sAMAccountName", "distinguishedName", "groupType", "description"],
            )
        except Exception as e:
            raise ADSearchError(f"Group search failed: {e}") from e

        groups = []
        for entry in self._connection.entries:
            groups.append(ADGroup.from_ldap_entry(entry.entry_attributes_as_dict | {"dn": entry.entry_dn}))

        logger.info("Found %d groups matching filter: %s", len(groups), filter)
        return groups

    # ========================================================================
    # Helper methods
    # ========================================================================

    def _ensure_connected(self) -> None:
        """Ensure client is connected, auto-connect if not."""
        if not self.is_connected:
            self.connect()

    def _find_user(self, username: str) -> Optional[ADUser]:
        """Find a user by SAM account name."""
        search_filter = f"(&(objectClass=user)(objectCategory=person)(sAMAccountName={self._escape_ldap_filter(username)}))"

        try:
            self._connection.search(
                search_base=self._base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=["sAMAccountName", "distinguishedName", "displayName", "mail", "userAccountControl"],
            )

            if self._connection.entries:
                entry = self._connection.entries[0]
                return ADUser.from_ldap_entry(entry.entry_attributes_as_dict | {"dn": entry.entry_dn})

        except Exception as e:
            logger.error("Error finding user %s: %s", username, e)

        return None

    def _resolve_group_dn(self, group_identifier: str) -> Optional[str]:
        """Resolve a group name or DN to its full DN."""
        # If it looks like a DN, use it directly
        if group_identifier.upper().startswith("CN="):
            return group_identifier

        # Search for the group by name
        search_filter = f"(&(objectClass=group)(|(cn={self._escape_ldap_filter(group_identifier)})(sAMAccountName={self._escape_ldap_filter(group_identifier)})))"

        try:
            self._connection.search(
                search_base=self._base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=["distinguishedName"],
            )

            if self._connection.entries:
                return self._connection.entries[0].entry_dn

        except Exception as e:
            logger.error("Error resolving group DN for %s: %s", group_identifier, e)

        return None

    def _normalize_groups(self, groups: Union[str, list, ADGroup]) -> list[str]:
        """Normalize various group input types to a list of identifiers."""
        if isinstance(groups, str):
            return [groups]
        if isinstance(groups, ADGroup):
            return [groups.distinguished_name]
        if isinstance(groups, list):
            result = []
            for g in groups:
                if isinstance(g, str):
                    result.append(g)
                elif isinstance(g, ADGroup):
                    result.append(g.distinguished_name)
                else:
                    result.append(str(g))
            return result
        return [str(groups)]

    @staticmethod
    def _escape_ldap_filter(value: str) -> str:
        """Escape special characters in LDAP filter values."""
        # RFC 4515 escaping
        escape_chars = {
            "\\": r"\5c",
            "*": r"\2a",
            "(": r"\28",
            ")": r"\29",
            "\x00": r"\00",
        }
        for char, escaped in escape_chars.items():
            value = value.replace(char, escaped)
        return value

    @staticmethod
    def _wildcard_to_ldap(pattern: str) -> str:
        """
        Convert PowerShell-style wildcard to LDAP filter.

        PowerShell uses * for any characters and ? for single character.
        LDAP uses * for any characters (no single char wildcard).
        """
        # LDAP * is the same as PowerShell *, but ? needs special handling
        # Since LDAP doesn't support single-char wildcard, we approximate ? with *
        result = pattern.replace("?", "*")
        return result

    @staticmethod
    def _match_wildcard(value: str, pattern: str) -> bool:
        """Match a value against a PowerShell-style wildcard pattern."""
        return fnmatch.fnmatch(value.lower(), pattern.lower())

    # ========================================================================
    # Magic methods
    # ========================================================================

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        status = "connected" if self.is_connected else "not connected"
        return f"ActiveDirectoryClient(server={self._server_address!r}, base_dn={self._base_dn!r}, {status})"

    def __str__(self) -> str:
        """User-friendly representation."""
        status = "connected" if self.is_connected else "not connected"
        return f"AD Client at {self._server_address} ({status})"

    def __bool__(self) -> bool:
        """Truthiness based on connection status."""
        return self.is_connected


# ========================================================================
# Convenience functions
# ========================================================================


def get_user_groups(
    username: str,
    server: str,
    base_dn: str,
    bind_username: str,
    bind_password: str,
    filter: Optional[str] = None,
) -> list[ADGroup]:
    """
    Convenience function to get user group membership.

    Creates a temporary client, fetches groups, and cleans up.

    Args:
        username: The user's SAM account name.
        server: LDAP server address.
        base_dn: Base DN for searches.
        bind_username: Username for LDAP bind.
        bind_password: Password for LDAP bind.
        filter: Optional wildcard filter for group names.

    Returns:
        list[ADGroup]: List of groups the user is a member of.

    Example:
        groups = get_user_groups(
            username="jdoe",
            server="ldap://dc.example.com",
            base_dn="DC=example,DC=com",
            bind_username="MYDOMAIN\\\\admin",
            bind_password="secret123",
            filter="SQL*"
        )
    """
    with ActiveDirectoryClient(
        server=server,
        base_dn=base_dn,
        username=bind_username,
        password=bind_password,
    ) as client:
        return client.get_user_group_membership(username, filter=filter)
