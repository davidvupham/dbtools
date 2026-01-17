# Monorepo structure review

**[← Back to Best Practices Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 17, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Type](https://img.shields.io/badge/Type-Review-blue)

> [!IMPORTANT]
> This document provides a comprehensive review of the dbtools monorepo structure against industry best practices, with actionable recommendations for improvement.

## Table of contents

- [Executive summary](#executive-summary)
- [Current structure overview](#current-structure-overview)
- [Strengths](#strengths)
- [Areas for improvement](#areas-for-improvement)
- [Detailed recommendations](#detailed-recommendations)
- [Implementation priority](#implementation-priority)

## Executive summary

The dbtools monorepo demonstrates strong adherence to industry best practices, particularly in Python package organization, documentation structure, and CI/CD automation. The UV workspace pattern, Diátaxis documentation framework, and layered architecture (abstract base classes with concrete implementations) are well-executed.

The primary opportunities for improvement center on reducing root-level clutter, consolidating scattered test locations, and applying more consistent organizational patterns to scripts and Docker configurations.

[↑ Back to Table of Contents](#table-of-contents)

## Current structure overview

### Top-level directories

| Directory | Purpose |
|-----------|---------|
| `python/` | 14 UV workspace packages (gds_* modules) |
| `PowerShell/` | Windows automation modules + build scripts |
| `ansible/` | Ansible playbooks, roles, and inventory |
| `docker/` | Docker Compose services for local development |
| `docs/` | Documentation (Diátaxis framework) |
| `.devcontainer/` | VS Code dev container configuration |
| `.github/` | GitHub workflows, templates, issue templates |
| `scripts/` | Utility and validation scripts |
| `tests/` | Root-level integration tests |
| `examples/` | Example code and configurations |
| `schemas/` | JSON schema definitions (Avro, etc.) |
| `snowflake_monitoring/` | Snowflake-specific monitoring utilities |

### Python package structure

All packages follow the src layout pattern:

```text
python/gds_[package_name]/
├── src/gds_[package_name]/
│   ├── __init__.py
│   └── [modules].py
├── tests/
│   ├── conftest.py
│   └── test_*.py
├── pyproject.toml
└── docs/ | examples/ (optional)
```

### PowerShell module structure

```text
PowerShell/Modules/GDS.[ModuleName]/
├── Public/
│   └── [exported_functions].ps1
├── Private/
│   └── [internal_functions].ps1
├── Tests/
│   └── [module].Tests.ps1
└── GDS.[ModuleName].psd1
```

[↑ Back to Table of Contents](#table-of-contents)

## Strengths

### 1. Python package organization

- **UV workspace with src layout**: Prevents import confusion and ensures installed packages behave identically to development versions
- **Clear abstraction hierarchy**: Abstract base (`gds_database`) with concrete implementations (`gds_postgres`, `gds_mssql`, `gds_mongodb`) follows the Open-Closed Principle
- **Self-contained packages**: Each package has its own `tests/`, `pyproject.toml`, and optional `docs/`/`examples/`
- **Single lockfile**: The root `uv.lock` ensures reproducible builds across all packages

### 2. Documentation structure

- **Diátaxis framework adherence**: Clear separation of tutorials, how-to guides, reference, and explanation
- **Consistent naming**: Kebab-case filenames throughout
- **Structured learning**: Dedicated `courses/` directory for comprehensive learning paths
- **Standards documentation**: Well-defined coding standards for Python and PowerShell

### 3. Configuration management

- **Centralized build commands**: `Makefile` provides unified interface for common operations
- **Pre-commit hooks**: `.pre-commit-config.yaml` enforces consistent code quality
- **Type checking**: `pyrightconfig.json` for static type analysis
- **Linting**: Ruff configuration in `pyproject.toml` with consistent rules

### 4. CI/CD and automation

- **GitHub Actions workflows**: CI, testing, CodeQL analysis, and artifact publishing
- **Molecule testing**: Automated testing for Ansible roles (`win_service_rights/molecule/`)
- **Dev container support**: Full development environment with verification scripts
- **Pre-commit integration**: Automated quality checks before commits

### 5. Multi-language support

- **Clean separation**: `python/` for Python packages, `PowerShell/Modules/` for PowerShell modules
- **Language-specific conventions**: Each follows its ecosystem's best practices
- **Shared infrastructure**: Common CI/CD and documentation patterns

### 6. Docker service organization

- **Comprehensive local development**: Services for Vault, Kafka, PostgreSQL, MongoDB, MSSQL, and more
- **Prometheus monitoring**: Pre-configured monitoring stack
- **Development parity**: Local services mirror production configurations

[↑ Back to Table of Contents](#table-of-contents)

## Areas for improvement

### 1. Root-level clutter

Several items at the repository root could be better organized:

| Item | Issue | Current Location |
|------|-------|------------------|
| `test_jupyter.ipynb` | Orphaned test file | Root |
| `validate_links.py` | Duplicated in `scripts/` | Root |
| `gds_certs/` | Symlink duplicates `python/gds_certs/` | Root |
| `snowflake_monitoring/` | Standalone directory, not a proper package | Root |
| `dbtools.egg-info/` | Build artifact | Root |

### 2. Inconsistent test locations

- Root `tests/` contains `gds_benchmark/` and `gds_hammerdb/` test directories
- Other packages have tests within `python/gds_*/tests/`
- Creates confusion about where to find and run tests

### 3. Docker organization inconsistency

- Some services have full subdirectory structures (`hvault/`, `prometheus/`)
- Others have minimal configuration
- No consistent pattern for docker-compose file naming

### 4. Scripts directory lacks structure

The `scripts/` directory mixes different concerns:
- Build scripts (`build_container_image.sh`)
- Operational scripts (`fix-liquibase-baseline.py`)
- Validation utilities (`validate_links.py`)
- Development helpers (`set_prompt.sh`)

### 5. Documentation sprawl

- 31 subdirectories in `docs/tutorials/` without grouping
- Difficult to navigate for newcomers
- Some overlap between `docs/tutorials/` and `docs/courses/`

### 6. Workspace file duplication

- Two VS Code workspace files: `dbtools.code-workspace` and `gds-dev-container-.code-workspace`
- Unclear which to use and when

[↑ Back to Table of Contents](#table-of-contents)

## Detailed recommendations

### Recommendation 1: Clean up root directory

**Priority:** High
**Effort:** Low
**Impact:** Improved developer experience and reduced confusion

Actions:
1. Move `test_jupyter.ipynb` to `examples/notebooks/` or delete if unused
2. Remove root `validate_links.py` (duplicate of `scripts/validate_links.py`)
3. Remove `gds_certs/` symlink from root (access via `python/gds_certs/`)
4. Add `dbtools.egg-info/` to `.gitignore` if not already ignored
5. Consider converting `snowflake_monitoring/` to a proper package in `python/gds_snowflake_monitoring/`

### Recommendation 2: Consolidate test locations

**Priority:** High
**Effort:** Medium
**Impact:** Consistent test discovery and execution

Actions:
1. Move `tests/gds_benchmark/` to `python/gds_benchmark/tests/`
2. Move `tests/gds_hammerdb/` to `python/gds_hammerdb/tests/`
3. Reserve root `tests/` for true cross-package integration tests only
4. Update `Makefile` test targets if necessary
5. Document test organization in `CONTRIBUTING.md`

### Recommendation 3: Organize scripts directory

**Priority:** Medium
**Effort:** Low
**Impact:** Easier script discovery and maintenance

Proposed structure:

```text
scripts/
├── build/
│   ├── build_container_image.sh
│   └── lint.sh
├── development/
│   ├── set_prompt.sh
│   ├── add_test_docstrings.py
│   └── devcontainer/
├── operations/
│   ├── fix-liquibase-baseline.py
│   ├── diagnose_vault_approle.py
│   └── prompt_mssql_password.sh
├── validation/
│   ├── validate_links.py
│   ├── validate_oop_docs.py
│   ├── verify_devcontainer.sh
│   ├── verify_sqlserver.sh
│   └── verify_pyodbc.sh
└── README.md
```

### Recommendation 4: Standardize Docker service structure

**Priority:** Medium
**Effort:** Medium
**Impact:** Consistent patterns for local development

Proposed pattern for each service:

```text
docker/[service]/
├── docker-compose.yml      # Primary compose file
├── Dockerfile              # Custom image (if needed)
├── config/                 # Configuration files
├── scripts/                # Initialization scripts
└── README.md               # Service-specific documentation
```

Actions:
1. Create consistent directory structure for all services
2. Add README.md to each service directory explaining usage
3. Consider a root `docker/docker-compose.yml` that includes common services

### Recommendation 5: Group tutorial documentation

**Priority:** Low
**Effort:** Medium
**Impact:** Improved documentation navigation

Proposed grouping for `docs/tutorials/`:

```text
docs/tutorials/
├── databases/
│   ├── postgres-ha/
│   ├── mongodb/
│   └── kafka/
├── infrastructure/
│   ├── docker/
│   ├── podman/
│   ├── kubernetes/
│   └── terraform/
├── languages/
│   ├── python/
│   └── powershell/
├── devops/
│   ├── github-actions/
│   ├── argocd/
│   └── ansible/
└── cloud/
    └── aws/
```

> [!NOTE]
> This reorganization requires updating internal links and should be done incrementally.

### Recommendation 6: Consolidate workspace files

**Priority:** Low
**Effort:** Low
**Impact:** Reduced confusion for developers

Actions:
1. Document the purpose of each workspace file in the repository README
2. Consider merging into a single workspace file with conditional settings
3. If both are necessary, rename to clarify purpose:
   - `dbtools.code-workspace` → `dbtools-local.code-workspace`
   - `gds-dev-container-.code-workspace` → `dbtools-devcontainer.code-workspace`

### Recommendation 7: Add CODEOWNERS for critical paths

**Priority:** Medium
**Effort:** Low
**Impact:** Clearer ownership and review requirements

Ensure `.github/CODEOWNERS` includes:

```text
# Python packages
/python/gds_database/     @database-team
/python/gds_vault/        @security-team

# Infrastructure
/ansible/                 @platform-team
/docker/                  @platform-team
/.devcontainer/           @platform-team

# Documentation
/docs/                    @docs-team
```

### Recommendation 8: Create architecture decision records

**Priority:** Medium
**Effort:** Low
**Impact:** Documented rationale for structural decisions

Actions:
1. Create `docs/explanation/architecture/decisions/` directory
2. Document key decisions:
   - Why UV workspace over alternatives
   - Why src layout for Python packages
   - Why Diátaxis for documentation
   - Database abstraction layer design

### Recommendation 9: Add package dependency visualization

**Priority:** Low
**Effort:** Medium
**Impact:** Easier understanding of package relationships

Actions:
1. Generate dependency graph using `uv` or `pipdeptree`
2. Add diagram to repository README or `docs/explanation/architecture/`
3. Consider automated generation in CI

### Recommendation 10: Standardize example locations

**Priority:** Low
**Effort:** Low
**Impact:** Consistent discoverability

Current state:
- Root `examples/` directory
- Package-level `examples/` in some packages
- Examples embedded in `docs/`

Actions:
1. Keep package-specific examples in package `examples/` directories
2. Move cross-cutting examples to root `examples/`
3. Link from documentation rather than duplicating

[↑ Back to Table of Contents](#table-of-contents)

## Implementation priority

### Immediate (low effort, high impact)

1. Clean up root directory (Recommendation 1)
2. Consolidate workspace files documentation (Recommendation 6)
3. Add CODEOWNERS entries (Recommendation 7)

### Short-term (medium effort, high impact)

4. Consolidate test locations (Recommendation 2)
5. Organize scripts directory (Recommendation 3)

### Medium-term (medium effort, medium impact)

6. Standardize Docker service structure (Recommendation 4)
7. Create architecture decision records (Recommendation 8)

### Long-term (higher effort, ongoing value)

8. Group tutorial documentation (Recommendation 5)
9. Add package dependency visualization (Recommendation 9)
10. Standardize example locations (Recommendation 10)

[↑ Back to Table of Contents](#table-of-contents)
