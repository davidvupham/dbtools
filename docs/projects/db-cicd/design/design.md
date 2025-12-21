# Detailed Design: db-cicd

This document provides an overview of component designs. Each major component has its own design document.

## Component Design Documents

| Component | Design Document | Status |
|-----------|-----------------|--------|
| Policy Engine | [policy-engine-design.md](policy-engine-design.md) | ⬜ |
| Drift Detector | [drift-detector-design.md](drift-detector-design.md) | ⬜ |
| GitHub Workflows | [workflow-design.md](workflow-design.md) | ⬜ |

## Design Principles

1. **CLI-First:** All components are command-line tools, no REST API
2. **Composable:** Components work independently and together
3. **Configurable:** Behavior controlled via YAML configuration
4. **Auditable:** All actions logged with full context
5. **Fail-Safe:** Default to blocking deployment on errors

## Directory Structure (Implementation)

```
packages/
  gds_db_cicd/
    src/
      gds_db_cicd/
        __init__.py
        policy/
          __init__.py
          engine.py
          rules/
            __init__.py
            no_drop_table.py
            require_rollback.py
        drift/
          __init__.py
          detector.py
          reporter.py
        logging/
          __init__.py
          transformer.py
        audit/
          __init__.py
          recorder.py
        cli.py
    tests/
    pyproject.toml
    README.md

.github/
  workflows/
    db-cicd-validate.yml
    db-cicd-deploy.yml
    db-cicd-drift-check.yml
  actions/
    policy-check/
      action.yml
    secrets-inject/
      action.yml

scripts/
  liquibase-with-vault.sh
  liquibase-with-aws.sh
```
