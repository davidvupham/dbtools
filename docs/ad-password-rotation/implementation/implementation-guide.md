# Implementation Guide: AD Password Rotation

This guide provides step-by-step instructions for implementing the AD Password Rotation system.

## Prerequisites

Before starting, ensure you have:

- [ ] HashiCorp Vault 1.7+ installed and unsealed
- [ ] Active Directory domain controller accessible via LDAPS (port 636)
- [ ] AD service account for Vault with "Reset Password" delegation
- [ ] Network connectivity from Vault to AD, and from DB servers to Vault

## Phase 1: Vault Configuration

### Step 1.1: Enable AD Secrets Engine

```bash
# Enable the AD secrets engine at the default path
vault secrets enable ad
```

### Step 1.2: Configure AD Connection

```bash
# Configure the AD backend
vault write ad/config \
    binddn="CN=svc_vault,OU=ServiceAccounts,DC=example,DC=com" \
    bindpass="$VAULT_BIND_PASSWORD" \
    url="ldaps://dc01.example.com" \
    userdn="OU=ServiceAccounts,DC=example,DC=com" \
    insecure_tls=false
```

> [!NOTE]
> Store `bindpass` in a secure location. Consider using Vault's own secrets for this initial bootstrap.

### Step 1.3: Create Roles

Create a role for each service account you want to manage:

```bash
# MSSQL Service Account
vault write ad/roles/mssql-prod-svc \
    service_account_name="svc_mssql_prod" \
    ttl=24h

# PostgreSQL Service Account
vault write ad/roles/postgres-prod-svc \
    service_account_name="svc_postgres_prod" \
    ttl=24h
```

### Step 1.4: Create Access Policies

```bash
# Create policy file
cat <<EOF > ad-rotation-policy.hcl
# Read credentials for MSSQL
path "ad/creds/mssql-prod-svc" {
  capabilities = ["read"]
}

# Read credentials for PostgreSQL
path "ad/creds/postgres-prod-svc" {
  capabilities = ["read"]
}

# Rotate credentials (operators only)
path "ad/rotate-role/*" {
  capabilities = ["update"]
}
EOF

# Apply policy
vault policy write ad-rotation ad-rotation-policy.hcl
```

## Phase 2: AppRole Authentication

### Step 2.1: Enable AppRole

```bash
vault auth enable approle
```

### Step 2.2: Create AppRole for Each Server

```bash
# Create AppRole for MSSQL server
vault write auth/approle/role/mssql-server-prod \
    token_policies="ad-rotation" \
    token_ttl=1h \
    token_max_ttl=4h \
    secret_id_ttl=720h \
    secret_id_num_uses=0
```

### Step 2.3: Retrieve Role ID and Secret ID

```bash
# Get Role ID (static, can be baked into image)
vault read auth/approle/role/mssql-server-prod/role-id

# Generate Secret ID (rotate periodically)
vault write -f auth/approle/role/mssql-server-prod/secret-id
```

## Phase 3: Vault Agent Deployment

### Step 3.1: Install Vault Agent

**Linux:**

```bash
# Download and install
curl -fsSL https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip -o vault.zip
unzip vault.zip
sudo mv vault /usr/local/bin/
```

**Windows:**

```powershell
# Download via Chocolatey
choco install vault
```

### Step 3.2: Create Agent Configuration

Create `/etc/vault.d/agent.hcl`:

```hcl
pid_file = "/var/run/vault-agent.pid"

vault {
  address = "https://vault.example.com:8200"
}

auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path   = "/etc/vault.d/role_id"
      secret_id_file_path = "/etc/vault.d/secret_id"
      remove_secret_id_file_after_reading = false
    }
  }

  sink "file" {
    config = {
      path = "/etc/vault.d/token"
      mode = 0600
    }
  }
}

template {
  source      = "/etc/vault.d/templates/mssql_creds.ctmpl"
  destination = "/etc/mssql/creds.json"
  perms       = 0600
  command     = "/opt/scripts/rotate-mssql.sh"
}
```

### Step 3.3: Create Credential Template

Create `/etc/vault.d/templates/mssql_creds.ctmpl`:

```hcl
{{ with secret "ad/creds/mssql-prod-svc" }}
{
  "username": "{{ .Data.username }}",
  "password": "{{ .Data.current_password }}"
}
{{ end }}
```

### Step 3.4: Create Rotation Script

**Linux (PostgreSQL):**

```bash
#!/bin/bash
# /opt/scripts/rotate-postgres.sh

# Regenerate keytab with new password
NEW_PASS=$(jq -r '.password' /etc/postgres/creds.json)
PRINCIPAL="postgres_svc@EXAMPLE.COM"

# Create new keytab
printf "%b" "addent -password -p $PRINCIPAL -k 1 -e aes256-cts-hmac-sha1-96\n$NEW_PASS\nwrite_kt /etc/postgres/postgres.keytab.new\nquit" | ktutil

# Atomic swap
mv /etc/postgres/postgres.keytab.new /etc/postgres/postgres.keytab
chown postgres:postgres /etc/postgres/postgres.keytab
chmod 600 /etc/postgres/postgres.keytab

# Reload PostgreSQL
systemctl reload postgresql

echo "$(date): Password rotated successfully" >> /var/log/vault-rotation.log
```

**Windows (MSSQL):**

```powershell
# C:\Ops\Rotate-MSSQL.ps1

$CredsFile = "C:\ProgramData\Vault\creds.json"
$Creds = Get-Content $CredsFile | ConvertFrom-Json

$ServiceName = "MSSQLSERVER"
$Username = $Creds.username
$Password = $Creds.password

# Update service credentials
$secPass = ConvertTo-SecureString $Password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($Username, $secPass)

sc.exe config $ServiceName obj= $Username password= $Password

# Restart service
Restart-Service $ServiceName -Force

Add-Content -Path "C:\Ops\rotation.log" -Value "$(Get-Date): Password rotated for $ServiceName"
```

### Step 3.5: Start Vault Agent

**Linux (systemd):**

```bash
sudo systemctl enable vault-agent
sudo systemctl start vault-agent
```

**Windows (Service):**

```powershell
# Register as Windows Service
New-Service -Name "VaultAgent" `
    -BinaryPathName "C:\HashiCorp\Vault\vault.exe agent -config=C:\HashiCorp\Vault\agent.hcl" `
    -StartupType Automatic

Start-Service VaultAgent
```

## Phase 4: Verification

### Step 4.1: Test Credential Retrieval

```bash
# Manually test credential retrieval
vault read ad/creds/mssql-prod-svc
```

### Step 4.2: Force Rotation

```bash
# Manually trigger rotation
vault write -f ad/rotate-role/mssql-prod-svc
```

### Step 4.3: Verify Service Authentication

```bash
# Check if the service can authenticate with new credentials
# (Database-specific verification)
sqlcmd -S localhost -E -Q "SELECT SYSTEM_USER"
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "LDAP connection failed" | Network/TLS issue | Verify LDAPS port 636, check CA cert |
| "Access denied" | Insufficient AD permissions | Verify "Reset Password" delegation |
| "Template rendering failed" | Invalid secret path | Check `vault read ad/creds/<role>` manually |
| "Service restart failed" | Permission issue | Run script as Administrator/root |

## Next Steps

After completing this implementation:

1. Configure monitoring/alerting for rotation failures
2. Set up regular Secret ID rotation (every 30 days)
3. Document break-glass procedures for emergency access
4. Train operations team on troubleshooting steps
