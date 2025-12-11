# Runbook: AD Password Rotation Operations

## 1. Overview

This runbook provides operational procedures for managing the AD Password Rotation system in production.

## 2. Quick Reference

| Action | Command | When to Use |
|--------|---------|-------------|
| Check rotation status | `vault read ad/creds/<role>` | Verify current password |
| Force rotation | `vault write -f ad/rotate-role/<role>` | Emergency rotation |
| Check audit logs | `vault audit list` | Investigate issues |
| Restart Vault Agent | `systemctl restart vault-agent` | Agent not syncing |

## 3. Day-to-Day Operations

### 3.1 Health Checks

**Daily Checklist:**

```bash
# 1. Verify Vault is unsealed
vault status

# 2. Check AD engine health
vault read ad/config

# 3. List managed roles
vault list ad/roles

# 4. Verify recent rotations (check audit log)
tail -100 /var/log/vault/audit.log | grep "ad/rotate"
```

### 3.2 Monitoring Alerts

| Alert | Severity | Response |
|-------|----------|----------|
| `vault_ad_rotation_failed` | Critical | See [Rotation Failure](#41-rotation-failure) |
| `vault_agent_token_expired` | High | See [Agent Auth Failure](#42-agent-authentication-failure) |
| `ad_account_locked` | Critical | See [Account Lockout](#43-account-lockout) |
| `vault_sealed` | Critical | Contact Platform Team |

## 4. Incident Response Procedures

### 4.1 Rotation Failure

**Symptoms:**
- Alert: `vault_ad_rotation_failed`
- Application auth failures
- Audit log shows LDAP errors

**Procedure:**

```bash
# Step 1: Check Vault connectivity to AD
vault write ad/config \
    url="ldaps://dc01.example.com" \
    # Re-apply config to test connectivity

# Step 2: Verify Vault service account permissions
# In AD: Check svc_vault has "Reset Password" on target OU

# Step 3: Check network connectivity
Test-NetConnection -ComputerName dc01.example.com -Port 636

# Step 4: Force rotation once resolved
vault write -f ad/rotate-role/<role>

# Step 5: Verify password updated
vault read ad/creds/<role>
```

### 4.2 Agent Authentication Failure

**Symptoms:**
- Alert: `vault_agent_token_expired`
- Credential file not updated
- Application using stale password

**Procedure:**

```bash
# Step 1: Check agent status
systemctl status vault-agent
journalctl -u vault-agent -n 50

# Step 2: Verify role_id and secret_id files exist
ls -la /etc/vault.d/role_id /etc/vault.d/secret_id

# Step 3: Test AppRole auth manually
vault write auth/approle/login \
    role_id=$(cat /etc/vault.d/role_id) \
    secret_id=$(cat /etc/vault.d/secret_id)

# Step 4: If Secret ID expired, generate new one
# (On Vault server or via GitHub Actions)
vault write -f auth/approle/role/<role>/secret-id

# Step 5: Update secret_id file and restart agent
systemctl restart vault-agent
```

### 4.3 Account Lockout

**Symptoms:**
- Alert: `ad_account_locked`
- AD Event ID 4740 (Account Locked Out)
- Multiple auth failures in application logs

**Procedure:**

```powershell
# Step 1: Unlock account in AD
Unlock-ADAccount -Identity svc_mssql_prod

# Step 2: Identify source of bad password attempts
Get-WinEvent -FilterHashtable @{LogName='Security';ID=4625} |
    Where-Object { $_.Properties[5].Value -eq 'svc_mssql_prod' }

# Step 3: Force password rotation to sync
vault write -f ad/rotate-role/mssql-prod-svc

# Step 4: Verify agent picks up new password
# Check /etc/mssql/creds.json or equivalent

# Step 5: Restart affected service if needed
Restart-Service MSSQLSERVER
```

### 4.4 Service Won't Start After Rotation

**Symptoms:**
- Service fails to start
- "Logon failure" errors
- Password mismatch between AD and service config

**Procedure:**

```powershell
# Step 1: Get current password from Vault
$creds = vault read -format=json ad/creds/mssql-prod-svc | ConvertFrom-Json
$password = $creds.data.current_password

# Step 2: Manually update service
sc.exe config MSSQLSERVER obj= "DOMAIN\svc_mssql_prod" password= $password

# Step 3: Start service
Start-Service MSSQLSERVER

# Step 4: Investigate why agent didn't update
# Check agent logs, template output, command execution
```

## 5. Emergency Procedures

### 5.1 Break Glass: Vault Unavailable

When Vault is completely unavailable and you need to restore service:

> [!CAUTION]
> Manual password changes bypass Vault. After Vault is restored, you must re-sync the account.

```powershell
# Step 1: Reset password in AD directly
Set-ADAccountPassword -Identity svc_mssql_prod -Reset -NewPassword (ConvertTo-SecureString "NewSecureP@ss123!" -AsPlainText -Force)

# Step 2: Update service with new password
sc.exe config MSSQLSERVER password= "NewSecureP@ss123!"

# Step 3: Start service
Start-Service MSSQLSERVER

# Step 4: Document the change
# - Time of manual reset
# - New password (store securely for Vault re-sync)
# - Reason for break-glass

# Step 5: After Vault restored, force rotation to re-sync
vault write -f ad/rotate-role/mssql-prod-svc
```

### 5.2 Mass Rotation (Security Incident)

If credentials may be compromised, rotate all managed accounts:

```bash
# Step 1: List all AD roles
vault list ad/roles

# Step 2: Force rotation on all roles
for role in $(vault list -format=json ad/roles | jq -r '.[]'); do
    echo "Rotating: $role"
    vault write -f ad/rotate-role/$role
done

# Step 3: Trigger agent sync on all servers
# (Agents will pick up new passwords on next poll)

# Step 4: Verify services are running
# Platform-specific health checks

# Step 5: Review audit logs for unauthorized access
vault audit list
```

## 6. Maintenance Procedures

### 6.1 Adding a New Managed Account

```bash
# Step 1: Create role in Vault
vault write ad/roles/new-app-svc \
    service_account_name="svc_new_app" \
    ttl=24h

# Step 2: Update Vault policy to allow access
vault policy write new-app-policy - <<EOF
path "ad/creds/new-app-svc" {
  capabilities = ["read"]
}
EOF

# Step 3: Create AppRole for the server
vault write auth/approle/role/new-app-server \
    token_policies="new-app-policy" \
    token_ttl=1h

# Step 4: Deploy Vault Agent on target server
# (Follow implementation guide Phase 3)

# Step 5: Test rotation
vault write -f ad/rotate-role/new-app-svc
```

### 6.2 Removing a Managed Account

```bash
# Step 1: Delete the role (password stops rotating)
vault delete ad/roles/old-app-svc

# Step 2: Remove AppRole
vault delete auth/approle/role/old-app-server

# Step 3: Stop Vault Agent on target server
systemctl stop vault-agent
systemctl disable vault-agent

# Step 4: Reset password in AD to static value (if needed)
# Document and store securely
```

### 6.3 Secret ID Rotation (Monthly)

```bash
# Automated via GitHub Actions, but manual procedure:
vault write -f auth/approle/role/<role>/secret-id

# Distribute new secret_id to servers
# Update /etc/vault.d/secret_id
# Restart vault-agent
```

## 7. Escalation Matrix

| Issue | First Response | Escalation (15 min) | Escalation (1 hour) |
|-------|---------------|---------------------|---------------------|
| Rotation failure | On-call DBA | Vault Admin | Security Team |
| Account lockout | On-call DBA | AD Team | Security Team |
| Vault unavailable | Platform Team | Infrastructure Lead | CTO |
| Security incident | Security Team | CISO | Executive Team |

## 8. Contact Information

| Role | Contact | Availability |
|------|---------|--------------|
| Vault Admin | vault-team@example.com | 24/7 PagerDuty |
| DBA Team | dba-team@example.com | Business hours |
| AD Team | ad-team@example.com | Business hours |
| Security | security@example.com | 24/7 PagerDuty |
