# HashiCorp Vault Tutorial: Beginner to Advanced

**Production-Ready Docker Configuration**

This directory contains a production-hardened HashiCorp Vault setup following [HashiCorp's Production Hardening Guidelines](https://developer.hashicorp.com/vault/docs/concepts/production-hardening).

## Quick Links

- [Operations Guide](OPERATIONS.md) - Complete operations documentation
- [Security Checklist](SECURITY_CHECKLIST.md) - Security hardening checklist
- [Tutorial](#tutorial) - Comprehensive Vault tutorial (below)

## Docker Setup

### Files and Structure

```
hvault/
├── config/
│   └── vault.hcl              # Production Vault configuration
├── policies/
│   ├── admin-policy.hcl       # Administrative access policy
│   ├── app-policy.hcl         # Application access policy
│   └── readonly-policy.hcl    # Read-only access policy
├── scripts/
│   ├── init-vault.sh          # Initialize new Vault
│   └── unseal-vault.sh        # Unseal sealed Vault
├── docker-compose.yml         # Production configuration
├── docker-compose.dev.yml     # Development mode (testing only)
├── Dockerfile                 # Vault container image
├── .env.example               # Environment variables template
├── OPERATIONS.md              # Operations guide
├── SECURITY_CHECKLIST.md      # Security checklist
└── README.md                  # This file
```

### Quick Start

#### Development Mode (Testing Only)

```bash
# Start Vault in dev mode
docker-compose -f docker-compose.dev.yml up -d

# Access Vault
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=root
vault status
```

⚠️ **WARNING:** Dev mode is insecure and stores data in memory only. Never use in production.

#### Production Mode

```bash
# 1. Create required directories
sudo mkdir -p /data/vault/vault{1,2}
sudo mkdir -p /logs/vault/vault{1,2}/audit
sudo chown -R 100:1000 /data/vault /logs/vault

# 2. Start Vault
docker-compose up -d

# 3. Initialize (first time only)
export VAULT_ADDR=http://localhost:8200
./scripts/init-vault.sh

# 4. Store unseal keys securely (from /tmp/vault-init-keys.json)

# 5. Access Vault (use root token from initialization)
export VAULT_TOKEN=<root-token>
vault status
```

See [OPERATIONS.md](OPERATIONS.md) for complete operational procedures.

### Security Features Implemented

✅ **Container Security:**

- Non-root user (vault)
- Minimal capabilities (IPC_LOCK only)
- No new privileges
- Core dumps disabled
- Proper ulimits configured

✅ **Memory Protection:**

- Memory locking enabled (prevents swapping)
- Secure memory limits

✅ **Monitoring:**

- Docker healthcheck
- Prometheus metrics
- Structured JSON logging

✅ **Operational Security:**

- Audit logging support
- Separate volumes for data/logs
- Read-only configuration mounts

⚠️ **Production Requirements:**

- Enable TLS (currently disabled for development)
- Configure auto-unseal
- Use Raft storage for HA
- Set up external monitoring

See [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) for complete security configuration.

---

## Tutorial

HashiCorp Vault is a tool for securely storing, accessing, and managing sensitive information such as API keys, database credentials, certificates, and encryption keys. This tutorial guides you from first principles to advanced operational scenarios. Each section builds on the previous one; complete it in sequence if you are new to Vault, or jump to the topics you need.

---

## Table of Contents

1. [What Vault Solves](#what-vault-solves)
2. [Core Concepts](#core-concepts)
3. [Install Vault](#install-vault)
4. [Your First Dev Server](#your-first-dev-server)
5. [CLI and HTTP API Basics](#cli-and-http-api-basics)
6. [Secret Engines](#secret-engines)
7. [Authentication Methods](#authentication-methods)
8. [Tokens and Policies](#tokens-and-policies)
9. [Dynamic Secrets](#dynamic-secrets)
10. [Encryption as a Service (Transit)](#encryption-as-a-service-transit)
11. [PKI and Certificate Management](#pki-and-certificate-management)
12. [Advanced Operations](#advanced-operations)
13. [Integrations and Automation](#integrations-and-automation)
14. [Security Best Practices](#security-best-practices)
15. [Troubleshooting and Observability](#troubleshooting-and-observability)
16. [Next Steps and Further Learning](#next-steps-and-further-learning)

---

## What Vault Solves

Modern applications rely on secrets. Hardcoding them or managing them manually is risky. Vault provides:

- A central location to store and version secrets with audit trails.
- Controlled access through authentication and policy enforcement.
- Dynamic secrets that are created on demand and revoked automatically.
- Encryption services to protect data without exposing keys.
- Integration hooks for clouds, databases, Kubernetes, and CI/CD pipelines.

Vault can secure secrets at rest, control who can read or generate secrets, and closely monitor usage.

---

## Core Concepts

Before running Vault, understand these fundamentals:

- **Server**: The Vault daemon (`vault server`) is stateless and relies on a storage backend.
- **Storage Backend**: Where Vault stores encrypted data (Consul, Raft integrated storage, cloud services, etc.).
- **Sealing**: Vault starts sealed. Operators must unseal it with key shards.
- **Authentication Methods (Auth Methods)**: Plugins that verify the identity of clients (tokens, userpass, GitHub, LDAP, Kubernetes, cloud IAM).
- **Secret Engines**: Plugins that store, generate, or encrypt data (KV, database, AWS, PKI, transit).
- **Policies**: Rules that grant or deny capabilities (`read`, `create`, `update`, `delete`, `list`, `sudo`) on specific paths.
- **Tokens**: Credentials issued by Vault after authentication. Tokens carry policies and limits.
- **Namespaces** (Enterprise): Hierarchical Vaults for multi-tenancy.

Terminology:

- **Path**: Secrets and configuration live under logical paths, e.g. `secret/data/app/config`.
- **Lease**: Represents time-bound access to a secret; dynamic secrets often have leases.
- **Seal/Unseal**: Vault encrypts its data; unseal keys reconstruct the master key that decrypts the data (Shamir secret sharing).

---

## Install Vault

### Prerequisites

- Linux, macOS, or Windows environment
- Administrative privileges
- Optional: Docker for container-based setups

### Using Package Manager (Linux)

```shell
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vault
vault -version
```

### Using Homebrew (macOS/Linux)

```shell
brew tap hashicorp/tap
brew install hashicorp/tap/vault
vault -version
```

### Using Chocolatey (Windows PowerShell)

```shell
choco install vault
vault -version
```

### Using Docker

```shell
docker pull hashicorp/vault:latest
docker run --cap-add=IPC_LOCK -e 'VAULT_DEV_ROOT_TOKEN_ID=root' hashicorp/vault server -dev
```

---

## Your First Dev Server

The `-dev` mode is great for experimentation; never use it in production. Create a dev server:

```shell
vault server -dev -dev-root-token-id=root
```

Output includes:

- A root token (`root`) with all privileges.
- The dev server listens on `http://127.0.0.1:8200`.
- Dev mode stores data in-memory only.

Export the environment variables so the CLI knows where to connect:

```shell
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=root
```

Verify status:

```shell
vault status
```

The status should show `Initialized`, `Sealed: false`, `HA Enabled: false`.

---

## CLI and HTTP API Basics

Vault exposes both a CLI and REST API. Most CLI commands wrap API calls.

### Write and Read a Key/Value Secret

```shell
vault kv put secret/app/config username="web_user" password="s3cr3t"
vault kv get secret/app/config
```

This uses the KV (key-value) secret engine under the mount path `secret/`. In KV version 2, secrets store metadata and versions.

### List Secrets

```shell
vault kv list secret/app
```

### Use curl with the API

```shell
curl --header "X-Vault-Token: $VAULT_TOKEN" \
     $VAULT_ADDR/v1/secret/data/app/config
```

The API returns JSON with `data` and `metadata`.

---

## Secret Engines

Secret engines are mounted under paths. Enable, configure, and use them based on your needs.

### Key/Value (KV) Secret Engine

The KV engine is enabled by default at `secret/`. You can enable additional mounts:

```shell
vault secrets enable -path=kv kv-v2
vault kv put kv/api key=value
```

KV version 1 lacks versioning; v2 adds check-and-set, metadata, and version history.

### Cubbyhole

- Available to every token at `cubbyhole/`.
- Accessible only by the token that wrote the data.

### Identity Secrets Engine

- Stores entities (users, services) and groups.
- Aggregates multiple auth methods into a single identity.

### Database Secret Engine

Allows Vault to dynamically generate short-lived DB credentials.

```shell
vault secrets enable database
vault write database/config/my-postgres \
    plugin_name=postgresql-database-plugin \
    connection_url="postgresql://{{username}}:{{password}}@db.example.com:5432/postgres?sslmode=disable" \
    allowed_roles="readonly" \
    username="vault" \
    password="vaultpassword"

vault write database/roles/readonly \
    db_name=my-postgres \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"
```

Later, clients obtain credentials:

```shell
vault read database/creds/readonly
```

### AWS Secret Engine

- Dynamically creates IAM credentials.
- Requires AWS IAM permissions for the Vault role.

### Transit Secret Engine

- Provides encryption-as-a-service (covered later).

### PKI Secret Engine

- Issues X.509 certificates with custom lifetimes.

---

## Authentication Methods

Clients authenticate using various methods, receiving tokens bound to policies.

### Token Auth (Built-in)

The root token is special; create limited tokens:

```shell
vault token create -policy=dev-team -ttl=24h
```

### Userpass

```shell
vault auth enable userpass
vault write auth/userpass/users/alice password="changeme" policies="dev-team"
```

Users authenticate:

```shell
VAULT_TOKEN=$(vault login -format=json -method=userpass username=alice password=changeme | jq -r ".auth.client_token")
```

### AppRole

- Useful for machine-to-machine access.
- Provides RoleID and SecretID to applications.

```shell
vault auth enable approle
vault write auth/approle/role/my-app \
    secret_id_ttl=60m \
    token_ttl=60m \
    token_max_ttl=24h \
    policies="app-policy"

ROLE_ID=$(vault read -field=role_id auth/approle/role/my-app/role-id)
SECRET_ID=$(vault write -field=secret_id auth/approle/role/my-app/secret-id)
vault write auth/approle/login role_id="$ROLE_ID" secret_id="$SECRET_ID"
```

### Cloud IAM Auth

- AWS, Azure, GCP auth methods validate cloud instance identities.
- Kubernetes auth uses service account tokens.

Example (Kubernetes):

1. Enable method:

   ```shell
   vault auth enable kubernetes
   ```

2. Configure the Kubernetes host, CA cert, and token reviewer JWT.

3. Map service accounts to policies.

---

## Tokens and Policies

### Token Types

- **Service tokens**: Default; renewable.
- **Batch tokens**: Lightweight, not persisted; cannot be renewed.
- **Orphan tokens**: No parent; unaffected by parent revocation.
- **Periodic tokens**: Must renew before TTL expires.

### Policies in HCL

```hcl
path "secret/data/app/*" {
  capabilities = ["read", "list"]
}

path "transit/encrypt/orders" {
  capabilities = ["update"]
}
```

Load policy:

```shell
vault policy write dev-team dev-team.hcl
```

Attach policy to tokens or auth roles.

### Sentinel (Enterprise)

- Policy-as-code with logic conditions.
- Useful for advanced compliance.

---

## Dynamic Secrets

Dynamic secrets are generated on demand and revoked automatically, reducing exposure.

### Database Example Recap

1. Enable database engine.
2. Configure connection.
3. Define roles (SQL statements).
4. Clients request credentials as needed.

### Secrets Lifecycle

- **Creation**: Vault generates credentials with TTL.
- **Lease**: Returned with `lease_id` and `lease_duration`.
- **Renewal**: `vault lease renew`.
- **Revocation**: `vault lease revoke`.

### Common Engines Supporting Dynamic Secrets

- `database/`
- `aws/`
- `gcp/`
- `azure/`
- `pki/` (certificates)
- `rabbitmq/`, `mongodb/`, custom plugins

### Advanced Tips

- Use short TTLs to limit exposure.
- Subscribe to audit logs to track secret issuance.
- Combine with response wrapping (see below) to pass secrets securely.

---

## Encryption as a Service (Transit)

The Transit engine performs cryptographic operations without exposing keys.

### Enable and Create a Key

```shell
vault secrets enable transit
vault write -f transit/keys/orders
```

### Encrypt Data

```shell
vault write transit/encrypt/orders plaintext=$(base64 <<<"order-12345")
```

Vault returns ciphertext like `vault:v1:...`.

### Decrypt Data

```shell
vault write transit/decrypt/orders ciphertext="vault:v1:..."
```

### Additional Capabilities

- **Key rotation**: `vault write -f transit/keys/orders/rotate`.
- **Data key generation**: `vault write transit/datakey/plaintext/orders`.
- **Signing and verification**: `vault write transit/sign/orders input=$(base64 <<<"payload")`.
- **Imported keys**: Provide your own master keys.

### Use Cases

- Encrypt application data before writing to databases.
- Sign JSON Web Tokens or API responses.
- Generate data keys for client-side encryption.

---

## PKI and Certificate Management

Vault can act as a CA to issue short-lived certificates.

### Enable PKI

```shell
vault secrets enable pki
vault secrets tune -max-lease-ttl=8760h pki
vault write pki/root/generate/internal common_name="example.com" ttl=8760h
vault write pki/config/urls \
    issuing_certificates="$VAULT_ADDR/v1/pki/ca" \
    crl_distribution_points="$VAULT_ADDR/v1/pki/crl"
```

### Create a Role and Issue Certificates

```shell
vault write pki/roles/web \
    allowed_domains="example.com" \
    allow_subdomains=true \
    max_ttl="720h"

vault write pki/issue/web common_name="app.example.com"
```

Vault returns certificate, private key, and CA chain.

### Intermediate CAs

1. Generate intermediate CSR: `vault write pki/intermediate/generate/internal ...`.
2. Sign with root or external CA.
3. Set signed certificate: `vault write pki/intermediate/set-signed certificate=@signed.pem`.

### Revocation and CRLs

- Revoke certificate: `vault write pki/revoke serial_number="..."`.
- Configure automated CRL rotation with `pki/config/crl`.

---

## Advanced Operations

### Deployment Architectures

- **Dev**: Single node, in-memory storage, root token.
- **Single-node server**: Integrated storage (Raft) or external (Consul) backend.
- **HA cluster**: Multiple Vault nodes with shared storage; leader handles writes.
- **Multi-datacenter**: Performance replication (Enterprise) and disaster recovery.

### Storage Backends

- **Integrated Storage (Raft)**: Default since Vault 1.4; recommended for most deployments.
- **Consul**: Mature option when you already operate Consul.
- **Cloud storage**: DynamoDB, Google Cloud Spanner, Azure Cosmos DB (Enterprise).

### Initialization

```shell
vault operator init -key-shares=5 -key-threshold=3
```

Vault outputs:

- Unseal keys (protect them carefully; do not store together).
- Initial root token (create limited tokens and revoke root token immediately after setup).

### Unsealing

```shell
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>
```

Automate with auto-unseal (cloud KMS, PKCS#11 HSM) in production.

### Sealing

```shell
vault operator seal
```

### Key Management

- Rotate encryption key: `vault operator rotate`.
- Check key status: `vault operator key-status`.

### Backup and Restore

- **Integrated storage snapshots**: `vault operator raft snapshot save backup.snap`.
- **Consul**: Use Consul snapshots.
- Ensure unseal keys and root token (if needed) are recoverable.

### Performance and DR Replication (Enterprise)

- **Performance**: Read scaling clusters.
- **DR**: Warm standby for disaster recovery.
- Consistency model: eventual where applicable.

### Namespaces (Enterprise)

- Allows multi-tenancy with delegated admin.
- Create namespace: `vault namespace create team1`.
- Switch namespace with CLI flag `-namespace=team1`.

---

## Integrations and Automation

### Terraform

Use the Vault Terraform provider to manage configuration as code.

```hcl
provider "vault" {
  address = "http://127.0.0.1:8200"
  token   = var.vault_token
}

resource "vault_policy" "dev_team" {
  name   = "dev-team"
  policy = file("dev-team.hcl")
}
```

### Ansible

- Modules: `hashivault_write`, `hashivault_read`, `hashivault_secret_engine`.
- Ideal for bootstrapping policies and auth methods.

### Kubernetes

- **Vault Agent Injector**: Mutating webhook that injects sidecars to fetch secrets.
- **CSI Provider**: Delivers secrets as volumes.
- **Secrets Operator**: Syncs Vault secrets to Kubernetes native `Secret` objects.

### CI/CD Pipelines

- Use short-lived tokens or AppRole.
- Leverage response wrapping (temp tokens containing secret material).

```shell
vault write -wrap-ttl=60s auth/approle/role/my-app/secret-id
```

The wrapping token can be safely handed to another pipeline stage that unwraps it with `vault unwrap`.

### Programming Libraries

- Official Go and Ruby clients.
- Third-party clients for Python, Java, Node.js.
- Use TTL renewal logic and retries in clients.

---

## Security Best Practices

These recommendations distill guidance from the official [HashiCorp Vault Production Hardening](https://developer.hashicorp.com/vault/docs/concepts/production-hardening) guide, [seal management best practices](https://developer.hashicorp.com/vault/docs/configuration/seal/seal-best-practices), and popular field tutorials such as the Vault Learn [Recommended Patterns](https://developer.hashicorp.com/vault/tutorials/recommended-patterns) series.

### Production Hardening Essentials

- **Enable TLS everywhere**: Issue certificates via Vault PKI or a trusted CA; set `tls_disable = 0`, prefer mutual TLS between clients and Vault, and enforce modern cipher suites.
- **Lock memory**: Run Vault with `mlock` capability (or `CAP_IPC_LOCK` in containers) to prevent secret material from being swapped to disk; if disabled, document the risk.
- **Dedicated OS user and systemd hardening**: Run Vault as a non-root service account, restrict file permissions, and leverage systemd hardening directives (`ProtectSystem=strict`, `NoNewPrivileges=yes`).
- **Disable swap and tune kernel limits**: HashiCorp recommends disabling swap, increasing file descriptors, and monitoring disk/CPU utilization to avoid performance regressions.
- **Integrated storage or hardened Consul**: Prefer Raft integrated storage for simplicity, or secure Consul with TLS, gossip encryption, ACLs, and access restrictions.

### Secrets Lifecycle Hygiene

- **Short TTLs and renewals**: Issue secrets with the minimum practical TTL, enable automatic renewal in clients, and revoke secrets immediately when no longer needed.
- **Automate rotation**: Use dynamic secrets, `vault lease renew`, and scheduled rotation pipelines (e.g., Terraform Cloud, Jenkins) to refresh credentials regularly.
- **Response wrapping by default**: When passing secrets between systems, wrap responses (`vault write -wrap-ttl=60s ...`) and unwrap only at the final destination to reduce exposure in logs or intercepts.
- **Inventory and clean-up**: Periodically list active leases (`vault list sys/leases/lookup/db`) and revoke stale entries. Combine with audit log analysis to flag dormant access paths.

### Access Patterns and Policy Design

- **Least privilege policies**: Grant only the `capabilities` required for each path; separate read, write, and administrative actions into distinct policies and attach them narrowly.
- **Policy as code**: Store HCL policies and Sentinel rules in version control, peer review them, and deploy via CI/CD or Terraform to maintain change history.
- **Use namespaces and mounts per environment**: Segment development, staging, and production either via namespaces (Enterprise) or separately mounted secret engines to prevent accidental cross-environment access.
- **Token management**: Prefer short-lived, renewable service tokens; use orphan tokens for automation so revoking parents (e.g., login tokens) does not cascade unexpectedly.

### Platform and Infra Controls

- **Auto-unseal with KMS/HSM**: Reduce operational toil and human exposure to unseal keys by integrating with cloud KMS (AWS KMS, Azure Key Vault, Google Cloud KMS) or hardware security modules.
- **Secure unseal key handling**: If manual unseal is required, distribute key shards via offline channels, store them separately, and rehearse disaster recovery to ensure quorum availability.
- **Audit everything**: Enable at least two audit devices (file + socket or syslog) so you have redundancy; forward logs to SIEM and monitor for anomalous paths or error spikes.
- **Network segmentation**: Place Vault in a trusted network segment behind firewalls, restrict inbound traffic, and ensure only authorized clients can reach `8200` (API) and `8201` (cluster replication).
- **Telemetry and alerting**: Expose Prometheus metrics (`telemetry { prometheus_retention_time = "24h" }`) and build alerts for seal status, leadership changes, and authentication error rates.

### Incident Response and Governance

- **Root token hygiene**: Use the root token only for initial bootstrap, then revoke it (`vault token revoke -self`) after creating dedicated admin policies.
- **Break-glass procedures**: Document how to generate emergency tokens (`vault token create -policy=break-glass`) and how to expire them immediately after use.
- **Change management**: Require human approval for enabling new secret engines or auth methods; log and monitor all configuration changes via audit devices.
- **Compliance reporting**: Leverage Sentinel (Enterprise) or external policy engines to enforce data residency, TTL limits, or key rotation intervals; export periodic reports for auditors.
- **Tabletop exercises**: Regularly rehearse seal/unseal, snapshot restoration, and replication failover to confirm operators can meet recovery time objectives.

---

## Troubleshooting and Observability

- **Enable audit logs**: Essential for compliance and debugging.
- **Monitor metrics**: Expose Prometheus telemetry (`telemetry { prometheus_retention_time = "24h" }`).
- **Check seals and health**: `vault status`, `vault operator raft list-peers`.
- **Diagnose auth issues**: `vault token lookup`, `vault token capabilities`.
- **Debug connections**: `vault diagnostics` (Enterprise) collects system info.
- **Common errors**:
  - `permission denied`: Review policies.
  - `lease not found`: Lease revoked or expired.
  - `connection refused`: Check `VAULT_ADDR` and TLS configuration.
  - `sealed`: Re-unseal or check auto-unseal configuration.

---

## Next Steps and Further Learning

- Practice with the [Vault Learn guides](https://developer.hashicorp.com/vault/tutorials).
- Complete the [Vault Production Hardening track](https://developer.hashicorp.com/vault/tutorials/production-hardening/production-hardening) to go deeper on OS, storage, and TLS requirements.
- Work through the [Recommended Patterns for AppRole and Vault Agent](https://developer.hashicorp.com/vault/tutorials/recommended-patterns/pattern-approle) to implement secure machine authentication flows.
- Read the [Vault architecture whitepaper](https://developer.hashicorp.com/vault/docs/internals/architecture).
- Experiment with multi-node HA using integrated storage.
- Integrate Vault with your CI/CD pipeline and rotate secrets automatically.
- Explore specialized secret engines: RabbitMQ, SSH, Azure, GCP, VMware, TOTP.
- Evaluate Vault Enterprise features (namespaces, Sentinel, replication) if you need multi-tenancy or advanced governance.

---

By following this tutorial, you should now understand the purpose of HashiCorp Vault, how to install and configure it, how to manage secrets and policies, and how to extend Vault to advanced operational and integration scenarios. Continue experimenting with real workloads, iterate on policies, and automate Vault configuration to embed it deeply into your security posture.
