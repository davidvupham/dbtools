# Active Directory Password Rotation with HashiCorp Vault

This directory contains all documentation for the AD Password Rotation project, which automates the rotation of Active Directory service account passwords using HashiCorp Vault.

## Quick Links

| Document | Purpose |
|----------|---------|
| [Project Plan](management/project-plan.md) | Timeline, effort, and resource planning |
| [Functional Specification](specs/functional-spec.md) | Requirements and acceptance criteria |
| [Technical Architecture](architecture/technical-architecture.md) | High-level system design |
| [Detailed Design](design/design.md) | Data flows, error handling, configurations |
| [Software Stack](architecture/software-stack.md) | Technology choices and CI/CD approach |
| [Implementation Guide](implementation/implementation-guide.md) | Step-by-step build instructions |
| [Platform Procedures](operations/platform-rotation-procedures.md) | Platform-specific rotation steps |

## Directory Structure

```
ad-password-rotation/
├── README.md                 # This file
├── architecture/
│   ├── technical-architecture.md   # High-level architecture diagram
│   └── software-stack.md           # Technology stack and CI/CD
├── design/
│   └── design.md                   # Detailed technical design
├── implementation/
│   └── implementation-guide.md     # Step-by-step implementation
├── management/
│   └── project-plan.md             # Project plan and timeline
├── operations/
│   └── platform-rotation-procedures.md  # DB-specific procedures
└── specs/
    └── functional-spec.md          # Functional requirements
```

## Related Documentation

- [How-to: Rotate AD Passwords with Vault](../how-to/rotate-ad-passwords-with-vault.md) - Quick reference guide
- [Workflow Engine Comparison](../explanation/workflow-engine-comparison.md) - Analysis of orchestration tools
- [Secrets Management Comparison](../explanation/secrets-management-comparison.md) - Vault vs alternatives

## Status

| Phase | Status |
|-------|--------|
| Planning | 🟡 In Progress |
| Infrastructure | ⬜ Not Started |
| Pilot | ⬜ Not Started |
| Production Rollout | ⬜ Not Started |
