# Sample Project

This is a scaffold using the Technical Project Management framework.

## Documentation Framework

| # | Phase | Document | Purpose | Status |
|---|-------|----------|---------|--------|
| 1 | Initiation | [Project Plan](management/project-plan.md) | Timeline, effort, resources | ⬜ |
| 2 | Initiation | [Decision Log](management/decision-log.md) | ADRs | ⬜ |
| 3 | Requirements | [Functional Spec](specs/functional-spec.md) | User stories, acceptance criteria | ⬜ |
| 4 | Design | [Technical Architecture](architecture/technical-architecture.md) | High-level design | ⬜ |
| 5 | Design | [Software Stack](architecture/software-stack.md) | Technology choices | ⬜ |
| 6 | Design | [Detailed Design](design/design.md) | Data flows, schemas | ⬜ |
| 7 | Validation | [Test Plan](testing/test-plan.md) | Test cases | ⬜ |
| 8 | Build | [Implementation Guide](implementation/implementation-guide.md) | Build instructions | ⬜ |
| 9 | Operations | [Procedures](operations/procedures.md) | Operational steps | ⬜ |
| 10 | Operations | [Runbook](operations/runbook.md) | Incident response | ⬜ |

## Quick Links

- [Project Charter](../../templates/project-charter.md)
- [RACI Matrix](../../templates/raci-matrix.md)
- [Communications Plan](../../templates/communications-plan.md)
- [RAID Log](../../templates/raid-log.md)
- [Release Readiness](../../templates/release-readiness-checklist.md)

## Getting Started Checklist

- [ ] Choose delivery model (Scrum/Kanban/Hybrid) and record in Project Charter
- [ ] Draft [Project Plan](management/project-plan.md) with scope, phases, timeline
- [ ] Create initial [Decision Log](management/decision-log.md) and add ADR-001
- [ ] Draft [Functional Spec](specs/functional-spec.md) with acceptance criteria
- [ ] Draft [Technical Architecture](architecture/technical-architecture.md) and perform security review
- [ ] Write [Test Plan](testing/test-plan.md) before implementation
- [ ] Configure PR governance (branch protection, required reviews via CODEOWNERS)
- [ ] Prepare [Release Readiness Checklist](../../templates/release-readiness-checklist.md) before go-live

## How to File ADRs

- Create entries in `management/decision-log.md` following the ADR template.
- Use consistent titles: `ADR-00X: <Decision Title>`.
- Reference related GitHub Issues/PRs and affected documents.
- Update status when accepted/deprecated; add a supersedes reference when needed.

## Status Reporting Cadence

- File weekly status reports in `management/` using `status-YYYY-MM-DD.md`.
- Use the [Weekly Status Report Template](../../templates/status-report-weekly.md).
- Recommended cadence: every Thursday; include links to ADRs and PRs.
