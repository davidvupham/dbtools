# High availability

**[← Back to Track C: Operations](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-4_Applied-blue)
![Lesson](https://img.shields.io/badge/Lesson-16-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Explain Vault's high availability architecture and Raft consensus
- Deploy a multi-node Vault cluster with integrated storage
- Configure auto-unseal with cloud KMS providers
- Implement disaster recovery strategies for Vault clusters

## Table of contents

- [High availability concepts](#high-availability-concepts)
- [Raft integrated storage](#raft-integrated-storage)
- [Deploying an HA cluster](#deploying-an-ha-cluster)
- [Auto-unseal configuration](#auto-unseal-configuration)
- [Disaster recovery](#disaster-recovery)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## High availability concepts

Vault high availability ensures continuous access to secrets even when individual nodes fail.

### HA architecture overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Vault HA Cluster Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                          ┌─────────────────┐                                │
│                          │  Load Balancer  │                                │
│                          │  (TCP/HTTPS)    │                                │
│                          └────────┬────────┘                                │
│                                   │                                          │
│              ┌────────────────────┼────────────────────┐                    │
│              │                    │                    │                    │
│              ▼                    ▼                    ▼                    │
│     ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│     │    Vault 1      │  │    Vault 2      │  │    Vault 3      │          │
│     │    (Active)     │  │   (Standby)     │  │   (Standby)     │          │
│     │                 │  │                 │  │                 │          │
│     │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │          │
│     │ │ Raft Data   │◀┼──┼▶│ Raft Data   │◀┼──┼▶│ Raft Data   │ │          │
│     │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │          │
│     └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                              │
│     Legend:                                                                 │
│     ◀──▶ Raft consensus replication                                        │
│     Active: Handles all requests                                            │
│     Standby: Ready to become active on leader failure                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key concepts

| Concept | Description |
|---------|-------------|
| **Active Node** | Handles all client requests; only one per cluster |
| **Standby Node** | Replicates data; ready to become active |
| **Raft Consensus** | Distributed consensus protocol for data replication |
| **Quorum** | Minimum nodes required for cluster operation (n/2 + 1) |
| **Leader Election** | Automatic process when active node fails |
| **Seal Status** | All nodes must be unsealed for cluster operation |

### Cluster sizing recommendations

| Cluster Size | Fault Tolerance | Use Case |
|-------------|-----------------|----------|
| 3 nodes | 1 node failure | Development, small production |
| 5 nodes | 2 node failures | Standard production |
| 7 nodes | 3 node failures | Large enterprise, critical workloads |

**Best practice:** Use odd numbers to avoid split-brain scenarios.

[↑ Back to Table of Contents](#table-of-contents)

---

## Raft integrated storage

Raft integrated storage is the recommended storage backend, eliminating external dependencies.

### How Raft works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Raft Consensus Flow                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. Client Write        2. Leader Replicates      3. Commit & Respond      │
│   ┌───────────┐          ┌───────────────────┐     ┌───────────────────┐   │
│   │  Client   │          │     Leader        │     │     Leader        │   │
│   │  Request  │ ───────▶ │  sends to peers   │ ──▶ │  confirms write   │   │
│   └───────────┘          └───────────────────┘     └───────────────────┘   │
│                                   │                         │               │
│                          ┌───────┴───────┐                 │               │
│                          ▼               ▼                 ▼               │
│                    ┌──────────┐    ┌──────────┐     ┌──────────┐          │
│                    │ Follower │    │ Follower │     │  Client  │          │
│                    │  writes  │    │  writes  │     │  success │          │
│                    └──────────┘    └──────────┘     └──────────┘          │
│                                                                              │
│   Quorum Required: For 3 nodes, 2 must acknowledge before commit            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Configuration example

```hcl
# vault.hcl - Raft integrated storage configuration
storage "raft" {
  path    = "/opt/vault/data"
  node_id = "vault-1"

  retry_join {
    leader_api_addr = "https://vault-2.example.com:8200"
  }

  retry_join {
    leader_api_addr = "https://vault-3.example.com:8200"
  }
}

listener "tcp" {
  address         = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_cert_file   = "/opt/vault/tls/vault.crt"
  tls_key_file    = "/opt/vault/tls/vault.key"
}

api_addr     = "https://vault-1.example.com:8200"
cluster_addr = "https://vault-1.example.com:8201"

ui = true
```

### Raft operations

```bash
# Check cluster status
vault operator raft list-peers

# Output:
# Node       Address                    State     Voter
# ----       -------                    -----     -----
# vault-1    vault-1.example.com:8201   leader    true
# vault-2    vault-2.example.com:8201   follower  true
# vault-3    vault-3.example.com:8201   follower  true

# Remove a failed node
vault operator raft remove-peer vault-3

# Take a snapshot
vault operator raft snapshot save backup.snap

# Restore from snapshot
vault operator raft snapshot restore backup.snap
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Deploying an HA cluster

Step-by-step guide to deploying a 3-node Vault cluster.

### Node configuration files

**vault-1.hcl:**
```hcl
storage "raft" {
  path    = "/opt/vault/data"
  node_id = "vault-1"

  retry_join {
    leader_api_addr = "https://vault-2:8200"
  }
  retry_join {
    leader_api_addr = "https://vault-3:8200"
  }
}

listener "tcp" {
  address         = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_disable     = true  # Enable TLS in production!
}

api_addr     = "http://vault-1:8200"
cluster_addr = "http://vault-1:8201"
cluster_name = "vault-cluster"
ui           = true
disable_mlock = true
```

**vault-2.hcl and vault-3.hcl:** Same structure, update `node_id` and addresses.

### Initialization process

```bash
# Initialize the first node (only once for the entire cluster)
vault operator init -key-shares=5 -key-threshold=3

# Output:
# Unseal Key 1: xxx
# Unseal Key 2: xxx
# Unseal Key 3: xxx
# Unseal Key 4: xxx
# Unseal Key 5: xxx
# Initial Root Token: hvs.xxx
#
# IMPORTANT: Store these keys securely!

# Unseal the first node
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>

# The other nodes will automatically join via retry_join
# Unseal each node with the same keys
```

### Verifying cluster health

```bash
# Check leader status
vault status

# List Raft peers
vault operator raft list-peers

# Check HA status
vault read sys/leader

# Sample output:
# Key             Value
# ---             -----
# ha_enabled      true
# is_self         true
# leader_address  https://vault-1:8200
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Auto-unseal configuration

Auto-unseal eliminates manual unsealing using cloud KMS services.

### Supported providers

| Provider | Seal Type | Use Case |
|----------|-----------|----------|
| AWS KMS | `awskms` | AWS deployments |
| Azure Key Vault | `azurekeyvault` | Azure deployments |
| GCP Cloud KMS | `gcpckms` | GCP deployments |
| HashiCorp Cloud | `hcp` | Multi-cloud |
| Transit (another Vault) | `transit` | Air-gapped environments |
| HSM (PKCS#11) | `pkcs11` | Hardware security modules |

### AWS KMS configuration

```hcl
# vault.hcl with AWS KMS auto-unseal
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "arn:aws:kms:us-east-1:123456789:key/12345678-1234-1234-1234-123456789abc"

  # Optional: Use specific credentials
  # access_key = "AKIAXXXXXXXX"
  # secret_key = "xxxxxxxxxx"
  # Or use IAM roles (recommended)
}

storage "raft" {
  path    = "/opt/vault/data"
  node_id = "vault-1"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = false
  tls_cert_file = "/opt/vault/tls/vault.crt"
  tls_key_file  = "/opt/vault/tls/vault.key"
}
```

**Required IAM permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:DescribeKey"
      ],
      "Resource": "arn:aws:kms:us-east-1:123456789:key/*"
    }
  ]
}
```

### Azure Key Vault configuration

```hcl
seal "azurekeyvault" {
  tenant_id     = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  client_id     = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  client_secret = "xxxxxxxxxx"
  vault_name    = "vault-unseal-keys"
  key_name      = "vault-key"
}
```

### GCP Cloud KMS configuration

```hcl
seal "gcpckms" {
  project     = "my-project"
  region      = "us-central1"
  key_ring    = "vault-keyring"
  crypto_key  = "vault-key"

  # Credentials via GOOGLE_APPLICATION_CREDENTIALS env var
  # or service account attached to GCE instance
}
```

### Migration from Shamir to auto-unseal

```bash
# 1. Update configuration to include seal stanza
# 2. Restart Vault - it will detect migration needed
# 3. Run migration
vault operator unseal -migrate

# Provide Shamir keys when prompted
# After migration, auto-unseal is active
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Disaster recovery

Strategies for protecting against data loss and enabling recovery.

### Backup strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Backup Strategy Comparison                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Method              RPO          RTO          Complexity                  │
│   ──────              ───          ───          ──────────                  │
│   Raft Snapshots      Minutes      Minutes      Low                         │
│   Raft Auto-Pilot     Real-time    Seconds      Medium (Enterprise)         │
│   DR Replication      Seconds      Minutes      High (Enterprise)           │
│   Cross-Region        Seconds      Minutes      High (Enterprise)           │
│                                                                              │
│   RPO = Recovery Point Objective (data loss tolerance)                      │
│   RTO = Recovery Time Objective (downtime tolerance)                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Raft snapshot backup

```bash
# Manual snapshot
vault operator raft snapshot save /backup/vault-$(date +%Y%m%d-%H%M%S).snap

# Verify snapshot
vault operator raft snapshot inspect /backup/vault-*.snap

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backup/vault"
RETENTION_DAYS=7

# Create backup
vault operator raft snapshot save "${BACKUP_DIR}/vault-$(date +%Y%m%d-%H%M%S).snap"

# Clean old backups
find "${BACKUP_DIR}" -name "*.snap" -mtime +${RETENTION_DAYS} -delete

# Upload to S3 (optional)
aws s3 sync "${BACKUP_DIR}" s3://my-vault-backups/
```

### Snapshot restore procedure

```bash
# 1. Stop all Vault nodes except one
systemctl stop vault  # on nodes 2 and 3

# 2. Restore snapshot on node 1
vault operator raft snapshot restore /backup/vault-latest.snap

# 3. Verify data integrity
vault secrets list
vault kv list secret/

# 4. Restart other nodes
systemctl start vault  # on nodes 2 and 3

# 5. Verify cluster health
vault operator raft list-peers
```

### DR replication (Enterprise)

```hcl
# Primary cluster configuration
replication {
  resolver_discover_servers = true
}

# Enable DR replication on primary
vault write -f sys/replication/dr/primary/enable

# Get secondary activation token
vault write sys/replication/dr/primary/secondary-token id=dr-secondary

# On secondary cluster
vault write sys/replication/dr/secondary/enable token=<activation-token>
```

### Recovery from total loss

```bash
# If all nodes lost but have snapshot:

# 1. Deploy new Vault node with same configuration
# 2. Initialize (creates new unseal keys)
vault operator init

# 3. Unseal
vault operator unseal

# 4. Restore snapshot
vault operator raft snapshot restore backup.snap

# 5. Data is restored, but note:
#    - Unseal keys are NEW (from step 2)
#    - Root token is NEW
#    - All other data (secrets, policies, auth) restored from snapshot
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Prerequisites

- Docker and Docker Compose installed
- The course Docker files from `docs/courses/vault/docker/`

### Setup

Navigate to the course Docker directory:

```bash
cd /path/to/docs/courses/vault/docker
```

### Exercise 1: Deploy a 3-node HA cluster

1. Start the HA cluster:

   ```bash
   docker-compose -f docker-compose.ha.yml up -d
   ```

2. Check container status:

   ```bash
   docker-compose -f docker-compose.ha.yml ps
   ```

3. Initialize the first node:

   ```bash
   # Connect to vault-1
   docker exec -it vault-1 sh

   # Inside container
   export VAULT_ADDR='http://127.0.0.1:8200'

   # Initialize
   vault operator init -key-shares=3 -key-threshold=2

   # Save the output! You'll need the unseal keys and root token
   ```

4. Unseal vault-1:

   ```bash
   # Still in vault-1 container
   vault operator unseal <key1>
   vault operator unseal <key2>

   vault status
   # Should show: Sealed = false
   ```

**Observation:** Vault-1 is now initialized and unsealed.

### Exercise 2: Join additional nodes

1. Unseal vault-2:

   ```bash
   # In new terminal
   docker exec -it vault-2 sh

   export VAULT_ADDR='http://127.0.0.1:8200'

   # Unseal with same keys
   vault operator unseal <key1>
   vault operator unseal <key2>
   ```

2. Unseal vault-3:

   ```bash
   docker exec -it vault-3 sh

   export VAULT_ADDR='http://127.0.0.1:8200'

   vault operator unseal <key1>
   vault operator unseal <key2>
   ```

3. Verify cluster status from vault-1:

   ```bash
   docker exec -it vault-1 sh

   export VAULT_ADDR='http://127.0.0.1:8200'
   export VAULT_TOKEN='<root-token>'

   vault operator raft list-peers
   ```

**Observation:** All three nodes should appear in the peer list.

### Exercise 3: Test failover

1. Create test data:

   ```bash
   # On vault-1
   vault secrets enable -path=secret kv-v2
   vault kv put secret/test message="HA cluster working"
   ```

2. Identify the leader:

   ```bash
   vault operator raft list-peers
   # Note which node is "leader"
   ```

3. Stop the leader:

   ```bash
   # Exit container, then stop leader
   docker stop vault-1  # if vault-1 was leader
   ```

4. Verify automatic failover:

   ```bash
   # Connect to another node
   docker exec -it vault-2 sh

   export VAULT_ADDR='http://127.0.0.1:8200'
   export VAULT_TOKEN='<root-token>'

   # Check new leader
   vault operator raft list-peers

   # Verify data is accessible
   vault kv get secret/test
   ```

**Observation:** A new leader was automatically elected and data remains accessible.

### Exercise 4: Backup and restore

1. Create a snapshot:

   ```bash
   # On the current leader
   vault operator raft snapshot save /tmp/backup.snap

   # Copy out of container
   docker cp vault-2:/tmp/backup.snap ./backup.snap
   ```

2. Add more data:

   ```bash
   vault kv put secret/important data="will be lost"
   ```

3. Restore from snapshot:

   ```bash
   # Copy snapshot back
   docker cp ./backup.snap vault-2:/tmp/backup.snap

   # Restore
   vault operator raft snapshot restore /tmp/backup.snap

   # Verify - the "important" secret should be gone
   vault kv get secret/important  # Should fail
   vault kv get secret/test       # Should work
   ```

**Observation:** Restore reverts to snapshot state; data added after snapshot is lost.

### Cleanup

```bash
docker-compose -f docker-compose.ha.yml down -v
rm -f backup.snap
```

---

## Key takeaways

1. **Odd node counts** - Use 3, 5, or 7 nodes to ensure clear quorum decisions
2. **Raft is recommended** - Integrated storage simplifies operations and removes external dependencies
3. **Unseal all nodes** - Every node must be unsealed for the cluster to function
4. **Auto-unseal for production** - Eliminates manual intervention after restarts
5. **Regular snapshots** - Automate Raft snapshots for disaster recovery
6. **Test failover** - Regularly validate that failover works as expected
7. **Secure unseal keys** - Use separate storage/custody for Shamir keys or protect KMS access

---

[← Back to Track C: Operations](./README.md) | [Next: Monitoring and Metrics →](./17-monitoring-metrics.md)
