"""gds-vault: HashiCorp Vault helper for secret retrieval."""

from gds_vault.vault import VaultClient, VaultError, get_secret_from_vault

__version__ = "0.1.0"
__all__ = ["VaultClient", "VaultError", "get_secret_from_vault"]
