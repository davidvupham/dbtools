# Procedures: Business Continuity (DR Readiness & Failover Management)

This document lists operational procedures that are specific to this service and its supported platforms. For incident response flow, see `runbook.md`.

## 1. Onboard a New Resource

**When to use:** Adding a new database/application dependency to monitoring and (optionally) controlled execution.

**Steps:**

1. Confirm **owner**, **tier** (Tier 1/2), environment, and sites (primary/DR).
2. Confirm **RPO target** and thresholds (source of truth) and record them in configuration.
3. Provision **service accounts**:
   - Monitoring account (read-only indicators)
   - Execution account (only if execution is enabled; least privilege)
4. Store credentials in the approved **secrets manager**.
5. Add the Resource and (if needed) Group configuration.
6. Validate monitoring:
   - Freshness updates
   - Status evaluates as expected
   - Alerts route correctly to non-prod or prod targets
7. For Tier 1, schedule a **non-prod drill** (or safe planned switchover window) before enabling execution in production.

**Verification:**

- [ ] Resource appears on dashboard with correct tier and owner.
- [ ] Freshness < 1 minute (or documented limitation).
- [ ] Audit log shows onboarding/config changes.

## 2. Configure Approval Policy (Tier 1 vs Tier 2)

**When to use:** Setting or changing approval requirements for actions.

**Default policy (per ADR-001):**

- Tier 1: IT Approver + Business/App Owner Approver required
- Tier 2: IT Approver required

**Steps:**

1. Validate required approver groups exist in SSO/IAM.
2. Update approval policy configuration (tier/type).
3. Test with a non-prod request:
   - Ensure partial approval does not allow execution
4. Document any policy exceptions in an ADR.

## 3. Run a Planned Switchover (Non-Prod Drill)

**When to use:** Regular DR validation, planned rotations, compliance exercises.

**Steps:**

1. Create execution request tagged as **Drill** or **Planned Rotation**.
2. Ensure approvals are obtained (Tier 1 dual-approval).
3. Review prechecks:
   - connectivity
   - replication indicators and markers
   - data freshness
   - heartbeat (if configured) as indicator only
4. Confirm and start execution.
5. Monitor progress and notifications.
6. Review postchecks:
   - service health
   - replication markers
   - integrity checks results (if configured)
7. Export audit evidence (CSV/JSON) for compliance.

**Verification:**

- [ ] Postchecks passed and recorded.
- [ ] Audit contains requester, approvals, steps, and outcomes.

## 4. Emergency Failover (Production)

**When to use:** Primary outage requires switching to DR.

**Steps:**

1. Open/confirm incident bridge and incident ticket.
2. Create failover execution request referencing incident/ticket.
3. Obtain approvals per Tier policy; use break-glass only if necessary and per runbook.
4. Run prechecks (as feasible); when visibility is reduced, explicitly document limitations.
5. Confirm and execute.
6. Postchecks and stabilize service.
7. Communicate status and evidence to stakeholders.

## 5. Break-glass Access (Emergency Only)

**When to use:** Approvers unavailable and delay causes unacceptable impact.

**Requirements:**

- Incident reference required
- Time-bound elevation
- Additional notification to security/compliance
- Post-incident review required

Follow the Break-glass procedure in `runbook.md`.
