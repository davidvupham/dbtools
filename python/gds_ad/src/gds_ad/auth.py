"""
Authentication strategies for Active Directory connections.

This module provides different authentication methods for connecting to AD,
following the Strategy pattern for flexibility.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ldap3 import Connection, Server

logger = logging.getLogger(__name__)


class AuthStrategy(ABC):
    """
    Abstract base class for authentication strategies.

    Subclasses implement specific authentication methods (Simple Bind, Kerberos, etc.).
    """

    @abstractmethod
    def authenticate(self, server: "Server") -> "Connection":
        """
        Authenticate and return an LDAP connection.

        Args:
            server: ldap3 Server object to connect to.

        Returns:
            Connection: Authenticated ldap3 Connection.

        Raises:
            ADAuthenticationError: If authentication fails.
        """
        pass


@dataclass
class SimpleBindAuth(AuthStrategy):
    """
    Simple bind authentication using username and password.

    This is the most common authentication method for AD.

    Attributes:
        username: The bind DN or sAMAccountName (e.g., "DOMAIN\\user" or "user@domain.com").
        password: The user's password.

    Example:
        auth = SimpleBindAuth(
            username="MYDOMAIN\\svc_account",
            password="secret123"
        )
        client = ActiveDirectoryClient(server="ldap://dc.example.com", auth=auth)
    """

    username: str
    password: str

    def authenticate(self, server: "Server") -> "Connection":
        """Create a connection with simple bind authentication."""
        from ldap3 import SIMPLE, Connection

        from gds_ad.exceptions import ADAuthenticationError

        logger.debug("Authenticating with simple bind as: %s", self.username)

        conn = Connection(
            server,
            user=self.username,
            password=self.password,
            authentication=SIMPLE,
            auto_bind=False,
            raise_exceptions=True,
        )

        try:
            if not conn.bind():
                raise ADAuthenticationError(f"Simple bind failed for user: {self.username}. {conn.result}")
        except Exception as e:
            raise ADAuthenticationError(f"Authentication failed: {e}") from e

        logger.info("Successfully authenticated as: %s", self.username)
        return conn


@dataclass
class EnvironmentAuth(SimpleBindAuth):
    """
    Simple bind authentication using environment variables.

    Reads credentials from environment variables for secure configuration.

    Environment Variables:
        AD_USERNAME: The bind username (required).
        AD_PASSWORD: The bind password (required).

    Example:
        # Set environment variables first:
        # export AD_USERNAME="MYDOMAIN\\svc_account"
        # export AD_PASSWORD="secret123"

        auth = EnvironmentAuth()
        client = ActiveDirectoryClient(server="ldap://dc.example.com", auth=auth)
    """

    username: str = ""
    password: str = ""

    def __post_init__(self):
        """Read credentials from environment variables."""
        self.username = os.getenv("AD_USERNAME", "")
        self.password = os.getenv("AD_PASSWORD", "")

        if not self.username or not self.password:
            from gds_ad.exceptions import ADConfigurationError

            raise ADConfigurationError("AD_USERNAME and AD_PASSWORD environment variables must be set")


class KerberosAuth(AuthStrategy):
    """
    Kerberos/GSSAPI authentication for Windows integrated auth.

    Uses the current user's Kerberos ticket for authentication.
    Requires the `gssapi` package to be installed.

    Example:
        auth = KerberosAuth()
        client = ActiveDirectoryClient(server="ldap://dc.example.com", auth=auth)
    """

    def __init__(self, principal: Optional[str] = None):
        """
        Initialize Kerberos auth.

        Args:
            principal: Optional Kerberos principal. If None, uses default credential cache.
        """
        self.principal = principal

    def authenticate(self, server: "Server") -> "Connection":
        """Create a connection with Kerberos/SASL authentication."""
        from ldap3 import SASL, Connection

        from gds_ad.exceptions import ADAuthenticationError

        logger.debug("Authenticating with Kerberos (principal: %s)", self.principal or "default")

        try:
            conn = Connection(
                server,
                authentication=SASL,
                sasl_mechanism="GSSAPI",
                sasl_credentials=(self.principal,) if self.principal else None,
                auto_bind=False,
                raise_exceptions=True,
            )

            if not conn.bind():
                raise ADAuthenticationError(f"Kerberos bind failed: {conn.result}")

        except ImportError as e:
            raise ADAuthenticationError("Kerberos authentication requires the 'gssapi' package. " "Install with: pip install gds-ad[kerberos]") from e
        except Exception as e:
            raise ADAuthenticationError(f"Kerberos authentication failed: {e}") from e

        logger.info("Successfully authenticated with Kerberos")
        return conn
