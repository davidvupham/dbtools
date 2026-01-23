"""
Data models for Active Directory objects.

This module provides dataclasses representing AD objects like users and groups,
making it easier to work with AD data in a type-safe manner.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GroupCategory(Enum):
    """Active Directory group category."""

    SECURITY = "Security"
    DISTRIBUTION = "Distribution"


class GroupScope(Enum):
    """Active Directory group scope."""

    DOMAIN_LOCAL = "DomainLocal"
    GLOBAL = "Global"
    UNIVERSAL = "Universal"


@dataclass
class ADGroup:
    """
    Represents an Active Directory group.

    Attributes:
        name: The group's SAM account name (e.g., "SQL_Admin").
        distinguished_name: Full LDAP DN (e.g., "CN=SQL_Admin,OU=Groups,DC=example,DC=com").
        category: Whether the group is Security or Distribution.
        scope: The group scope (DomainLocal, Global, Universal).
        description: Optional group description.
        members: List of member DNs (only populated when explicitly requested).

    Example:
        group = ADGroup(
            name="SQL_Admin",
            distinguished_name="CN=SQL_Admin,OU=Groups,DC=example,DC=com",
            category=GroupCategory.SECURITY,
        )
    """

    name: str
    distinguished_name: str
    category: GroupCategory = GroupCategory.SECURITY
    scope: Optional[GroupScope] = None
    description: Optional[str] = None
    members: list[str] = field(default_factory=list)

    @classmethod
    def from_ldap_entry(cls, entry: dict) -> "ADGroup":
        """
        Create an ADGroup from an LDAP search entry.

        Args:
            entry: Dictionary from ldap3 search result.

        Returns:
            ADGroup: Populated group object.
        """
        attributes = entry.get("attributes", entry)

        # Parse groupType to determine category and scope
        group_type = attributes.get("groupType", 0)
        if isinstance(group_type, list):
            group_type = group_type[0] if group_type else 0

        # Security groups have bit 0x80000000 set
        is_security = bool(int(group_type) & 0x80000000)
        category = GroupCategory.SECURITY if is_security else GroupCategory.DISTRIBUTION

        # Determine scope from groupType
        scope = None
        group_type_int = int(group_type) & 0x0000000F
        if group_type_int == 4:
            scope = GroupScope.DOMAIN_LOCAL
        elif group_type_int == 2:
            scope = GroupScope.GLOBAL
        elif group_type_int == 8:
            scope = GroupScope.UNIVERSAL

        # Get name - try cn first, then sAMAccountName
        name = attributes.get("cn", attributes.get("sAMAccountName", ""))
        if isinstance(name, list):
            name = name[0] if name else ""

        # Get DN
        dn = entry.get("dn", attributes.get("distinguishedName", ""))
        if isinstance(dn, list):
            dn = dn[0] if dn else ""

        # Get description
        description = attributes.get("description")
        if isinstance(description, list):
            description = description[0] if description else None

        return cls(
            name=name,
            distinguished_name=dn,
            category=category,
            scope=scope,
            description=description,
        )


@dataclass
class ADUser:
    """
    Represents an Active Directory user.

    Attributes:
        username: The user's SAM account name (e.g., "jdoe").
        distinguished_name: Full LDAP DN.
        display_name: User's display name.
        email: User's email address.
        enabled: Whether the account is enabled.
        groups: List of group DNs the user is a member of.

    Example:
        user = ADUser(
            username="jdoe",
            distinguished_name="CN=John Doe,OU=Users,DC=example,DC=com",
            display_name="John Doe",
            email="jdoe@example.com",
        )
    """

    username: str
    distinguished_name: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    enabled: bool = True
    groups: list[str] = field(default_factory=list)

    @classmethod
    def from_ldap_entry(cls, entry: dict) -> "ADUser":
        """
        Create an ADUser from an LDAP search entry.

        Args:
            entry: Dictionary from ldap3 search result.

        Returns:
            ADUser: Populated user object.
        """
        attributes = entry.get("attributes", entry)

        def get_single(attr_name: str) -> Optional[str]:
            value = attributes.get(attr_name)
            if isinstance(value, list):
                return value[0] if value else None
            return value

        # Get DN
        dn = entry.get("dn", get_single("distinguishedName") or "")

        # Parse userAccountControl for enabled status
        uac = get_single("userAccountControl")
        enabled = True
        if uac:
            # Bit 2 (0x2) is ACCOUNTDISABLE
            enabled = not bool(int(uac) & 0x2)

        return cls(
            username=get_single("sAMAccountName") or "",
            distinguished_name=dn,
            display_name=get_single("displayName"),
            email=get_single("mail"),
            enabled=enabled,
        )
