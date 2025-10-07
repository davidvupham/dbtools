# SSL Certificate Configuration Guide

This guide explains how to configure SSL certificate verification when connecting to HashiCorp Vault servers.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Configuration Methods](#configuration-methods)
- [Common Scenarios](#common-scenarios)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

---

## Overview

When connecting to Vault servers over HTTPS, SSL/TLS certificate verification is essential for secure communication. The `gds-vault` package supports three SSL configuration modes:

1. **Default verification** - Uses system's CA certificates (recommended for production)
2. **Custom CA certificate** - Use a specific certificate bundle
3. **Disabled verification** - Skip SSL verification (NOT recommended for production)

---

## Quick Start

### Option 1: Use System Certificates (Default)

If your Vault server uses certificates signed by a trusted CA:

```python
from gds_vault import VaultClient

# SSL verification is enabled by default
client = VaultClient(vault_addr="https://vault.example.com")
secret = client.get_secret('secret/data/myapp')
```

### Option 2: Use Custom Certificate

If your Vault server uses a self-signed certificate or custom CA:

```python
from gds_vault import VaultClient

# Specify custom certificate path
client = VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="/path/to/vault-ca.crt"
)
secret = client.get_secret('secret/data/myapp')
```

### Option 3: Use Environment Variable

```bash
# Set environment variable
export VAULT_SSL_CERT="/path/to/vault-ca.crt"
export VAULT_ADDR="https://vault.example.com"
```

```python
from gds_vault import VaultClient

# Automatically uses VAULT_SSL_CERT
client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

### Option 4: Disable SSL Verification (Not Recommended)

```python
from gds_vault import VaultClient

# WARNING: Only use this in development/testing!
client = VaultClient(
    vault_addr="https://vault.example.com",
    verify_ssl=False
)
```

---

## Configuration Methods

### Method 1: Constructor Parameters

```python
from gds_vault import VaultClient

# Enable verification with custom certificate
client = VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="/path/to/cert/vault-ca.crt",
    verify_ssl=True  # This is the default
)

# Disable verification (not recommended)
client = VaultClient(
    vault_addr="https://vault.example.com",
    verify_ssl=False
)
```

### Method 2: Environment Variables

Set these environment variables before running your application:

```bash
# Vault server address
export VAULT_ADDR="https://vault.example.com"

# SSL certificate path (optional)
export VAULT_SSL_CERT="/path/to/vault-ca.crt"

# Authentication credentials
export VAULT_ROLE_ID="your-role-id"
export VAULT_SECRET_ID="your-secret-id"
```

Then use the client without parameters:

```python
from gds_vault import VaultClient

client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

### Method 3: Context Manager

```python
from gds_vault import VaultClient

with VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="/path/to/vault-ca.crt"
) as client:
    secret = client.get_secret('secret/data/myapp')
    # Client automatically cleans up on exit
```

### Method 4: Dynamic Configuration

```python
from gds_vault import VaultClient

client = VaultClient(vault_addr="https://vault.example.com")

# Update SSL configuration after initialization
client.ssl_cert_path = "/path/to/vault-ca.crt"
client.verify_ssl = True

secret = client.get_secret('secret/data/myapp')
```

---

## Common Scenarios

### Scenario 1: Corporate Environment with Custom CA

Many organizations use internal Certificate Authorities. Here's how to configure it:

```python
from gds_vault import VaultClient

# Path to your organization's CA bundle
client = VaultClient(
    vault_addr="https://vault.corp.example.com",
    ssl_cert_path="/etc/ssl/certs/corporate-ca-bundle.crt"
)

secret = client.get_secret('secret/data/myapp')
```

### Scenario 2: Development with Self-Signed Certificate

For development environments with self-signed certificates:

#### Step 1: Export the certificate from Vault server

```bash
# On the Vault server
openssl s_client -connect vault.dev.local:8200 -showcerts \
    < /dev/null 2>/dev/null | \
    openssl x509 -outform PEM > vault-dev.crt
```

#### Step 2: Copy certificate to your project

```bash
cp vault-dev.crt /path/to/cert/
```

#### Step 3: Configure client

```python
from gds_vault import VaultClient
import os

# Get the absolute path to the certificate
cert_path = os.path.join(
    os.path.dirname(__file__), 
    "gds_vault", 
    "cert", 
    "vault-dev.crt"
)

client = VaultClient(
    vault_addr="https://vault.dev.local:8200",
    ssl_cert_path=cert_path
)
```

### Scenario 3: Multiple Vault Servers

If you need to connect to multiple Vault servers with different certificates:

```python
from gds_vault import VaultClient

# Production Vault
prod_client = VaultClient(
    vault_addr="https://vault.prod.example.com",
    ssl_cert_path="/etc/ssl/certs/prod-ca.crt"
)

# Development Vault
dev_client = VaultClient(
    vault_addr="https://vault.dev.example.com",
    ssl_cert_path="/path/to/dev-ca.crt"
)

# Use each client for its environment
prod_secret = prod_client.get_secret('secret/data/prod/app')
dev_secret = dev_client.get_secret('secret/data/dev/app')
```

### Scenario 4: CI/CD Pipeline

In CI/CD environments, use environment variables:

```yaml
# .github/workflows/deploy.yml
env:
  VAULT_ADDR: ${{ secrets.VAULT_ADDR }}
  VAULT_ROLE_ID: ${{ secrets.VAULT_ROLE_ID }}
  VAULT_SECRET_ID: ${{ secrets.VAULT_SECRET_ID }}
  VAULT_SSL_CERT: /etc/ssl/certs/vault-ca.crt

steps:
  - name: Setup SSL certificate
    run: |
      echo "${{ secrets.VAULT_CA_CERT }}" > /etc/ssl/certs/vault-ca.crt
      chmod 600 /etc/ssl/certs/vault-ca.crt
  
  - name: Fetch secrets
    run: python deploy.py
```

```python
# deploy.py
from gds_vault import VaultClient

# Uses environment variables automatically
client = VaultClient()
secrets = client.get_secret('secret/data/deploy/config')
```

### Scenario 5: Docker Container

When running in Docker, mount the certificate:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Copy certificate
COPY certs/vault-ca.crt /app/certs/vault-ca.crt
RUN chmod 600 /app/certs/vault-ca.crt

# Set environment variable
ENV VAULT_SSL_CERT=/app/certs/vault-ca.crt

COPY . /app
WORKDIR /app

RUN pip install -e .
CMD ["python", "app.py"]
```

Or mount it at runtime:

```bash
docker run -v /path/to/cert:/certs:ro \
    -e VAULT_SSL_CERT=/cert/vault-ca.crt \
    -e VAULT_ADDR=https://vault.example.com \
    my-app
```

---

## Troubleshooting

### Error: SSL Certificate Verify Failed

**Symptom:**
```
requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] 
certificate verify failed: unable to get local issuer certificate
```

**Solutions:**

1. **Specify the CA certificate:**
   ```python
   client = VaultClient(
       vault_addr="https://vault.example.com",
       ssl_cert_path="/path/to/ca-bundle.crt"
   )
   ```

2. **Check certificate path is correct:**
   ```python
   import os
   cert_path = "/path/to/ca-bundle.crt"
   assert os.path.exists(cert_path), f"Certificate not found: {cert_path}"
   ```

3. **Verify certificate is readable:**
   ```bash
   ls -la /path/to/ca-bundle.crt
   chmod 644 /path/to/ca-bundle.crt
   ```

4. **Test with curl:**
   ```bash
   curl --cacert /path/to/ca-bundle.crt https://vault.example.com/v1/sys/health
   ```

### Error: Certificate Has Expired

**Symptom:**
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired
```

**Solutions:**

1. **Update your certificate:**
   - Contact your Vault administrator for a new certificate
   - Replace the old certificate file with the new one

2. **Check certificate validity:**
   ```bash
   openssl x509 -in vault-ca.crt -noout -dates
   ```

### Error: Hostname Mismatch

**Symptom:**
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: 
Hostname mismatch, certificate is not valid for 'vault.example.com'
```

**Solutions:**

1. **Verify hostname matches certificate:**
   ```bash
   openssl x509 -in vault-ca.crt -noout -text | grep -A1 "Subject Alternative Name"
   ```

2. **Use correct hostname in VAULT_ADDR:**
   ```python
   # Wrong - IP address may not match certificate
   client = VaultClient(vault_addr="https://192.168.1.100:8200")
   
   # Correct - use the hostname from the certificate
   client = VaultClient(vault_addr="https://vault.example.com:8200")
   ```

### Error: Permission Denied

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: '/path/to/vault-ca.crt'
```

**Solutions:**

1. **Fix file permissions:**
   ```bash
   chmod 644 /path/to/vault-ca.crt
   ```

2. **Check directory permissions:**
   ```bash
   chmod 755 /path/to/cert/
   ```

### Error: File Not Found

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/vault-ca.crt'
```

**Solutions:**

1. **Use absolute path:**
   ```python
   import os
   cert_path = os.path.abspath("cert/vault-ca.crt")
   client = VaultClient(ssl_cert_path=cert_path)
   ```

2. **Verify file exists:**
   ```bash
   ls -la /path/to/vault-ca.crt
   ```

---

## Security Best Practices

### 1. Always Verify SSL in Production

```python
# ✅ GOOD - Verification enabled (default)
client = VaultClient(vault_addr="https://vault.example.com")

# ❌ BAD - Verification disabled
client = VaultClient(vault_addr="https://vault.example.com", verify_ssl=False)
```

### 2. Protect Certificate Files

```bash
# Set restrictive permissions
chmod 600 vault-ca.crt

# Restrict directory access
chmod 700 cert/

# Never commit certificates to version control
echo "*.crt" >> .gitignore
echo "*.pem" >> .gitignore
```

### 3. Use Environment Variables for Paths

```python
# ✅ GOOD - Configurable via environment
cert_path = os.getenv("VAULT_SSL_CERT", "/etc/ssl/certs/vault-ca.crt")
client = VaultClient(ssl_cert_path=cert_path)

# ❌ BAD - Hardcoded path
client = VaultClient(ssl_cert_path="/home/user/vault-ca.crt")
```

### 4. Validate Certificate Before Use

```python
import os
from pathlib import Path

def get_vault_client(vault_addr: str, cert_path: str) -> VaultClient:
    """Create Vault client with certificate validation."""
    
    # Validate certificate exists
    if not Path(cert_path).exists():
        raise FileNotFoundError(f"Certificate not found: {cert_path}")
    
    # Validate certificate is readable
    if not os.access(cert_path, os.R_OK):
        raise PermissionError(f"Certificate not readable: {cert_path}")
    
    return VaultClient(
        vault_addr=vault_addr,
        ssl_cert_path=cert_path
    )
```

### 5. Monitor Certificate Expiration

```python
import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

def check_cert_expiry(cert_path: str, warning_days: int = 30):
    """Check if certificate will expire soon."""
    with open(cert_path, 'rb') as f:
        cert = x509.load_pem_x509_certificate(f.read(), default_backend())
    
    expiry = cert.not_valid_after
    days_until_expiry = (expiry - datetime.datetime.now()).days
    
    if days_until_expiry < 0:
        raise ValueError(f"Certificate expired {abs(days_until_expiry)} days ago")
    elif days_until_expiry < warning_days:
        print(f"WARNING: Certificate expires in {days_until_expiry} days")
    
    return days_until_expiry
```

### 6. Separate Certificates by Environment

```python
import os

# Directory structure:
# cert/
#   ├── prod/vault-ca.crt
#   ├── staging/vault-ca.crt
#   └── dev/vault-ca.crt

env = os.getenv("ENVIRONMENT", "dev")
cert_path = f"cert/{env}/vault-ca.crt"

client = VaultClient(
    vault_addr=os.getenv(f"VAULT_ADDR_{env.upper()}"),
    ssl_cert_path=cert_path
)
```

### 7. Use Certificate Bundles

If you need to trust multiple CAs:

```bash
# Create a certificate bundle
cat ca1.crt ca2.crt ca3.crt > vault-ca-bundle.crt
```

```python
client = VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="cert/vault-ca-bundle.crt"
)
```

---

## Certificate Management

### Obtaining Certificates

#### From Vault Administrator

Contact your Vault administrator to obtain:
- CA certificate (`.crt` or `.pem` file)
- Certificate validity period
- Any special configuration requirements

#### From Vault Server

```bash
# Extract certificate from running Vault server
openssl s_client -connect vault.example.com:8200 -showcerts \
    < /dev/null 2>/dev/null | \
    openssl x509 -outform PEM > vault-ca.crt
```

#### From System Trust Store

On Linux systems with system-wide trust:

```python
# Use system certificates
client = VaultClient(
    vault_addr="https://vault.example.com",
    # verify_ssl=True uses system certificates by default
)
```

### Certificate Rotation

When certificates are rotated:

1. **Obtain new certificate** from your administrator
2. **Test new certificate** in non-production environment
3. **Update production** certificate file
4. **Restart applications** to pick up new certificate

```bash
# Backup old certificate
cp vault-ca.crt vault-ca.crt.old

# Deploy new certificate
cp new-vault-ca.crt vault-ca.crt

# Restart application
systemctl restart myapp
```

---

## Environment-Specific Configuration

### Development Environment

```python
# dev_config.py
from gds_vault import VaultClient

def get_dev_client():
    """Development Vault client with lenient SSL."""
    return VaultClient(
        vault_addr="https://vault.dev.local:8200",
        ssl_cert_path="cert/dev/vault-dev.crt",
        timeout=30  # Longer timeout for dev
    )
```

### Staging Environment

```python
# staging_config.py
from gds_vault import VaultClient

def get_staging_client():
    """Staging Vault client with proper SSL."""
    return VaultClient(
        vault_addr="https://vault.staging.example.com",
        ssl_cert_path="/etc/ssl/certs/vault-staging-ca.crt"
    )
```

### Production Environment

```python
# prod_config.py
from gds_vault import VaultClient
import os

def get_prod_client():
    """Production Vault client with strict SSL."""
    # Use environment variables in production
    vault_addr = os.getenv("VAULT_ADDR")
    cert_path = os.getenv("VAULT_SSL_CERT")
    
    if not vault_addr or not cert_path:
        raise ValueError("VAULT_ADDR and VAULT_SSL_CERT must be set")
    
    return VaultClient(
        vault_addr=vault_addr,
        ssl_cert_path=cert_path,
        timeout=10,
        verify_ssl=True  # Never disable in production!
    )
```

---

## Testing SSL Configuration

### Test Script

```python
#!/usr/bin/env python3
"""Test Vault SSL configuration."""

import sys
from gds_vault import VaultClient
from gds_vault.exceptions import VaultError

def test_ssl_config():
    """Test SSL configuration."""
    try:
        client = VaultClient(
            vault_addr="https://vault.example.com",
            ssl_cert_path="/path/to/vault-ca.crt"
        )
        
        # Try to authenticate
        client.authenticate()
        print("✅ SSL configuration successful!")
        print(f"✅ Connected to {client.vault_addr}")
        return 0
        
    except VaultError as e:
        print(f"❌ SSL configuration failed: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(test_ssl_config())
```

Run the test:

```bash
python test_ssl.py
```

---

## Additional Resources

- [HashiCorp Vault TLS Documentation](https://www.vaultproject.io/docs/configuration/listener/tcp#tls_parameters)
- [Python Requests SSL Verification](https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification)
- [OpenSSL Commands](https://www.openssl.org/docs/man1.1.1/man1/)
- [Certificate Formats](https://knowledge.digicert.com/solution/SO26449.html)

---

## Summary

### Key Takeaways

1. **Always enable SSL verification in production** - Use `verify_ssl=True` (default)
2. **Use custom certificates for self-signed or internal CAs** - Specify `ssl_cert_path`
3. **Protect certificate files** - Use appropriate permissions and never commit to version control
4. **Use environment variables** - Keep configuration flexible across environments
5. **Monitor certificate expiration** - Set up alerts for certificate renewal
6. **Test your configuration** - Verify SSL setup before deploying

### Quick Reference

```python
# Production (recommended)
client = VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="/path/to/ca-bundle.crt"
)

# Development (with environment variables)
export VAULT_ADDR="https://vault.dev.local"
export VAULT_SSL_CERT="/path/to/dev-ca.crt"
client = VaultClient()

# Testing only (not for production!)
client = VaultClient(
    vault_addr="https://vault.test.local",
    verify_ssl=False
)
```

---

**Need Help?**

- Check [cert/README.md](cert/README.md) for certificate directory setup
- Review [README.md](README.md) for general usage
- See [examples/ssl_example.py](examples/ssl_example.py) for code samples
