# Project Plan: db-cicd

**Version:** 1.1
**Last Updated:** 2026-01-17
**Status:** Draft

## Overview

This plan outlines the timeline, resources, and phases for delivering the Database Change Management CI/CD Platform supporting SQL Server, PostgreSQL, Snowflake, and MongoDB.

## Approach

**Strategy:** Pilot-first rollout
1. Build core platform with one database (SQL Server)
2. Validate with pilot team
3. Extend to remaining platforms
4. Roll out to all teams

## Timeline Summary

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 1: Foundation | 2 weeks | Project structure, CI/CD skeleton, pilot DB baseline |
| Phase 2: Core Platform | 3 weeks | Deploy pipeline, secrets, logging for SQL Server |
| Phase 3: Governance | 2 weeks | Policy checks, drift detection |
| Phase 4: Multi-Platform | 3 weeks | PostgreSQL, Snowflake, MongoDB support |
| Phase 5: Rollout | 2 weeks | Documentation, training, team onboarding |
| **Total** | **12 weeks** | |

---

## Phase 1: Foundation (Weeks 1-2)

**Goal:** Establish project structure and baseline pilot database

### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1.1 | Project structure | `database/` folder with platform subfolders |
| 1.2 | Master changelog | Root `changelog.xml` with includes |
| 1.3 | Properties templates | Environment-specific properties files |
| 1.4 | CODEOWNERS | Platform ownership definitions |
| 1.5 | Pilot baseline | SQL Server baseline from existing database |

### Tasks

| Task | Effort | Owner |
|------|--------|-------|
| Create `database/platforms/{mssql,postgres,snowflake,mongodb}` structure | 2h | Platform Eng |
| Create changelog.xml templates for each platform | 4h | Platform Eng |
| Create liquibase.{dev,stg,prd}.properties templates | 2h | Platform Eng |
| Define CODEOWNERS for each platform folder | 1h | Tech Lead |
| Select pilot database (SQL Server) | - | DBA Team |
| Generate baseline from pilot production DB | 4h | DBA Team |
| Review and clean baseline changelog | 8h | DBA Team |
| Sync baseline to dev/stg environments | 2h | DBA Team |
| Capture baseline snapshot | 1h | Platform Eng |

### Exit Criteria

- [ ] Project structure committed to repository
- [ ] Pilot database baseline generated and reviewed
- [ ] Baseline synced to all environments (`changelogSync`)
- [ ] Baseline snapshot captured for drift detection
- [ ] ADRs reviewed by team (status → Accepted or revised)

### Milestone: **M1 - Foundation Complete**

---

## Phase 2: Core Platform (Weeks 3-5)

**Goal:** Working CI/CD pipeline for SQL Server pilot

### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 2.1 | Validation workflow | PR validation (syntax, policy check) |
| 2.2 | Deploy pipeline | Dev → Stg → Prd auto-deploy |
| 2.3 | Secrets integration | Vault or AWS SM credential fetch |
| 2.4 | Structured logging | JSON log output for SIEM |
| 2.5 | First migration | Test changeset through full pipeline |

### Tasks

| Task | Effort | Owner |
|------|--------|-------|
| Create `.github/workflows/validate-pr.yml` | 8h | Platform Eng |
| Create `.github/workflows/deploy-pipeline.yml` | 16h | Platform Eng |
| Implement secrets wrapper (Vault client) | 16h | Platform Eng |
| Implement log transformer (JSON output) | 8h | Platform Eng |
| Configure GitHub branch protection rules | 2h | Platform Eng |
| Create test changeset (add column or table) | 2h | Pilot Team |
| Deploy test changeset through pipeline | 4h | Pilot Team |
| Verify audit trail in GitHub Actions logs | 2h | Platform Eng |
| Document troubleshooting guide | 8h | Platform Eng |

### Exit Criteria

- [ ] PR validation blocks invalid changelogs
- [ ] Merge to main triggers deploy to Dev → Stg → Prd
- [ ] Credentials fetched from Vault/AWS SM (not in repo)
- [ ] Logs available in JSON format
- [ ] One successful migration through full pipeline

### Milestone: **M2 - SQL Server Pipeline Live**

---

## Phase 3: Governance (Weeks 6-7)

**Goal:** Policy enforcement and drift detection

### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 3.1 | Policy engine | Python-based rule evaluator |
| 3.2 | Policy rules | Initial rule set (naming, rollback required) |
| 3.3 | Drift detector | Compare DB state vs snapshot |
| 3.4 | Drift alerts | Slack/PagerDuty notifications |
| 3.5 | Scheduled workflow | Daily drift detection |

### Tasks

| Task | Effort | Owner |
|------|--------|-------|
| Design policy rule schema (YAML) | 4h | Platform Eng |
| Implement policy engine (parse SQL, evaluate rules) | 40h | Platform Eng |
| Create initial rule set | 8h | DBA Team |
| Integrate policy check into PR validation | 4h | Platform Eng |
| Implement drift detector (compare snapshot to live) | 24h | Platform Eng |
| Create `.github/workflows/drift-detection.yml` | 8h | Platform Eng |
| Configure Slack/PagerDuty alerting | 4h | Platform Eng |
| Test policy violations (should block PR) | 4h | Pilot Team |
| Test drift detection (introduce manual change) | 4h | DBA Team |

### Policy Rules (Initial Set)

| Rule | Severity | Description |
|------|----------|-------------|
| `require-rollback` | Error | All changesets must have rollback |
| `naming-convention` | Warning | File names must match `V*__*.sql` |
| `no-drop-table-prod` | Error | Block `DROP TABLE` in production |
| `require-comment` | Warning | Changesets should have description |

### Exit Criteria

- [ ] Policy engine blocks PRs with violations
- [ ] Drift detection runs daily on pilot DB
- [ ] Alerts sent when drift detected
- [ ] Team can add/modify policy rules

### Milestone: **M3 - Governance Active**

---

## Phase 4: Multi-Platform (Weeks 8-10)

**Goal:** Extend support to PostgreSQL, Snowflake, MongoDB

### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 4.1 | PostgreSQL support | Baseline, pipeline, drift detection |
| 4.2 | Snowflake support | Baseline, pipeline, drift detection |
| 4.3 | MongoDB support | YAML changelog, pipeline |
| 4.4 | Platform matrix | Single workflow supporting all platforms |

### Tasks

| Task | Effort | Owner |
|------|--------|-------|
| **PostgreSQL** | | |
| Install PostgreSQL driver (LPM) | 2h | Platform Eng |
| Generate PostgreSQL pilot baseline | 4h | DBA Team |
| Test PostgreSQL deploy pipeline | 8h | Platform Eng |
| Configure PostgreSQL drift detection | 4h | Platform Eng |
| **Snowflake** | | |
| Install Snowflake driver (LPM) | 2h | Platform Eng |
| Generate Snowflake pilot baseline | 4h | Data Team |
| Test Snowflake deploy pipeline | 8h | Platform Eng |
| Configure Snowflake drift detection | 4h | Platform Eng |
| **MongoDB** | | |
| Install MongoDB extension (LPM) | 4h | Platform Eng |
| Create YAML changelog template | 4h | Platform Eng |
| Generate MongoDB pilot baseline | 4h | NoSQL Team |
| Test MongoDB deploy pipeline | 8h | Platform Eng |
| **Integration** | | |
| Refactor workflows for platform matrix | 16h | Platform Eng |
| Update CODEOWNERS for all platforms | 2h | Tech Lead |
| Cross-platform documentation | 8h | Platform Eng |

### Exit Criteria

- [ ] All 4 platforms have working pipelines
- [ ] Each platform has at least one baseline synced
- [ ] Drift detection active for all platforms
- [ ] Single workflow handles platform selection

### Milestone: **M4 - Multi-Platform Complete**

---

## Phase 5: Rollout (Weeks 11-12)

**Goal:** Documentation, training, and team onboarding

### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 5.1 | User guide | How to author changesets, create PRs |
| 5.2 | Admin guide | How to add databases, manage policies |
| 5.3 | Training session | Recorded walkthrough |
| 5.4 | Onboarding checklist | Per-team setup steps |
| 5.5 | Support channel | Slack channel for questions |

### Tasks

| Task | Effort | Owner |
|------|--------|-------|
| Write user guide (authoring changesets) | 8h | Platform Eng |
| Write admin guide (platform setup) | 8h | Platform Eng |
| Create troubleshooting guide | 4h | Platform Eng |
| Record training video | 4h | Platform Eng |
| Create team onboarding checklist | 4h | Platform Eng |
| Set up #db-cicd Slack channel | 1h | Platform Eng |
| Conduct pilot team retrospective | 2h | Tech Lead |
| Onboard first non-pilot team | 8h | Platform Eng |
| Gather feedback and iterate | 8h | Platform Eng |

### Exit Criteria

- [ ] Documentation complete and reviewed
- [ ] Training materials available
- [ ] At least 2 teams onboarded beyond pilot
- [ ] Support channel active
- [ ] No critical issues from pilot

### Milestone: **M5 - General Availability**

---

## Resources

| Role | Allocation | Responsibilities |
|------|------------|------------------|
| Platform Engineer | 1 FTE | Build platform, workflows, automation |
| DBA (SQL Server) | 0.25 FTE | Baseline, policy rules, drift review |
| DBA (PostgreSQL) | 0.25 FTE | Baseline, validation |
| Data Engineer (Snowflake) | 0.25 FTE | Baseline, validation |
| NoSQL Engineer (MongoDB) | 0.25 FTE | Baseline, validation |
| Tech Lead | 0.1 FTE | ADR review, architecture decisions |

## Effort Summary

| Phase | Effort (hours) |
|-------|----------------|
| Phase 1: Foundation | 24h |
| Phase 2: Core Platform | 66h |
| Phase 3: Governance | 100h |
| Phase 4: Multi-Platform | 78h |
| Phase 5: Rollout | 47h |
| **Total** | **~315 hours** |

*Note: Estimates assume familiarity with Liquibase and GitHub Actions.*

---

## Dependencies

| Dependency | Owner | Required By | Status |
|------------|-------|-------------|--------|
| GitHub repo created | Platform Eng | Phase 1 | ⬜ |
| SQL Server pilot DB identified | DBA Team | Phase 1 | ⬜ |
| Vault/AWS SM access configured | Platform Team | Phase 2 | ⬜ |
| GitHub Actions runners available | DevOps Team | Phase 2 | ⬜ |
| PostgreSQL pilot DB identified | DBA Team | Phase 4 | ⬜ |
| Snowflake pilot DB identified | Data Team | Phase 4 | ⬜ |
| MongoDB pilot DB identified | NoSQL Team | Phase 4 | ⬜ |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pilot database too complex | Medium | High | Choose simple, non-critical DB first |
| Vault/AWS SM access delayed | Medium | High | Use GitHub Secrets as interim fallback |
| Team adoption resistance | Medium | Medium | Early involvement, clear documentation |
| MongoDB extension limitations | Low | Medium | Evaluate during Phase 4, adjust scope |
| Snowflake warehouse costs | Low | Low | Use dedicated dev warehouse with limits |

---

## Success Metrics

| Metric | Target | Measured At |
|--------|--------|-------------|
| Pipeline success rate | > 95% | M2, M4 |
| Mean time to deploy (commit → prod) | < 30 min | M2 |
| Drift detection coverage | 100% of managed DBs | M4 |
| Policy check violations caught | > 90% in PR | M3 |
| Teams onboarded | ≥ 3 | M5 |
| Documentation satisfaction | > 4/5 rating | M5 |

---

## Next Steps

1. [ ] **Review this plan** with stakeholders
2. [ ] **Identify pilot database** (SQL Server recommended)
3. [ ] **Confirm resource availability** for Phase 1
4. [ ] **Set start date** and create calendar milestones
5. [ ] **Schedule ADR review meeting** to accept/revise decisions
