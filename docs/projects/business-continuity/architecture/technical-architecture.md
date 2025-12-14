# Technical Architecture: Business Continuity (DR Readiness & Failover Management)

## 1. Overview

This document describes the high-level architecture for the Business Continuity service, a DR readiness monitoring system with **approval-gated failover (emergency) and switchover (planned) workflows**.

The architecture is designed to:

- Provide a **single control plane** for visibility across heterogeneous database platforms
- Minimize blast radius by separating **read-only monitoring** from **state-changing execution**
- Enforce **RBAC + separation of duties** for high-risk actions (Operator vs Approver(s))
- Produce **auditable evidence** for DR readiness and exercise outcomes

Primary reference for requirements: `../specs/functional-spec.md`.

## 2. Architecture Diagram

```mermaid
graph TB
    subgraph External["External Systems"]
        CMDB["CMDB (read-only)"]
        IDP["Identity Provider (SSO + MFA)"]
        NOTIF["gds_notification (PagerDuty, email, etc.)"]
        SECRETS["Secrets Manager (Vault/approved store)"]
        ITSM["ITSM / Change Tickets (optional)"]
    end

    subgraph Core["Business Continuity Service"]
        UI["Web UI (React)"]
        API["Backend API (Python)"]
        WORKER["Worker / Scheduler (jobs + executions)"]
        RULES["Status Rules Engine (Green/Yellow/Red)"]
        CONNECT["Connector Framework (Mongo, SQL, Postgres, Snowflake)"]
        STORE["Config and State Store"]
        AUDIT["Append-only Audit Log"]
        METRICS["Time-series History Store"]
    end

    subgraph Targets["Monitored and Controlled Targets"]
        MONGO["MongoDB (replica sets/clusters)"]
        MSSQL["SQL Server (e.g., AlwaysOn AG)"]
        PG["PostgreSQL (streaming/managed)"]
        SNOW["Snowflake (replication/failover groups)"]
    end

    IDP --> UI
    UI --> API

    CMDB --> API
    ITSM --> API

    API --> STORE
    STORE --> API
    API --> AUDIT
    API --> RULES

    WORKER --> STORE
    STORE --> WORKER
    WORKER --> AUDIT
    WORKER --> CONNECT

    CONNECT --> MONGO
    CONNECT --> MSSQL
    CONNECT --> PG
    CONNECT --> SNOW

    RULES --> NOTIF
    WORKER --> NOTIF

    SECRETS --> API
    SECRETS --> WORKER

    WORKER --> METRICS
    API --> METRICS
```

## 3. Component Descriptions

### Web UI

- **Purpose:** Operator and approver interface for monitoring dashboards, requests/approvals, and execution status.
- **Technology:** React (per functional spec constraints).
- **Interfaces:** HTTPS to Backend API; SSO redirect to Identity Provider.

### Backend API

- **Purpose:** Control plane for configuration, inventory, dashboards, approvals, audit access, and data exports.
- **Technology:** Python (per functional spec constraints).
- **Interfaces:**
  - REST/JSON (or equivalent) to UI
  - CMDB read-only integration
  - Identity provider integration (SSO + group claims)
  - Notification integration via `gds_notification`

### Worker / Scheduler

- **Purpose:**
  - Periodic monitoring collection jobs (health + replication indicators + optional heartbeat)
  - Execution orchestration (failover/switchover/failback) with prechecks/postchecks
  - Schedule handling (scheduling can create requests, but execution remains approval-gated)
- **Technology:** Python job runner (exact framework TBD in `software-stack.md` / ADRs).
- **Interfaces:** Uses Connector Framework; writes to Stores; emits notifications.

### Connector Framework

- **Purpose:** A consistent abstraction for interacting with heterogeneous systems.
- **Responsibilities:**
  - Collect indicators (health, replication position/lag, freshness)
  - Run prechecks/postchecks
  - Execute platform-specific procedures via APIs/CLIs (where supported)
  - Provide clear “not supported / monitor-only” behavior when capabilities differ by platform
- **Supported connectors (initial):** MongoDB, SQL Server, PostgreSQL, Snowflake.

### Status Rules Engine

- **Purpose:** Evaluate status per resource/group (Green/Yellow/Red) based on thresholds and rules.
- **Inputs:** Observations + configured RPO thresholds, freshness requirements, connectivity state.
- **Outputs:** Current status + reason codes suitable for UI and alerting.

### Config + State Store

- **Purpose:** Persistent configuration and current state.
- **Examples of stored entities:**
  - Resources and dependency groups (Tier, owners, environments)
  - RPO targets and alert thresholds
  - Approval policy by tier/type
  - Execution requests and state machine status
- **Implementation:** Database-backed store (technology choice documented in `software-stack.md`).

### Audit Log (Append-only)

- **Purpose:** Tamper-evident record of high-impact events for compliance evidence:
  - request created
  - approvals/denials
  - execution started/completed/failed
  - break-glass invocation
  - configuration changes
- **Implementation requirement:** Append-only or immutability-supporting backend (exact approach captured in ADRs).

### Time-series History Store

- **Purpose:** Retain short-horizon history (e.g., 24h+) of key indicators for trends and evidence.
- **Examples:** replication lag over time, freshness, heartbeat timestamps, rule outcomes.

## 4. Data Flow

### 4.1 Monitoring Collection (read-only)

```mermaid
sequenceDiagram
    participant W as Worker/Scheduler
    participant C as Connector
    participant D as Database Target
    participant S as State Store
    participant M as Metrics Store
    participant R as Rules Engine
    participant N as Notification

    W->>C: Run health/replication indicator collection
    C->>D: Query status/replication markers (read-only)
    D-->>C: Observations (timestamped)
    C-->>W: Observations
    W->>S: Persist latest observation + freshness
    W->>M: Append time-series datapoints
    W->>R: Evaluate thresholds/status rules
    R-->>W: Status (Green/Yellow/Red) + reasons
    W->>S: Persist status outcome
    alt breach detected
        R->>N: Send alert via gds_notification
    end
```

### 4.2 Controlled Failover / Switchover (approval-gated)

```mermaid
sequenceDiagram
    participant U as Operator
    participant A as Approvers
    participant UI as Web UI
    participant API as Backend API
    participant W as Worker
    participant C as Connector
    participant T as Target Platform
    participant AUD as Audit Log
    participant N as Notification

    U->>UI: Create execution request (type, scope, target site)
    UI->>API: POST /requests
    API->>AUD: Append request created
    API-->>UI: Request pending approval

    A->>UI: Approve request(s)
    UI->>API: POST /requests/{id}/approve
    API->>AUD: Append approvals
    API->>N: Notify request approved

    U->>UI: Confirm + start execution
    UI->>API: POST /requests/{id}/start (with confirmation)
    API->>AUD: Append execution start
    API->>W: Enqueue execution job
    API->>N: Notify execution started

    W->>C: Prechecks
    C->>T: Validate readiness (read-only)
    T-->>C: Precheck results
    W->>AUD: Append precheck results

    W->>C: Execute procedure steps
    C->>T: Execute platform-specific actions
    T-->>C: Step outcomes
    W->>AUD: Append step outcomes
    W->>N: Notify progress / completion / failure

    W->>C: Postchecks (health + markers)
    C->>T: Validate post state
    T-->>C: Postcheck results
    W->>AUD: Append postcheck results
```

## 5. Security Architecture

- **Authentication:** SSO with MFA (via Identity Provider).
- **Authorization:** RBAC with separation of duties:
  - Viewer (read-only)
  - Operator (request + run prechecks; initiate start with confirmation)
  - Approver(s) (IT and Business/App Owner, configurable by tier/type)
  - Admin (configuration)
- **Approval policy:** Tier 1 may require multi-approval (two-person rule).
- **Encryption:** TLS in transit (target TLS 1.3 where feasible); at-rest encryption per chosen data store defaults/controls.
- **Secrets management:** All credentials/keys via approved secrets manager; no secrets in config files or source control.
- **Audit logging:** Append-only audit log for approvals and executions; include actor identity, timestamps, request payload, outcome, and reason codes.
- **Break-glass:** Emergency access is time-bound, policy-driven, and fully audited (who/why/when).

## 6. High Availability

- **Redundancy:** Deploy the control plane (API + worker + stores) in a highly available configuration appropriate to the hosting environment (VM/K8s).
- **Degraded mode:** If targets are unreachable (e.g., during incident), the UI/API must clearly indicate **loss of visibility** and show the last known good data with timestamps.
- **Failover (of the tool):** The service should be deployable in a way that remains reachable during primary-site outages (design captured in `software-stack.md` and ADRs).
- **Recovery:** The service’s own RTO/RPO targets should be defined (ideally at least as resilient as Tier 1 monitoring needs).

## 7. Open Decisions (to capture as ADRs)

- Choice of persistence layer(s) for state, time-series history, and append-only audit.
- Job runner/execution framework and deployment model.
- Connector capability matrix per platform (monitor-only vs executable actions).
- Required change-management integration (ticket mandatory for Tier 1?).
