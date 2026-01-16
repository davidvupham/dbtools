# How to Fix Vault SSL Certificate Errors - Complete Guide

## Problem Statement

When connecting to HashiCorp Vault servers with self-signed certificates or custom Certificate Authorities (CAs), you may encounter SSL certificate verification errors like:

```
requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
certificate verify failed: unable to get local issuer certificate
```

## Solution Overview

The `gds-vault` package now supports three ways to handle SSL certificates:

1. **Use custom CA certificate** (Recommended) ✅
2. **Use environment variable** (Flexible) ✅
3. **Disable SSL verification** (Development only) ⚠️

---

## Quick Fix (3 Steps)

### Step 1: Get Your Certificate

Ask your Vault administrator for the CA certificate, or extract it:

```bash
openssl s_client -connect vault.example.com:8200 -showcerts \
    < /dev/null 2>/dev/null | \
    openssl x509 -outform PEM > vault-ca.crt
```

### Step 2: Place the Certificate

```bash
# Create directory
mkdir -p cert

# Copy certificate
cp vault-ca.crt cert/

# Set permissions
chmod 600 cert/vault-ca.crt
```

### Step 3: Update Your Code

**Option A: Direct Parameter**
```python
from gds_vault import VaultClient

client = VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="cert/vault-ca.crt"
)
secret = client.get_secret('secret/data/myapp')
```

**Option B: Environment Variable**
```bash
export VAULT_SSL_CERT="/path/to/cert/vault-ca.crt"
```
```python
from gds_vault import VaultClient

client = VaultClient()  # Uses VAULT_SSL_CERT automatically
secret = client.get_secret('secret/data/myapp')
```

**That's it!** ✅

---

## Detailed Solutions

### Solution 1: Use Custom Certificate (Recommended)

This is the **recommended approach** for production environments.

```python
from gds_vault import VaultClient

# Specify certificate path
client = VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="/path/to/vault-ca.crt"
)

# Use the client
secret = client.get_secret('secret/data/myapp')
password = secret['password']
```

**Advantages:**
- ✅ Secure - verifies server identity
- ✅ Works with self-signed certificates
- ✅ Works with custom CAs
- ✅ Production-ready

### Solution 2: Environment Variable

Best for containerized environments, CI/CD, and flexible deployments.

```bash
# Set environment variables
export VAULT_ADDR="https://vault.example.com"
export VAULT_SSL_CERT="/path/to/vault-ca.crt"
export VAULT_ROLE_ID="your-role-id"
export VAULT_SECRET_ID="your-secret-id"
```

```python
from gds_vault import VaultClient

# Client reads all config from environment
client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

**Advantages:**
- ✅ No hardcoded paths
- ✅ Easy to change per environment
- ✅ Works with Docker/Kubernetes
- ✅ CI/CD friendly

### Solution 3: Disable SSL Verification (Development Only)

**⚠️ WARNING: Only use in development/testing! Never in production!**

```python
from gds_vault import VaultClient

# Disable SSL verification
client = VaultClient(
    vault_addr="https://vault.dev.local",
    verify_ssl=False  # ⚠️ NOT for production!
)
secret = client.get_secret('secret/data/myapp')
```

**Use cases:**
- ⚠️ Local development only
- ⚠️ Testing environments
- ❌ Never in production
- ❌ Never with sensitive data

---

## Complete Configuration Examples

### Example 1: Production Setup

```python
"""Production configuration with proper SSL verification."""
import os
from gds_vault import VaultClient

def get_production_client():
    # Use environment variables in production
    vault_addr = os.getenv("VAULT_ADDR")
    cert_path = os.getenv("VAULT_SSL_CERT")

    if not vault_addr or not cert_path:
        raise ValueError("VAULT_ADDR and VAULT_SSL_CERT required")

    return VaultClient(
        vault_addr=vault_addr,
        ssl_cert_path=cert_path,
        verify_ssl=True  # Always true in production!
    )

# Usage
client = get_production_client()
db_secret = client.get_secret('secret/data/prod/database')
```

### Example 2: Docker Container

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Copy certificate
COPY certs/vault-ca.crt /app/certs/vault-ca.crt
RUN chmod 600 /app/certs/vault-ca.crt

# Set environment
ENV VAULT_SSL_CERT=/app/certs/vault-ca.crt
ENV VAULT_ADDR=https://vault.example.com

# Install app
COPY . /app
WORKDIR /app
RUN pip install -e .

CMD ["python", "app.py"]
```

**app.py:**
```python
from gds_vault import VaultClient

# Uses environment variables from Dockerfile
client = VaultClient()
secret = client.get_secret('secret/data/myapp')
```

**Or mount certificate at runtime:**
```bash
docker run -v /host/certs:/certs:ro \
    -e VAULT_SSL_CERT=/cert/vault-ca.crt \
    -e VAULT_ADDR=https://vault.example.com \
    my-app
```

### Example 3: Multiple Environments

```python
"""Handle multiple environments with different certificates."""
import os
from gds_vault import VaultClient

# Environment-specific configuration
ENVIRONMENTS = {
    'prod': {
        'vault_addr': 'https://vault.prod.example.com',
        'cert_path': '/etc/ssl/certs/prod-vault-ca.crt'
    },
    'staging': {
        'vault_addr': 'https://vault.staging.example.com',
        'cert_path': '/etc/ssl/certs/staging-vault-ca.crt'
    },
    'dev': {
        'vault_addr': 'https://vault.dev.local',
        'cert_path': 'cert/dev-vault-ca.crt'
    }
}

def get_client_for_environment(env: str):
    config = ENVIRONMENTS.get(env)
    if not config:
        raise ValueError(f"Unknown environment: {env}")

    return VaultClient(
        vault_addr=config['vault_addr'],
        ssl_cert_path=config['cert_path']
    )

# Usage
env = os.getenv('ENVIRONMENT', 'dev')
client = get_client_for_environment(env)
```

---

## Troubleshooting

### Problem: Certificate file not found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/vault-ca.crt'
```

**Solutions:**
1. Verify file exists: `ls -la /path/to/vault-ca.crt`
2. Use absolute path: `os.path.abspath('cert/vault-ca.crt')`
3. Check spelling and path

### Problem: Permission denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/path/to/vault-ca.crt'
```

**Solutions:**
```bash
# Make file readable
chmod 644 /path/to/vault-ca.crt

# Or for more security
chmod 600 /path/to/vault-ca.crt
```

### Problem: Certificate expired

**Error:**
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate has expired
```

**Solutions:**
1. Get updated certificate from Vault administrator
2. Check expiry: `openssl x509 -in vault-ca.crt -noout -dates`
3. Replace expired certificate

### Problem: Hostname mismatch

**Error:**
```
Hostname mismatch, certificate is not valid for 'vault.example.com'
```

**Solutions:**
1. Use hostname from certificate (not IP address)
2. Check certificate SAN: `openssl x509 -in vault-ca.crt -noout -text | grep -A1 "Subject Alternative Name"`
3. Ensure `VAULT_ADDR` matches certificate hostname

---

## Testing Your Configuration

### Quick Test Script

```python
#!/usr/bin/env python3
"""Test SSL configuration."""
import sys
from gds_vault import VaultClient
from gds_vault.exceptions import VaultError

def test_ssl():
    try:
        client = VaultClient(
            vault_addr="https://vault.example.com",
            ssl_cert_path="/path/to/vault-ca.crt"
        )

        # Test authentication
        client.authenticate()
        print("✅ SSL configuration successful!")
        print(f"✅ Connected to: {client.vault_addr}")
        return 0

    except VaultError as e:
        print(f"❌ Failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_ssl())
```

Run test:
```bash
python test_ssl.py
```

---

## Security Best Practices

### ✅ DO:

1. **Always verify SSL in production**
   ```python
   client = VaultClient(verify_ssl=True)  # This is the default
   ```

2. **Use custom certificates for self-signed CAs**
   ```python
   client = VaultClient(ssl_cert_path="/path/to/ca.crt")
   ```

3. **Protect certificate files**
   ```bash
   chmod 600 vault-ca.crt
   ```

4. **Use environment variables**
   ```bash
   export VAULT_SSL_CERT="/path/to/cert.crt"
   ```

5. **Keep certificates outside version control**
   ```bash
   echo "*.crt" >> .gitignore
   ```

### ❌ DON'T:

1. **Never disable SSL in production**
   ```python
   # ❌ BAD - Never do this in production!
   client = VaultClient(verify_ssl=False)
   ```

2. **Never commit certificates to git**
   ```bash
   # ❌ BAD
   git add vault-ca.crt
   ```

3. **Never hardcode certificate paths**
   ```python
   # ❌ BAD - Use environment variables instead
   client = VaultClient(ssl_cert_path="/home/user/cert.crt")
   ```

4. **Never use expired certificates**
   - Check expiry regularly
   - Set up renewal reminders

---

## Certificate Management

### Obtaining Certificates

**From Vault Administrator:**
- Contact your Vault/security team
- Request CA certificate bundle
- Get validity period information

**From Vault Server:**
```bash
# Extract certificate
openssl s_client -connect vault.example.com:8200 -showcerts \
    < /dev/null 2>/dev/null | \
    openssl x509 -outform PEM > vault-ca.crt

# Verify certificate
openssl x509 -in vault-ca.crt -text -noout
```

### Certificate Rotation

When certificates are renewed:

1. **Test new certificate in non-prod first**
2. **Backup old certificate**
   ```bash
   cp vault-ca.crt vault-ca.crt.backup.$(date +%Y%m%d)
   ```
3. **Update certificate file**
   ```bash
   cp new-vault-ca.crt vault-ca.crt
   ```
4. **Restart applications**
5. **Verify connections work**

---

## Additional Resources

### Documentation

- 📘 **Complete Guide:** [SSL_CONFIGURATION.md](SSL_CONFIGURATION.md) - 400+ line comprehensive guide
- 📁 **Certificate Setup:** [cert/README.md](cert/README.md) - Certificate directory guide
- 💻 **Code Examples:** [examples/ssl_example.py](examples/ssl_example.py) - 10+ working examples
- 📖 **Main Docs:** [README.md](README.md) - Package documentation
- 📋 **Quick Ref:** [SSL_QUICK_REFERENCE.md](SSL_QUICK_REFERENCE.md) - Quick solutions
- 📝 **Summary:** [SSL_IMPLEMENTATION_SUMMARY.md](SSL_IMPLEMENTATION_SUMMARY.md) - Implementation details

### Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VAULT_ADDR` | Yes | Vault server address | `https://vault.example.com` |
| `VAULT_ROLE_ID` | Yes* | AppRole role_id | `role-id-string` |
| `VAULT_SECRET_ID` | Yes* | AppRole secret_id | `secret-id-string` |
| `VAULT_TOKEN` | Yes** | Direct token | `hvs.CAESIF...` |
| `VAULT_SSL_CERT` | No | SSL certificate path | `/path/to/vault-ca.crt` |

\* Required for AppRole authentication
\** Required for Token authentication (alternative to AppRole)

---

## Summary

### Problem
SSL certificate verification errors when connecting to Vault

### Solution
1. Obtain CA certificate from Vault administrator
2. Place certificate in `cert/` directory
3. Configure client with `ssl_cert_path` parameter or `VAULT_SSL_CERT` environment variable

### Quick Start
```python
from gds_vault import VaultClient

client = VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="cert/vault-ca.crt"
)
secret = client.get_secret('secret/data/myapp')
```

### Benefits
- ✅ Secure SSL verification
- ✅ Works with self-signed certificates
- ✅ Works with custom CAs
- ✅ Production-ready
- ✅ Flexible configuration
- ✅ Backward compatible

---

## Need Help?

1. **Quick Reference:** See [SSL_QUICK_REFERENCE.md](SSL_QUICK_REFERENCE.md)
2. **Detailed Guide:** Read [SSL_CONFIGURATION.md](SSL_CONFIGURATION.md)
3. **Examples:** Run [examples/ssl_example.py](examples/ssl_example.py)
4. **Certificate Setup:** Check [cert/README.md](cert/README.md)
5. **Contact:** Your Vault administrator for certificate-specific issues

---

**Version:** 0.2.0+ssl
**Last Updated:** October 7, 2025
**Status:** ✅ Production Ready
