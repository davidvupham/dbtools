"""Secure token storage for dbtool.

Uses the system keyring for secure credential storage when available,
with fallback to file-based storage with restricted permissions.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Service name for keyring storage
KEYRING_SERVICE = "dbtool"
KEYRING_USERNAME = "vault_token"

# Fallback file location (with restricted permissions)
TOKEN_FILE = Path.home() / ".dbtool_token"


def _use_keyring() -> bool:
    """Check if keyring is available and functional."""
    try:
        import keyring
        from keyring.backends.fail import Keyring as FailKeyring

        # Check if we have a real keyring backend (not the fail backend)
        backend = keyring.get_keyring()
        if isinstance(backend, FailKeyring):
            return False

        # Test that we can actually use the keyring
        keyring.get_password(KEYRING_SERVICE, "__test__")
        return True
    except Exception:
        return False


def save_token(token: str) -> None:
    """Save Vault token securely.

    Attempts to use system keyring first, falls back to file storage
    with restricted permissions (600) if keyring unavailable.

    Args:
        token: The Vault token to store.
    """
    if _use_keyring():
        try:
            import keyring

            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, token)
            logger.debug("Token saved to system keyring")
            # Remove any old file-based token
            if TOKEN_FILE.exists():
                TOKEN_FILE.unlink()
            return
        except Exception as e:
            logger.warning(f"Failed to save to keyring, using file: {e}")

    # Fallback to file-based storage
    TOKEN_FILE.write_text(token)
    TOKEN_FILE.chmod(0o600)
    logger.debug(f"Token saved to {TOKEN_FILE}")


def load_token() -> str | None:
    """Load Vault token from secure storage.

    Checks system keyring first, then falls back to file storage.

    Returns:
        The stored token, or None if not found.
    """
    if _use_keyring():
        try:
            import keyring

            token = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            if token:
                logger.debug("Token loaded from system keyring")
                return token
        except Exception as e:
            logger.warning(f"Failed to load from keyring: {e}")

    # Fallback to file-based storage
    if TOKEN_FILE.exists():
        try:
            token = TOKEN_FILE.read_text().strip()
            if token:
                logger.debug(f"Token loaded from {TOKEN_FILE}")
                return token
        except Exception as e:
            logger.warning(f"Failed to load token file: {e}")

    return None


def delete_token() -> None:
    """Delete stored Vault token from all storage locations.

    Clears token from both keyring and file storage.
    """
    if _use_keyring():
        try:
            import keyring

            keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
            logger.debug("Token deleted from system keyring")
        except Exception as e:
            logger.debug(f"No token in keyring to delete: {e}")

    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        logger.debug(f"Token file deleted: {TOKEN_FILE}")


def get_token_location() -> str:
    """Get description of where token is stored.

    Returns:
        Human-readable description of token storage location.
    """
    if _use_keyring():
        return "system keyring"
    return str(TOKEN_FILE)
