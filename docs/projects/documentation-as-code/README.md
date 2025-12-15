# Documentation as Code

This project defines a **documented, repeatable process** for implementing **documentation as code (DaC)** in an internal repository.

- Audience: internal engineering / operations teams
- Publishing: **no website required** (docs are read in Git UI and IDEs)
- Platforms: **mixed** (Linux/WSL + Windows)
- Languages covered: SQL, PowerShell, Python, Ansible, Terraform, Vault HCL, YAML

## Documentation Framework

| # | Topic | Document | Purpose | Status |
|---|-------|----------|---------|--------|
| 1 | Overview | [README](README.md) | What DaC is and what you get | 📝 |
| 2 | Process | [Process](process.md) | Step-by-step implementation and rollout | 📝 |
| 3 | Structure | [Structure](structure.md) | Recommended information architecture and folders | 📝 |
| 4 | Standards | [Standards](standards.md) | Writing and formatting rules teams can adopt | 📝 |
| 5 | Tooling | [Tooling](tooling/README.md) | Copy/paste configs + scripts (pre-commit + CI) | 📝 |
| 6 | Templates | [Templates](templates/) | ADR, runbook, and how-to templates | 📝 |

## What “documentation as code” means (in practice)

Documentation as code means documentation is treated like software:

- Source is **plain text** (usually Markdown)
- Docs are stored in **Git**
- Changes go through **pull requests** and **reviews**
- Quality checks are **automated** (lint, spellcheck, link checks)
- CI blocks merges when docs are broken

## Quickstart Checklist (for another team)

Use this as the minimum adoption path for a new repository:

- [ ] Create a `docs/` folder and pick a structure (see [Structure](structure.md)).
- [ ] Add templates for ADRs, runbooks, and how-tos (see [Templates](templates/)).
- [ ] Add doc standards and enforce them (see [Standards](standards.md)).
- [ ] Add local checks (pre-commit) using the examples in [Tooling](tooling/README.md).
- [ ] Add CI checks (GitHub Actions) using the examples in [Tooling](tooling/README.md).
- [ ] Add CODEOWNERS + PR checklist so doc changes are reviewed.
- [ ] Roll out in two phases: warn-only → enforce (details in [Process](process.md)).

## Design principles

- **Make it easy**: provide auto-fix where possible.
- **Fail fast**: catch doc issues before merge.
- **One source of truth**: don’t duplicate reference data.
- **Optimize for the reader**: task-focused docs; consistent navigation.
