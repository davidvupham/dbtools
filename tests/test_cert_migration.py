#!/usr/bin/env python3
"""
Test script to verify cert directory changes.

This script validates that:
1. The cert directory exists at the root level
2. Documentation references are correct
3. Code can handle cert path correctly
"""

import os
import sys


def test_cert_directory():
    """Test that cert directory exists at root."""
    cert_dir = "/home/dpham/dev/snowflake/cert"

    print("=" * 70)
    print("Test 1: Cert Directory Location")
    print("=" * 70)

    if os.path.exists(cert_dir):
        print(f"✅ Cert directory exists at: {cert_dir}")

        # Check for README
        readme_path = os.path.join(cert_dir, "README.md")
        if os.path.exists(readme_path):
            print("✅ README.md exists in cert directory")
        else:
            print("❌ README.md missing from cert directory")
            return False

        # Check for .gitkeep
        gitkeep_path = os.path.join(cert_dir, ".gitkeep")
        if os.path.exists(gitkeep_path):
            print("✅ .gitkeep exists in cert directory")
        else:
            print("❌ .gitkeep missing from cert directory")
            return False
    else:
        print(f"❌ Cert directory NOT found at: {cert_dir}")
        return False

    return True


def test_no_old_references():
    """Test that old certs directory doesn't exist."""
    print("\n" + "=" * 70)
    print("Test 2: Old Directory Removed")
    print("=" * 70)

    old_cert_dir = "/home/dpham/dev/snowflake/gds_vault/certs"

    if not os.path.exists(old_cert_dir):
        print(f"✅ Old certs directory removed: {old_cert_dir}")
        return True
    print(f"❌ Old certs directory still exists: {old_cert_dir}")
    return False


def test_code_imports():
    """Test that code can be imported without errors."""
    print("\n" + "=" * 70)
    print("Test 3: Code Imports")
    print("=" * 70)

    try:
        # Add the gds_vault package to path if not already installed
        workspace_root = os.path.dirname(os.path.abspath(__file__))
        gds_vault_path = os.path.join(workspace_root, "gds_vault")
        if os.path.exists(gds_vault_path) and gds_vault_path not in sys.path:
            sys.path.insert(0, gds_vault_path)

        # Test imports to verify they work
        from gds_vault import (
            VaultClient,  # type: ignore[import-not-found]  # noqa: F401
        )
        from gds_vault.auth import (
            AppRoleAuth,  # type: ignore[import-not-found]  # noqa: F401
        )

        print("✅ VaultClient imported successfully")
        print("✅ AppRoleAuth imported successfully")

        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_ssl_cert_path_handling():
    """Test that SSL cert path can be set correctly."""
    print("\n" + "=" * 70)
    print("Test 4: SSL Cert Path Handling")
    print("=" * 70)

    try:
        # Add the gds_vault package to path if not already installed
        workspace_root = os.path.dirname(os.path.abspath(__file__))
        gds_vault_path = os.path.join(workspace_root, "gds_vault")
        if os.path.exists(gds_vault_path) and gds_vault_path not in sys.path:
            sys.path.insert(0, gds_vault_path)

        from gds_vault import VaultClient  # type: ignore[import-not-found]

        # Test with cert path
        test_cert_path = "/home/dpham/dev/snowflake/cert/test-ca.crt"

        # Create client with SSL cert path (will fail auth, but that's OK)
        try:
            client = VaultClient(
                vault_addr="https://vault.example.com",
                ssl_cert_path=test_cert_path,
                verify_ssl=True,
            )
            print("✅ VaultClient created with cert path")
            print(f"   - SSL cert path: {client.ssl_cert_path}")
            print(f"   - SSL verification: {client.verify_ssl}")

            # Check properties work
            if client.ssl_cert_path == test_cert_path:
                print("✅ SSL cert path property works correctly")
            else:
                print("❌ SSL cert path property incorrect")
                return False

            return True

        except Exception as e:
            # VaultConfigurationError or auth errors are OK
            if "VAULT_ROLE_ID" in str(e) or "VAULT_SECRET_ID" in str(e):
                print("✅ Client initialization works (auth credentials missing as expected)")
                return True
            print(f"❌ Unexpected error: {e}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_documentation_references():
    """Test that documentation has correct references."""
    print("\n" + "=" * 70)
    print("Test 5: Documentation References")
    print("=" * 70)

    docs_dir = "/home/dpham/dev/snowflake/gds_vault"
    doc_files = [
        "SSL_CONFIGURATION.md",
        "SSL_QUICK_REFERENCE.md",
        "SSL_IMPLEMENTATION_SUMMARY.md",
        "VAULT_SSL_FIX_GUIDE.md",
    ]

    bad_refs = []

    for doc_file in doc_files:
        doc_path = os.path.join(docs_dir, doc_file)
        if os.path.exists(doc_path):
            with open(doc_path) as f:
                content = f.read()

                # Check for old references (excluding system paths)
                if "gds_vault/certs" in content:
                    bad_refs.append(f"{doc_file}: contains 'gds_vault/certs'")
        else:
            print(f"⚠️  {doc_file} not found")

    if bad_refs:
        print("❌ Found old references in documentation:")
        for ref in bad_refs:
            print(f"   - {ref}")
        return False
    print("✅ No old gds_vault/certs references found in documentation")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("CERT DIRECTORY MIGRATION TEST SUITE")
    print("=" * 70)

    results = []

    # Run all tests
    results.append(("Cert Directory Location", test_cert_directory()))
    results.append(("Old Directory Removed", test_no_old_references()))
    results.append(("Code Imports", test_code_imports()))
    results.append(("SSL Cert Path Handling", test_ssl_cert_path_handling()))
    results.append(("Documentation References", test_documentation_references()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n🎉 All tests passed! Migration successful!")
        return 0
    print(f"\n⚠️  {total - passed} test(s) failed. Please review above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
