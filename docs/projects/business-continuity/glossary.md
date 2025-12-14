# Glossary: Business Continuity (DR Readiness & Failover Management)

This glossary defines common terms used throughout these project documents.

## A

**ADR (Architecture Decision Record)**
A short record of a significant technical decision: the context, the decision, alternatives considered, and consequences. In this project, ADRs are kept in `management/decision-log.md` (e.g., `ADR-001`).

## B

**BC (Business Continuity)**
The organizational capability to continue critical business functions during and after a disruption. This project primarily focuses on the **technology DR** portion of BC.

## C

**CMDB (Configuration Management Database)**
A source of truth for infrastructure/application inventory and metadata (owners, tiers, environments). This project may read from a CMDB to populate resource inventory.

## D

**DR (Disaster Recovery)**
The processes and capabilities to restore technology services after an outage or disaster.

**Drill**
A planned exercise to validate DR readiness (people/process/technology) under controlled conditions.

## F

**Failover**
An unplanned or urgent move of production service from primary to DR (usually due to an outage).

**Failback**
Returning service from DR back to the primary site after an incident is resolved (typically controlled and planned).

## I

**ITSM (IT Service Management)**
Service management processes and tooling (e.g., incident/change/ticketing). Some organizations require an ITSM change ticket for production-impacting actions.

## K

**Kanban**
A workflow management method emphasizing continuous flow, work-in-progress (WIP) limits, and visualizing work on a board. Often used for operations/platform work.

## R

**RBAC (Role-Based Access Control)**
Authorization model where permissions are granted based on roles (e.g., Viewer, Operator, Approver, Admin).

**RPO (Recovery Point Objective)**
Maximum acceptable data loss measured in time (e.g., “up to 5 minutes of data loss”). RPO is a target/objective; signals like replication lag and heartbeats are used to evaluate whether RPO is being met.

**RTO (Recovery Time Objective)**
Maximum acceptable time to restore service after an outage (e.g., “service restored within 30 minutes”).

## S

**Scrum**
An agile delivery framework using timeboxed iterations (“sprints”), a prioritized backlog, and regular ceremonies (planning/review/retro). Often used for feature delivery with a predictable cadence.

**SSO (Single Sign-On)**
Authentication method where users sign in via a central identity provider.

**Switchover**
A planned, controlled move of service from primary to DR (or between sites) for testing, maintenance, or rotations.

## T

**Tier 1 / Tier 2**
Criticality labels used to prioritize monitoring/alerting and enforce stricter approval and change controls for the most critical systems (Tier 1).
