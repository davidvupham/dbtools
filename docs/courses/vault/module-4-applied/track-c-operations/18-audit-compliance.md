# Audit and compliance

**[← Back to Track C: Operations](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-4_Applied-blue)
![Lesson](https://img.shields.io/badge/Lesson-18-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Configure and manage Vault audit devices
- Analyze audit logs for security investigation
- Implement compliance controls using Vault features
- Create audit reports for regulatory requirements

## Table of contents

- [Audit device fundamentals](#audit-device-fundamentals)
- [Configuring audit devices](#configuring-audit-devices)
- [Log analysis and investigation](#log-analysis-and-investigation)
- [Compliance controls](#compliance-controls)
- [Reporting and documentation](#reporting-and-documentation)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Audit device fundamentals

Vault's audit system provides a complete record of all requests and responses for security and compliance.

### Audit architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Vault Audit Flow                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐                                                           │
│   │   Client    │                                                           │
│   │   Request   │                                                           │
│   └──────┬──────┘                                                           │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         Vault Server                                 │   │
│   │                                                                      │   │
│   │   1. Request    2. Audit Log      3. Process      4. Audit Log      │   │
│   │      Received      Request           Request         Response        │   │
│   │         │             │                 │               │            │   │
│   │         ▼             ▼                 ▼               ▼            │   │
│   │    ┌────────┐   ┌──────────┐     ┌──────────┐   ┌──────────┐       │   │
│   │    │ Parse  │──▶│  Write   │────▶│ Execute  │──▶│  Write   │       │   │
│   │    │Request │   │  Audit   │     │ Request  │   │  Audit   │       │   │
│   │    └────────┘   └──────────┘     └──────────┘   └──────────┘       │   │
│   │                      │                               │              │   │
│   └──────────────────────┼───────────────────────────────┼──────────────┘   │
│                          │                               │                   │
│                          ▼                               ▼                   │
│                   ┌─────────────────────────────────────────────────┐       │
│                   │              Audit Devices                       │       │
│                   │  ┌─────────┐  ┌─────────┐  ┌─────────┐         │       │
│                   │  │  File   │  │ Syslog  │  │ Socket  │         │       │
│                   │  └─────────┘  └─────────┘  └─────────┘         │       │
│                   └─────────────────────────────────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Audit device types

| Type | Description | Use Case |
|------|-------------|----------|
| **File** | Writes JSON to local file | Local storage, log shipping |
| **Syslog** | Sends to syslog daemon | Centralized logging infrastructure |
| **Socket** | Streams to TCP/UDP socket | Real-time SIEM integration |

### What gets logged

Every request and response is logged with:

| Field | Description |
|-------|-------------|
| `time` | Timestamp of the operation |
| `type` | "request" or "response" |
| `auth` | Authentication information (token, policies, metadata) |
| `request` | Request details (path, operation, data) |
| `response` | Response details (data, warnings, errors) |
| `error` | Error message if operation failed |

### HMAC protection

Sensitive values are HMAC-hashed by default to prevent exposure while enabling verification:

```json
{
  "auth": {
    "client_token": "hmac-sha256:xxxxxxxxxxxxx",
    "accessor": "hmac-sha256:xxxxxxxxxxxxx",
    "policies": ["default", "app-read"]
  },
  "request": {
    "data": {
      "password": "hmac-sha256:xxxxxxxxxxxxx"
    }
  }
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Configuring audit devices

Set up audit devices for comprehensive logging.

### File audit device

```bash
# Enable file audit device
vault audit enable file file_path=/var/log/vault/audit.log

# With options
vault audit enable -path=file-audit file \
    file_path=/var/log/vault/audit.log \
    log_raw=false \
    hmac_accessor=true \
    mode=0600
```

**Configuration options:**

| Option | Description | Default |
|--------|-------------|---------|
| `file_path` | Path to audit log file | Required |
| `log_raw` | Log sensitive values unhashed | false |
| `hmac_accessor` | HMAC token accessors | true |
| `mode` | File permissions | 0600 |
| `format` | Output format (json/jsonx) | json |

### Syslog audit device

```bash
# Enable syslog audit device
vault audit enable syslog

# With options
vault audit enable -path=syslog-audit syslog \
    tag="vault" \
    facility="AUTH" \
    log_raw=false
```

**Syslog configuration:**

| Option | Description | Default |
|--------|-------------|---------|
| `facility` | Syslog facility | AUTH |
| `tag` | Syslog tag | vault |
| `log_raw` | Log unhashed values | false |

### Socket audit device

```bash
# Enable socket audit device (TCP)
vault audit enable socket \
    address="logstash.example.com:5000" \
    socket_type="tcp"

# UDP socket
vault audit enable -path=socket-udp socket \
    address="siem.example.com:514" \
    socket_type="udp"
```

### Multiple audit devices

Best practice: Enable multiple audit devices for redundancy.

```bash
# Primary: File
vault audit enable -path=file-primary file \
    file_path=/var/log/vault/audit.log

# Secondary: Syslog
vault audit enable -path=syslog-backup syslog \
    facility="LOCAL0"

# Tertiary: Socket to SIEM
vault audit enable -path=siem socket \
    address="siem.example.com:5000" \
    socket_type="tcp"
```

**Important:** Vault requires at least one audit device to successfully log before processing requests. If all devices fail, Vault stops processing requests.

### Managing audit devices

```bash
# List enabled audit devices
vault audit list

# List with detailed info
vault audit list -detailed

# Disable an audit device
vault audit disable file-audit

# Check audit device health
vault read sys/audit
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Log analysis and investigation

Techniques for analyzing audit logs for security and troubleshooting.

### Audit log format

```json
{
  "time": "2026-01-22T10:30:00.000000Z",
  "type": "request",
  "auth": {
    "client_token": "hmac-sha256:abc123...",
    "accessor": "hmac-sha256:def456...",
    "display_name": "approle",
    "policies": ["default", "app-read"],
    "token_policies": ["default", "app-read"],
    "metadata": {
      "role_name": "myapp"
    },
    "entity_id": "xxx-xxx-xxx",
    "token_type": "service"
  },
  "request": {
    "id": "xxx-xxx-xxx",
    "operation": "read",
    "client_token": "hmac-sha256:abc123...",
    "client_token_accessor": "hmac-sha256:def456...",
    "namespace": {
      "id": "root"
    },
    "path": "secret/data/myapp/config",
    "remote_address": "10.0.1.50"
  }
}
```

### Common analysis queries

**Using jq for log analysis:**

```bash
# Find all failed requests
cat audit.log | jq 'select(.type == "response" and .error != null)'

# Find requests from specific IP
cat audit.log | jq 'select(.request.remote_address == "10.0.1.50")'

# Find all token creation events
cat audit.log | jq 'select(.request.path == "auth/token/create")'

# Find access to specific path
cat audit.log | jq 'select(.request.path | startswith("secret/data/production"))'

# Find operations by specific policy
cat audit.log | jq 'select(.auth.policies | contains(["admin"]))'

# Count operations by type
cat audit.log | jq -r '.request.operation' | sort | uniq -c | sort -rn

# Find requests in time range
cat audit.log | jq 'select(.time >= "2026-01-22T10:00:00" and .time <= "2026-01-22T11:00:00")'
```

### Verifying HMAC values

Vault can verify that an HMAC value matches a specific input:

```bash
# Get the HMAC accessor for a token
vault read sys/audit-hash/file-audit input=<token-accessor>

# Compare with log entry
# If they match, the log entry is for that specific token
```

### Log shipping to SIEM

**Filebeat configuration for Elasticsearch:**

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/vault/audit.log
    json.keys_under_root: true
    json.add_error_key: true
    fields:
      log_type: vault_audit

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "vault-audit-%{+yyyy.MM.dd}"

setup.template.name: "vault-audit"
setup.template.pattern: "vault-audit-*"
```

**Fluentd configuration:**

```ruby
<source>
  @type tail
  path /var/log/vault/audit.log
  pos_file /var/log/td-agent/vault-audit.pos
  tag vault.audit
  format json
  time_key time
  time_format %Y-%m-%dT%H:%M:%S.%NZ
</source>

<match vault.audit>
  @type elasticsearch
  host elasticsearch.example.com
  port 9200
  index_name vault-audit
  type_name audit
</match>
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Compliance controls

Implement Vault features to meet regulatory requirements.

### Common compliance frameworks

| Framework | Key Requirements | Vault Features |
|-----------|------------------|----------------|
| **SOC 2** | Access control, audit logging | Policies, audit devices, entities |
| **PCI DSS** | Encryption, access logs, key management | Transit, audit, PKI |
| **HIPAA** | PHI protection, audit trails | KV encryption, audit logs |
| **GDPR** | Data protection, access logs | Namespaces, audit, policies |

### Access control implementation

```hcl
# Least privilege policy example
path "secret/data/{{identity.entity.name}}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Deny policy for sensitive paths
path "secret/data/production/credentials" {
  capabilities = ["deny"]
}

# Time-based access (Enterprise)
path "secret/data/finance/*" {
  capabilities = ["read"]
  required_parameters = ["reason"]
  allowed_parameters = {
    "reason" = []
  }
}
```

### Separation of duties

```bash
# Create separate authentication for different roles
# Admin role - can manage policies but not read secrets
vault policy write admin - <<EOF
path "sys/policies/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
path "secret/*" {
  capabilities = ["deny"]
}
EOF

# Operator role - can read secrets but not modify policies
vault policy write operator - <<EOF
path "sys/policies/*" {
  capabilities = ["read", "list"]
}
path "secret/data/*" {
  capabilities = ["read", "list"]
}
EOF
```

### Control points matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Compliance Control Points                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Control                  │ Vault Feature          │ Evidence               │
│   ─────────────────────────┼────────────────────────┼─────────────────────   │
│   Authentication required  │ Auth methods           │ Audit logs             │
│   Authorization enforced   │ Policies               │ Policy files           │
│   Access logged            │ Audit devices          │ Audit logs             │
│   Data encrypted at rest   │ Barrier encryption     │ Config documentation   │
│   Data encrypted in transit│ TLS                    │ TLS certificates       │
│   Secrets rotated          │ Dynamic secrets        │ Lease records          │
│   Key management           │ Transit, PKI           │ Key metadata           │
│   Separation of duties     │ Policies, namespaces   │ Policy definitions     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Namespaces for multi-tenancy (Enterprise)

```bash
# Create namespace per team/environment
vault namespace create team-a
vault namespace create team-b

# Each namespace has isolated:
# - Secrets engines
# - Auth methods
# - Policies
# - Audit logs (can be filtered by namespace)
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Reporting and documentation

Generate compliance reports and maintain documentation.

### Audit log report script

```bash
#!/bin/bash
# generate-audit-report.sh

AUDIT_LOG="${1:-/var/log/vault/audit.log}"
REPORT_DATE=$(date +%Y-%m-%d)
OUTPUT_FILE="vault-audit-report-${REPORT_DATE}.md"

cat > "$OUTPUT_FILE" <<EOF
# Vault Audit Report
**Generated:** $(date)
**Period:** Last 24 hours
**Source:** ${AUDIT_LOG}

## Summary Statistics

### Request Counts by Operation
\`\`\`
$(cat "$AUDIT_LOG" | jq -r 'select(.type == "request") | .request.operation' | sort | uniq -c | sort -rn)
\`\`\`

### Top 10 Accessed Paths
\`\`\`
$(cat "$AUDIT_LOG" | jq -r 'select(.type == "request") | .request.path' | sort | uniq -c | sort -rn | head -10)
\`\`\`

### Requests by Source IP
\`\`\`
$(cat "$AUDIT_LOG" | jq -r 'select(.type == "request") | .request.remote_address' | sort | uniq -c | sort -rn | head -10)
\`\`\`

### Failed Requests
\`\`\`
$(cat "$AUDIT_LOG" | jq -r 'select(.type == "response" and .error != null) | "\(.time) \(.request.path) \(.error)"' | tail -20)
\`\`\`

### Authentication Events
\`\`\`
$(cat "$AUDIT_LOG" | jq -r 'select(.request.path | startswith("auth/")) | "\(.time) \(.request.path) \(.request.operation)"' | tail -20)
\`\`\`

## Policy Compliance

### Denied Operations
\`\`\`
$(cat "$AUDIT_LOG" | jq -r 'select(.error | contains("permission denied"))' | wc -l) permission denied errors
\`\`\`

EOF

echo "Report generated: $OUTPUT_FILE"
```

### Configuration documentation

Maintain documentation of Vault configuration for auditors:

```markdown
# Vault Configuration Documentation

## Cluster Architecture
- 3-node Raft cluster
- Auto-unseal via AWS KMS
- TLS encryption enabled

## Authentication Methods
| Method | Path | Purpose |
|--------|------|---------|
| AppRole | auth/approle | Application authentication |
| LDAP | auth/ldap | Human user authentication |
| Kubernetes | auth/kubernetes | K8s workload authentication |

## Secrets Engines
| Engine | Path | Purpose |
|--------|------|---------|
| KV v2 | secret/ | Static secrets |
| Database | database/ | Dynamic database credentials |
| Transit | transit/ | Encryption as a service |
| PKI | pki/ | Certificate management |

## Policies
| Policy | Purpose | Assigned To |
|--------|---------|-------------|
| admin | Full administrative access | admin-group |
| app-read | Read application secrets | app-role |
| db-creds | Database credential generation | backend-apps |

## Audit Devices
| Device | Path | Destination |
|--------|------|-------------|
| file-primary | file/ | /var/log/vault/audit.log |
| syslog-backup | syslog/ | LOCAL0 facility |

## Key Management
- Master key: Shamir split (5 shares, 3 threshold) + AWS KMS auto-unseal
- Encryption key rotation: Quarterly
- Certificate renewal: Automated via PKI engine
```

### Evidence collection checklist

```markdown
## Audit Evidence Checklist

### Access Control
- [ ] Policy definitions exported
- [ ] Role assignments documented
- [ ] Entity/group mappings exported
- [ ] Auth method configurations documented

### Audit Logging
- [ ] Audit device configurations captured
- [ ] Sample audit logs collected
- [ ] Log retention policy documented
- [ ] Log shipping/archival verified

### Encryption
- [ ] TLS certificate information
- [ ] Encryption key metadata
- [ ] Seal configuration documented

### Operations
- [ ] Backup procedures documented
- [ ] Disaster recovery plan
- [ ] Incident response procedures
- [ ] Change management records
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Prerequisites

- Vault dev server running
- jq installed for JSON processing

### Setup

```bash
# Start Vault dev server
docker run -d --name vault-audit \
    -p 8200:8200 \
    -v $(pwd)/audit:/vault/audit \
    -e 'VAULT_DEV_ROOT_TOKEN_ID=root' \
    --cap-add=IPC_LOCK \
    hashicorp/vault:1.15

export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Create audit directory
mkdir -p audit
```

### Exercise 1: Enable and configure audit devices

1. Enable file audit device:

   ```bash
   vault audit enable file file_path=/vault/audit/audit.log
   ```

2. Verify audit device is enabled:

   ```bash
   vault audit list -detailed
   ```

3. Perform some operations to generate logs:

   ```bash
   # Enable secrets engine
   vault secrets enable -path=secret kv-v2

   # Write secrets
   vault kv put secret/app/config username="admin" password="secret123"

   # Read secrets
   vault kv get secret/app/config

   # List secrets
   vault kv list secret/app
   ```

4. Check audit log:

   ```bash
   cat audit/audit.log | jq '.' | head -50
   ```

**Observation:** Every operation is logged with request and response entries.

### Exercise 2: Analyze audit logs

1. Find all write operations:

   ```bash
   cat audit/audit.log | jq 'select(.request.operation == "update" or .request.operation == "create")'
   ```

2. Find access to specific path:

   ```bash
   cat audit/audit.log | jq 'select(.request.path | contains("secret/data/app"))'
   ```

3. Count operations by type:

   ```bash
   cat audit/audit.log | jq -r '.request.operation' | sort | uniq -c
   ```

4. Find the client token accessor used (HMAC'd):

   ```bash
   cat audit/audit.log | jq -r '.auth.accessor' | sort -u
   ```

**Observation:** You can analyze access patterns and identify who accessed what.

### Exercise 3: Simulate failed access

1. Create a restricted policy:

   ```bash
   vault policy write restricted - <<EOF
   path "secret/data/public/*" {
     capabilities = ["read"]
   }
   EOF
   ```

2. Create a token with restricted policy:

   ```bash
   RESTRICTED_TOKEN=$(vault token create -policy=restricted -format=json | jq -r '.auth.client_token')
   ```

3. Try to access forbidden path:

   ```bash
   VAULT_TOKEN=$RESTRICTED_TOKEN vault kv get secret/app/config
   # Should fail with permission denied
   ```

4. Find the denied request in audit log:

   ```bash
   cat audit/audit.log | jq 'select(.error != null and (.error | contains("permission denied")))'
   ```

**Observation:** Failed access attempts are logged with error details.

### Exercise 4: Generate a simple audit report

1. Create a report script:

   ```bash
   cat > generate-report.sh <<'EOF'
   #!/bin/bash
   AUDIT_LOG="audit/audit.log"

   echo "=== Vault Audit Summary ==="
   echo "Generated: $(date)"
   echo ""

   echo "=== Operation Counts ==="
   cat "$AUDIT_LOG" | jq -r 'select(.type == "request") | .request.operation' | sort | uniq -c | sort -rn

   echo ""
   echo "=== Unique Paths Accessed ==="
   cat "$AUDIT_LOG" | jq -r 'select(.type == "request") | .request.path' | sort -u

   echo ""
   echo "=== Failed Requests ==="
   FAILED=$(cat "$AUDIT_LOG" | jq 'select(.error != null)' | wc -l)
   echo "Total failed requests: $FAILED"

   echo ""
   echo "=== Recent Errors ==="
   cat "$AUDIT_LOG" | jq -r 'select(.error != null) | "\(.time): \(.error)"' | tail -5
   EOF

   chmod +x generate-report.sh
   ```

2. Run the report:

   ```bash
   ./generate-report.sh
   ```

**Observation:** You can generate compliance-ready reports from audit logs.

### Cleanup

```bash
docker stop vault-audit && docker rm vault-audit
rm -rf audit generate-report.sh
```

---

## Key takeaways

1. **Enable multiple audit devices** - Redundancy ensures logging even if one device fails
2. **Vault blocks on audit failure** - If all audit devices fail, Vault stops processing requests
3. **HMAC protects sensitive data** - Tokens and secrets are hashed but verifiable
4. **Log analysis is critical** - Use jq and SIEM tools for security investigation
5. **Ship logs to central SIEM** - Enable correlation with other security events
6. **Document everything** - Maintain configuration documentation for compliance
7. **Regular audit reviews** - Schedule periodic review of access patterns and anomalies

---

[← Previous: Monitoring and Metrics](./17-monitoring-metrics.md) | [Back to Track C: Operations](./README.md)
