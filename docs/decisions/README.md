# Architecture Decision Records

**[← Back to Documentation Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)

This directory contains Architecture Decision Records (ADRs) documenting significant technical decisions made in this project.

## What is an ADR?

An Architecture Decision Record captures:
- **Context**: The situation and forces at play
- **Decision**: What was decided
- **Consequences**: The results of the decision (positive and negative)

ADRs provide a historical record of why things are the way they are, helping future team members understand the reasoning behind architectural choices.

## Decision Log

| ID | Title | Status | Date |
|:---|:---|:---|:---|
| *No decisions recorded yet* | | | |

<!-- Add new decisions to the table above as they are created -->
<!-- Example:
| [0001](./0001-use-postgresql.md) | Use PostgreSQL for primary database | Accepted | January 22, 2026 |
| [0002](./0002-api-versioning.md) | API versioning strategy | Accepted | January 25, 2026 |
-->

## Creating a New ADR

1. Copy the template:
   ```bash
   cp docs/templates/adr-template.md docs/decisions/NNNN-short-title.md
   ```

2. Use the next available number (zero-padded to 4 digits):
   - `0001-first-decision.md`
   - `0002-second-decision.md`

3. Fill in all sections of the template

4. Submit for review via pull request

5. Update the Decision Log table above when accepted

## ADR Lifecycle

```text
Proposed → Accepted → [Deprecated | Superseded]
```

- **Proposed**: Under discussion, not yet approved
- **Accepted**: Approved and in effect
- **Deprecated**: No longer relevant (context changed)
- **Superseded**: Replaced by a newer ADR (link to replacement)

## Guidelines

- **Keep ADRs short**: Focus on the essential context, decision, and consequences
- **One decision per ADR**: Don't bundle multiple decisions
- **Immutable once accepted**: Create a new ADR to change a decision, don't edit the original
- **Link related ADRs**: Reference previous decisions that informed this one

## References

- [ADR GitHub Organization](https://adr.github.io/)
- [Documenting Architecture Decisions - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
