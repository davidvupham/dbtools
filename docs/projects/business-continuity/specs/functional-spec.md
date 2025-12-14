# Functional Specification: Business Continuity (DR Readiness & Failover Management)

## 1. Introduction

The Business Continuity Service is a disaster recovery (DR) **readiness monitoring** system with **approval-gated failover (emergency) and switchover (planned) workflows**. It provides a centralized dashboard to view the health, replication lag (an input into RPO compliance), and readiness status of critical database systems and related business applications.

When this document says “controlled”, it means the service **adds safety controls** around high-impact DR actions so they are deliberate, repeatable, and auditable:

- **Permissioned**: only allowed roles can request/execute actions (RBAC)
- **Approval-gated**: one or more approvers must authorize actions before execution (separation of duties). For Tier 1, this may be a **two-person rule** (e.g., one IT approver + one business/application owner approver).
- **Confirmed**: explicit “are you sure?” confirmation just before execution
- **Checked**: prechecks/postchecks run and results are visible
- **Audited**: who requested/approved/executed and outcomes are logged for evidence

It allows authorized users to **initiate and manage** failover/switchover procedures for:

- Actual disaster recovery events
- Routine DR drills
- Planned, controlled datacenter rotations (e.g., alternating active datacenters weekly)

### 1.1 Purpose

This document defines functional, non-functional, security, and integration requirements for the Business Continuity (DR) service.

### 1.2 Audience

- DBAs / SRE / IT Operations
- Security / Compliance / Audit
- Engineering teams implementing and operating the service

### 1.3 Definitions & Acronyms

- **BC**: Business Continuity (people/process/technology). This product primarily addresses the **technology DR** component.
- **DR**: Disaster Recovery.
- **RPO (Recovery Point Objective)**: Maximum acceptable data loss measured in time.
- **RTO (Recovery Time Objective)**: Maximum acceptable time to restore service.
- **Replication lag**: Observed delay between primary and replica; an *indicator* used to evaluate RPO compliance, not RPO itself.
- **Failover**: Unplanned/urgent move of production to DR.
- **Switchover**: Planned/controlled move (rotation/test).
- **Drill**: Planned exercise to validate preparedness.
- **Tier 1 / Tier 2**: Criticality levels used for alerting/permissions and operational expectations.
- **Resource**: A monitored entity (database instance/cluster/warehouse, or an application dependency).
- **Group**: A set of resources that must move together (dependency-aware).

### 1.4 References

- `../architecture/technical-architecture.md`
- `../operations/runbook.md`
- `../testing/test-plan.md`
- `../management/raci-matrix.md`

## 2. Scope

### 2.1 In Scope

- **Monitoring:** Near real-time DR readiness monitoring for MongoDB, SQL Server, PostgreSQL, and Snowflake.
- **Metrics:** RPO target configuration per resource and continuous evaluation using replication/health indicators.
- **Failover/Switchover:** User-initiated execution workflow for single resources or dependency groups.
- **Testing & Rotation:** Support for *planned* switchovers and drills, including scheduling and pre-notification.
- **Dashboard:** Responsive web UI for status visualization and controlled actions.
- **Notification:** Alerting via `gds_notification` for health issues, RPO violations, and execution events.
- **Tiering:** Distinction between Tier 1 (Critical) and Tier 2 (Non-Critical) systems.
- **Extensibility:** Connector-based architecture supporting future apps and database types.
- **Auditability:** Exportable event history suitable for compliance evidence.

### 2.2 Out of Scope

- **Unattended automatic failover** execution without human approval.
- **Native mobile applications** (iOS/Android).
- **Replacing vendor-native DR capabilities** (e.g., this service does not create replication; it observes and orchestrates documented procedures).

## 3. Users, Roles, and Permissions

### 3.1 User Roles (minimum)

- **Viewer**: View dashboards and read audit history.
- **Operator**: Initiate a *request* for switchover/failover, run prechecks.
- **Approver (IT)**: Approve/deny execution requests from an IT risk perspective (platform readiness, operational safety).
- **Approver (Business/App Owner)**: Approve/deny execution requests from a business risk perspective (customer impact, timing, change windows).
- **Admin**: Manage configuration (resources, thresholds, schedules, connectors).

Notes:

- Emergency access (“break-glass”) is permitted only via documented security process and is fully audited.

## 4. Functional Requirements (by capability)

> Requirements are written to be testable/verifiable. User stories below map to these requirements.

### 4.1 Inventory & Configuration

- **FR-001 (Resource Inventory):** The system SHALL maintain an inventory of monitored resources and groups, including tier, owner, environment, and dependency metadata.
- **FR-002 (CMDB Sync):** The system SHOULD support read-only ingestion/sync of inventory metadata from a CMDB.
- **FR-003 (RPO Targets):** The system SHALL allow configuring an RPO target (time) and alert threshold(s) per resource/group.

### 4.2 Monitoring & Status Evaluation

- **FR-010 (Health Checks):** The system SHALL periodically collect health/replication indicators from each supported platform connector.
- **FR-011 (Freshness):** The system SHALL timestamp each observation and surface data freshness in the UI.
- **FR-012 (Status Rules):** The system SHALL compute a status (Green/Yellow/Red) per resource using documented thresholds and rule logic.
- **FR-013 (Historical Trend):** The system SHOULD retain time-series history for lag/health metrics for at least 24 hours.
- **FR-014 (Heartbeat Indicator - Optional):** The system SHOULD support an optional, per-resource “heartbeat” indicator (e.g., a table/collection updated periodically) as an additional, operator-friendly signal of write propagation.
  - The system SHALL treat heartbeat as an **RPO-indicator** only (not proof of “no data loss”). It MAY be used to estimate an **upper bound** on missing time based on its update interval and observed delays.

#### Heartbeat guidance (what it can and cannot prove)

If each database has a heartbeat table/collection updated every minute with the current date/time, it is a **good operator-friendly indicator** of replication/write propagation, but it does **not** by itself prove “no data loss”.

- **What heartbeat can tell you**
  - **Upper bound on missing time (coarse):** If the last heartbeat timestamp in DR is \(T\), you have evidence that heartbeat writes were applied up to \(T\). With a 1-minute interval, your “known caught-up-to” granularity is ~1 minute (often worse once you include replication delay).
  - **Liveness:** It shows the write path and replication pipeline were functioning at least up to that point.
- **What heartbeat cannot prove**
  - **No partial loss inside the interval:** You can lose other transactions in the same minute even if the heartbeat replicated.
  - **No selective loss:** Some tables/collections or workloads can fail/lag while the heartbeat continues.
  - **No completeness without a reference marker:** A successful heartbeat does not guarantee all earlier intended writes exist unless you also validate authoritative replication positions and/or data invariants.
- **When heartbeat becomes “good enough”**
  - Heartbeat is stronger when it is written through the **same application/transaction path** as critical writes (not a separate background job), and when paired with:
    - **Authoritative replication markers** (LSN/WAL/optime equivalents) captured before/after failover, and/or
    - **Targeted integrity checks** (checksums, row counts, business invariants) for critical datasets.
- **How to report conclusions**
  - Prefer precise statements such as: “DR is caught up to heartbeat timestamp \(T\); potential loss window up to ~1 minute + replication delay,” rather than claiming “no data loss” solely from heartbeat.

### 4.3 Alerting & Notifications

- **FR-020 (RPO Violation Alert):** The system SHALL trigger an alert when observed indicators breach configured thresholds for a tiered duration.
- **FR-021 (Connectivity Alert):** The system SHALL alert on loss of connectivity/visibility to primary or DR.
- **FR-022 (Execution Notifications):** The system SHALL notify stakeholders on request created, approved, started, succeeded, failed, and rolled back.

### 4.4 Controlled Execution (Failover / Switchover / Drill)

- **FR-030 (Execution Request):** The system SHALL support creating an execution request specifying scope (resource/group), type (Failover/Switchover/Drill), target site, and change ticket reference (if required).
- **FR-031 (Approval Policy):** The system SHALL require approval(s) prior to executing any state-changing action and SHALL support configurable approval policies by tier/type (e.g., Tier 1 requires 2 approvals: IT Approver + Business/App Owner Approver).
- **FR-032 (Confirmation):** The system SHALL require an explicit confirmation (e.g., typed phrase) immediately prior to execution.
- **FR-033 (Prechecks):** The system SHALL run prechecks appropriate to platform and type (e.g., replication health, target readiness) and display results.
- **FR-034 (Execution Orchestration):** The system SHALL execute the defined procedure steps via connector-specific mechanisms (APIs/CLI) and report progress.
- **FR-035 (Idempotency/Resume):** The system SHOULD support safe retry/resume of interrupted executions, where technically feasible.
- **FR-036 (Postchecks):** The system SHALL run postchecks (health, connectivity) and present results before marking complete.
- **FR-037 (Integrity Checks / Data-Loss Determination):** The system SHOULD support optional integrity checks (e.g., row counts/checksums/business invariants) when applicable; where not feasible, it SHALL clearly indicate limitations.
  - Where platforms provide authoritative replication markers (e.g., LSN/WAL/optime equivalents), the system SHOULD capture and present those markers before/after execution as the primary evidence for completeness.
  - Where only heartbeat-style indicators exist, the system SHALL present conclusions conservatively (e.g., “caught up to heartbeat timestamp X; potential loss window up to Y”) and SHALL avoid claiming “no data loss” solely from heartbeat.
- **FR-038 (Failback):** The system SHALL support a controlled failback workflow with prechecks and approvals.

### 4.5 Audit & Reporting

- **FR-040 (Audit Log):** The system SHALL record all state-changing actions and approvals with actor, timestamp, request payload, and outcome.
- **FR-041 (Immutability):** The audit log SHOULD be stored in an append-only/immutability-supporting backend.
- **FR-042 (Export):** The system SHALL support exporting audit history as CSV and JSON.

### 4.6 Scheduling (No Unattended Execution)

- **FR-050 (Schedule Definition):** The system SHALL allow defining schedules for planned switchovers/drills.
- **FR-051 (Pre-Notification):** The system SHALL notify stakeholders before a scheduled event.
- **FR-052 (Approval Still Required):** A schedule SHALL NOT execute without an explicit approval at time-of-change (unless a documented break-glass policy permits it).

## 5. User Stories

### US-001: View System Health

> **As a** DBA or IT Manager,
> **I want** to see a traffic-light dashboard of all critical systems,
> **So that** I can instantly know if any system is at risk.

**Acceptance Criteria:**

- [ ] Dashboard displays list of all monitored systems.
- [ ] Status is color-coded: Green (Healthy), Yellow (Warning), Red (Failed/High Lag).
- [ ] UI displays last refresh timestamp and data freshness per system.
- [ ] Status updates automatically (e.g., every 30 seconds).

### US-002: Monitor RPO/Lag

> **As a** DBA,
> **I want** to see the detailed replication indicators for a specific database,
> **So that** I can ensure we are meeting our RPO targets.

**Acceptance Criteria:**

- [ ] Detail view shows configured RPO target and current indicator value(s) (e.g., lag in seconds/minutes where applicable).
- [ ] Historical graph of indicators over the last 24 hours.
- [ ] Alert triggered if breach exceeds defined threshold.

### US-003: Trigger Failover (Controlled)

> **As an** Operator,
> **I want** to request and execute a failover for a specific database group,
> **So that** I can move operations to the DR site during an outage.

**Acceptance Criteria:**

- [ ] Action button available based on RBAC.
- [ ] Execution requires approval before running.
- [ ] Confirmation modal requires explicit typed phrase.
- [ ] Audit log records who requested, who approved, and who executed.
- [ ] UI reflects in-progress status during execution.
- [ ] Postchecks displayed before marking complete.

### US-004: Receive DR Alerts

> **As an** IT Operator,
> **I want** to receive notification via PagerDuty/Email when a Tier 1 system exceeds thresholds,
> **So that** I can investigate immediately.

**Acceptance Criteria:**

- [ ] Integration with `gds_notification`.
- [ ] Alerts sent for RPO-indicator threshold breaches.
- [ ] Alerts sent for loss of connectivity/visibility.

### US-005: Audit Report

> **As an** Auditor,
> **I want** to view a history of all failover events and health checks,
> **So that** I can verify compliance with DR policies.

**Acceptance Criteria:**

- [ ] Read-only view of Audit Log.
- [ ] Filter by date range and system name.
- [ ] Export capability (CSV/JSON).

### US-006: Scheduled Switchover (Planned)

> **As an** IT Manager,
> **I want** to schedule a planned switchover for a group of databases,
> **So that** I can rotate active datacenters for testing/compliance without treating it as an emergency.

**Acceptance Criteria:**

- [ ] Option to tag execution as "Planned Rotation".
- [ ] Stakeholder pre-notification is sent.
- [ ] Approval is still required prior to execution.
- [ ] Validation of post-switchover health before completing.

### US-007: Failback to Primary

> **As an** Operator,
> **I want** to execute a failback from the DR site to the primary site,
> **So that** I can restore normal operations after an incident.

**Acceptance Criteria:**

- [ ] Failback option available only when prerequisites are met.
- [ ] Pre-failback health check of primary site required.
- [ ] Data synchronization status displayed before allowing failback.
- [ ] Audit log records failback event.

### US-008: Schedule DR Drills

> **As an** IT Manager,
> **I want** to schedule recurring DR drills,
> **So that** I can ensure the team is prepared and the system is validated regularly.

**Acceptance Criteria:**

- [ ] Calendar-based scheduling of drill events.
- [ ] Notification sent to stakeholders before scheduled drill.
- [ ] Drill execution requires explicit approval and is tagged as "Drill".
- [ ] Drill results are logged for compliance reporting.

## 6. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-001 | **Latency (UI)** | Dashboard P95 load time < 2 seconds under normal conditions. |
| NFR-002 | **Availability (Control Plane)** | Service availability 99.9% (excluding dependency outages). |
| NFR-003 | **Freshness** | Status data freshness < 1 minute (where dependencies permit). |
| NFR-004 | **Scalability** | Support up to 500 monitored resources. |
| NFR-005 | **Execution Overhead** | The service overhead to initiate an approved action SHOULD be < 2 minutes (excluding database/vendor operation time). |

## 7. Security Requirements

| ID | Requirement | Details |
|----|-------------|---------|
| SEC-001 | **Authentication** | All users authenticate via SSO with MFA. |
| SEC-002 | **Authorization (RBAC)** | Least-privilege roles; separation of duties (Operator vs Approver). |
| SEC-003 | **Audit Logging** | All approvals and state changes must be recorded with integrity protections. |
| SEC-004 | **Encryption (Transit)** | TLS for all data in transit; target TLS 1.3 where feasible. |
| SEC-005 | **Secrets Management** | Credentials/keys stored in approved secrets manager; never in config files. |
| SEC-006 | **Break-glass** | Emergency access path documented, time-bound, and fully audited. |

## 8. Constraints

1. **Network:** Deployment must have connectivity to both Primary and DR database networks.
2. **Dependencies:** Must use existing `gds_notification` package for outbound notifications.
3. **Technology:** Python (Backend) and React (Frontend).

## 9. External Interfaces

- **CMDB** (read-only): resource metadata ingestion/sync.
- **Identity Provider (SSO)**: authentication and group membership.
- **Notification**: `gds_notification` for PagerDuty/email/etc.
- **Supported database platforms**:
  - MongoDB (replica sets / clusters)
  - SQL Server (e.g., AlwaysOn AG where applicable)
  - PostgreSQL (streaming replication / managed equivalents)
  - Snowflake (where account replication/failover groups are configured)

## 10. Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| `gds_notification` | Platform Team | ✅ Available |
| DB Access Service Accounts | DBA Team | ⬜ Not Started |
| Hosting Environment (VM/K8s) | Ops Team | ⬜ Not Started |
| Identity Provider / SSO Groups | Security/IAM | ⬜ Not Started |
| CMDB Access | Platform Team | ⬜ Not Started |
| Secrets Manager Access | Security/Platform | ⬜ Not Started |

## 11. Open Questions

- What are the authoritative RPO/RTO targets per Tier and per application group (source of truth)?
- What is the required approval model (1 approver vs 2-person rule) for Tier 1 executions?
- What is the required retention period for audit logs and monitoring history?
- What is the change-management integration requirement (e.g., ServiceNow ticket mandatory for Tier 1)?
