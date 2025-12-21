# db-cicd: Database Change Management CI/CD Platform

Implements Liquibase Secure features without licensing, with full GitHub Actions integration.

## Documentation Framework

| # | Phase | Document | Purpose | Status |
|---|-------|----------|---------|--------|
| 1 | Initiation | [Project Plan](management/project-plan.md) | Timeline, effort, resources | ⬜ |
| 2 | Initiation | [Decision Log](management/decision-log.md) | ADRs | ⬜ |
| 3 | Requirements | [Functional Spec](specs/functional-spec.md) | User stories, acceptance criteria | ⬜ |
| 4 | Design | [Technical Architecture](architecture/technical-architecture.md) | High-level design | ⬜ |
| 5 | Design | [Software Stack](architecture/software-stack.md) | Technology choices | ⬜ |
| 6 | Design | [Detailed Design](design/design.md) | Component designs | ⬜ |
| 7 | Validation | [Test Plan](testing/test-plan.md) | Test cases | ⬜ |
| 8 | Build | [Implementation Guide](implementation/implementation-guide.md) | Build instructions | ⬜ |
| 9 | Operations | [Procedures](operations/procedures.md) | Operational steps | ⬜ |
| 10 | Operations | [Runbook](operations/runbook.md) | Incident response | ⬜ |

## Quick Links

- [Project Charter](management/project-charter.md)
- [RACI Matrix](management/raci-matrix.md)
- [Glossary](glossary.md)

## Features

| Feature | Priority | Status |
|---------|----------|--------|
| Secrets Management (Vault/AWS) | P1 | ⬜ |
| Structured Logging (JSON/SIEM) | P1 | ⬜ |
| Drift Detection + Alerting | P1 | ⬜ |
| Policy Checks (Python engine) | P1 | ⬜ |
| Approval Workflows (GitHub) | P1 | ⬜ |
| GitHub Actions Integration | P1 | ⬜ |
| Audit Trails | P2 | ⬜ |
| Operation Reports (HTML) | P2 | ⬜ |
| Stored Logic Extraction | P2 | ⬜ |
| Targeted Rollback Wrapper | P3 | ⬜ |
| Flowfile Enhancements | P3 | ⬜ |

## Timeline

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 1: Foundation | 2 weeks | Secrets, logging, basic workflows |
| Phase 2: Governance | 3 weeks | Policy engine, drift, approvals |
| Phase 3: Reporting | 2 weeks | Reports, audit, dashboards |
| Phase 4: Advanced | 3 weeks | Stored logic, targeted rollback |
| Phase 5: Integration | 2 weeks | E2E testing, docs, rollout |

**Total:** ~12 weeks (1 FTE)

## Getting Started

- [ ] Review [Project Plan](management/project-plan.md)
- [ ] Record initial ADR in [Decision Log](management/decision-log.md)
- [ ] Draft [Functional Spec](specs/functional-spec.md)
- [ ] Draft [Technical Architecture](architecture/technical-architecture.md)
