# Software Stack: Business Continuity (DR Readiness & Failover Management)

This document describes the proposed software stack and operational tooling for the Business Continuity service.

> Constraints from the Functional Spec: Python backend and React frontend; notifications via `gds_notification`.

## 1. Application Stack (proposed defaults)

### Backend API

- **Language/runtime:** Python 3.x (repo standard)
- **Web framework:** FastAPI (recommended for typed APIs and OpenAPI) or Flask (acceptable if repo standard dictates)
- **Authn integration:** SSO via reverse proxy / OIDC middleware (implementation choice captured as ADR when selected)
- **Validation:** Pydantic models for request/response schemas
- **Background jobs:** Celery/RQ/Arq (or Kubernetes CronJob + worker) — choose one and document in ADR

### Frontend UI

- **Framework:** React
- **Auth:** SSO session via IdP (OIDC) and API tokens/cookies as appropriate
- **UI components:** Prefer existing repo conventions (if any); otherwise adopt a minimal component library

## 2. Persistence & Data Stores (separate concerns)

This system has three distinct data categories with different requirements:

1. **Configuration and current state**
   - Resources, groups, thresholds, approval policies, requests, execution state
2. **Time-series / history**
   - Short-horizon monitoring history for trends and evidence
3. **Audit log**
   - Append-only event record with integrity protections

### Recommended approach (baseline)

- **Config + State Store:** PostgreSQL (transactional, relational, easy backups)
- **Time-series history:** PostgreSQL (initially) with time-bucketing; consider Prometheus/Timescale later if needed
- **Audit log:** Append-only table in PostgreSQL + periodic export to immutable storage (e.g., object storage with retention/WORM), depending on compliance needs

> This is intentionally conservative: start simple with PostgreSQL, then split stores only when scale or compliance requires.

## 3. Secrets Management

- **Secrets store:** Vault (or organization-approved secrets manager)
- **Rules:**
  - No secrets in repo, config files, or CI logs
  - Use short-lived credentials where possible
  - Separate service accounts for monitoring vs execution

## 4. Identity, RBAC, and Approvals

- **Identity provider:** Organization SSO (OIDC/SAML)
- **RBAC source:** IdP group claims mapped to application roles (Viewer/Operator/Approver-IT/Approver-Business/Admin)
- **Approval policy:** Tier-based multi-approver support; Tier 1 requires 2-person rule (see ADR-001)

## 5. Notifications

- **Library/service:** `gds_notification`
- **Channels:** PagerDuty, email, Slack (as configured)
- **Routing:** Tier-based routing; non-prod must never page production on-call

## 6. Observability

### Logging

- **Backend:** structured JSON logs (request id, user, request id, execution id)
- **Audit:** separate append-only audit records (not just logs)

### Metrics

- **System health:** API latency, worker queue depth, job runtimes, connector error rates
- **Domain metrics:** per-resource freshness, rule outcomes, alert rates, execution success/failure

### Tracing (optional)

- OpenTelemetry (recommended if the platform supports it)

## 7. CI/CD and Governance

- **CI:** GitHub Actions (repo standard) with linting + tests
- **CD:** environment-specific deployment pipeline (K8s/VM) — document in Implementation Guide
- **Controls:**
  - Required reviews for execution-path changes
  - Secret scanning and branch protections
  - Change tickets for production executions (policy-driven)

## 8. Deployment Model (target)

- **Preferred:** Kubernetes (API + worker + scheduler) with HA replicas and controlled rollouts
- **Alternative:** VMs with systemd services and a job scheduler
- **Network:** Must reach both primary and DR networks; enforce least-privilege network policies

## 9. Connector Runtime Requirements

- **Connector model:** plugin-style connectors with clear capability flags:
  - Monitoring-only vs supports execution steps
  - Replication marker availability (LSN/WAL/optime equivalents)
  - Heartbeat support (optional) and limitations

## 10. Open Items (to close via ADRs)

- Exact backend framework and worker framework selection
- Definitive data store strategy for audit immutability and retention
- Hosting environment specifics (K8s vs VM) and “DR of the tool”
