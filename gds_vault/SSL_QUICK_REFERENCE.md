# SSL Certificate Quick Reference

## Quick Solutions for Common SSL Errors

### ❌ Error: `[SSL: CERTIFICATE_VERIFY_FAILED]`

**Problem:** Vault uses self-signed or custom CA certificate

**Solution 1 - Specify Certificate:**
```python
from gds_vault import VaultClient

client = VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="/path/to/vault-ca.crt"
)
```

**Solution 2 - Environment Variable:**
```bash
export VAULT_SSL_CERT="/path/to/vault-ca.crt"
```
```python
client = VaultClient()  # Uses env var automatically
```

**Solution 3 - Disable (DEV ONLY):**
```python
client = VaultClient(verify_ssl=False)  # ⚠️ NOT for production!
```

---

## Quick Setup Guide

### Step 1: Get Certificate

Contact your Vault administrator or extract from server:
```bash
openssl s_client -connect vault.example.com:8200 -showcerts \
    < /dev/null 2>/dev/null | \
    openssl x509 -outform PEM > vault-ca.crt
```

### Step 2: Place Certificate

```bash
mkdir -p cert
cp vault-ca.crt cert/
chmod 600 cert/vault-ca.crt
```

### Step 3: Use in Code

```python
from gds_vault import VaultClient

client = VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="cert/vault-ca.crt"
)
secret = client.get_secret('secret/data/myapp')
```

---

## Configuration Cheat Sheet

| Method | Code Example |
|--------|-------------|
| **Default (System CA)** | `VaultClient()` |
| **Custom Certificate** | `VaultClient(ssl_cert_path="/path/to/cert.crt")` |
| **Environment Variable** | `export VAULT_SSL_CERT="/path/cert.crt"` |
| **Disable SSL (Dev)** | `VaultClient(verify_ssl=False)` |

---

## Environment Variables

```bash
# Required
export VAULT_ADDR="https://vault.example.com"
export VAULT_ROLE_ID="your-role-id"
export VAULT_SECRET_ID="your-secret-id"

# Optional - SSL Certificate
export VAULT_SSL_CERT="/path/to/vault-ca.crt"
```

---

## Test Your Configuration

```python
from gds_vault import VaultClient

try:
    client = VaultClient(ssl_cert_path="/path/to/vault-ca.crt")
    client.authenticate()
    print("✅ SSL configuration works!")
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## File Permissions

```bash
# Certificate file
chmod 600 vault-ca.crt

# Certificate directory
chmod 700 cert/
```

---

## Complete Documentation

- 📘 **Full Guide:** [SSL_CONFIGURATION.md](SSL_CONFIGURATION.md)
- 📁 **Certificate Setup:** [cert/README.md](cert/README.md)
- 💻 **Examples:** [examples/ssl_example.py](examples/ssl_example.py)
- 📖 **Main Docs:** [README.md](README.md)
