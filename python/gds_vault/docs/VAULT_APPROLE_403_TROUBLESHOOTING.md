# Vault AppRole 403 Error Troubleshooting Guide

## Error Message
```
AppRole authentication failed with status 403: {"errors":["permission denied"]}
```

## What This Error Means

A **403 Forbidden** response from Vault's AppRole authentication endpoint indicates that:
- The request reached Vault successfully
- Vault understood the request
- **BUT** Vault rejected the credentials or the AppRole lacks proper authorization

---

## Common Causes & Solutions

### 1. Invalid or Expired Credentials ⚠️ (Most Common)

**Problem:** Your `role_id` or `secret_id` are incorrect, expired, or have been rotated.

**Check:**
```bash
# Print your credentials (redacted)
echo "VAULT_ROLE_ID: ${VAULT_ROLE_ID:0:8}...${VAULT_ROLE_ID: -4}"
echo "VAULT_SECRET_ID: ${VAULT_SECRET_ID:0:8}...${VAULT_SECRET_ID: -4}"
```

**Solutions:**
- Verify credentials with your Vault administrator
- Check if credentials were recently rotated
- Ensure you're using the correct environment (dev/staging/prod)
- Look for typos or extra whitespace in credentials

**Generate new credentials (requires Vault CLI & token):**
```bash
# Get a new secret_id for your role
vault write -f auth/approle/role/YOUR-ROLE-NAME/secret-id

# Output will include new secret_id
```

---

### 2. Secret ID Already Used (Single-Use Configuration)

**Problem:** Secret IDs can be configured as single-use. Once used, they're invalid.

**Check AppRole configuration:**
```bash
vault read auth/approle/role/YOUR-ROLE-NAME
# Look for: secret_id_num_uses
```

If `secret_id_num_uses = 1`, each secret_id can only be used once.

**Solution:**
```bash
# Generate a fresh secret_id
vault write -f auth/approle/role/YOUR-ROLE-NAME/secret-id
```

---

### 3. IP/CIDR Restrictions

**Problem:** AppRole may be bound to specific IP addresses or CIDR ranges.

**Check your current IP:**
```bash
curl -s ifconfig.me
# or
curl -s https://api.ipify.org
```

**Check AppRole IP restrictions:**
```bash
vault read auth/approle/role/YOUR-ROLE-NAME
# Look for: bound_cidr_list, secret_id_bound_cidrs
```

**Example output:**
```
bound_cidr_list = [10.0.0.0/8, 172.16.0.0/12]
```

**Solution:**
- Ensure you're connecting from an allowed IP
- Contact Vault admin to update CIDR restrictions
- If testing locally, add your IP to the allowed list

**Update CIDR list (requires admin privileges):**
```bash
vault write auth/approle/role/YOUR-ROLE-NAME \
    bound_cidr_list="10.0.0.0/8,172.16.0.0/12,YOUR.IP.ADDRESS/32"
```

---

### 4. AppRole Not Properly Configured

**Problem:** AppRole exists but lacks necessary policies or configuration.

**Check if AppRole exists:**
```bash
vault list auth/approle/role
vault read auth/approle/role/YOUR-ROLE-NAME
```

**Check assigned policies:**
```bash
vault read auth/approle/role/YOUR-ROLE-NAME
# Look for: token_policies or policies
```

**Solution:**
Contact your Vault administrator to verify:
- AppRole has correct policies attached
- Policies grant necessary permissions
- AppRole is enabled and active

---

### 5. AppRole Auth Method Not Enabled or Wrong Path

**Problem:** AppRole auth method might not be enabled or mounted at a different path.

**Check enabled auth methods:**
```bash
vault auth list
```

**Expected output should include:**
```
Path         Type        Description
----         ----        -----------
approle/     approle     n/a
```

**If not enabled:**
```bash
vault auth enable approle
```

**If mounted at different path:**
Update your code to use the correct path:
```python
# Default path
login_url = f"{vault_addr}/v1/auth/approle/login"

# Custom path (e.g., 'app-auth')
login_url = f"{vault_addr}/v1/auth/app-auth/login"
```

---

### 6. Network/SSL Issues

**Problem:** Network issues, SSL certificate problems, or firewall rules.

**Test basic connectivity:**
```bash
# Test Vault health endpoint
curl -k https://your-vault-server:8200/v1/sys/health

# Test AppRole endpoint with credentials
curl -k -X POST \
  https://your-vault-server:8200/v1/auth/approle/login \
  -d '{"role_id":"YOUR-ROLE-ID","secret_id":"YOUR-SECRET-ID"}'
```

**SSL Certificate Issues:**
```bash
# Option 1: Set custom cert path
export VAULT_SSL_CERT=/path/to/ca-bundle.crt

# Option 2: Disable SSL verification (NOT for production!)
export VAULT_SKIP_VERIFY=true
```

---

### 7. Vault Server Issues

**Problem:** Vault is sealed, not initialized, or having internal issues.

**Check Vault status:**
```bash
vault status
```

**If sealed:**
```bash
vault operator unseal
# Enter unseal keys when prompted
```

---

## Diagnostic Script

Run the included diagnostic script to automatically check for common issues:

```bash
# Set your environment variables
export VAULT_ADDR="https://your-vault-server:8200"
export VAULT_ROLE_ID="your-role-id"
export VAULT_SECRET_ID="your-secret-id"

# Run diagnostic
python diagnose_vault_approle.py
```

---

## Quick Test with gds_vault

Test authentication using the gds_vault library:

```python
from gds_vault import VaultClient, AppRoleAuth

# Explicit credentials
auth = AppRoleAuth(
    role_id="your-role-id",
    secret_id="your-secret-id"
)

try:
    client = VaultClient(
        vault_addr="https://your-vault-server:8200",
        auth=auth
    )
    # Try to fetch a test secret
    secret = client.get_secret("secret/data/test")
    print("✓ Authentication successful!")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
```

---

## Vault Administrator Actions

If you're a Vault administrator, here's how to troubleshoot from the Vault side:

### 1. Check AppRole Configuration
```bash
# List all AppRoles
vault list auth/approle/role

# Read specific AppRole details
vault read auth/approle/role/YOUR-ROLE-NAME
```

### 2. Verify Role ID
```bash
# Get role_id for an AppRole
vault read auth/approle/role/YOUR-ROLE-NAME/role-id
```

### 3. Generate New Secret ID
```bash
# Generate a new secret_id
vault write -f auth/approle/role/YOUR-ROLE-NAME/secret-id

# Generate with custom TTL
vault write auth/approle/role/YOUR-ROLE-NAME/secret-id ttl=1h
```

### 4. Check Audit Logs
```bash
# View audit logs for failed authentication attempts
vault audit list

# Tail audit log (if file-based)
tail -f /var/log/vault/audit.log | grep approle
```

### 5. Update AppRole Policies
```bash
# Update policies attached to AppRole
vault write auth/approle/role/YOUR-ROLE-NAME \
    token_policies="policy1,policy2,policy3"
```

### 6. Update CIDR Restrictions
```bash
# Allow additional IPs
vault write auth/approle/role/YOUR-ROLE-NAME \
    bound_cidr_list="10.0.0.0/8,172.16.0.0/12,192.168.1.0/24"
```

---

## Testing Workflow

Follow this workflow to systematically identify the issue:

1. **Verify environment variables are set**
   ```bash
   echo $VAULT_ADDR
   echo $VAULT_ROLE_ID
   echo $VAULT_SECRET_ID
   ```

2. **Test Vault connectivity**
   ```bash
   curl -k $VAULT_ADDR/v1/sys/health
   ```

3. **Run diagnostic script**
   ```bash
   python diagnose_vault_approle.py
   ```

4. **Test with curl**
   ```bash
   curl -k -X POST $VAULT_ADDR/v1/auth/approle/login \
     -d "{\"role_id\":\"$VAULT_ROLE_ID\",\"secret_id\":\"$VAULT_SECRET_ID\"}"
   ```

5. **Contact Vault administrator** if all above steps fail

---

## Prevention Tips

To avoid future 403 errors:

1. **Use token lifecycle management** - Rotate credentials regularly
2. **Monitor secret_id usage** - Track when secret_ids are consumed
3. **Set up alerts** - Monitor failed authentication attempts
4. **Document CIDR ranges** - Keep track of allowed IP addresses
5. **Use automation** - Automate credential rotation
6. **Test after changes** - Always test after infrastructure changes

---

## Related Documentation

- [gds_vault README](./gds_vault/README.md)
- [Vault Module Tutorial](./docs/tutorials/02_VAULT_MODULE_TUTORIAL.md)
- [SSL Configuration Guide](./gds_vault/SSL_CONFIGURATION.md)
- [HashiCorp Vault AppRole Docs](https://developer.hashicorp.com/vault/docs/auth/approle)

---

## Getting Help

If you're still experiencing issues:

1. Run the diagnostic script and save the output
2. Collect relevant log files
3. Note your Vault version: `vault version`
4. Contact your Vault administrator with:
   - Error message
   - Diagnostic output
   - Your IP address
   - The AppRole name you're trying to use

---

## Summary Checklist

- [ ] Environment variables are set correctly
- [ ] Vault server is reachable
- [ ] Vault is unsealed and healthy
- [ ] AppRole auth method is enabled
- [ ] role_id and secret_id are valid and not expired
- [ ] secret_id hasn't been used (if single-use)
- [ ] Your IP address is in the allowed CIDR range
- [ ] AppRole has correct policies attached
- [ ] Policies grant necessary permissions
- [ ] SSL certificates are configured properly
- [ ] No typos or extra whitespace in credentials
