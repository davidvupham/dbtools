#!/usr/bin/env python3
"""
SSL Certificate Configuration Examples for gds-vault.

This module demonstrates various ways to configure SSL certificate
verification when connecting to HashiCorp Vault servers.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gds_vault import VaultClient
from gds_vault.exceptions import VaultError


def example_1_default_ssl():
    """
    Example 1: Default SSL Verification (Recommended for Production)
    
    Uses system's trusted CA certificates to verify the Vault server.
    This is the recommended approach when your Vault server uses
    certificates from a trusted CA.
    """
    print("\n" + "=" * 70)
    print("Example 1: Default SSL Verification")
    print("=" * 70)
    
    try:
        # SSL verification is enabled by default
        client = VaultClient(
            vault_addr="https://vault.example.com"
        )
        
        print(f"✅ Connected to: {client.vault_addr}")
        print(f"✅ SSL verification: {client.verify_ssl}")
        print("✅ Using system CA certificates")
        
        # Fetch a secret
        # secret = client.get_secret('secret/data/myapp')
        # print(f"✅ Retrieved secret successfully")
        
    except VaultError as e:
        print(f"❌ Failed: {e}")


def example_2_custom_certificate():
    """
    Example 2: Custom CA Certificate
    
    Use this when your Vault server uses a self-signed certificate
    or a certificate from a custom Certificate Authority.
    """
    print("\n" + "=" * 70)
    print("Example 2: Custom CA Certificate")
    print("=" * 70)
    
    # Path to your custom CA certificate
    cert_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "cert",
        "vault-ca.crt"
    )
    
    try:
        client = VaultClient(
            vault_addr="https://vault.example.com",
            ssl_cert_path=cert_path
        )
        
        print(f"✅ Connected to: {client.vault_addr}")
        print(f"✅ SSL certificate: {client.ssl_cert_path}")
        print(f"✅ SSL verification: {client.verify_ssl}")
        
        # Fetch a secret
        # secret = client.get_secret('secret/data/myapp')
        # print(f"✅ Retrieved secret successfully")
        
    except VaultError as e:
        print(f"❌ Failed: {e}")


def example_3_environment_variables():
    """
    Example 3: Using Environment Variables
    
    Configure SSL certificate path via environment variables.
    This is ideal for containerized or CI/CD environments.
    """
    print("\n" + "=" * 70)
    print("Example 3: Environment Variables")
    print("=" * 70)
    
    # Set environment variables (normally done in shell or Docker)
    os.environ["VAULT_ADDR"] = "https://vault.example.com"
    os.environ["VAULT_SSL_CERT"] = "/path/to/vault-ca.crt"
    os.environ["VAULT_ROLE_ID"] = "your-role-id"
    os.environ["VAULT_SECRET_ID"] = "your-secret-id"
    
    try:
        # Client automatically reads from environment
        client = VaultClient()
        
        print(f"✅ Connected to: {client.vault_addr}")
        print(f"✅ SSL certificate from env: {os.getenv('VAULT_SSL_CERT')}")
        print("✅ All configuration from environment variables")
        
    except VaultError as e:
        print(f"❌ Failed: {e}")


def example_4_disable_ssl_verification():
    """
    Example 4: Disable SSL Verification (NOT RECOMMENDED FOR PRODUCTION)
    
    Only use this in development/testing environments where you have
    complete control and understand the security implications.
    """
    print("\n" + "=" * 70)
    print("Example 4: Disable SSL Verification (DEV/TEST ONLY!)")
    print("=" * 70)
    
    try:
        client = VaultClient(
            vault_addr="https://vault.dev.local",
            verify_ssl=False
        )
        
        print(f"⚠️  Connected to: {client.vault_addr}")
        print(f"⚠️  SSL verification: {client.verify_ssl}")
        print("⚠️  WARNING: SSL verification disabled!")
        print("⚠️  Never use this in production!")
        
    except VaultError as e:
        print(f"❌ Failed: {e}")


def example_5_context_manager():
    """
    Example 5: Context Manager with SSL
    
    Use context manager for automatic resource cleanup.
    SSL configuration works the same way.
    """
    print("\n" + "=" * 70)
    print("Example 5: Context Manager with SSL")
    print("=" * 70)
    
    cert_path = "/path/to/vault-ca.crt"
    
    try:
        with VaultClient(
            vault_addr="https://vault.example.com",
            ssl_cert_path=cert_path
        ) as client:
            print(f"✅ Connected to: {client.vault_addr}")
            print(f"✅ SSL certificate: {cert_path}")
            
            # Fetch secrets
            # secret1 = client.get_secret('secret/data/app1')
            # secret2 = client.get_secret('secret/data/app2')
            
            print("✅ Secrets retrieved successfully")
        
        print("✅ Client cleaned up automatically")
        
    except VaultError as e:
        print(f"❌ Failed: {e}")


def example_6_multiple_vault_servers():
    """
    Example 6: Multiple Vault Servers with Different Certificates
    
    Connect to multiple Vault servers, each with its own SSL certificate.
    Useful for multi-environment setups.
    """
    print("\n" + "=" * 70)
    print("Example 6: Multiple Vault Servers")
    print("=" * 70)
    
    try:
        # Production Vault
        prod_client = VaultClient(
            vault_addr="https://vault.prod.example.com",
            ssl_cert_path="/etc/ssl/certs/prod-vault-ca.crt"
        )
        print(f"✅ Production: {prod_client.vault_addr}")
        
        # Staging Vault
        staging_client = VaultClient(
            vault_addr="https://vault.staging.example.com",
            ssl_cert_path="/etc/ssl/certs/staging-vault-ca.crt"
        )
        print(f"✅ Staging: {staging_client.vault_addr}")
        
        # Development Vault (self-signed cert)
        dev_client = VaultClient(
            vault_addr="https://vault.dev.local",
            ssl_cert_path="cert/dev-vault-ca.crt"
        )
        print(f"✅ Development: {dev_client.vault_addr}")
        
        print("✅ All environments configured successfully")
        
    except VaultError as e:
        print(f"❌ Failed: {e}")


def example_7_dynamic_ssl_configuration():
    """
    Example 7: Dynamic SSL Configuration
    
    Update SSL settings after client initialization.
    Useful for testing or runtime configuration changes.
    """
    print("\n" + "=" * 70)
    print("Example 7: Dynamic SSL Configuration")
    print("=" * 70)
    
    try:
        # Create client with default settings
        client = VaultClient(vault_addr="https://vault.example.com")
        print(f"Initial SSL verification: {client.verify_ssl}")
        
        # Update SSL certificate path
        client.ssl_cert_path = "/path/to/new-cert.crt"
        print(f"✅ Updated certificate path: {client.ssl_cert_path}")
        
        # Note: Changes take effect on next request
        # secret = client.get_secret('secret/data/myapp')
        
    except VaultError as e:
        print(f"❌ Failed: {e}")


def example_8_certificate_validation():
    """
    Example 8: Certificate Validation Before Use
    
    Validate certificate file exists and is readable before
    attempting to connect to Vault.
    """
    print("\n" + "=" * 70)
    print("Example 8: Certificate Validation")
    print("=" * 70)
    
    def validate_and_create_client(vault_addr: str, cert_path: str):
        """Create Vault client with certificate validation."""
        
        # Check certificate exists
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"Certificate not found: {cert_path}")
        
        # Check certificate is readable
        if not os.access(cert_path, os.R_OK):
            raise PermissionError(f"Certificate not readable: {cert_path}")
        
        # Check certificate is a file (not a directory)
        if not os.path.isfile(cert_path):
            raise ValueError(f"Certificate path is not a file: {cert_path}")
        
        print(f"✅ Certificate validated: {cert_path}")
        
        return VaultClient(
            vault_addr=vault_addr,
            ssl_cert_path=cert_path
        )
    
    try:
        _cert_path = "/path/to/vault-ca.crt"
        # client = validate_and_create_client(
        #     "https://vault.example.com",
        #     _cert_path
        # )
        print("✅ Client created with validated certificate")
        
    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"❌ Certificate validation failed: {e}")
    except VaultError as e:
        print(f"❌ Vault connection failed: {e}")


def example_9_docker_environment():
    """
    Example 9: Docker Container Configuration
    
    Example of how to configure SSL certificates in Docker.
    This shows the Python code; see Dockerfile for complete setup.
    """
    print("\n" + "=" * 70)
    print("Example 9: Docker Environment")
    print("=" * 70)
    
    print("""
Docker Setup:

1. Dockerfile:
   FROM python:3.11-slim
   
   # Copy certificate into container
   COPY certs/vault-ca.crt /app/certs/vault-ca.crt
   RUN chmod 600 /app/certs/vault-ca.crt
   
   # Set environment variable
   ENV VAULT_SSL_CERT=/app/certs/vault-ca.crt
   ENV VAULT_ADDR=https://vault.example.com
   
   # Install application
   COPY . /app
   WORKDIR /app
   RUN pip install -e .
   
   CMD ["python", "app.py"]

2. Docker run with mounted certificate:
   docker run -v /host/certs:/certs:ro \\
       -e VAULT_SSL_CERT=/certs/vault-ca.crt \\
       -e VAULT_ADDR=https://vault.example.com \\
       my-app

3. Python code (app.py):
""")
    
    try:
        # Automatically uses environment variables
        client = VaultClient()
        print(f"✅ Connected to: {client.vault_addr}")
        print(f"✅ Using certificate: {client.ssl_cert_path}")
        
    except VaultError as e:
        print(f"❌ Failed: {e}")


def example_10_comprehensive_error_handling():
    """
    Example 10: Comprehensive Error Handling
    
    Proper error handling for SSL-related issues.
    """
    print("\n" + "=" * 70)
    print("Example 10: Error Handling")
    print("=" * 70)
    
    import requests
    
    def safe_vault_connection(vault_addr: str, cert_path: str = None):
        """Safely connect to Vault with comprehensive error handling."""
        try:
            client = VaultClient(
                vault_addr=vault_addr,
                ssl_cert_path=cert_path
            )
            
            # Try to authenticate
            client.authenticate()
            
            print(f"✅ Successfully connected to {vault_addr}")
            return client
            
        except FileNotFoundError as e:
            print(f"❌ Certificate file not found: {e}")
            print("   Solution: Check certificate path and ensure file exists")
            
        except PermissionError as e:
            print(f"❌ Permission denied: {e}")
            print("   Solution: Check file permissions (chmod 644 cert.crt)")
            
        except requests.exceptions.SSLError as e:
            print(f"❌ SSL verification failed: {e}")
            print("   Solutions:")
            print("   1. Verify you have the correct CA certificate")
            print("   2. Check certificate hasn't expired")
            print("   3. Ensure hostname matches certificate")
            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection failed: {e}")
            print("   Solution: Check Vault server is reachable")
            
        except VaultError as e:
            print(f"❌ Vault error: {e}")
            print("   Solution: Check credentials and permissions")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        return None
    
    # Try connecting with various scenarios
    # client = safe_vault_connection(
    #     "https://vault.example.com",
    #     "/path/to/vault-ca.crt"
    # )


def main():
    """Run all SSL configuration examples."""
    print("\n" + "=" * 70)
    print("GDS-VAULT SSL Certificate Configuration Examples")
    print("=" * 70)
    
    examples = [
        ("Default SSL Verification", example_1_default_ssl),
        ("Custom CA Certificate", example_2_custom_certificate),
        ("Environment Variables", example_3_environment_variables),
        ("Disable SSL (DEV ONLY)", example_4_disable_ssl_verification),
        ("Context Manager", example_5_context_manager),
        ("Multiple Vault Servers", example_6_multiple_vault_servers),
        ("Dynamic Configuration", example_7_dynamic_ssl_configuration),
        ("Certificate Validation", example_8_certificate_validation),
        ("Docker Environment", example_9_docker_environment),
        ("Error Handling", example_10_comprehensive_error_handling),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning all examples...")
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Example '{name}' failed with error: {e}")
    
    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)
    print("\nFor more information:")
    print("  - SSL Configuration Guide: ../SSL_CONFIGURATION.md")
    print("  - Certificate Directory: ../cert/README.md")
    print("  - Main Documentation: ../README.md")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
