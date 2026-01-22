# Database Restore Self-Service Workflow
## High-Level Design Document

| Document Info | |
|---------------|---|
| **Version** | 1.0 |
| **Status** | Draft - Pending Review |
| **Author** | Infrastructure Team |
| **Date** | 2026-01-22 |
| **Reviewers** | |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Proposed Solution](#3-proposed-solution)
4. [Workflow Diagrams](#4-workflow-diagrams)
5. [Architecture Overview](#5-architecture-overview)
6. [Key Design Decisions](#6-key-design-decisions)
7. [Security & Compliance](#7-security--compliance)
8. [Notification Strategy](#8-notification-strategy)
9. [Handling Long-Running Restores](#9-handling-long-running-restores)
10. [Infrastructure Requirements](#10-infrastructure-requirements)
11. [Team Onboarding Model](#11-team-onboarding-model)
12. [Risks & Mitigations](#12-risks--mitigations)
13. [Implementation Phases](#13-implementation-phases)
14. [Success Criteria](#14-success-criteria)
15. [Open Questions](#15-open-questions)
16. [Appendix](#appendix)

---

## 1. Executive Summary

This document proposes a self-service database restore workflow using GitHub Actions that enables development teams to request and receive copies of production databases in development environments. The solution provides:

- **Self-service requests** - Developers submit restore requests through GitHub
- **Team-based approvals** - Only designated database owners can approve their team's requests
- **Automated execution** - Approved restores run automatically with full audit trail
- **Notifications** - Microsoft Teams and/or email notifications at each stage

The solution uses a **single shared repository** with environment-based access controls, eliminating the need for separate repositories per team while maintaining proper isolation and approval chains.

---

## 2. Problem Statement

### Current State

| Challenge | Impact |
|-----------|--------|
| Database restore requests go through manual ticketing | Delays of hours to days |
| DBAs manually execute restores | Resource bottleneck, human error risk |
| No standardized approval process | Inconsistent governance |
| Limited visibility into request status | Developers left waiting without updates |
| Post-restore scripts run inconsistently | Data masking sometimes missed |

### Desired State

| Capability | Benefit |
|------------|---------|
| Self-service request submission | Immediate request creation |
| Automated team-based approval routing | Right people approve, no DBA bottleneck |
| Automated execution upon approval | Consistent, reliable restores |
| Real-time status notifications | Teams stay informed |
| Mandatory post-restore scripts | Consistent data masking/sanitization |
| Complete audit trail | Compliance and troubleshooting |

---

## 3. Proposed Solution

### 3.1 Solution Overview

Use **GitHub Actions** as the workflow orchestration platform with the following components:

| Component | Purpose |
|-----------|---------|
| **GitHub Workflow** | Orchestrates the entire process |
| **GitHub Environments** | Provides team-specific approval gates |
| **GitHub Teams** | Maps to database ownership groups |
| **Self-Hosted Runners** | Execute restores on-premises with network access |
| **Existing Restore Process** | Runners invoke current restore procedures |
| **MS Teams Webhooks** | Deliver notifications to team channels |

### 3.2 Request Parameters

Each restore request will capture:

| Parameter | Description | Example |
|-----------|-------------|---------|
| Team | Requesting team (determines approvers) | team-alpha |
| Database Name | Database to restore | CustomerDB |
| Source Server | Production SQL Server | prod-sql01 |
| Destination Server | Development SQL Server | dev-sql01 |
| Point-in-Time | Recovery point (or latest) | 2026-01-22T14:30:00 |
| Scheduled Start | When to begin restore | now / 2026-01-22T22:00:00 |
| Justification | Business reason for request | Testing release 2.5 |

---

## 4. Workflow Diagrams

### 4.1 End-to-End Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE RESTORE WORKFLOW                                      │
└─────────────────────────────────────────────────────────────────────────────────────────┘

     DEVELOPER                    TEAM OWNER                     SYSTEM
         │                            │                             │
         │  1. Submit Request         │                             │
         │  (via GitHub Actions)      │                             │
         ├───────────────────────────────────────────────────────────►
         │                            │                             │
         │                            │      2. Validate Request    │
         │                            │◄────────────────────────────┤
         │                            │                             │
         │                            │      3. Send Notification   │
         │◄───────────────────────────┼─────────────────────────────┤
         │  "Request pending          │      (to team channel)      │
         │   approval"                │                             │
         │                            │                             │
         │                            │  4. Review & Approve        │
         │                            ├─────────────────────────────►
         │                            │  (in GitHub UI)             │
         │                            │                             │
         │                            │      5. Send Approval       │
         │◄───────────────────────────┼─────────────────────────────┤
         │  "Request approved"        │      Notification           │
         │                            │                             │
         │                            │      6. Wait for Schedule   │
         │                            │      (if scheduled)         │
         │                            │◄────────────────────────────┤
         │                            │                             │
         │                            │      7. Execute Restore     │
         │◄───────────────────────────┼─────────────────────────────┤
         │  "Restore started"         │      (self-hosted runner)   │
         │                            │                             │
         │                            │      8. Monitor Progress    │
         │                            │◄────────────────────────────┤
         │                            │                             │
         │                            │      9. Run Post-Restore    │
         │                            │         Scripts             │
         │                            │◄────────────────────────────┤
         │                            │                             │
         │                            │     10. Send Completion     │
         │◄───────────────────────────┼─────────────────────────────┤
         │  "Restore complete"        │         Notification        │
         │                            │                             │
         ▼                            ▼                             ▼
```

### 4.2 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    GITHUB.COM                                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│   │                         DATABASE-RESTORE REPOSITORY                               │  │
│   ├──────────────────────────────────────────────────────────────────────────────────┤  │
│   │                                                                                   │  │
│   │   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │  │
│   │   │   ENVIRONMENT   │    │   ENVIRONMENT   │    │   ENVIRONMENT   │             │  │
│   │   │  team-alpha-    │    │  team-beta-     │    │  team-gamma-    │             │  │
│   │   │    restore      │    │    restore      │    │    restore      │             │  │
│   │   ├─────────────────┤    ├─────────────────┤    ├─────────────────┤             │  │
│   │   │ Reviewers:      │    │ Reviewers:      │    │ Reviewers:      │             │  │
│   │   │ team-alpha-     │    │ team-beta-      │    │ team-gamma-     │             │  │
│   │   │ db-owners       │    │ db-owners       │    │ db-owners       │             │  │
│   │   └─────────────────┘    └─────────────────┘    └─────────────────┘             │  │
│   │                                                                                   │  │
│   │   ┌─────────────────────────────────────────────────────────────────────────┐   │  │
│   │   │                        GITHUB ACTIONS WORKFLOW                           │   │  │
│   │   │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌───────────────────────┐ │   │  │
│   │   │  │ Validate │──▶│ Approval │──▶│ Schedule │──▶│ Execute on Runner     │ │   │  │
│   │   │  │ Request  │   │   Gate   │   │   Wait   │   │ (Start Restore)       │ │   │  │
│   │   │  └──────────┘   └──────────┘   └──────────┘   └───────────────────────┘ │   │  │
│   │   └─────────────────────────────────────────────────────────────────────────┘   │  │
│   │                                                                                   │  │
│   └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                          │
└───────────────────────────────────────┬──────────────────────────────────────────────────┘
                                        │
                                        │ HTTPS (outbound from runner)
                                        │
┌───────────────────────────────────────▼──────────────────────────────────────────────────┐
│                              ON-PREMISES / CORPORATE NETWORK                              │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│   │                         SELF-HOSTED RUNNERS (Windows)                            │    │
│   │                                                                                  │    │
│   │   ┌────────────────┐    ┌────────────────┐    ┌────────────────┐               │    │
│   │   │   Runner 01    │    │   Runner 02    │    │   Runner 03    │               │    │
│   │   │ (sql-restore)  │    │ (sql-restore)  │    │ (sql-restore)  │               │    │
│   │   └───────┬────────┘    └───────┬────────┘    └───────┬────────┘               │    │
│   │           │                     │                     │                         │    │
│   └───────────┼─────────────────────┼─────────────────────┼─────────────────────────┘    │
│               │                     │                     │                              │
│               └─────────────────────┼─────────────────────┘                              │
│                                     │                                                    │
│                    ┌────────────────┴────────────────┐                                   │
│                    │     EXISTING RESTORE PROCESS     │                                   │
│                    │   (PowerShell/SQL Agent/etc.)    │                                   │
│                    └────────────────┬────────────────┘                                   │
│                                     │                                                    │
│         ┌───────────────────────────┼───────────────────────────┐                        │
│         │                           │                           │                        │
│         ▼                           ▼                           ▼                        │
│   ┌───────────┐             ┌─────────────┐             ┌─────────────┐                  │
│   │ PROD SQL  │             │   DEV SQL   │             │  BACKUP     │                  │
│   │ SERVERS   │             │   SERVERS   │             │  STORAGE    │                  │
│   │           │             │             │             │  (Network   │                  │
│   │ prod-sql01│             │ dev-sql01   │             │   Share)    │                  │
│   │ prod-sql02│             │ dev-sql02   │             │             │                  │
│   └───────────┘             │ test-sql01  │             └─────────────┘                  │
│                             └─────────────┘                                              │
│                                                                                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Approval Flow Detail

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              APPROVAL ROUTING LOGIC                                      │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                              Developer Submits Request
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │   Developer selects "Team"    │
                        │   in request form             │
                        └───────────────┬───────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
            ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
            │  team-alpha   │   │  team-beta    │   │  team-gamma   │
            └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
                    │                   │                   │
                    ▼                   ▼                   ▼
            ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
            │  Environment: │   │  Environment: │   │  Environment: │
            │  team-alpha-  │   │  team-beta-   │   │  team-gamma-  │
            │  restore      │   │  restore      │   │  restore      │
            └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
                    │                   │                   │
                    ▼                   ▼                   ▼
            ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
            │  Required     │   │  Required     │   │  Required     │
            │  Reviewers:   │   │  Reviewers:   │   │  Reviewers:   │
            │               │   │               │   │               │
            │ team-alpha-   │   │ team-beta-    │   │ team-gamma-   │
            │ db-owners     │   │ db-owners     │   │ db-owners     │
            │               │   │               │   │               │
            │ (GitHub Team) │   │ (GitHub Team) │   │ (GitHub Team) │
            └───────────────┘   └───────────────┘   └───────────────┘

                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │  Only members of the team's   │
                        │  db-owners group can approve  │
                        │  that team's restore requests │
                        └───────────────────────────────┘
```

### 4.4 Long-Running Restore Pattern (>6 hours)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    ASYNC RESTORE PATTERN FOR LARGE DATABASES                             │
└─────────────────────────────────────────────────────────────────────────────────────────┘

TIME ──────────────────────────────────────────────────────────────────────────────────────►

     T+0                T+5min            T+10min           T+6hrs            T+6hrs+5min
      │                   │                  │                 │                   │
      ▼                   ▼                  ▼                 ▼                   ▼

┌──────────┐        ┌──────────┐       ┌──────────┐                          ┌──────────┐
│ WORKFLOW │        │ MONITOR  │       │ MONITOR  │         ...              │ MONITOR  │
│    1     │        │ WORKFLOW │       │ WORKFLOW │                          │ WORKFLOW │
│          │        │ (cron)   │       │ (cron)   │                          │ (cron)   │
│ Start    │        │          │       │          │                          │          │
│ Restore  │        │ Check    │       │ Check    │                          │ Check    │
│ (async)  │        │ Status   │       │ Status   │                          │ Status   │
│          │        │          │       │          │                          │          │
│ Save     │        │ Still    │       │ Still    │                          │ COMPLETE!│
│ Tracking │        │ Running  │       │ Running  │                          │          │
│ Info     │        │ (42%)    │       │ (58%)    │                          │ Run Post │
│          │        │          │       │          │                          │ Scripts  │
│ Exit     │        │ Exit     │       │ Exit     │                          │          │
│          │        │          │       │          │                          │ Notify   │
└──────────┘        └──────────┘       └──────────┘                          └──────────┘
      │                   │                  │                                     │
      │                   │                  │                                     │
      ▼                   ▼                  ▼                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                           │
│   ██████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│   ▲                 ▲                    ▲                                          ▲    │
│   │                 │                    │                                          │    │
│   Start           42%                  58%                                       100%    │
│                                                                                          │
│                            SQL SERVER RESTORE OPERATION                                  │
│                            (Running independently)                                       │
│                                                                                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘


TRACKING FILE (stored in repo or artifact storage):
┌────────────────────────────────────────┐
│  {                                     │
│    "run_id": "12345",                  │
│    "database": "LargeDB",              │
│    "destination": "dev-sql01",         │
│    "team": "team-alpha",               │
│    "requestor": "jsmith",              │
│    "start_time": "2026-01-22T10:00:00",│
│    "status": "RUNNING"                 │
│  }                                     │
└────────────────────────────────────────┘
```

---

## 5. Architecture Overview

### 5.1 Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **GitHub Repository** | Stores workflow definitions, configuration, tracking files |
| **GitHub Environments** | Enforces team-specific approval requirements |
| **GitHub Teams** | Defines who can approve each team's requests |
| **GitHub Actions Workflow** | Orchestrates validation, approval, execution |
| **Self-Hosted Runners** | Execute restore commands within corporate network |
| **Existing Restore Process** | Actual database restore logic (unchanged) |
| **MS Teams Webhooks** | Receive and display notifications |
| **SQL Server DMVs** | Provide restore progress information |

### 5.2 Data Flow

```
1. Request Submission
   Developer → GitHub UI → Workflow Triggered → Validation → Notification Sent

2. Approval
   Team Owner → GitHub UI → Environment Approval → Notification Sent

3. Execution
   Workflow → Self-Hosted Runner → Existing Restore Process → SQL Server

4. Monitoring (for long restores)
   Scheduled Workflow → Query SQL Server DMVs → Check Status → Update Tracking

5. Completion
   Restore Finishes → Post-Restore Scripts → Notification Sent → Tracking Updated
```

---

## 6. Key Design Decisions

### 6.1 Single Repository vs Multiple Repositories

| Decision | **Single Repository** (Recommended) |
|----------|-------------------------------------|
| **Rationale** | Easier maintenance, consistent workflows, centralized audit |
| **How it works** | GitHub Environments provide team isolation within one repo |
| **Trade-off** | Slightly more complex initial setup, but better long-term |

**Alternative considered:** One repo per team
- Rejected because: Maintenance burden, configuration drift, harder to audit

### 6.2 Approval Mechanism

| Decision | **GitHub Environment Protection Rules** |
|----------|----------------------------------------|
| **Rationale** | Native GitHub feature, no custom code needed |
| **How it works** | Each environment requires approval from designated team |
| **Trade-off** | Approval UI is in GitHub, not in Teams/email |

### 6.3 Runner Architecture

| Decision | **Dedicated Self-Hosted Runners** |
|----------|-----------------------------------|
| **Rationale** | Guaranteed availability, network access to SQL Servers |
| **How it works** | Windows runners with `sql-restore` label |
| **Trade-off** | Additional infrastructure to maintain |

### 6.4 Long-Running Restore Handling

| Decision | **Async Start + Polling Monitor** |
|----------|-----------------------------------|
| **Rationale** | GitHub Actions has 6-hour job limit |
| **How it works** | Start restore async, separate workflow polls every 5 min |
| **Trade-off** | Slightly more complex, but handles any restore duration |

---

## 7. Security & Compliance

### 7.1 Access Control Model

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ACCESS CONTROL MATRIX                                       │
├──────────────────────┬────────────────┬────────────────┬────────────────────────────────┤
│       Role           │  Can Request   │  Can Approve   │  Can View Logs                 │
├──────────────────────┼────────────────┼────────────────┼────────────────────────────────┤
│ Team Developer       │ Own team's DBs │      No        │ Own team's workflow runs       │
├──────────────────────┼────────────────┼────────────────┼────────────────────────────────┤
│ Team DB Owner        │ Own team's DBs │ Own team's DBs │ Own team's workflow runs       │
├──────────────────────┼────────────────┼────────────────┼────────────────────────────────┤
│ DBA Admin            │    Any DB      │    Any DB      │ All workflow runs              │
├──────────────────────┼────────────────┼────────────────┼────────────────────────────────┤
│ Repository Admin     │    Any DB      │    Any DB      │ All workflow runs              │
└──────────────────────┴────────────────┴────────────────┴────────────────────────────────┘
```

### 7.2 Security Controls

| Control | Implementation |
|---------|----------------|
| **Authentication** | GitHub SSO (existing) |
| **Authorization** | GitHub Teams + Environment protection rules |
| **Credential Storage** | GitHub Secrets (encrypted at rest) |
| **Network Security** | Runners on internal network, no public SQL exposure |
| **Audit Trail** | GitHub workflow run logs (retained per policy) |
| **Data Protection** | Mandatory post-restore scripts for PII masking |

### 7.3 Compliance Considerations

| Requirement | How Addressed |
|-------------|---------------|
| Separation of duties | Requestor cannot approve own request |
| Audit logging | All actions logged in GitHub with timestamps |
| Data masking | Post-restore scripts sanitize PII before dev access |
| Access reviews | GitHub Team membership reviewed quarterly |

---

## 8. Notification Strategy

### 8.1 Notification Points

| Event | Channel | Recipients |
|-------|---------|------------|
| Request Submitted | MS Teams | Team channel |
| Pending Approval | MS Teams | Team channel (with approve link) |
| Request Approved | MS Teams | Team channel + requestor |
| Restore Started | MS Teams | Team channel + requestor |
| Restore Completed | MS Teams + Email | Team channel + requestor |
| Restore Failed | MS Teams + Email | Team channel + requestor + DBA |

### 8.2 Notification Content

**Request Submitted:**
```
Database Restore Request #12345
─────────────────────────────────
Database:     CustomerDB
Source:       prod-sql01
Destination:  dev-sql01
Requestor:    jsmith
Team:         team-alpha
Point-in-Time: latest

Awaiting approval from team-alpha-db-owners
[View & Approve Request]
```

**Restore Completed:**
```
Database Restore COMPLETED
─────────────────────────────────
Database:     CustomerDB
Destination:  dev-sql01
Duration:     2h 34m
Requestor:    jsmith

Post-restore scripts executed successfully.
Database is ready for use.
```

---

## 9. Handling Long-Running Restores

### 9.1 Problem
GitHub Actions jobs have a maximum runtime of 6 hours. Large database restores may exceed this limit.

### 9.2 Solution
Use an asynchronous pattern with status polling:

| Phase | Description |
|-------|-------------|
| **1. Start** | Workflow initiates restore process (fire-and-forget) |
| **2. Track** | Save restore metadata to tracking file |
| **3. Exit** | Workflow completes, runner freed |
| **4. Poll** | Separate scheduled workflow checks status every 5 minutes |
| **5. Complete** | When done, run post-restore scripts and notify |

### 9.3 Status Monitoring
SQL Server provides restore progress via Dynamic Management Views (DMVs):
- `sys.dm_exec_requests` shows active restores
- Returns: percent complete, estimated completion time
- **Note:** Final recovery phase may show 100% but still be running

### 9.4 Limitations
- Polling interval of 5 minutes means up to 5-minute delay in completion notification
- Very long restores (multi-day) will accumulate many polling runs in workflow history

---

## 10. Infrastructure Requirements

### 10.1 Self-Hosted Runners

| Requirement | Specification |
|-------------|---------------|
| **Quantity** | Minimum 2, recommended 3-4 |
| **OS** | Windows Server 2019 or later |
| **Sizing** | 4 CPU, 8 GB RAM (runner overhead is minimal) |
| **Network** | Access to SQL Servers, backup storage, GitHub.com |
| **Software** | PowerShell 7+, SqlServer module |
| **Labels** | `self-hosted`, `sql-restore`, `windows` |

### 10.2 Runner Concurrency

**Each runner processes one job at a time.**

| Scenario | Runners Needed |
|----------|----------------|
| 1 concurrent restore | 1 runner (no redundancy) |
| 1 concurrent + 1 queued | 2 runners |
| 2 concurrent + buffer | 3-4 runners |
| High volume (5+ teams) | 5+ runners |

### 10.3 Network Requirements

| Source | Destination | Port | Purpose |
|--------|-------------|------|---------|
| Runner | github.com | 443 | GitHub API, workflow execution |
| Runner | SQL Servers | 1433 | Restore commands, status queries |
| Runner | Backup Storage | 445 | Access backup files |
| Runner | MS Teams | 443 | Webhook notifications |

### 10.4 GitHub Configuration

| Item | Quantity |
|------|----------|
| GitHub Environments | 1 per team |
| GitHub Teams | 1 per team (db-owners) |
| Repository Secrets | 3-5 (SQL credentials, webhook URLs) |
| Repository Variables | 2-3 (server lists, paths) |

---

## 11. Team Onboarding Model

### 11.1 Per-Team Setup

When onboarding a new team:

| Step | Action | Owner |
|------|--------|-------|
| 1 | Create GitHub Team: `{team}-db-owners` | GitHub Admin |
| 2 | Add team members to GitHub Team | Team Lead |
| 3 | Create GitHub Environment: `{team}-restore` | Repo Admin |
| 4 | Configure environment reviewers | Repo Admin |
| 5 | Add team's databases to ownership config | Repo Admin |
| 6 | Configure MS Teams webhook for team channel | Team Lead |
| 7 | Test end-to-end with non-production database | Team |

### 11.2 Database Ownership Configuration

A configuration file maps databases to teams:

| Database | Owner Team | Allowed Destinations |
|----------|------------|---------------------|
| CustomerDB | team-alpha | dev-sql01, test-sql01 |
| OrdersDB | team-alpha | dev-sql01 |
| InventoryDB | team-beta | dev-sql02 |
| AnalyticsDB | team-gamma | dev-sql01, dev-sql02 |

This prevents Team A from restoring Team B's databases.

---

## 12. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Runner unavailable | Medium | High | Deploy 2+ runners, monitor health |
| Large restore exceeds 6 hours | Medium | Medium | Async polling pattern handles this |
| Approval delayed | Low | Low | Notifications prompt approvers |
| Network connectivity loss | Low | High | Runner on reliable network, retry logic |
| Post-restore script fails | Low | Medium | Script validation, notifications on failure |
| Wrong database restored | Very Low | High | Ownership validation, approver verification |
| Credentials exposed in logs | Very Low | Critical | GitHub Secrets, masked in logs |

---

## 13. Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up repository structure
- [ ] Create GitHub Teams and Environments for pilot team
- [ ] Deploy 2 self-hosted runners
- [ ] Configure secrets and variables
- [ ] Create basic workflow (request → approve → notify)

### Phase 2: Core Functionality (Weeks 3-4)
- [ ] Integrate with existing restore process
- [ ] Implement MS Teams notifications
- [ ] Add post-restore script execution
- [ ] Test end-to-end with pilot team
- [ ] Create user documentation

### Phase 3: Production Readiness (Weeks 5-6)
- [ ] Add database ownership validation
- [ ] Implement async pattern for long restores
- [ ] Add progress monitoring
- [ ] Security review
- [ ] Load testing with concurrent requests

### Phase 4: Rollout (Weeks 7-8)
- [ ] Onboard remaining teams
- [ ] Training sessions
- [ ] Collect feedback
- [ ] Iterate on UX improvements

---

## 14. Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Request-to-approval time | < 4 hours (business hours) | GitHub workflow logs |
| Approval-to-completion time | Restore time + 15 min overhead | GitHub workflow logs |
| Success rate | > 95% | Workflow success/failure ratio |
| User satisfaction | > 4/5 rating | Survey after rollout |
| DBA time saved | > 10 hours/month | Before/after comparison |
| Adoption rate | 100% of eligible teams | Usage tracking |

---

## 15. Open Questions

| # | Question | Status | Decision |
|---|----------|--------|----------|
| 1 | Should DBAs be able to override any approval? | Open | |
| 2 | What is the retention period for tracking files? | Open | |
| 3 | Do we need approval expiration (e.g., 24 hours)? | Open | |
| 4 | Should we limit concurrent restores per team? | Open | |
| 5 | How do we handle restore to shared dev databases? | Open | |
| 6 | What data masking scripts are required? | Open | |
| 7 | Do we need emergency bypass for production restores? | Out of Scope | N/A |

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| **GitHub Environment** | A deployment target with protection rules (approvers, wait timers) |
| **GitHub Team** | A group of GitHub users within an organization |
| **Self-Hosted Runner** | A machine you manage that runs GitHub Actions jobs |
| **DMV** | Dynamic Management View - SQL Server system views for monitoring |
| **Point-in-Time Recovery** | Restoring a database to a specific moment in time |
| **Post-Restore Script** | SQL scripts run after restore to mask data, reset configs |

### B. Related Documents

| Document | Purpose |
|----------|---------|
| Technical Implementation Spec | Detailed code and configuration |
| Post-Restore Script Standards | Data masking requirements |
| Runner Setup Guide | Step-by-step runner installation |
| User Guide | How to request a restore |

### C. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-22 | Infrastructure Team | Initial draft |

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Technical Lead | | | |
| Security | | | |
| DBA Team Lead | | | |
| Engineering Manager | | | |
