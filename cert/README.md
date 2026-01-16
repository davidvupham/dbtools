# SSL Certificates Directory

This directory is for storing SSL certificates used to verify connections to HashiCorp Vault servers.

## Purpose

When connecting to Vault servers with self-signed certificates or custom Certificate Authorities (CAs), you need to provide the CA certificate bundle to verify the SSL/TLS connection.

## How to Use

### 1. Place Your Certificate Here

Copy your Vault server's CA certificate bundle to this directory:

```bash
cp /path/to/your/vault-ca.crt python/gds_vault/certs/vault-ca.crt
```

### 2. Configure Your VaultClient

Then reference it in your code:

```python
from gds_vault import VaultClient

# Option 1: Specify path directly
client = VaultClient(
    vault_addr="https://vault.example.com",
    ssl_cert_path="/path/to/python/gds_vault/certs/vault-ca.crt"
)

# Option 2: Use environment variable
# Set VAULT_SSL_CERT=/path/to/python/gds_vault/certs/vault-ca.crt
client = VaultClient(vault_addr="https://vault.example.com")

# Option 3: Disable SSL verification (NOT RECOMMENDED for production)
client = VaultClient(
    vault_addr="https://vault.example.com",
    verify_ssl=False
)
```

## Certificate Formats

The certificate file should be in PEM format. Common file extensions:
- `.crt`
- `.pem`
- `.cer`

### Example PEM Format

```
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKZ5HHKJZl8DMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
...
-----END CERTIFICATE-----
```

## Common Scenarios

### Self-Signed Certificate

If your Vault server uses a self-signed certificate:

1. Export the certificate from your Vault server
2. Copy it to this directory
3. Configure your client to use it

### Custom CA

If your organization uses a custom Certificate Authority:

1. Obtain the CA certificate bundle from your security team
2. Copy it to this directory
3. Configure your client to use it

### Certificate Bundle

If you need to trust multiple CAs, create a bundle file:

```bash
cat ca1.crt ca2.crt ca3.crt > vault-ca-bundle.crt
```

## Security Best Practices

1. **Never commit certificates to version control** - Add `*.crt`, `*.pem` to `.gitignore`
2. **Restrict file permissions** - `chmod 600 vault-ca.crt`
3. **Use certificate verification in production** - Never disable `verify_ssl` in production
4. **Keep certificates up-to-date** - Monitor expiration dates
5. **Use environment variables** - Don't hardcode paths in production code

## Troubleshooting

### SSL Certificate Verify Failed

```
requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions:**
1. Ensure you have the correct CA certificate
2. Check that the certificate file path is correct
3. Verify the certificate is in PEM format
4. Check file permissions (must be readable)

### Certificate Has Expired

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired
```

**Solutions:**
1. Obtain an updated certificate from your Vault administrator
2. Update the certificate in this directory
3. Restart your application

### Hostname Mismatch

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: 
Hostname mismatch, certificate is not valid for 'vault.example.com'
```

**Solutions:**
1. Ensure `VAULT_ADDR` matches the certificate's Common Name (CN) or Subject Alternative Name (SAN)
2. Use the correct hostname in your Vault address
3. Obtain a certificate with the correct hostname

## Example Certificate Setup

```bash
# 1. Create certs directory (if not exists)
mkdir -p python/gds_vault/certs

# 2. Copy your certificate
cp ~/Downloads/vault-ca.crt python/gds_vault/certs/

# 3. Set secure permissions
chmod 600 python/gds_vault/certs/vault-ca.crt

# 4. Set environment variable (optional)
export VAULT_SSL_CERT="$(pwd)/python/gds_vault/certs/vault-ca.crt"

# 5. Run your application
python your_app.py
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VAULT_SSL_CERT` | Path to SSL certificate bundle | `/path/to/certs/vault-ca.crt` |
| `VAULT_ADDR` | Vault server address | `https://vault.example.com` |

## Related Documentation

- [SSL_CONFIGURATION.md](../SSL_CONFIGURATION.md) - Complete SSL configuration guide
- [README.md](../README.md) - Main package documentation
- [examples/ssl_example.py](../examples/ssl_example.py) - SSL usage examples

## .gitignore

Add these patterns to your `.gitignore`:

```gitignore
# SSL Certificates (never commit these!)
*.crt
*.pem
*.cer
*.key
*.p12
*.pfx

# Keep the README
!certs/README.md
```

## Support

For issues with SSL certificates:
1. Check this README for common solutions
2. Consult your Vault administrator
3. Review Vault server logs
4. Check your organization's security documentation
