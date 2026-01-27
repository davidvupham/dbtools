# HashiCorp Vault Docker Configuration - Refactoring Summary

## Overview

Refactored the HashiCorp Vault Docker setup based on [HashiCorp's Production Hardening Guidelines](https://developer.hashicorp.com/vault/docs/concepts/production-hardening) and container security best practices.

## Changes Made

### 1. Docker Compose Configuration (`docker-compose.yml`)

**Security Enhancements:**

- Added `cap_drop: ALL` to drop all unnecessary capabilities
- Restricted capabilities to only `IPC_LOCK` (required for memory locking)
- Added `security_opt: no-new-privileges` to prevent privilege escalation
- Configured comprehensive `ulimits`:
  - `nofile: 65536` - adequate file descriptors
  - `memlock: -1` - unlimited memory lock (required for Vault)
  - `core: 0` - disable core dumps (security risk)

**Operational Improvements:**

- Added hostname for better cluster identification
- Separated audit logs to dedicated volume (`/vault/logs/audit`)
- Added environment variables for configuration flexibility:
  - `VAULT_LOG_LEVEL` and `VAULT_LOG_FORMAT`
  - `VAULT_SKIP_VERIFY`
  - `VAULT_TELEMETRY_ENABLED`
- Implemented Docker healthcheck with proper timing:
  - Checks Vault status every 30s
  - 30s start period for initialization
  - 3 retries before marking unhealthy
- Added extensive documentation comments

**Structure:**

- Two-node configuration (vault1, vault2) for HA testing
- Separate port mappings (8200/8201 and 8210/8211)
- Read-only configuration mounts
- Prepared for TLS certificate mounting (commented)

### 2. Vault Configuration (`config/vault.hcl`)

**Enhanced Configuration:**

- Comprehensive comments explaining each section
- Production TLS configuration (commented, ready to enable)
- Prepared for Raft Integrated Storage (HA setup)
- Added telemetry configuration for Prometheus
- Configured log format and level
- Added lease TTL recommendations
- Documented auto-unseal options for AWS, Azure, and GCP

**Key Settings:**

- `disable_mlock = false` - critical security feature
- `ui = true` - web interface enabled
- Structured JSON logging
- Prometheus metrics endpoint enabled

### 3. New Files Created

#### Operational Scripts

- **`scripts/init-vault.sh`** - Automated initialization script
  - Creates key shares with configurable threshold
  - Automatically enables audit logging
  - Unseals Vault after initialization
  - Provides security reminders
  - Outputs structured JSON

- **`scripts/unseal-vault.sh`** - Automated unseal script
  - Reads keys from JSON file
  - Checks seal status
  - Applies threshold number of keys
  - Error handling and validation

#### Policy Templates

- **`policies/admin-policy.hcl`** - Administrative access
  - Full auth method management
  - Secret engine management
  - Policy management
  - Seal/unseal operations
  - Token and lease management

- **`policies/readonly-policy.hcl`** - Read-only access
  - Read secrets from KV engines
  - View configuration
  - Token self-management

- **`policies/app-policy.hcl`** - Application access
  - Read/write to application secrets
  - Database credential reading
  - Transit encryption operations
  - Token self-management

#### Configuration Files

- **`.env.example`** - Environment variable template
  - Vault configuration options
  - TLS settings
  - Development mode warnings

- **`docker-compose.dev.yml`** - Development mode setup
  - Minimal configuration for testing
  - In-memory storage
  - Pre-configured root token
  - Clear warnings about security

#### Documentation

- **`OPERATIONS.md`** - Comprehensive operations guide
  - Quick start for dev and production
  - Key operations (init, unseal, backup)
  - HA setup instructions
  - Security best practices
  - Monitoring and troubleshooting
  - Migration and upgrade procedures

- **`SECURITY_CHECKLIST.md`** - Security assessment checklist
  - Pre-deployment checklist
  - Configuration security items
  - Container security verification
  - Operational security procedures
  - Monitoring requirements
  - Compliance considerations
  - Implementation status tracking

- **Updated `README.md`** - Enhanced main documentation
  - Added quick links to operational docs
  - Directory structure overview
  - Quick start guides
  - Security features summary
  - Production requirements callout

## Security Improvements

### Implemented

✅ Memory protection (mlock enabled, IPC_LOCK capability)
✅ Minimal container capabilities
✅ Privilege escalation prevention
✅ Core dump prevention
✅ Proper file descriptor limits
✅ Audit logging support
✅ Structured logging
✅ Healthcheck monitoring
✅ Telemetry for metrics
✅ Non-root user execution
✅ Read-only configuration mounts
✅ Separate volumes for data/logs/audit

### Prepared for Production

⚠️ TLS configuration (ready to enable)
⚠️ Auto-unseal setup (AWS/Azure/GCP KMS)
⚠️ Raft storage for HA (configuration included)
⚠️ Certificate mounting (volume mounts commented)

### Recommended Next Steps

❌ Generate and configure TLS certificates
❌ Set up cloud KMS for auto-unseal
❌ Configure external monitoring (Prometheus/Grafana)
❌ Implement log forwarding to SIEM
❌ Set up automated backups
❌ Configure production storage backend (Raft)

## Best Practices Applied

### From HashiCorp Documentation

1. **Memory Protection**
   - mlock enabled to prevent swapping
   - IPC_LOCK capability granted
   - Core dumps disabled

2. **Minimal Privileges**
   - Running as vault user (non-root)
   - Dropped all unnecessary capabilities
   - No privilege escalation allowed

3. **Audit Logging**
   - Separate volume for audit logs
   - Initialization script enables audit device
   - Structured JSON format

4. **Operational Security**
   - Short default lease TTLs (7 days)
   - Maximum lease TTL configured (30 days)
   - Root token management guidance
   - Unseal key distribution strategy

5. **Monitoring**
   - Docker healthcheck implemented
   - Prometheus metrics enabled
   - Structured JSON logging
   - Telemetry configuration

6. **Configuration Management**
   - Configuration as code
   - Version-controlled policies
   - Environment variable support
   - Commented production settings

### Container Best Practices

1. **Security**
   - Capability dropping (ALL)
   - Minimal capability addition (IPC_LOCK only)
   - Security options (no-new-privileges)
   - Read-only mounts for config

2. **Resource Management**
   - File descriptor limits
   - Memory lock limits
   - Core dump limits
   - Restart policy configured

3. **Observability**
   - Healthcheck with appropriate timing
   - Structured logging
   - Metrics exposure
   - Volume separation for logs

## File Structure Comparison

### Before

```
vault/
├── config/
│   └── vault.hcl
├── data/
├── Dockerfile
└── README.md
```

### After

```
vault/
├── config/
│   └── vault.hcl              # Enhanced with production config
├── policies/                   # NEW
│   ├── admin-policy.hcl
│   ├── app-policy.hcl
│   └── readonly-policy.hcl
├── scripts/                    # NEW
│   ├── init-vault.sh
│   └── unseal-vault.sh
├── data/
├── .env.example               # NEW
├── docker-compose.yml         # Enhanced security
├── docker-compose.dev.yml     # NEW
├── Dockerfile
├── OPERATIONS.md              # NEW
├── SECURITY_CHECKLIST.md      # NEW
└── README.md                  # Updated
```

## Usage Examples

### Development

```bash
docker-compose -f docker-compose.dev.yml up -d
export VAULT_ADDR=http://localhost:8200 VAULT_TOKEN=root
vault status
```

### Production Setup

```bash
# Create directories
sudo mkdir -p /data/vault/vault{1,2} /logs/vault/vault{1,2}/audit

# Start Vault
docker-compose up -d

# Initialize
export VAULT_ADDR=http://localhost:8200
./scripts/init-vault.sh

# Access
export VAULT_TOKEN=<token-from-init>
vault status
```

### Enable TLS (Production)

1. Generate certificates
2. Update `vault.hcl`:

   ```hcl
   listener "tcp" {
     tls_disable = 0
     tls_cert_file = "/vault/certs/vault.crt"
     tls_key_file = "/vault/certs/vault.key"
   }
   ```

3. Uncomment certificate volume mounts in `docker-compose.yml`
4. Restart Vault

## Testing Performed

- ✅ Docker Compose syntax validation
- ✅ Dockerfile build verification
- ✅ Script syntax checking
- ✅ HCL configuration validation
- ✅ Policy syntax verification
- ✅ Documentation markdown linting

## References

- [HashiCorp Vault Production Hardening](https://developer.hashicorp.com/vault/docs/concepts/production-hardening)
- [Vault Security Model](https://developer.hashicorp.com/vault/docs/internals/security)
- [Vault on Kubernetes Security](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-security-concerns)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Linux Capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)

## Maintenance

To keep this configuration secure and up-to-date:

1. Subscribe to [HashiCorp Security Bulletins](https://discuss.hashicorp.com/c/vault/vault-announcements/)
2. Review [Vault CHANGELOG](https://github.com/hashicorp/vault/blob/main/CHANGELOG.md) before upgrades
3. Regularly update base image: `docker pull hashicorp/vault:latest`
4. Review and update policies as requirements change
5. Test upgrades in non-production environment first
6. Follow [OPERATIONS.md](OPERATIONS.md) for operational procedures
7. Use [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) for audits
