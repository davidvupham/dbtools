# Vault Architecture Guide

**[← Back to Vault Documentation Index](./README.md)** — Navigation guide for all Vault docs

> **Document Version:** 1.0
> **Last Updated:** January 15, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Vault Version](https://img.shields.io/badge/Vault-1.15%2B-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

> [!IMPORTANT]
> **Related Docs:** [Concepts](./vault-concepts.md) | [Operations](../../how-to/vault/vault-operations-guide.md) | [Reference](../../reference/vault/vault-reference.md)

## Table of Contents

- [Server Architecture](#server-architecture)
  - [Core Components](#core-components)
  - [Data Flow](#data-flow)
  - [Storage Backends](#storage-backends)
- [High Availability](#high-availability)
  - [Integrated Storage (Raft)](#integrated-storage-raft)
  - [Active/Standby Architecture](#activestandby-architecture)
  - [Performance Replication](#performance-replication)
- [Security Architecture](#security-architecture)
  - [Encryption Layers](#encryption-layers)
  - [Seal Mechanisms](#seal-mechanisms)
  - [Network Security](#network-security)
- [Production Hardening](#production-hardening)
  - [Baseline Recommendations](#baseline-recommendations)
  - [Operating System Hardening](#operating-system-hardening)
  - [TLS Configuration](#tls-configuration)
  - [Memory Protection](#memory-protection)
- [Audit Logging](#audit-logging)
  - [Audit Devices](#audit-devices)
  - [Log Format](#log-format)
  - [Best Practices](#audit-best-practices)
- [Monitoring and Observability](#monitoring-and-observability)
  - [Health Endpoints](#health-endpoints)
  - [Telemetry](#telemetry)
  - [Alerting](#alerting)
- [Disaster Recovery](#disaster-recovery)
  - [Backup Strategies](#backup-strategies)
  - [Recovery Procedures](#recovery-procedures)
- [Our Deployment Standards](#our-deployment-standards)

## Server Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           VAULT SERVER                                  │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │    HTTP     │  │   Token     │  │   Policy    │  │   Audit     │    │
│  │   Server    │  │   Store     │  │   Engine    │  │  Devices    │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │           │
│         └────────────────┴────────────────┴────────────────┘           │
│                                   │                                     │
│                                   ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         BARRIER                                  │   │
│  │              (Encryption/Decryption Layer)                       │   │
│  │                    AES-256-GCM                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                     │
│                                   ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     STORAGE BACKEND                              │   │
│  │            (Integrated Storage / Consul / etc.)                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Components:**

| Component | Purpose |
|:---|:---|
| **HTTP Server** | Handles API requests (REST) |
| **Token Store** | Manages authentication tokens |
| **Policy Engine** | Evaluates access control policies |
| **Audit Devices** | Logs all requests and responses |
| **Barrier** | Encrypts all data before storage |
| **Storage Backend** | Persists encrypted data |

### Data Flow

When a client requests a secret:

```
Client                    Vault Server                    Storage
   │                           │                             │
   │ 1. Request Secret         │                             │
   ├──────────────────────────►│                             │
   │                           │                             │
   │                    2. Authenticate Token                │
   │                    3. Check Policies                    │
   │                    4. Write Audit Log                   │
   │                           │                             │
   │                           │ 5. Read Encrypted Data      │
   │                           ├────────────────────────────►│
   │                           │                             │
   │                           │◄────────────────────────────┤
   │                           │ 6. Encrypted Response       │
   │                           │                             │
   │                    7. Decrypt with Barrier Key          │
   │                           │                             │
   │ 8. Return Secret          │                             │
   │◄──────────────────────────┤                             │
   │                           │                             │
```

### Storage Backends

| Backend | HA Support | Use Case |
|:---|:---:|:---|
| **Integrated Storage (Raft)** | Yes | Recommended for most deployments |
| **Consul** | Yes | Existing Consul infrastructure |
| **PostgreSQL/MySQL** | No | Simple deployments |
| **S3/GCS** | No | Disaster recovery backups |
| **File** | No | Development only |

**Recommendation:** Use **Integrated Storage (Raft)** for new deployments. It provides high availability without external dependencies.

[↑ Back to Table of Contents](#table-of-contents)

## High Availability

### Integrated Storage (Raft)

Vault's Integrated Storage uses the Raft consensus protocol for HA:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        VAULT CLUSTER                                    │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   Node 1        │  │   Node 2        │  │   Node 3        │         │
│  │   (Leader)      │  │   (Follower)    │  │   (Follower)    │         │
│  │                 │  │                 │  │                 │         │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │         │
│  │  │   Raft    │◄─┼──┼─►│   Raft    │◄─┼──┼─►│   Raft    │  │         │
│  │  │  Storage  │  │  │  │  Storage  │  │  │  │  Storage  │  │         │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                         │
│         │                     │                     │                   │
│         └─────────────────────┴─────────────────────┘                   │
│                         Raft Consensus                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Points:**

- **Leader Election** - Automatic failover if leader fails
- **Data Replication** - All data replicated to followers
- **Quorum** - Requires majority of nodes (2 of 3, 3 of 5)
- **Ports** - 8200 (API), 8201 (Cluster)

### Active/Standby Architecture

| Node Type | Can Serve Requests | Write Capability |
|:---|:---:|:---:|
| **Active (Leader)** | Yes | Yes |
| **Standby (Follower)** | Forward to leader | No |
| **Performance Standby** | Yes (read-only) | No |

### Performance Replication

For geographically distributed deployments:

- **Primary Cluster** - Source of truth
- **Secondary Clusters** - Read replicas in other regions
- **Disaster Recovery** - Warm standby for failover

[↑ Back to Table of Contents](#table-of-contents)

## Security Architecture

### Encryption Layers

Vault uses multiple layers of encryption:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Layer 1: TLS (Transport)                                               │
│  - Encrypts client ↔ Vault communication                                │
│  - TLS 1.3 recommended                                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Layer 2: Barrier (Application)                                         │
│  - AES-256-GCM encryption                                               │
│  - Encrypts all data before storage                                     │
│  - Master key never written to disk                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Layer 3: Storage Backend                                               │
│  - May provide additional encryption                                    │
│  - Not relied upon for security                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Seal Mechanisms

**Shamir's Secret Sharing (Default):**

```
Master Key
    │
    ├──► Key Share 1 (Admin A)
    ├──► Key Share 2 (Admin B)
    ├──► Key Share 3 (Admin C)
    ├──► Key Share 4 (Admin D)
    └──► Key Share 5 (Admin E)

Unseal requires 3 of 5 shares (configurable threshold)
```

**Auto-Unseal (Production):**

| Provider | Service |
|:---|:---|
| **AWS** | KMS |
| **Azure** | Key Vault |
| **GCP** | Cloud KMS |
| **HSM** | PKCS#11 |

**Benefits of Auto-Unseal:**
- No manual intervention required after restart
- Master key protected by cloud KMS
- Supports automated deployments

### Network Security

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        NETWORK ARCHITECTURE                             │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    PRIVATE NETWORK                               │   │
│  │                                                                  │   │
│  │    ┌─────────────┐              ┌─────────────────────────┐     │   │
│  │    │ Load        │              │     VAULT CLUSTER       │     │   │
│  │    │ Balancer    │─────────────►│                         │     │   │
│  │    │ (TLS Term)  │   :8200      │  ┌─────┐ ┌─────┐ ┌─────┐│     │   │
│  │    └─────────────┘              │  │ N1  │ │ N2  │ │ N3  ││     │   │
│  │          ▲                      │  └─────┘ └─────┘ └─────┘│     │   │
│  │          │                      │         :8201           │     │   │
│  │          │                      │    (Cluster Traffic)    │     │   │
│  │    ┌─────┴─────┐                └─────────────────────────┘     │   │
│  │    │ Firewall  │                                                │   │
│  │    │ Rules     │                                                │   │
│  │    └───────────┘                                                │   │
│  │          ▲                                                      │   │
│  └──────────┼──────────────────────────────────────────────────────┘   │
│             │                                                           │
│  ┌──────────┴──────────────────────────────────────────────────────┐   │
│  │                     APPLICATIONS                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Firewall Rules:**

| Source | Destination | Port | Purpose |
|:---|:---|:---:|:---|
| Applications | Load Balancer | 443 | Client API |
| Load Balancer | Vault Nodes | 8200 | API forwarding |
| Vault Node | Vault Node | 8201 | Cluster traffic |
| Admin | Vault Nodes | 8200 | Management |

[↑ Back to Table of Contents](#table-of-contents)

## Production Hardening

### Baseline Recommendations

> [!WARNING]
> These recommendations are based on [HashiCorp's Production Hardening Guide](https://developer.hashicorp.com/vault/docs/concepts/production-hardening). All production deployments should follow these guidelines.

| Recommendation | Reason |
|:---|:---|
| **Don't run as root** | Minimize privilege escalation risk |
| **Minimal write permissions** | Prevent binary/config tampering |
| **End-to-end TLS** | Encrypt all traffic |
| **Single tenancy** | Reduce attack surface |
| **Disable swap** | Prevent secrets paging to disk |
| **Disable core dumps** | Prevent key extraction |

### Operating System Hardening

**Linux (Recommended):**

```bash
# Run as dedicated user
useradd --system --home /etc/vault.d --shell /bin/false vault

# Set file permissions
chown root:vault /etc/vault.d/vault.hcl
chmod 640 /etc/vault.d/vault.hcl

# Disable core dumps for vault user
echo "vault hard core 0" >> /etc/security/limits.conf

# Configure SELinux/AppArmor
# See HashiCorp's SELinux policy
```

**systemd Service:**

```ini
[Unit]
Description=HashiCorp Vault
Requires=network-online.target
After=network-online.target

[Service]
User=vault
Group=vault
ExecStart=/usr/bin/vault server -config=/etc/vault.d/vault.hcl
ExecReload=/bin/kill --signal HUP $MAINPID
KillMode=process
KillSignal=SIGINT
Restart=on-failure
RestartSec=5
LimitNOFILE=65536
LimitMEMLOCK=infinity

[Install]
WantedBy=multi-user.target
```

### TLS Configuration

> [!IMPORTANT]
> **Always use TLS in production.** Never disable TLS verification unless absolutely necessary for development.

**Server Configuration:**

```hcl
listener "tcp" {
  address         = "0.0.0.0:8200"
  tls_cert_file   = "/etc/vault.d/tls/vault.crt"
  tls_key_file    = "/etc/vault.d/tls/vault.key"
  tls_min_version = "tls13"

  # HSTS header
  custom_response_headers {
    "default" = {
      "Strict-Transport-Security" = ["max-age=31536000; includeSubDomains"]
    }
  }
}
```

**Recommended TLS Settings:**

| Setting | Value | Reason |
|:---|:---|:---|
| **Min Version** | TLS 1.3 | Modern encryption, forward secrecy |
| **Cipher Suites** | AES-256-GCM | Strong encryption |
| **Certificate** | Valid CA-signed | No self-signed in production |
| **HSTS** | Enabled | Prevent downgrade attacks |

### Memory Protection

**Disable Swap:**

```bash
# Temporarily
sudo swapoff -a

# Permanently (edit /etc/fstab)
# Comment out swap lines
```

**Memory Locking:**

```hcl
# vault.hcl
disable_mlock = false  # Keep memory locked
```

```ini
# systemd service
LimitMEMLOCK=infinity
```

[↑ Back to Table of Contents](#table-of-contents)

## Audit Logging

### Audit Devices

Vault supports multiple audit device types:

| Type | Output | Use Case |
|:---|:---|:---|
| **File** | Local file | Simple deployments |
| **Syslog** | Syslog daemon | Centralized logging |
| **Socket** | TCP/UDP socket | Log forwarding |

**Enable File Audit:**

```bash
vault audit enable file file_path=/var/log/vault/audit.log
```

**Enable Syslog Audit:**

```bash
vault audit enable syslog tag="vault" facility="LOCAL0"
```

> [!WARNING]
> **Enable at least two audit devices.** If Vault cannot write to any audit device, it will stop responding to requests. Multiple devices provide redundancy.

### Log Format

Audit logs are JSON formatted:

```json
{
  "time": "2026-01-15T10:30:45.123456Z",
  "type": "request",
  "auth": {
    "client_token": "hmac-sha256:abc123...",
    "accessor": "hmac-sha256:def456...",
    "display_name": "approle",
    "policies": ["default", "myapp-policy"],
    "token_policies": ["default", "myapp-policy"]
  },
  "request": {
    "id": "12345-abcde-67890",
    "operation": "read",
    "client_token": "hmac-sha256:abc123...",
    "path": "secret/data/myapp/database",
    "remote_address": "10.0.1.50"
  }
}
```

**Key Fields:**

| Field | Description |
|:---|:---|
| `time` | Request timestamp |
| `type` | request or response |
| `auth.display_name` | Auth method used |
| `auth.policies` | Policies on the token |
| `request.operation` | read, write, delete, list |
| `request.path` | Secret path accessed |
| `request.remote_address` | Client IP address |

### Audit Best Practices

1. **Enable multiple audit devices** - Redundancy prevents lockout
2. **Forward to SIEM** - Centralized analysis and alerting
3. **Monitor disk space** - Audit logs can grow quickly
4. **Rotate logs** - Use logrotate or similar
5. **Alert on sensitive operations** - Root token creation, policy changes

**Common Audit Queries:**

```bash
# Find all secret reads
jq 'select(.request.operation == "read")' /var/log/vault/audit.log

# Find permission denied errors
jq 'select(.error != null and .error | contains("permission denied"))' /var/log/vault/audit.log

# Find requests from specific IP
jq 'select(.request.remote_address == "10.0.1.50")' /var/log/vault/audit.log
```

[↑ Back to Table of Contents](#table-of-contents)

## Monitoring and Observability

### Health Endpoints

| Endpoint | Purpose | Auth Required |
|:---|:---|:---:|
| `/v1/sys/health` | Overall health status | No |
| `/v1/sys/seal-status` | Seal/unseal status | No |
| `/v1/sys/leader` | HA leader status | No |
| `/v1/sys/metrics` | Prometheus metrics | Yes |

**Health Check Response:**

```bash
curl https://vault.example.com:8200/v1/sys/health
```

```json
{
  "initialized": true,
  "sealed": false,
  "standby": false,
  "performance_standby": false,
  "replication_performance_mode": "disabled",
  "replication_dr_mode": "disabled",
  "server_time_utc": 1705312245,
  "version": "1.15.0",
  "cluster_name": "vault-cluster",
  "cluster_id": "abc123-def456"
}
```

### Telemetry

**Enable Prometheus Metrics:**

```hcl
# vault.hcl
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
}
```

**Key Metrics:**

| Metric | Description |
|:---|:---|
| `vault.core.handle_request` | Request processing time |
| `vault.token.lookup` | Token lookup operations |
| `vault.audit.log_request` | Audit log write time |
| `vault.expire.num_leases` | Active lease count |
| `vault.runtime.alloc_bytes` | Memory allocation |

### Alerting

**Critical Alerts:**

| Condition | Alert |
|:---|:---|
| `sealed == true` | Vault is sealed |
| Health endpoint unreachable | Vault is down |
| `expire.num_leases` > threshold | Lease explosion |
| Disk space < 10% | Audit log disk full |
| Memory > 90% | Memory pressure |

**Warning Alerts:**

| Condition | Alert |
|:---|:---|
| `standby == true` (on expected leader) | Unexpected leadership change |
| Request latency > 500ms | Performance degradation |
| Token renewal failures | Authentication issues |

[↑ Back to Table of Contents](#table-of-contents)

## Disaster Recovery

### Backup Strategies

**Integrated Storage Snapshots:**

```bash
# Create snapshot
vault operator raft snapshot save backup.snap

# Restore snapshot
vault operator raft snapshot restore backup.snap
```

**Backup Schedule:**

| Frequency | Retention | Purpose |
|:---|:---|:---|
| Hourly | 24 hours | Quick recovery |
| Daily | 7 days | Short-term DR |
| Weekly | 4 weeks | Medium-term DR |
| Monthly | 12 months | Compliance |

### Recovery Procedures

**Scenario: Single Node Failure**

1. Cluster continues operating (if quorum maintained)
2. Replace failed node
3. Join new node to cluster
4. Data replicates automatically

**Scenario: Complete Cluster Loss**

1. Deploy new Vault cluster
2. Initialize with same unseal keys or auto-unseal config
3. Restore from snapshot
4. Verify all secrets accessible
5. Update DNS/load balancer

**Recovery Time Objectives:**

| Scenario | RTO Target |
|:---|:---|
| Single node failure | 0 (automatic failover) |
| Cluster loss with snapshot | < 30 minutes |
| Cluster loss, no snapshot | > 1 hour (recreate secrets) |

[↑ Back to Table of Contents](#table-of-contents)

## Our Deployment Standards

### Environment Configuration

| Environment | Nodes | Auto-Unseal | Audit Logging |
|:---|:---:|:---:|:---:|
| Development | 1 | No (manual) | Optional |
| Staging | 3 | Yes (KMS) | Required |
| Production | 5 | Yes (KMS) | Required |

### Naming Conventions

| Resource | Convention | Example |
|:---|:---|:---|
| Secret paths | `secret/data/{team}/{app}/{secret}` | `secret/data/platform/myapp/database` |
| AppRole names | `{team}-{app}-{env}` | `platform-myapp-prod` |
| Policies | `{team}-{app}-{access}` | `platform-myapp-readonly` |

### Access Control

| Role | Capabilities |
|:---|:---|
| **Application** | Read own secrets only |
| **Developer** | Read non-prod secrets |
| **Operations** | Read all, write non-prod |
| **Admin** | Full access |

### Integration with gds_vault

Our `gds_vault` Python package is the standard client library:

```python
from gds_vault import VaultClient

# Production configuration
client = VaultClient(
    vault_addr="https://vault.example.com:8200",
    verify_ssl=True,
    ssl_cert_path="/etc/ssl/certs/ca-certificates.crt"
)

# Use rotation-aware caching
from gds_vault.cache import RotationAwareCache
client = VaultClient(cache=RotationAwareCache(buffer_minutes=10))
```

See [Vault Operations Guide](../../how-to/vault/vault-operations-guide.md) for detailed usage.

[↑ Back to Table of Contents](#table-of-contents)

## Related Documentation

- **[Vault Concepts Guide](./vault-concepts.md)** - Core concepts and fundamentals
- **[Vault Operations Guide](../../how-to/vault/vault-operations-guide.md)** - Using Vault in applications
- **[Vault Reference](../../reference/vault/vault-reference.md)** - API reference and troubleshooting

## Sources and Further Reading

### Official HashiCorp Documentation

- [Production Hardening](https://developer.hashicorp.com/vault/docs/concepts/production-hardening) - Official hardening guide
- [Harden Server Deployments Tutorial](https://developer.hashicorp.com/vault/tutorials/archive/production-hardening) - Step-by-step hardening
- [Audit Devices](https://developer.hashicorp.com/vault/docs/audit) - Audit logging documentation
- [Audit Logging Best Practices](https://developer.hashicorp.com/vault/docs/audit/best-practices) - Audit configuration guidance
- [Troubleshoot Vault](https://developer.hashicorp.com/vault/tutorials/monitoring/troubleshooting-vault) - Troubleshooting guide
- [Query Audit Device Logs](https://developer.hashicorp.com/vault/tutorials/monitoring/query-audit-device-logs) - Audit log analysis

### Security Resources

- [Hardening HashiCorp Vault with SELinux](https://www.hashicorp.com/en/blog/hardening-hashicorp-vault-with-selinux) - SELinux configuration
- [Vault Security Hardening - KodeKloud](https://notes.kodekloud.com/docs/HashiCorp-Certified-Vault-Operations-Professional-2022/Create-a-working-Vault-server-configuration-given-a-scenario/Vault-Security-Hardening) - Security checklist
- [Complete Guide to Security Hardening HashiCorp Vault](https://lgcybersec.co.uk/complete-guide-to-security-hardening-hashicorp-vault-essential-best-practices-for-smbs/) - SMB hardening guide

### Monitoring and Operations

- [Monitor HashiCorp Vault metrics and logs - Datadog](https://www.datadoghq.com/blog/monitor-vault-metrics-and-logs/) - Monitoring integration
- [Audit and Operational Log Details](https://support.hashicorp.com/hc/en-us/articles/360000995548-Audit-and-Operational-Log-Details) - Log level guidance
- [Vault Deployment Guide](https://gist.github.com/gblok/118ff4765c8c38d7055b5d128e5a7ca5) - Community deployment guide
