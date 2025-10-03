"""gds-hvault: HashiCorp Vault helper for secret retrieval."""

from gds_hvault.vault import get_secret_from_vault, VaultError

__version__ = "0.1.0"
__all__ = ["get_secret_from_vault", "VaultError"]
