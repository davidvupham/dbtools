#!/usr/bin/env python3
"""
Diagnostic script for troubleshooting Vault AppRole 403 errors.

This script helps identify the root cause of AppRole authentication failures.
"""

import json
import os
import sys
from typing import Optional

import requests


def check_environment_variables() -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Check if required environment variables are set."""
    print("=" * 70)
    print("1. CHECKING ENVIRONMENT VARIABLES")
    print("=" * 70)

    role_id = os.getenv("VAULT_ROLE_ID")
    secret_id = os.getenv("VAULT_SECRET_ID")
    vault_addr = os.getenv("VAULT_ADDR")

    print(f"VAULT_ADDR:     {'✓ Set' if vault_addr else '✗ NOT SET'}")
    if vault_addr:
        print(f"  Value: {vault_addr}")

    print(f"VAULT_ROLE_ID:  {'✓ Set' if role_id else '✗ NOT SET'}")
    if role_id:
        print(f"  Value: {role_id[:8]}...{role_id[-4:] if len(role_id) > 12 else ''}")

    print(f"VAULT_SECRET_ID: {'✓ Set' if secret_id else '✗ NOT SET'}")
    if secret_id:
        print(f"  Value: {secret_id[:8]}...{secret_id[-4:] if len(secret_id) > 12 else ''}")

    print()

    if not all([role_id, secret_id, vault_addr]):
        print("❌ ERROR: Missing required environment variables!")
        return None, None, None

    return role_id, secret_id, vault_addr


def test_vault_connectivity(vault_addr: str) -> bool:
    """Test basic connectivity to Vault server."""
    print("=" * 70)
    print("2. TESTING VAULT CONNECTIVITY")
    print("=" * 70)

    try:
        # Try to reach Vault health endpoint
        health_url = f"{vault_addr}/v1/sys/health"
        print(f"Testing connection to: {health_url}")

        resp = requests.get(health_url, timeout=5)
        print(f"✓ Connection successful (Status: {resp.status_code})")

        # Check if Vault is sealed
        if resp.status_code == 200:
            data = resp.json()
            sealed = data.get("sealed", True)
            print(f"  Vault sealed: {sealed}")
            if sealed:
                print("  ⚠️  WARNING: Vault is sealed! You need to unseal it first.")
                return False

        print()
        return True

    except requests.ConnectionError as e:
        print("❌ CONNECTION ERROR: Cannot reach Vault server")
        print(f"   Error: {e}")
        print("\n   Possible causes:")
        print("   - Vault server is not running")
        print("   - Wrong VAULT_ADDR")
        print("   - Network/firewall issues")
        print("   - SSL certificate issues")
        print()
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        return False


def test_approle_login(vault_addr: str, role_id: str, secret_id: str) -> None:
    """Attempt AppRole login and provide detailed diagnostics."""
    print("=" * 70)
    print("3. TESTING APPROLE AUTHENTICATION")
    print("=" * 70)

    login_url = f"{vault_addr}/v1/auth/approle/login"
    print(f"Login URL: {login_url}")

    payload = {"role_id": role_id, "secret_id": secret_id}

    try:
        resp = requests.post(login_url, json=payload, timeout=10)

        print(f"Response Status: {resp.status_code}")

        if resp.ok:
            print("✓ AUTHENTICATION SUCCESSFUL!")
            data = resp.json()
            token = data.get("auth", {}).get("client_token", "N/A")
            lease = data.get("auth", {}).get("lease_duration", "N/A")
            policies = data.get("auth", {}).get("policies", [])

            print(f"\n  Token: {token[:10]}...{token[-5:] if len(token) > 15 else ''}")
            print(f"  Lease Duration: {lease} seconds")
            print(f"  Policies: {', '.join(policies)}")
            print()
            return

        # Authentication failed
        print("❌ AUTHENTICATION FAILED!")
        print("\nResponse Body:")
        try:
            error_data = resp.json()
            print(json.dumps(error_data, indent=2))

            errors = error_data.get("errors", [])
            if errors:
                print("\nError Messages:")
                for error in errors:
                    print(f"  - {error}")
        except (json.JSONDecodeError, ValueError):
            print(resp.text)

        # Provide specific guidance based on status code
        print("\n" + "=" * 70)
        print("DIAGNOSIS & RECOMMENDED ACTIONS")
        print("=" * 70)

        if resp.status_code == 403:
            print("❌ 403 FORBIDDEN - Permission Denied")
            print("\nPossible Causes:")
            print("  1. Invalid role_id or secret_id")
            print("     → Verify credentials with your Vault administrator")
            print("     → Check if credentials were recently rotated")
            print()
            print("  2. AppRole not configured properly in Vault")
            print("     → Verify AppRole exists: vault read auth/approle/role/<role-name>")
            print("     → Check AppRole policies are correct")
            print()
            print("  3. Secret ID already used (if configured as single-use)")
            print("     → Generate a new secret_id")
            print("     → Command: vault write -f auth/approle/role/<role-name>/secret-id")
            print()
            print("  4. IP/CIDR restrictions on AppRole")
            print("     → Check bound_cidr_list in AppRole configuration")
            print("     → Verify your IP is allowed")
            print()
            print("  5. AppRole might be disabled")
            print("     → Check: vault auth list")
            print("     → Enable: vault auth enable approle")

        elif resp.status_code == 404:
            print("❌ 404 NOT FOUND")
            print("\nPossible Causes:")
            print("  1. AppRole auth method not enabled")
            print("     → Enable: vault auth enable approle")
            print()
            print("  2. AppRole mounted at different path")
            print("     → Check: vault auth list")
            print("     → Try different path: /v1/auth/<path>/login")

        elif resp.status_code == 400:
            print("❌ 400 BAD REQUEST")
            print("\nPossible Causes:")
            print("  1. Malformed request")
            print("  2. Missing required fields")
            print("  3. Invalid credential format")

        print()

    except requests.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
        print()


def check_auth_methods(vault_addr: str) -> None:
    """Try to list all auth methods (requires a valid token)."""
    print("=" * 70)
    print("4. ADDITIONAL CHECKS")
    print("=" * 70)

    # Check if VAULT_TOKEN is available for additional diagnostics
    vault_token = os.getenv("VAULT_TOKEN")
    if vault_token:
        print("Found VAULT_TOKEN - attempting to list auth methods...")

        try:
            url = f"{vault_addr}/v1/sys/auth"
            headers = {"X-Vault-Token": vault_token}
            resp = requests.get(url, headers=headers, timeout=5)

            if resp.ok:
                auth_methods = resp.json()
                print("\n✓ Available auth methods:")
                for path, info in auth_methods.items():
                    auth_type = info.get("type", "unknown")
                    print(f"  - {path:20} (type: {auth_type})")
                    if auth_type == "approle":
                        print(f"    → AppRole is mounted at: /v1/auth/{path}login")
            else:
                print(f"Cannot list auth methods (Status: {resp.status_code})")
        except Exception as e:
            print(f"Error checking auth methods: {e}")
    else:
        print("ℹ️  Set VAULT_TOKEN to enable additional diagnostics")

    print()


def main():
    """Main diagnostic routine."""
    print("\n" + "=" * 70)
    print("VAULT APPROLE AUTHENTICATION DIAGNOSTIC TOOL")
    print("=" * 70)
    print()

    # Step 1: Check environment variables
    role_id, secret_id, vault_addr = check_environment_variables()
    if not all([role_id, secret_id, vault_addr]):
        print("\n⚠️  Please set the required environment variables and try again.")
        print("\nExample:")
        print('  export VAULT_ADDR="https://vault.example.com:8200"')
        print('  export VAULT_ROLE_ID="your-role-id"')
        print('  export VAULT_SECRET_ID="your-secret-id"')
        sys.exit(1)

    # Type narrowing: at this point, all values are guaranteed to be str (not None)
    assert role_id is not None
    assert secret_id is not None
    assert vault_addr is not None

    # Step 2: Test connectivity
    if not test_vault_connectivity(vault_addr):
        print("⚠️  Fix connectivity issues before proceeding.")
        sys.exit(1)

    # Step 3: Test AppRole login
    test_approle_login(vault_addr, role_id, secret_id)

    # Step 4: Additional checks
    check_auth_methods(vault_addr)

    print("=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
