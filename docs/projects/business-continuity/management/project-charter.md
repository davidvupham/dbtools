# Project Charter: Business Continuity (DR Readiness & Failover Management)

## Document Control

- **Version:** 0.2
- **Owner:** TBD
- **Last Updated:** 2025-12-13

## Project Overview

- **Name:** Business Continuity (DR Readiness & Failover Management)
- **Sponsor:** TBD
- **Product Owner:** TBD
- **Technical Lead:** TBD
- **Project Manager:** TBD (or Technical Lead acting as PM)
- **Goal:** Improve technology disaster recovery (DR) readiness by providing centralized monitoring, audit evidence, and controlled workflows to execute failovers/switchovers for supported platforms.

> Note: This project primarily addresses the **technology DR** portion of Business Continuity (BC). Broader BC (people/process, facilities, crisis comms) is out of scope unless explicitly added.

## Business Case

- **Problem/Opportunity:**
  - **Lack of Visibility:** IT teams lack a centralized, near real-time view of DR readiness (health, replication indicators, data freshness) across heterogeneous systems (MongoDB, SQL Server, Postgres, Snowflake), relying on manual checks or disparate tools.
  - **Inconsistent Execution:** Failover/switchover procedures vary by platform and are often manual, increasing risk of human error during high-stress incidents.
  - **Compliance Evidence Gap:** Difficulty proving DR readiness (ongoing monitoring + exercise outcomes) to auditors without consolidated records.
- **Benefits:** Reduced operational risk, faster decision-making during incidents, improved adherence to RPO targets, and improved auditability via continuous monitoring and logged DR exercises.

## Measurable Objectives & Success Criteria

- **Coverage:** 100% of Tier 1 database resources onboarded with monitoring and alerting.
- **Readiness Visibility:** Single dashboard showing current status + last refresh time for all Tier 1 resources.
- **Alerting:** RPO-indicator threshold alerts integrated with `gds_notification` for Tier 1.
- **Controlled Execution:** Documented and audited workflow for failover/switchover requests, approvals, and execution.
- **Exercises:** At least one successful DR drill (or planned switchover) per Tier 1 group, with exported evidence.

## High-Level Requirements

- Centralized inventory of resources and dependency groups (Tier 1 / Tier 2).
- Near real-time monitoring via platform connectors.
- Threshold-based status evaluation and alerting.
- RBAC with separation of duties (Operator vs Approver) and immutable audit logging.
- Support planned switchovers/drills without unattended automatic execution.

## Scope

### In Scope

- Monitoring DR readiness for MongoDB, SQL Server, PostgreSQL, and Snowflake.
- Responsive web application for dashboards and controlled actions.
- Backend API and frontend UI.
- Controlled failover/switchover workflows (request → approve → execute → verify).
- Extensible architecture to support future platforms and business applications.
- **Data Sources:** Integration with CMDB (read-only) and platform/system views/APIs for health indicators.
- **Tiering:** Tier 1 vs Tier 2 with differentiated alerting and controls.
- **Notification:** Alert stakeholders of readiness issues and execution events.

### Out of Scope

- Unattended automatic failover without human approval.
- Creating/operating vendor replication strategies (the service observes and orchestrates; it does not replace vendor-native DR features).
- Native mobile apps (responsive web only).

## Key Deliverables

- Monitoring dashboard with tiered readiness status.
- Connector implementations for initial supported platforms.
- Alerting integration via `gds_notification`.
- Controlled execution workflow (failover/switchover/failback) with audit evidence.
- Runbook alignment and test artifacts (links to existing docs).

## Timeline & Milestones (MVP-first)

Assuming **1 developer**, delivery should be phased to reduce risk:

- **Phase 1 (MVP Monitoring):** Inventory + monitoring + dashboard for 1–2 platforms; tiered alerting.
- **Phase 2 (Broaden Monitoring):** Remaining platforms; history/trends; audit exports.
- **Phase 3 (Controlled Execution):** Approval-gated workflows; prechecks/postchecks; initial platform execution support.
- **Phase 4 (Exercises & Release):** Drill/switchover execution, evidence export, operational hardening.

(See `project-plan.md` for detailed scheduling.)

## Governance & Delivery Model

- **Model:** Agile / Kanban
- **Cadence:** Weekly stakeholder sync; ad-hoc working sessions as needed
- **Approvals/Gates:** Code review, security review for execution paths, UAT, release readiness checklist
- **Decision Records:** Logged in `decision-log.md`

## Stakeholders

- IT Ops / SRE
- DBAs (MongoDB, SQL Server, PostgreSQL)
- Security / IAM
- Compliance / Audit
- Application owners for Tier 1 systems

## Risks, Assumptions, and Mitigations

### Top Risks

- **Platform execution complexity:** Different failover mechanisms per platform.
  - *Mitigation:* Phase execution capability; start with monitoring and one platform.
- **Control plane dependency:** The monitoring/orchestration service may be impacted during disasters.
  - *Mitigation:* Deploy with DR-aware architecture and document degraded-mode operation.
- **Data integrity risk:** Failover when replication is behind can cause data loss.
  - *Mitigation:* Require prechecks, explicit approvals, and clear indicator visibility; document limitations.
- **Security risk:** A web UI that can trigger failover is a high-impact control surface.
  - *Mitigation:* RBAC + separation of duties + MFA + immutable audit logs + break-glass process.

### Assumptions

- Required access to platform APIs/CLIs can be provisioned (least privilege).
- Replication/DR primitives already exist (the tool does not create them).
- Stakeholders will participate in drills/UAT.

## Budget & Resources

- **People:** 1 developer (initial); plus part-time support from DBAs/Ops/Security for access, review, and drills.
- **Infra/Tools:** Existing hosting infrastructure; existing notification tooling.

## Communications

- **Channels:** Email/Slack; incident bridge (as applicable)
- **Escalation Matrix:**

| Level | Role | Contact Method | SLA |
|-------|------|----------------|-----|
| L1 | On-Call DBA | PagerDuty/Slack | 5 min |
| L2 | DBA Team Lead | Phone/Slack | 15 min |
| L3 | IT Manager | Phone/Email | 30 min |
| L4 | VP of IT | Phone | 1 hr |

## Project Approval Requirements & Exit Criteria

- **Approval requirements:** Sponsor sign-off on charter; security sign-off on execution controls; UAT sign-off for Tier 1 readiness dashboards.
- **Exit criteria (MVP):** Tier 1 inventory onboarded, monitoring + alerting operational, audit export available, at least one drill executed with evidence.

## References

- [Functional Spec](../specs/functional-spec.md)
- [Technical Architecture](../architecture/technical-architecture.md)
- [Project Plan](project-plan.md)

## Authorization

| Name | Role | Signature | Date |
|------|------|-----------|------|
| TBD | Stakeholder | | |
| TBD | Project Sponsor | | |
