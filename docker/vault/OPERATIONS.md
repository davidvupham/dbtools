# HashiCorp Vault Operations Guide

## Quick Start

### Development Mode (Testing Only)

```bash
# Start Vault in development mode
cd /workspaces/dbtools/docker/vault
docker-compose -f docker-compose.dev.yml up -d

# Access Vault
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=root

# Verify
vault status
```

### Production Mode

```bash
# 1. Create required directories
sudo mkdir -p /data/vault/vault{1,2}
sudo mkdir -p /logs/vault/vault{1,2}/audit

# 2. Set proper permissions
sudo chown -R 100:1000 /data/vault
sudo chown -R 100:1000 /logs/vault

# 3. Start Vault servers
cd /workspaces/dbtools/docker/vault
docker-compose up -d

# 4. Initialize Vault (first time only)
export VAULT_ADDR=http://localhost:8200
./scripts/init-vault.sh

# 5. Securely store the unseal keys and root token from /tmp/vault-init-keys.json
# CRITICAL: Distribute keys to separate secure locations

# 6. Unseal Vault (after restarts)
./scripts/unseal-vault.sh
```

## Key Operations

### Initialize Vault

```bash
# Manual initialization
vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -format=json > vault-init-keys.json

# Save this file securely and distribute keys
```

### Unseal Vault

```bash
# After restart, Vault starts sealed
vault operator unseal <unseal-key-1>
vault operator unseal <unseal-key-2>
vault operator unseal <unseal-key-3>

# Or use the script
./scripts/unseal-vault.sh
```

### Enable Audit Logging

```bash
# File audit device (recommended)
vault audit enable file file_path=/vault/logs/audit/audit.log

# View audit logs
docker exec vault1 cat /vault/logs/audit/audit.log | jq
```

### Manage Policies

```bash
# Write a policy
vault policy write admin policies/admin-policy.hcl
vault policy write readonly policies/readonly-policy.hcl
vault policy write app policies/app-policy.hcl

# List policies
vault policy list

# Read a policy
vault policy read admin
```

### Authentication Methods

```bash
# Enable userpass authentication
vault auth enable userpass

# Create a user
vault write auth/userpass/users/alice \
  password=changeme \
  policies=admin

# Login as user
vault login -method=userpass username=alice
```

### Secret Engines

```bash
# Enable KV v2 secret engine
vault secrets enable -path=kv kv-v2

# Write a secret
vault kv put kv/app/config \
  username=admin \
  password=secret123

# Read a secret
vault kv get kv/app/config

# List secrets
vault kv list kv/app
```

### Token Management

```bash
# Create a token with policy
vault token create -policy=app -ttl=24h

# Lookup token info
vault token lookup

# Renew token
vault token renew

# Revoke token
vault token revoke <token>
```

## High Availability Setup

### Using Raft Integrated Storage

1. Update `config/vault.hcl` to use Raft storage:

```hcl
storage "raft" {
  path    = "/vault/file"
  node_id = "vault1"

  retry_join {
    leader_api_addr = "http://vault2:8200"
  }
}
```

2. Initialize the first node:

```bash
docker-compose up -d vault1
export VAULT_ADDR=http://localhost:8200
vault operator init
```

3. Join additional nodes:

```bash
docker exec vault2 vault operator raft join http://vault1:8200
```

## Security Best Practices

### 1. Enable TLS

Create certificates and update `vault.hcl`:

```hcl
listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_disable   = 0
  tls_cert_file = "/vault/certs/vault.crt"
  tls_key_file  = "/vault/certs/vault.key"
  tls_min_version = "tls13"
}
```

### 2. Use Auto-Unseal

Configure cloud KMS (AWS, Azure, GCP) for automatic unsealing:

```hcl
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "your-kms-key-id"
}
```

### 3. Root Token Management

```bash
# Revoke root token after initial setup
vault token revoke <root-token>

# Generate new root token when needed
vault operator generate-root -init
vault operator generate-root -cancel  # If needed
```

### 4. Regular Token Rotation

```bash
# Use short-lived tokens
vault token create -policy=app -ttl=1h

# Enable periodic tokens for services
vault token create -policy=app -period=24h
```

### 5. Monitor Audit Logs

```bash
# View recent audit events
docker exec vault1 tail -f /vault/logs/audit/audit.log | jq

# Search for specific operations
docker exec vault1 cat /vault/logs/audit/audit.log | \
  jq 'select(.request.operation == "create")'
```

## Monitoring and Health Checks

### Health Check

```bash
# Basic health check
vault status

# Detailed health with HTTP
curl http://localhost:8200/v1/sys/health

# Sealed status
curl http://localhost:8200/v1/sys/seal-status
```

### Metrics

```bash
# Prometheus metrics endpoint
curl http://localhost:8200/v1/sys/metrics?format=prometheus

# View telemetry
vault read sys/metrics
```

### Container Health

```bash
# Check container health
docker ps --filter name=vault
docker inspect vault1 | jq '.[0].State.Health'

# View logs
docker logs vault1
docker logs vault1 --follow
```

## Backup and Recovery

### Backup Vault Data

```bash
# Backup storage data
sudo tar -czf vault-backup-$(date +%Y%m%d).tar.gz /data/vault/vault1

# Backup using Raft snapshots (if using Raft storage)
vault operator raft snapshot save backup.snap
```

### Restore from Backup

```bash
# Stop Vault
docker-compose down

# Restore data
sudo tar -xzf vault-backup-YYYYMMDD.tar.gz -C /

# Restart Vault
docker-compose up -d

# Unseal
./scripts/unseal-vault.sh
```

### Using Raft Snapshots

```bash
# Save snapshot
vault operator raft snapshot save backup.snap

# Restore snapshot
vault operator raft snapshot restore backup.snap
```

## Troubleshooting

### Vault Won't Start

```bash
# Check logs
docker logs vault1

# Verify configuration
docker exec vault1 vault operator diagnose

# Check file permissions
ls -la /data/vault/vault1
ls -la /logs/vault/vault1
```

### Vault is Sealed

```bash
# Check seal status
vault status

# Unseal with keys
vault operator unseal <key-1>
vault operator unseal <key-2>
vault operator unseal <key-3>
```

### Permission Denied Errors

```bash
# Check token capabilities
vault token capabilities <path>

# Review policy
vault policy read <policy-name>

# Check token info
vault token lookup
```

### Memory Lock Errors

```bash
# Verify IPC_LOCK capability
docker inspect vault1 | jq '.[0].HostConfig.CapAdd'

# If needed, disable mlock (not recommended for production)
# Set disable_mlock = true in vault.hcl
```

## Migration and Upgrade

### Upgrade Vault Version

```bash
# 1. Backup data
./scripts/backup-vault.sh

# 2. Update docker-compose.yml with new version
# Change: image: hashicorp/vault:1.15.0

# 3. Pull new image
docker-compose pull

# 4. Stop and start (not restart to ensure new image)
docker-compose down
docker-compose up -d

# 5. Unseal
./scripts/unseal-vault.sh

# 6. Verify version
vault version
```

### Migrate to Raft Storage

See HashiCorp's official migration guide:
<https://developer.hashicorp.com/vault/tutorials/raft/raft-migration>

## Additional Resources

- [Official Documentation](https://developer.hashicorp.com/vault/docs)
- [Production Hardening](https://developer.hashicorp.com/vault/docs/concepts/production-hardening)
- [Security Model](https://developer.hashicorp.com/vault/docs/internals/security)
- [Vault API](https://developer.hashicorp.com/vault/api-docs)
- [Best Practices](https://developer.hashicorp.com/vault/tutorials/operations)
