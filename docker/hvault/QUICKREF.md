# HashiCorp Vault Docker - Quick Reference

## Common Commands

### Start Vault

```bash
# Development mode (insecure, for testing only)
docker-compose -f docker-compose.dev.yml up -d

# Production mode
docker-compose up -d
```

### Stop Vault

```bash
docker-compose down
# or for dev
docker-compose -f docker-compose.dev.yml down
```

### View Logs

```bash
docker logs vault1
docker logs vault1 --follow
docker logs vault2
```

### Check Status

```bash
# Container status
docker ps --filter name=vault

# Vault status
export VAULT_ADDR=http://localhost:8200
vault status
```

### Initialize Vault (First Time)

```bash
export VAULT_ADDR=http://localhost:8200
./scripts/init-vault.sh

# Or manually
vault operator init -key-shares=5 -key-threshold=3
```

### Unseal Vault

```bash
export VAULT_ADDR=http://localhost:8200
./scripts/unseal-vault.sh

# Or manually
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>
```

### Access Vault

```bash
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=<your-token>
vault status
```

## Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Production configuration |
| `docker-compose.dev.yml` | Development mode |
| `config/vault.hcl` | Vault server configuration |
| `.env.example` | Environment variables template |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init-vault.sh` | Initialize new Vault |
| `scripts/unseal-vault.sh` | Unseal sealed Vault |
| `scripts/validate-config.sh` | Validate configuration |

## Policies

| Policy | Access Level |
|--------|-------------|
| `policies/admin-policy.hcl` | Full administrative access |
| `policies/app-policy.hcl` | Application read/write access |
| `policies/readonly-policy.hcl` | Read-only access |

### Apply a Policy

```bash
vault policy write admin policies/admin-policy.hcl
vault policy write app policies/app-policy.hcl
vault policy write readonly policies/readonly-policy.hcl
```

## Common Operations

### Enable Secret Engine

```bash
# KV v2 (versioned secrets)
vault secrets enable -path=kv kv-v2

# Database
vault secrets enable database

# Transit (encryption)
vault secrets enable transit
```

### Write/Read Secrets

```bash
# Write
vault kv put secret/myapp/config username=admin password=secret

# Read
vault kv get secret/myapp/config

# List
vault kv list secret/myapp
```

### Create User

```bash
# Enable userpass
vault auth enable userpass

# Create user
vault write auth/userpass/users/alice \
  password=changeme \
  policies=app

# Login
vault login -method=userpass username=alice
```

### Create Token

```bash
# Create token with policy
vault token create -policy=app -ttl=24h

# Create periodic token for services
vault token create -policy=app -period=24h
```

### Enable Audit Logging

```bash
vault audit enable file file_path=/vault/logs/audit/audit.log

# View logs
docker exec vault1 cat /vault/logs/audit/audit.log | jq
```

## Directory Structure

```
/data/vault/
  ├── vault1/           # Vault 1 data
  └── vault2/           # Vault 2 data

/logs/vault/
  ├── vault1/
  │   ├── audit/        # Audit logs
  │   └── *.log         # Operational logs
  └── vault2/
      ├── audit/
      └── *.log
```

## Ports

| Service | API Port | Cluster Port |
|---------|----------|--------------|
| vault1 | 8200 | 8201 |
| vault2 | 8210 | 8211 |

## Health Check

```bash
# HTTP endpoint
curl http://localhost:8200/v1/sys/health

# CLI
vault status

# Seal status
curl http://localhost:8200/v1/sys/seal-status
```

## Troubleshooting

### Vault is Sealed

```bash
vault operator unseal <key>
# Repeat with threshold number of keys
```

### Permission Denied

```bash
# Check token
vault token lookup

# Check policy
vault policy read <policy-name>

# Check capabilities
vault token capabilities <path>
```

### Container Won't Start

```bash
# Check logs
docker logs vault1

# Check config
docker-compose config

# Validate
./scripts/validate-config.sh
```

### Memory Lock Error

```bash
# Verify IPC_LOCK capability
docker inspect vault1 | jq '.[0].HostConfig.CapAdd'
```

## Backup and Restore

### Backup

```bash
# Stop Vault
docker-compose down

# Backup data
sudo tar -czf vault-backup-$(date +%Y%m%d).tar.gz \
  /data/vault/vault1

# Restart
docker-compose up -d
```

### Restore

```bash
# Stop Vault
docker-compose down

# Restore
sudo tar -xzf vault-backup-YYYYMMDD.tar.gz -C /

# Start and unseal
docker-compose up -d
./scripts/unseal-vault.sh
```

## Environment Variables

```bash
# Required for CLI
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=<your-token>

# Optional
export VAULT_SKIP_VERIFY=true  # Skip TLS verification (dev only)
export VAULT_LOG_LEVEL=debug   # Logging level
```

## Security Reminders

- [ ] Never use dev mode in production
- [ ] Enable TLS for production
- [ ] Distribute unseal keys separately
- [ ] Revoke root token after setup
- [ ] Enable audit logging
- [ ] Use short TTLs for tokens
- [ ] Regularly rotate secrets
- [ ] Keep Vault updated

## Documentation

- [OPERATIONS.md](OPERATIONS.md) - Detailed operations guide
- [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) - Security checklist
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Implementation details
- [README.md](README.md) - Full tutorial

## Support Resources

- [Official Docs](https://developer.hashicorp.com/vault/docs)
- [Tutorials](https://developer.hashicorp.com/vault/tutorials)
- [API Reference](https://developer.hashicorp.com/vault/api-docs)
- [Community Forum](https://discuss.hashicorp.com/c/vault)
