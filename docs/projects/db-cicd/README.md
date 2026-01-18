# db-cicd: Database Change Management CI/CD Platform

Implements Liquibase Secure features without licensing, with full GitHub Actions integration.

**Platforms:** SQL Server, PostgreSQL, Snowflake, MongoDB
**Approval Model:** CODEOWNERS-based PR review (no environment gates)

## Documentation Framework

| # | Phase | Document | Purpose | Status |
|---|-------|----------|---------|--------|
| 1 | Initiation | [Project Charter](management/project-charter.md) | Scope, stakeholders, RACI | ✅ |
| 2 | Initiation | [Project Plan](management/project-plan.md) | Phases, milestones, effort | ✅ |
| 3 | Initiation | [Decision Log](management/decision-log.md) | ADRs (6 recorded) | ✅ |
| 4 | Requirements | [Functional Spec](specs/functional-spec.md) | User stories, acceptance criteria | ✅ |
| 5 | Design | [Technical Architecture](architecture/technical-architecture.md) | High-level design | ✅ |
| 6 | Design | [Software Stack](architecture/software-stack.md) | Technology choices | ⬜ |
| 7 | Design | [Detailed Design](design/design.md) | Component designs | ⬜ |
| 8 | Validation | [Test Plan](testing/test-plan.md) | Test cases | ⬜ |
| 9 | Build | [Implementation Guide](implementation/implementation-guide.md) | Build instructions | ⬜ |
| 10 | Operations | [Procedures](operations/procedures.md) | Operational steps | ⬜ |
| 11 | Operations | [Runbook](operations/runbook.md) | Incident response | ⬜ |

## Next Steps (Resume Here)

**Last Updated:** 2026-01-17

Before starting implementation:

1. [ ] **Review documents with team** - Schedule ADR review meeting to accept/revise 6 proposed ADRs
2. [ ] **Identify pilot database** - Select SQL Server database for Phase 1 (recommend simple, non-critical)
3. [ ] **Confirm dependencies:**
   - [ ] GitHub repo created for database changelogs
   - [ ] Vault/AWS SM access configured
   - [ ] GitHub Actions runners available
4. [ ] **Set start date** - Assign resources and begin Phase 1: Foundation

**To continue implementation:** Start with Phase 1 tasks in [Project Plan](management/project-plan.md#phase-1-foundation-weeks-1-2)

---

## Quick Links

- [Project Charter](management/project-charter.md) - Scope, RACI, workflow diagram
- [Project Plan](management/project-plan.md) - 5 phases, 12 weeks, milestones
- [Decision Log](management/decision-log.md) - All ADRs including changelog format, baseline strategy
- [Technical Architecture](architecture/technical-architecture.md) - Multi-platform architecture diagrams
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
