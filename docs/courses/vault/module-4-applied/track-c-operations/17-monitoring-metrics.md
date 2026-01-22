# Monitoring and metrics

**[← Back to Track C: Operations](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-4_Applied-blue)
![Lesson](https://img.shields.io/badge/Lesson-17-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Configure Vault telemetry for metrics collection
- Set up Prometheus to scrape Vault metrics
- Create Grafana dashboards for Vault monitoring
- Implement alerting rules for critical Vault conditions

## Table of contents

- [Vault telemetry overview](#vault-telemetry-overview)
- [Prometheus integration](#prometheus-integration)
- [Grafana dashboards](#grafana-dashboards)
- [Alerting strategies](#alerting-strategies)
- [Health monitoring](#health-monitoring)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Vault telemetry overview

Vault exposes comprehensive metrics for monitoring cluster health, performance, and usage patterns.

### Telemetry architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Vault Monitoring Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐                                                       │
│   │     Vault       │                                                       │
│   │    Cluster      │                                                       │
│   │                 │     ┌─────────────────┐     ┌─────────────────┐      │
│   │  /v1/sys/metrics│────▶│   Prometheus    │────▶│    Grafana      │      │
│   │  (Prometheus)   │     │                 │     │                 │      │
│   │                 │     │  Scrape & Store │     │  Visualize &    │      │
│   │  Telemetry      │     │  Time Series    │     │  Alert          │      │
│   │  (StatsD/etc)   │     └────────┬────────┘     └─────────────────┘      │
│   └─────────────────┘              │                                        │
│                                    │                                        │
│                           ┌────────▼────────┐                               │
│                           │  Alertmanager   │                               │
│                           │                 │                               │
│                           │  Route alerts   │                               │
│                           │  to Slack/PD    │                               │
│                           └─────────────────┘                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Enabling telemetry

```hcl
# vault.hcl - Telemetry configuration
telemetry {
  # Prometheus metrics endpoint
  prometheus_retention_time = "30s"
  disable_hostname          = true

  # Optional: StatsD for alternative collection
  # statsd_address = "statsd.example.com:8125"

  # Optional: DogStatsD for Datadog
  # dogstatsd_addr = "127.0.0.1:8125"
  # dogstatsd_tags = ["env:production", "service:vault"]
}

# Ensure metrics endpoint is accessible
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = false

  # Unauthenticated metrics (use with caution)
  telemetry {
    unauthenticated_metrics_access = true
  }
}
```

### Key metric categories

| Category | Description | Example Metrics |
|----------|-------------|-----------------|
| **Runtime** | Go runtime stats | `vault.runtime.alloc_bytes`, `vault.runtime.num_goroutines` |
| **Audit** | Audit log operations | `vault.audit.log_request`, `vault.audit.log_response` |
| **Barrier** | Storage barrier operations | `vault.barrier.put`, `vault.barrier.get` |
| **Core** | Core Vault operations | `vault.core.handle_request`, `vault.core.unsealed` |
| **Token** | Token operations | `vault.token.create`, `vault.token.lookup` |
| **Policy** | Policy operations | `vault.policy.get_policy`, `vault.policy.set_policy` |
| **Expire** | Lease management | `vault.expire.num_leases`, `vault.expire.revoke` |
| **Raft** | Raft consensus | `vault.raft.commitTime`, `vault.raft.leader` |

[↑ Back to Table of Contents](#table-of-contents)

---

## Prometheus integration

Prometheus can scrape Vault's metrics endpoint directly.

### Vault configuration for Prometheus

```hcl
# vault.hcl
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname          = true
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = false

  telemetry {
    unauthenticated_metrics_access = false  # Require auth for metrics
  }
}
```

### Prometheus scrape configuration

**With authentication:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'vault'
    metrics_path: '/v1/sys/metrics'
    params:
      format: ['prometheus']
    scheme: https
    tls_config:
      ca_file: /etc/prometheus/vault-ca.crt
    authorization:
      type: Bearer
      credentials_file: /etc/prometheus/vault-token
    static_configs:
      - targets:
          - 'vault-1.example.com:8200'
          - 'vault-2.example.com:8200'
          - 'vault-3.example.com:8200'
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '(.+):\d+'
        replacement: '${1}'
```

**Without authentication (not recommended for production):**

```yaml
scrape_configs:
  - job_name: 'vault'
    metrics_path: '/v1/sys/metrics'
    params:
      format: ['prometheus']
    scheme: http
    static_configs:
      - targets: ['vault:8200']
```

### Creating a metrics policy

```bash
# Create a policy for Prometheus
vault policy write prometheus-metrics - <<EOF
path "sys/metrics" {
  capabilities = ["read"]
}
EOF

# Create a token for Prometheus
vault token create \
    -policy=prometheus-metrics \
    -period=24h \
    -orphan \
    -display-name="prometheus"

# Store the token in /etc/prometheus/vault-token
```

### Key metrics to monitor

```promql
# Cluster health
vault_core_unsealed{instance=~"vault.*"}

# Active/Standby status
vault_core_active{instance=~"vault.*"}

# Request rate
rate(vault_core_handle_request_count[5m])

# Request latency (p99)
histogram_quantile(0.99, rate(vault_core_handle_request_bucket[5m]))

# Token creation rate
rate(vault_token_create_count[5m])

# Active leases
vault_expire_num_leases

# Raft commit time
vault_raft_commitTime{quantile="0.99"}

# Memory usage
vault_runtime_alloc_bytes
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Grafana dashboards

Visualize Vault metrics with Grafana dashboards.

### Dashboard structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Vault Monitoring Dashboard                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      CLUSTER HEALTH                                   │   │
│  │  [Sealed: 0/3]  [Active: vault-1]  [Standby: 2]  [Version: 1.15.0]  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌────────────────────────────┐  ┌────────────────────────────┐            │
│  │     REQUEST RATE           │  │     REQUEST LATENCY        │            │
│  │  ╭─────────────────╮       │  │  ╭─────────────────╮       │            │
│  │  │    /‾‾‾\        │       │  │  │   ___           │       │            │
│  │  │   /    \____    │       │  │  │  /   \___       │       │            │
│  │  │  /          \   │       │  │  │ /        \      │       │            │
│  │  ╰─────────────────╯       │  │  ╰─────────────────╯       │            │
│  │  500 req/s                 │  │  p99: 15ms                 │            │
│  └────────────────────────────┘  └────────────────────────────┘            │
│                                                                              │
│  ┌────────────────────────────┐  ┌────────────────────────────┐            │
│  │     TOKEN OPERATIONS       │  │     ACTIVE LEASES          │            │
│  │  ╭─────────────────╮       │  │  ╭─────────────────╮       │            │
│  │  │ ████████████    │       │  │  │ ▄▄▄▄▄▄▄▄▄▄▄▄▄  │       │            │
│  │  │ ████████        │       │  │  │ █████████████  │       │            │
│  │  │ ████            │       │  │  │ █████████████  │       │            │
│  │  ╰─────────────────╯       │  │  ╰─────────────────╯       │            │
│  │  Create: 100  Revoke: 50   │  │  Total: 1,234              │            │
│  └────────────────────────────┘  └────────────────────────────┘            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Example dashboard JSON (key panels)

```json
{
  "dashboard": {
    "title": "Vault Cluster Monitoring",
    "panels": [
      {
        "title": "Cluster Seal Status",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(vault_core_unsealed)",
            "legendFormat": "Unsealed Nodes"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 2},
                {"color": "green", "value": 3}
              ]
            }
          }
        }
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(vault_core_handle_request_count[5m])) by (instance)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Request Latency (p99)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sum(rate(vault_core_handle_request_bucket[5m])) by (le, instance))",
            "legendFormat": "{{instance}} p99"
          }
        ]
      },
      {
        "title": "Active Leases",
        "type": "gauge",
        "targets": [
          {
            "expr": "vault_expire_num_leases",
            "legendFormat": "Leases"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "max": 10000,
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 7500},
                {"color": "red", "value": 9000}
              ]
            }
          }
        }
      }
    ]
  }
}
```

### Essential panels

| Panel | Metric | Purpose |
|-------|--------|---------|
| Seal Status | `vault_core_unsealed` | Ensure all nodes unsealed |
| Active Node | `vault_core_active` | Identify leader |
| Request Rate | `rate(vault_core_handle_request_count[5m])` | Track load |
| Latency p99 | `histogram_quantile(0.99, ...)` | Performance SLI |
| Token Create Rate | `rate(vault_token_create_count[5m])` | Auth activity |
| Active Leases | `vault_expire_num_leases` | Lease accumulation |
| Raft Commit Time | `vault_raft_commitTime` | Storage performance |
| Memory Usage | `vault_runtime_alloc_bytes` | Resource utilization |

[↑ Back to Table of Contents](#table-of-contents)

---

## Alerting strategies

Configure alerts for critical Vault conditions.

### Prometheus alerting rules

```yaml
# vault-alerts.yml
groups:
  - name: vault
    rules:
      # Seal alerts
      - alert: VaultSealed
        expr: vault_core_unsealed == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Vault node is sealed"
          description: "{{ $labels.instance }} has been sealed for more than 1 minute"

      - alert: VaultClusterDegraded
        expr: sum(vault_core_unsealed) < 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Vault cluster degraded"
          description: "Only {{ $value }} nodes are unsealed (expected 3)"

      # Leadership alerts
      - alert: VaultNoLeader
        expr: sum(vault_core_active) == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "No active Vault leader"
          description: "No Vault node is active/leader"

      - alert: VaultMultipleLeaders
        expr: sum(vault_core_active) > 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Multiple Vault leaders detected"
          description: "{{ $value }} nodes report being active (split brain?)"

      # Performance alerts
      - alert: VaultHighLatency
        expr: histogram_quantile(0.99, rate(vault_core_handle_request_bucket[5m])) > 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Vault high request latency"
          description: "{{ $labels.instance }} p99 latency is {{ $value }}s"

      - alert: VaultHighRequestRate
        expr: rate(vault_core_handle_request_count[5m]) > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High Vault request rate"
          description: "{{ $labels.instance }} handling {{ $value }} req/s"

      # Lease alerts
      - alert: VaultHighLeaseCount
        expr: vault_expire_num_leases > 50000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High number of Vault leases"
          description: "{{ $value }} active leases may indicate a leak"

      # Token alerts
      - alert: VaultTokenCreationSpike
        expr: rate(vault_token_create_count[5m]) > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Spike in Vault token creation"
          description: "{{ $value }} tokens/s being created"

      # Raft alerts
      - alert: VaultRaftSlowCommit
        expr: vault_raft_commitTime{quantile="0.99"} > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow Raft commits"
          description: "{{ $labels.instance }} p99 commit time is {{ $value }}s"

      - alert: VaultRaftPeerMissing
        expr: count(vault_raft_peers) < 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Raft peer missing"
          description: "Only {{ $value }} Raft peers detected"
```

### Alertmanager configuration

```yaml
# alertmanager.yml
global:
  slack_api_url: 'https://hooks.slack.com/services/xxx/xxx/xxx'

route:
  receiver: 'default'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true

    - match:
        severity: critical
      receiver: 'slack-critical'

    - match:
        severity: warning
      receiver: 'slack-warning'

receivers:
  - name: 'default'
    slack_configs:
      - channel: '#vault-alerts'

  - name: 'slack-critical'
    slack_configs:
      - channel: '#vault-critical'
        color: 'danger'
        title: '🚨 Vault Critical Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'slack-warning'
    slack_configs:
      - channel: '#vault-alerts'
        color: 'warning'

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '<pagerduty-service-key>'
        severity: critical
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Health monitoring

Beyond metrics, implement health checks for operational monitoring.

### Health check endpoints

```bash
# Basic health check (returns 200 if initialized and unsealed)
curl -s https://vault.example.com:8200/v1/sys/health

# Detailed health check options
curl -s "https://vault.example.com:8200/v1/sys/health?\
standbyok=true&\
perfstandbyok=true&\
sealedcode=503&\
uninitcode=501"

# Response includes:
# {
#   "initialized": true,
#   "sealed": false,
#   "standby": false,
#   "performance_standby": false,
#   "replication_performance_mode": "disabled",
#   "replication_dr_mode": "disabled",
#   "server_time_utc": 1640000000,
#   "version": "1.15.0",
#   "cluster_name": "vault-cluster",
#   "cluster_id": "xxx"
# }
```

### Health check response codes

| Code | Condition |
|------|-----------|
| 200 | Initialized, unsealed, active |
| 429 | Unsealed, standby |
| 472 | DR secondary, active |
| 473 | Performance standby |
| 501 | Not initialized |
| 503 | Sealed |

### Load balancer health checks

**HAProxy example:**

```haproxy
backend vault
    option httpchk GET /v1/sys/health?standbyok=true
    http-check expect status 200,429

    server vault-1 vault-1.example.com:8200 check
    server vault-2 vault-2.example.com:8200 check
    server vault-3 vault-3.example.com:8200 check
```

**AWS ALB target group:**

```hcl
resource "aws_lb_target_group" "vault" {
  name     = "vault"
  port     = 8200
  protocol = "HTTPS"
  vpc_id   = var.vpc_id

  health_check {
    enabled             = true
    path                = "/v1/sys/health?standbyok=true"
    port                = "traffic-port"
    protocol            = "HTTPS"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 10
    matcher             = "200,429"
  }
}
```

### Synthetic monitoring

```bash
#!/bin/bash
# vault-health-check.sh - Run as a cron job or synthetic monitor

VAULT_ADDR="${VAULT_ADDR:-https://vault.example.com:8200}"
ALERT_WEBHOOK="${ALERT_WEBHOOK:-https://hooks.slack.com/xxx}"

# Check health endpoint
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    "${VAULT_ADDR}/v1/sys/health?standbyok=true")

if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "429" ]; then
    # Send alert
    curl -X POST "$ALERT_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{\"text\": \"Vault health check failed: HTTP $HTTP_CODE\"}"
    exit 1
fi

# Optionally test secret read
export VAULT_TOKEN="$MONITORING_TOKEN"
vault kv get -field=value secret/health-check/canary || {
    curl -X POST "$ALERT_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d '{"text": "Vault read test failed"}'
    exit 1
}

echo "Vault health check passed"
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Prerequisites

- Docker and Docker Compose
- Vault dev server or HA cluster from previous lab

### Setup

```bash
# Create working directory
mkdir -p ~/vault-monitoring-lab && cd ~/vault-monitoring-lab

# Create docker-compose.yml for monitoring stack
cat > docker-compose.yml <<'EOF'
version: '3.8'

services:
  vault:
    image: hashicorp/vault:1.15
    cap_add:
      - IPC_LOCK
    ports:
      - "8200:8200"
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: root
      VAULT_DEV_LISTEN_ADDRESS: "0.0.0.0:8200"
    command: server -dev -dev-root-token-id=root

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  grafana-data:
EOF
```

### Exercise 1: Configure Prometheus scraping

1. Create Prometheus configuration:

   ```bash
   cat > prometheus.yml <<'EOF'
   global:
     scrape_interval: 15s

   scrape_configs:
     - job_name: 'vault'
       metrics_path: '/v1/sys/metrics'
       params:
         format: ['prometheus']
       scheme: http
       static_configs:
         - targets: ['vault:8200']
   EOF
   ```

2. Start the stack:

   ```bash
   docker-compose up -d
   ```

3. Verify Vault metrics:

   ```bash
   # Wait for services to start
   sleep 10

   # Check Vault metrics endpoint
   curl -s http://localhost:8200/v1/sys/metrics?format=prometheus | head -20
   ```

4. Verify Prometheus is scraping:

   Open http://localhost:9090 and go to Status → Targets

**Observation:** Prometheus should show the Vault target as "UP".

### Exercise 2: Explore metrics in Prometheus

1. Open Prometheus UI at http://localhost:9090

2. Try these queries:

   ```promql
   # Check if Vault is unsealed
   vault_core_unsealed

   # Request count
   vault_core_handle_request_count

   # Memory usage
   vault_runtime_alloc_bytes

   # Number of goroutines
   vault_runtime_num_goroutines
   ```

3. Generate some load:

   ```bash
   export VAULT_ADDR='http://127.0.0.1:8200'
   export VAULT_TOKEN='root'

   # Enable KV and write some secrets
   vault secrets enable -path=secret kv-v2

   # Generate load
   for i in {1..100}; do
       vault kv put secret/test-$i value="secret-$i"
   done
   ```

4. Check metrics again:

   ```promql
   # Request rate
   rate(vault_core_handle_request_count[1m])
   ```

**Observation:** You should see metrics reflecting the load you generated.

### Exercise 3: Set up Grafana dashboard

1. Open Grafana at http://localhost:3000
   - Username: admin
   - Password: admin

2. Add Prometheus data source:
   - Go to Configuration → Data Sources
   - Add Prometheus
   - URL: http://prometheus:9090
   - Save & Test

3. Create a simple dashboard:
   - Create → Dashboard → Add visualization
   - Select Prometheus data source
   - Query: `vault_core_unsealed`
   - Title: "Vault Seal Status"

4. Add more panels:

   ```promql
   # Panel 2: Request Rate
   rate(vault_core_handle_request_count[5m])

   # Panel 3: Memory Usage
   vault_runtime_alloc_bytes / 1024 / 1024

   # Panel 4: Goroutines
   vault_runtime_num_goroutines
   ```

**Observation:** You now have a basic Vault monitoring dashboard.

### Exercise 4: Test alerting (conceptual)

1. Review the alerting rules from the lesson

2. Simulate a sealed vault scenario:

   ```bash
   # Seal Vault
   vault operator seal

   # Check the metric
   curl -s "http://localhost:8200/v1/sys/metrics?format=prometheus" | grep vault_core_unsealed
   # Should show: vault_core_unsealed 0

   # Unseal again
   vault operator unseal # (won't work in dev mode, restart container instead)
   docker-compose restart vault
   ```

**Observation:** In production, the `VaultSealed` alert would fire when unsealed metric becomes 0.

### Cleanup

```bash
docker-compose down -v
cd ~ && rm -rf ~/vault-monitoring-lab
```

---

## Key takeaways

1. **Enable telemetry** - Configure `prometheus_retention_time` for metrics exposure
2. **Secure the metrics endpoint** - Use authentication in production
3. **Monitor seal status** - Critical alert when any node is sealed
4. **Track request latency** - p99 latency is a key performance indicator
5. **Watch lease counts** - High lease counts may indicate application issues
6. **Alert on leadership** - Both no-leader and multi-leader are critical conditions
7. **Health checks for LBs** - Use `/v1/sys/health` with appropriate parameters

---

[← Previous: High Availability](./16-high-availability.md) | [Back to Track C: Operations](./README.md) | [Next: Audit and Compliance →](./18-audit-compliance.md)
