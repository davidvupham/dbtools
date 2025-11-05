"""
Authentication mechanisms example for MongoDB.

This example demonstrates various authentication methods
supported by gds_mongodb including SCRAM, Kerberos, LDAP, and X.509.
"""

from gds_mongodb import MongoDBConnection


def example_scram_sha256():
    """
    SCRAM-SHA-256 Authentication (Default for MongoDB 4.0+).

    This is the recommended authentication mechanism for MongoDB.
    """
    print("1. SCRAM-SHA-256 Authentication:")

    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="mydb",
        username="myuser",
        password="mypassword",
        auth_mechanism="SCRAM-SHA-256",
        auth_source="admin",
    )

    print(f"   Auth Mechanism: {conn.config['auth_mechanism']}")
    print(f"   Auth Source: {conn.config['auth_source']}\n")


def example_scram_sha1():
    """
    SCRAM-SHA-1 Authentication.

    Authentication mechanism for MongoDB.
    """
    print("2. SCRAM-SHA-1 Authentication:")

    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="mydb",
        username="myuser",
        password="mypassword",
        auth_mechanism="SCRAM-SHA-1",
        auth_source="admin",
    )

    print(f"   Auth Mechanism: {conn.config['auth_mechanism']}\n")


def example_kerberos():
    """
    GSSAPI (Kerberos) Authentication.

    For enterprise environments using Kerberos authentication.
    Requires the kerberos dependencies to be installed:
    pip install pymongo[gssapi]
    """
    print("3. GSSAPI (Kerberos) Authentication:")

    conn = MongoDBConnection(
        host="kerberos.example.com",
        port=27017,
        database="mydb",
        username="user@EXAMPLE.COM",  # Kerberos principal
        auth_mechanism="GSSAPI",
        auth_source="$external",  # Required for GSSAPI
    )

    print(f"   Auth Mechanism: {conn.config['auth_mechanism']}")
    print(f"   Username (Principal): {conn.config['username']}")
    print(f"   Auth Source: {conn.config['auth_source']}")
    print("   Note: Requires Kerberos ticket (kinit)\n")


def example_ldap():
    """
    PLAIN (LDAP) Authentication.

    For LDAP/Active Directory authentication.
    Requires MongoDB Enterprise and LDAP configuration.
    """
    print("4. PLAIN (LDAP) Authentication:")

    conn = MongoDBConnection(
        host="ldap.example.com",
        port=27017,
        database="mydb",
        username="ldapuser",
        password="ldappassword",
        auth_mechanism="PLAIN",
        auth_source="$external",  # Required for LDAP
        tls=True,  # Recommended for PLAIN mechanism
    )

    print(f"   Auth Mechanism: {conn.config['auth_mechanism']}")
    print(f"   Auth Source: {conn.config['auth_source']}")
    print(f"   TLS: {conn.config.get('tls', False)}")
    print("   Note: Requires MongoDB Enterprise\n")


def example_x509():
    """
    MONGODB-X509 Authentication.

    Certificate-based authentication using X.509 certificates.
    Requires TLS/SSL and properly configured certificates.
    """
    print("5. MONGODB-X509 (Certificate) Authentication:")

    conn = MongoDBConnection(
        host="secure.example.com",
        port=27017,
        database="mydb",
        username="CN=myuser,OU=users,DC=example,DC=com",
        auth_mechanism="MONGODB-X509",
        auth_source="$external",  # Required for X.509
        tls=True,  # Required for X.509
    )

    print(f"   Auth Mechanism: {conn.config['auth_mechanism']}")
    print(f"   Username (DN): {conn.config['username']}")
    print(f"   Auth Source: {conn.config['auth_source']}")
    print(f"   TLS: {conn.config.get('tls', False)}")
    print("   Note: Requires client certificate configuration\n")


def example_no_authentication():
    """
    No Authentication (for local development).

    Connect to MongoDB without authentication.
    Only works if MongoDB is running without --auth.
    """
    print("6. No Authentication (Development):")

    # Example connection without authentication (connection not used in this demo)
    _ = MongoDBConnection(
        host="localhost",
        port=27017,
        database="mydb",
    )

    print("   No authentication configured")
    print("   Use only in development environments\n")


def example_with_config_dict():
    """
    Using configuration dictionary for authentication.
    """
    print("7. Configuration Dictionary Approach:")

    # SCRAM-SHA-256 with config
    config = {
        "host": "localhost",
        "port": 27017,
        "database": "mydb",
        "username": "myuser",
        "password": "mypassword",
        "auth_mechanism": "SCRAM-SHA-256",
        "auth_source": "admin",
        "server_selection_timeout_ms": 5000,
    }

    conn = MongoDBConnection(config=config)

    print(f"   Auth Mechanism: {conn.config['auth_mechanism']}")
    print(f"   Config keys: {list(config.keys())}\n")


def main():
    """Run all authentication examples."""
    print("=== MongoDB Authentication Mechanisms ===\n")

    # Note: These examples show configuration patterns
    # Actual connections will fail without proper MongoDB setup

    example_scram_sha256()
    example_scram_sha1()
    example_kerberos()
    example_ldap()
    example_x509()
    example_no_authentication()
    example_with_config_dict()

    print("=== Authentication Mechanisms Summary ===")
    print("\nSupported Mechanisms:")
    print("  • SCRAM-SHA-256: Default for MongoDB 4.0+")
    print("  • SCRAM-SHA-1: SHA-1 based authentication")
    print("  • GSSAPI: Kerberos authentication (Enterprise)")
    print("  • PLAIN: LDAP authentication (Enterprise)")
    print("  • MONGODB-X509: Certificate-based authentication")
    print("\nNotes:")
    print("  • GSSAPI and PLAIN require auth_source='$external'")
    print("  • X.509 requires TLS and auth_source='$external'")
    print("  • PLAIN should always be used with TLS")
    print("  • Enterprise features require MongoDB Enterprise Edition")

    print("\n=== Examples Complete ===")


if __name__ == "__main__":
    main()
