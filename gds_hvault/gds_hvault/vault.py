import os
import requests


class VaultError(Exception):
    pass


def get_secret_from_vault(secret_path: str, vault_addr: str = None) -> dict:
    """
    Retrieve a secret from HashiCorp Vault using AppRole authentication.
    Expects HVAULT_ROLE_ID and HVAULT_SECRET_ID in environment variables.
    Optionally, VAULT_ADDR or HVAULT_ADDR for Vault address.

    Args:
        secret_path: Path to the secret in Vault (e.g., 'secret/data/myapp')
        vault_addr: Vault address (overrides env if provided)
    Returns:
        dict: Secret data
    Raises:
        VaultError: On failure to authenticate or fetch secret
    """
    role_id = os.getenv("HVAULT_ROLE_ID")
    secret_id = os.getenv("HVAULT_SECRET_ID")
    if not role_id or not secret_id:
        raise VaultError(
            "HVAULT_ROLE_ID and HVAULT_SECRET_ID must be set in environment"
        )

    vault_addr = vault_addr or os.getenv("HVAULT_ADDR") or os.getenv("VAULT_ADDR")
    if not vault_addr:
        raise VaultError("Vault address must be set in HVAULT_ADDR or VAULT_ADDR")

    # Step 1: Login with AppRole
    login_url = f"{vault_addr}/v1/auth/approle/login"
    login_payload = {"role_id": role_id, "secret_id": secret_id}
    resp = requests.post(login_url, json=login_payload, timeout=10)
    if not resp.ok:
        raise VaultError(f"Vault AppRole login failed: {resp.text}")
    client_token = resp.json()["auth"]["client_token"]

    # Step 2: Read secret
    secret_url = f"{vault_addr}/v1/{secret_path}"
    headers = {"X-Vault-Token": client_token}
    resp = requests.get(secret_url, headers=headers, timeout=10)
    if not resp.ok:
        raise VaultError(f"Vault secret fetch failed: {resp.text}")
    data = resp.json()
    # Support both v1 and v2 kv
    if "data" in data and "data" in data["data"]:
        # kv v2
        return data["data"]["data"]
    elif "data" in data:
        # kv v1
        return data["data"]
    else:
        raise VaultError("Secret data not found in Vault response")
