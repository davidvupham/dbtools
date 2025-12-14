# Test Plan: Business Continuity (DR Readiness & Failover Management)

## 1. Overview

This test plan defines the validation approach for the Business Continuity service described in `../specs/functional-spec.md`. It focuses on proving:

- Monitoring accuracy and freshness
- Alerting correctness and routing
- Approval-gated execution safety controls
- Auditability and evidence exports
- Clear, conservative “data-loss determination” reporting (including heartbeat limitations)

## 2. Test Objectives

- Validate **RBAC** and **separation of duties** (Operator vs Approver(s)).
- Validate **monitoring collectors** per connector (health/replication indicators, freshness timestamps, history).
- Validate **status rule evaluation** (Green/Yellow/Red) and breach detection.
- Validate `gds_notification` integration for alerts and execution events.
- Validate **controlled execution** workflow gates (request → approve → confirm → prechecks → execute → postchecks).
- Validate **audit log** completeness and export functionality (CSV/JSON).
- Validate **scheduling behavior** (can create requests; cannot execute without approval).
- Validate **failure modes** (target unreachable, partial failures, rollback/stop behavior) and operator UX for degraded mode.

### 2.1 TDD Policy (where we use it)

We use **test-driven development (TDD)** where it provides the most value: deterministic, safety-critical logic.

- **TDD REQUIRED for:**
  - Status rules / threshold evaluation (Green/Yellow/Red)
  - Approval policy logic (multi-approver rules, separation of duties, break-glass constraints)
  - Workflow/state machine transitions (request → approve → confirm → execute → postcheck)
  - Input validation and audit record formatting
- **TDD RECOMMENDED (but not always strict) for:**
  - Connector adapters (use unit tests with mocks and contract-style tests)
  - API handlers (unit + integration tests)
- **TDD NOT EXPECTED for:**
  - Pure UI layout changes (still testable via component/e2e tests where risk warrants)

## 3. Test Environment

| Environment | Purpose | Configuration |
|-------------|---------|---------------|
| **Dev** | Unit tests + local smoke tests | Local API/UI; mocked connectors; test DB for storage |
| **Non-Prod** | Integration + end-to-end testing | Non-prod deployments; test instances of each supported platform; non-prod SSO + notification routing |
| **Prod** | Limited production validation | Read-only monitoring first; controlled drills during approved windows; production notification routing |

## 4. Test Cases

### 4.1 Authentication, Authorization, and Approval Policy

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-001 | SSO login required | Attempt to access UI/API without auth | Redirect to SSO; unauthenticated API calls rejected | ⬜ |
| TC-002 | Viewer is read-only | Login as Viewer; attempt to create request | UI hides actions; API denies with authorization error; audit not polluted with failed action (or records denied attempt per policy) | ⬜ |
| TC-003 | Operator can create requests | Login as Operator; create failover request | Request created in pending approval state; audit event recorded | ⬜ |
| TC-004 | Multi-approver policy enforced (Tier 1) | Configure Tier 1 to require IT + Business approvals; approve with only one role | Request remains pending; UI shows missing approval; audit shows partial approval | ⬜ |
| TC-005 | Approval required before execution | Operator attempts to start unapproved request | Start blocked; audit records denial reason | ⬜ |
| TC-006 | Break-glass path audited | Use break-glass procedure (if enabled in non-prod) | Access is time-bound; all actions are fully audited and notifications emitted | ⬜ |

### 4.2 Inventory & Configuration

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-010 | Create resource and group | Add resource + dependency group | Resource appears on dashboard; stored with tier/owner metadata | ⬜ |
| TC-011 | CMDB ingestion (read-only) | Trigger CMDB sync | New/updated metadata ingested; no writes to CMDB | ⬜ |
| TC-012 | RPO targets and thresholds | Configure per-resource thresholds | Thresholds stored; rule evaluation uses configured values | ⬜ |

### 4.3 Monitoring & Status Evaluation

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-020 | Collect indicators (each connector) | Run monitoring job for Mongo/SQL/PG/Snow | Observations captured with timestamp; freshness displayed | ⬜ |
| TC-021 | Data freshness displayed | Delay/disable collection temporarily | UI shows stale indicator with timestamp; status degrades per rules | ⬜ |
| TC-022 | Historical trend retention | Collect over time (24h+ in non-prod) | Trend graph available for configured metrics | ⬜ |
| TC-023 | Heartbeat indicator handled conservatively | Enable heartbeat (1-minute) for a resource; simulate missed interval | UI/report shows “caught up to heartbeat T; potential loss window …”; does not claim “no data loss” solely from heartbeat | ⬜ |

### 4.4 Alerting & Notifications (`gds_notification`)

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-030 | RPO-indicator breach alert | Force breach condition above threshold | Alert emitted via `gds_notification`; includes resource, tier, reason | ⬜ |
| TC-031 | Connectivity loss alert | Block connectivity to target | Alert emitted; UI marks loss of visibility | ⬜ |
| TC-032 | Execution event notifications | Run a test switchover | Notifications for request created/approved/started/succeeded/failed | ⬜ |

### 4.5 Controlled Execution (Switchover/Failover/Failback)

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-040 | Confirmation required | Start approved request without confirmation phrase | Start blocked; clear UX message | ⬜ |
| TC-041 | Prechecks executed and visible | Start approved request | Prechecks run; results visible before actions; audit contains results | ⬜ |
| TC-042 | Execution progress and audit trail | Execute a non-prod switchover | UI shows progress; step outcomes recorded; final state correct | ⬜ |
| TC-043 | Postchecks and markers shown | Complete execution | Postchecks run; replication markers shown where available; limitations clearly stated | ⬜ |
| TC-044 | Failure handling | Inject failure mid-execution | Execution marked failed; notifications sent; audit contains reason; safe stop/rollback behavior documented | ⬜ |
| TC-045 | Failback flow | Perform failback in non-prod | Prechecks/approvals enforced; postchecks validate normal operations | ⬜ |

### 4.6 Audit & Evidence Export

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-050 | Audit log completeness | Perform request → approve → execute | Audit includes actors (requester/approvers/executor), timestamps, payload, outcome | ⬜ |
| TC-051 | Export audit log | Export by date/system | CSV/JSON export succeeds; includes required fields; data matches UI view | ⬜ |
| TC-052 | Immutability controls (as implemented) | Attempt to modify/delete audit record (admin) | Not permitted or captured as immutable append-only behavior per design | ⬜ |

### 4.7 Scheduling (No Unattended Execution)

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-060 | Scheduled drill creates request | Create schedule and wait for trigger | Request is created and notifications sent | ⬜ |
| TC-061 | Schedule cannot auto-execute | Do not approve scheduled request | No execution occurs; request remains pending | ⬜ |

## 5. Test Execution Schedule

| Phase | Tests | Environment | Duration | Owner |
|-------|-------|-------------|----------|-------|
| Unit | TC-001 to TC-0XX (logic-level) | Dev | TBD | Dev |
| Integration | TC-010 to TC-0XX | Non-Prod | TBD | Dev + DBA |
| E2E (Controlled) | TC-040 to TC-0XX | Non-Prod | TBD | Dev + DBA + Approvers |
| Production Validation | Subset of TC-020/030/050 | Prod | TBD | Ops + DBA |
| **Total** | TBD | | **TBD** | |

## 6. Entry/Exit Criteria

### Entry Criteria

- [ ] Functional Spec approved for current iteration.
- [ ] Test environments provisioned and reachable (including target DB instances).
- [ ] SSO groups configured for Viewer/Operator/Approver/Admin roles.
- [ ] Notification routing configured for non-prod (does not page real on-call).
- [ ] Secrets are stored in the approved secrets manager and accessible to the service.

### Exit Criteria

- [ ] All **critical** test cases pass (TC-001/002/003/004/005/041/042/050/051/061).
- [ ] No **Critical/High** defects open.
- [ ] UAT walkthrough completed with DBA + approver representatives.
- [ ] Evidence export validated (audit export and at least one drill record).

## 7. Defect Management

| Severity | Definition | Resolution SLA |
|----------|------------|----------------|
| **Critical** | Causes unsafe execution, bypasses approvals, or corrupts audit trail | Fix before any rollout |
| **High** | Breaks monitoring/alerting for Tier 1 or misreports readiness materially | Fix before Tier 1 onboarding |
| **Medium** | Partial feature degradation with workaround | Fix in next iteration |
| **Low** | Cosmetic/UX issue; no functional impact | Fix as time permits |
