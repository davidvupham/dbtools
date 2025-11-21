# HashiCorp Vault Docker Setup - Security Checklist

This checklist follows HashiCorp's [Production Hardening Guide](https://developer.hashicorp.com/vault/docs/concepts/production-hardening).

## Pre-Deployment

- [ ] Review and understand the [Vault Security Model](https://developer.hashicorp.com/vault/docs/internals/security)
- [ ] Plan key distribution strategy for unseal keys
- [ ] Prepare TLS certificates for production deployment
- [ ] Configure backup and disaster recovery procedures
- [ ] Set up monitoring and alerting infrastructure

## Configuration Security

### Storage

- [ ] Use appropriate storage backend (Raft for HA, not file)
- [ ] Restrict storage access to Vault process only
- [ ] Enable encryption at rest on storage volume
- [ ] Configure regular backups

### Network Security

- [ ] Enable TLS (set `tls_disable = 0` in vault.hcl)
- [ ] Use TLS 1.3 minimum version
- [ ] Configure firewall rules (allow only necessary ports)
- [ ] Use network segmentation
- [ ] Configure load balancer health checks properly

### Listener Configuration

- [x] Disable HTTP in production (enable TLS)
- [ ] Configure custom HTTP response headers (HSTS)
- [ ] Set appropriate timeout values
- [ ] Configure TLS cipher suites

### Memory Protection

- [x] Keep `disable_mlock = false` to prevent memory swapping
- [x] Grant `IPC_LOCK` capability to container
- [x] Set `ulimits` for memlock (-1)
- [x] Set core dump limits to 0

## Container Security

### Capabilities

- [x] Use `CAP_DROP: ALL` to drop unnecessary capabilities
- [x] Add only `IPC_LOCK` capability
- [x] Enable `no-new-privileges` security option

### Resource Limits

- [x] Set file descriptor limits (`nofile: 65536`)
- [x] Set memory lock limits (`memlock: -1`)
- [x] Disable core dumps (`core: 0`)
- [ ] Set memory limits appropriate for workload
- [ ] Set CPU limits if needed

### User and Permissions

- [x] Run as non-root user (vault user in base image)
- [ ] Set read-only root filesystem if possible
- [ ] Mount configuration files as read-only
- [ ] Restrict write access to data and log directories only

## Operational Security

### Initialization and Unsealing

- [ ] Use sufficient key shares (recommended: 5)
- [ ] Use appropriate key threshold (recommended: 3)
- [ ] Distribute unseal keys to separate operators
- [ ] Store keys in separate secure locations (HSM, KMS, etc.)
- [ ] Never store all keys together
- [ ] Consider using auto-unseal (AWS KMS, Azure Key Vault, GCP KMS)

### Root Token Management

- [ ] Use root token only for initial setup
- [ ] Revoke root token after configuration
- [ ] Generate new root token only when necessary
- [ ] Immediately revoke root token after emergency use
- [ ] Never hardcode root token in configuration

### Audit Logging

- [ ] Enable audit device immediately after initialization
- [ ] Store audit logs on separate volume
- [ ] Restrict access to audit logs
- [ ] Set up log rotation
- [ ] Forward logs to SIEM or central logging
- [ ] Monitor audit logs for suspicious activity

### Authentication and Authorization

- [ ] Disable default authentication methods not in use
- [ ] Enable appropriate auth methods for your environment
- [ ] Configure user lockout settings
- [ ] Use principle of least privilege for policies
- [ ] Regular review of policies and permissions
- [ ] Use namespaces for multi-tenancy (Enterprise)

### Tokens and Leases

- [ ] Use short TTLs for tokens (hours, not days)
- [ ] Use periodic tokens for long-running services
- [ ] Configure appropriate default and max lease TTLs
- [ ] Implement token renewal in applications
- [ ] Regular token cleanup and revocation

## Monitoring and Maintenance

### Health Checks

- [x] Configure Docker healthcheck
- [ ] Set up external monitoring (Prometheus, etc.)
- [ ] Monitor seal status
- [ ] Alert on seal events
- [ ] Monitor storage capacity

### Telemetry

- [x] Enable telemetry collection
- [ ] Configure Prometheus metrics export
- [ ] Set up dashboards (Grafana, etc.)
- [ ] Monitor key metrics:
  - [ ] Request rate and latency
  - [ ] Token usage
  - [ ] Storage capacity
  - [ ] Memory usage
  - [ ] Seal/unseal events

### Logging

- [x] Use structured logging (JSON format)
- [x] Set appropriate log level (info in production)
- [ ] Forward operational logs to central logging
- [ ] Set up log retention policies
- [ ] Monitor logs for errors and warnings

### Backup and Recovery

- [ ] Implement regular backup schedule
- [ ] Test backup restoration procedures
- [ ] Store backups securely and separately
- [ ] Document recovery procedures
- [ ] Test disaster recovery plan

## Maintenance

### Updates and Patching

- [ ] Subscribe to HashiCorp security announcements
- [ ] Keep Vault version up to date
- [ ] Test upgrades in non-production first
- [ ] Review CHANGELOG before upgrading
- [ ] Follow immutable upgrade pattern (new containers)

### Key Rotation

- [ ] Rotate encryption keys regularly
- [ ] Document key rotation procedures
- [ ] Test key rotation process
- [ ] Plan for rekey operations

### Access Management

- [ ] Implement off-boarding procedures
- [ ] Regular access reviews
- [ ] Revoke unused tokens and leases
- [ ] Remove stale auth method mounts
- [ ] Clean up old policies

## Compliance and Documentation

### Documentation

- [ ] Document Vault architecture
- [ ] Maintain runbooks for common operations
- [ ] Document disaster recovery procedures
- [ ] Keep inventory of policies and roles
- [ ] Document key custodians and responsibilities

### Compliance

- [ ] Review compliance requirements (SOC2, PCI-DSS, etc.)
- [ ] Configure audit logging per requirements
- [ ] Implement access controls per policy
- [ ] Regular security assessments
- [ ] Penetration testing

## Production-Specific

### Before Going Live

- [ ] Complete security assessment
- [ ] Penetration testing completed
- [ ] Disaster recovery plan tested
- [ ] Monitoring and alerting operational
- [ ] Team trained on operations
- [ ] Runbooks documented and reviewed
- [ ] On-call procedures established

### Launch

- [ ] TLS enabled and verified
- [ ] Auto-unseal configured (if applicable)
- [ ] Audit logging enabled
- [ ] Monitoring active
- [ ] Backups configured
- [ ] Access controls verified
- [ ] Initial secrets migrated
- [ ] Applications integrated and tested

### Post-Launch

- [ ] Monitor performance and capacity
- [ ] Regular security reviews
- [ ] Update documentation as needed
- [ ] Train additional team members
- [ ] Plan for scaling

## Status

Current implementation status:

✅ **Completed:**

- Docker security hardening (capabilities, ulimits, security options)
- Memory protection configuration
- Healthcheck implementation
- Logging configuration
- Telemetry setup
- Development mode configuration
- Policy templates
- Initialization scripts

⚠️ **Needs Configuration:**

- TLS certificates and configuration
- Auto-unseal setup (cloud KMS)
- Production storage backend (Raft)
- External monitoring integration

❌ **Production Requirements:**

- Enable TLS
- Configure auto-unseal
- Set up external monitoring
- Configure log forwarding
- Implement backup automation
