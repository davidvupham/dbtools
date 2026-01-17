# Architecture decision records

This directory contains Architecture Decision Records (ADRs) documenting significant technical decisions made in this project.

## What is an ADR?

An Architecture Decision Record captures a single architecture decision along with its context and consequences. ADRs help teams:

- Understand why decisions were made
- Onboard new team members quickly
- Avoid re-discussing settled decisions
- Track the evolution of the architecture

## ADR format

Each ADR follows this structure:

1. **Title**: Short descriptive name
2. **Status**: Proposed, Accepted, Deprecated, Superseded
3. **Context**: What is the issue that motivated this decision?
4. **Decision**: What is the change that we're proposing?
5. **Consequences**: What becomes easier or harder after this change?

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [001](./001-uv-workspace-monorepo.md) | Use UV workspace for Python monorepo | Accepted |
| [002](./002-src-layout-python-packages.md) | Use src layout for Python packages | Accepted |
| [003](./003-diataxis-documentation.md) | Follow Diátaxis framework for documentation | Accepted |
| [004](./004-database-abstraction-layer.md) | Database abstraction layer design | Accepted |

## Creating new ADRs

1. Copy an existing ADR as a template
2. Number sequentially (e.g., `005-topic-name.md`)
3. Fill in all sections
4. Submit for review via PR
