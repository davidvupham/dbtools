# Decision Log: Business Continuity (DR Readiness & Failover Management)

This document records key architectural and operational decisions using Architecture Decision Records (ADRs).

## ADR-001: Control Plane Safety Model (Approvals, Audit, and Break-glass)

- **Date:** 2025-12-14
- **Status:** Proposed
- **Deciders:** Platform/DevOps, DBAs, Security/IAM, Application Owners

### Context

This project introduces a **high-impact control plane** that can initiate failover/switchover actions across Tier 1 systems. That makes it a privileged operational surface with strong requirements for:

- Separation of duties and explicit approvals
- Audit evidence sufficient for compliance and post-incident review
- A safe emergency (“break-glass”) option that does not become a bypass
- Clear, conservative reporting around data-loss risk (e.g., heartbeat limitations)

The system also needs to operate during real incidents, which often involve reduced visibility, partial outages, and time pressure.

### Decision

We adopt the following baseline safety model:

1. **Approval-gated actions**
   - All state-changing actions (failover, switchover, failback) require explicit approval(s) before execution.
   - Approval policy is configurable by **tier** and **action type**.
2. **Tier-based approval policies**
   - **Tier 1** actions require a **two-person rule**: one IT approver + one business/application owner approver.
   - **Tier 2** actions may use a single IT approver (policy-driven).
3. **Separation of duties**
   - Operator and Approver roles are distinct; the same identity cannot both request and approve Tier 1 actions.
4. **Confirmation and prechecks**
   - After approvals, execution requires explicit confirmation (“typed phrase” or equivalent) immediately prior to start.
   - Prechecks/postchecks are mandatory for Tier 1 actions and strongly recommended for Tier 2.
5. **Audit evidence**
   - All requests, approvals/denials, executions, and configuration changes are captured in an append-only audit log.
   - Audit entries include actor identity, timestamps, request payload, approval policy satisfied, outcome, and reason codes.
6. **Break-glass**
   - A break-glass path is allowed only via documented security process:
     - time-bound elevation
     - explicit incident reference
     - additional alerting/notification
   - Break-glass must be fully audited and reviewable after the event.
7. **Conservative data-loss reporting**
   - Heartbeat indicators are treated as **RPO indicators** only, not proof of “no data loss”.
   - Where authoritative replication markers exist (LSN/WAL/optime equivalents), they are used as primary evidence before/after execution.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Unattended automation | Fastest response | High safety/compliance risk; unacceptable blast radius |
| Single-approver for Tier 1 | Simpler and faster | Weaker governance and business risk management |
| No break-glass | Reduces abuse risk | Operationally unrealistic during major incidents |
| Rely on heartbeat only | Simple and uniform | Can misrepresent data loss; not defensible for Tier 1 |

### Consequences

- **Positive**
  - Strong safety controls for Tier 1 actions and defensible audit evidence
  - Clear operational model that works in both drills and real incidents
  - Reduces risk of unauthorized or accidental failover actions
- **Negative**
  - More process overhead; approvals can slow down Tier 1 actions
  - Requires IAM/SSO group management and documented approver on-call coverage
- **Risks**
  - Approval latency during incidents if approvers are unavailable
    - Mitigation: define approver coverage and break-glass runbook; pre-authorize approver groups
