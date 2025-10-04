"""gds-vault: HashiCorp Vault helper for secret retrieval."""

from gds_vault.vault import get_secret_from_vault, VaultClient, VaultError

__version__ = "0.1.0"
__all__ = ["get_secret_from_vault", "VaultClient", "VaultError"]
