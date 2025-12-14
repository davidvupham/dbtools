# Implementation Guide: Business Continuity (DR Readiness & Failover Management)

This guide describes a recommended implementation and rollout approach for the Business Continuity service.

> This project is safety-critical. Start with read-only monitoring in non-prod, then expand scope and privileges.

## 1. Prerequisites

- Network connectivity to both primary and DR networks (as required).
- Identity Provider/SSO groups defined for:
  - Viewer, Operator, Approver-IT, Approver-Business, Admin
- Secrets manager access (Vault/approved store).
- `gds_notification` configuration for non-prod and prod routing.
- Non-prod database targets for each platform connector you intend to support.

## 2. Phase 1 — Monitoring MVP (non-prod)

**Goal:** Inventory + monitoring + dashboard + alerting without any execution privileges.

Steps:

1. Implement/read configuration model:
   - Resources, groups, tiers
   - RPO targets and thresholds
2. Implement core monitoring loop:
   - connector interface
   - observation persistence
   - freshness and status rule evaluation
3. Implement UI:
   - list view (traffic light)
   - details view (freshness + indicators + 24h trend)
4. Integrate notifications via `gds_notification`:
   - RPO indicator breach
   - loss of visibility
5. Validate using `testing/test-plan.md` (TC-010..TC-032).

## 3. Phase 2 — Evidence and Audit (non-prod)

**Goal:** Compliance-grade evidence for readiness and drills.

Steps:

1. Implement append-only audit log for:
   - config changes
   - requests and approvals (even if execution not yet enabled)
   - monitoring rule outcomes (optional; at least store significant changes)
2. Implement export endpoints (CSV/JSON).
3. Validate using test plan (TC-050..TC-052).

## 4. Phase 3 — Controlled Execution (non-prod first)

**Goal:** Approval-gated workflows with prechecks/postchecks.

Steps:

1. Implement request model and state machine.
2. Implement RBAC + approval policy enforcement (ADR-001).
3. Implement confirmation gate.
4. Implement connector prechecks/postchecks and (where safe) execution steps.
5. Add clear limitations for:
   - missing replication markers
   - heartbeat-only evidence
6. Validate with test plan (TC-040..TC-045).

## 5. Phase 4 — Scheduling (no unattended execution)

**Goal:** Support drills/rotations without bypassing approvals.

Steps:

1. Implement schedules that create requests and notify stakeholders.
2. Enforce “approval still required” for execution.
3. Validate with test plan (TC-060..TC-061).

## 6. Production Rollout Guidance (risk-managed)

1. **Start with monitoring-only** for Tier 1 (read-only accounts).
2. Run at least one non-prod drill per Tier 1 group.
3. Enable execution only after:
   - approver coverage is defined
   - break-glass procedure is approved
   - audit export and retention meets compliance expectations
4. Schedule first Tier 1 production drill in a planned window with stakeholders.

## 7. Operational Readiness Checklist (minimum)

- [ ] Alerts route correctly for Tier 1 and do not page production on-call from non-prod.
- [ ] Audit export works and can be stored for evidence.
- [ ] Approver groups exist and are staffed.
- [ ] Break-glass procedure tested (tabletop at minimum).
- [ ] Clear rollback/stop guidance exists for failed executions.
