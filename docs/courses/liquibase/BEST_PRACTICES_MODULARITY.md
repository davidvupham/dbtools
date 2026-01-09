# Best Practices: Modularity and Reusability

This document outlines best practices for maintaining modular, reusable tutorials and scripts in the Liquibase course.

## Script Naming Convention

### Principles

1. **Descriptive names over step numbers**
   - ✅ `start_mssql_containers.sh` (describes what it does)
   - ❌ `step02_start_containers.sh` (requires remembering step order)

2. **Consistent prefixes**
   - `setup_*` - Environment and project setup
   - `start_*` - Starting services/containers
   - `create_*` - Creating databases, schemas, objects
   - `populate_*` - Adding sample data
   - `generate_*` - Generating Liquibase artifacts
   - `deploy_*` - Deploying changes to environments
   - `validate_*` - Validation and verification
   - `cleanup_*` - Cleanup and teardown

3. **Self-documenting**
   - Script names should clearly indicate their purpose
   - No need to reference external documentation to understand what a script does

### Examples

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| `step01_setup_environment.sh` | `setup_liquibase_environment.sh` | Describes setup operation |
| `step02_start_containers.sh` | `start_mssql_containers.sh` | Specifies what containers |
| `step03_create_databases.sh` | `create_orderdb_databases.sh` | Specifies which database |
| `step04_populate_dev.sh` | `populate_dev_database.sh` | Clearer operation name |
| `step05_generate_baseline.sh` | `generate_liquibase_baseline.sh` | Specifies tool context |
| `step06_deploy_baseline.sh` | `deploy_liquibase_baseline.sh` | Specifies tool context |

## Tutorial Modularity

### Principles

1. **Reference, don't duplicate**
   - Tutorials should reference other tutorials for detailed steps
   - Avoid copying large blocks of content
   - Use links to guide users to the right place

2. **Single source of truth**
   - Each concept/step should be documented in one primary location
   - Other tutorials reference the primary location
   - Reduces maintenance burden and inconsistency

3. **Clear navigation**
   - End-to-end guides should provide a "navigation map"
   - Point users to specific sections in referenced tutorials
   - Provide quick-start summaries with links to details

### Structure

**End-to-End Guide Pattern:**
```markdown
## Phase X: Description

This phase covers [topic]. **Follow [Part Y] of the series tutorial** for detailed instructions.

### Quick Start: Use Part Y Tutorial

**Follow [Part Y: Title](./series-partY.md), starting at "[Section]":**

- **Step N:** Description
- **Step N+1:** Description

**Key steps:**
1. Brief summary
2. Brief summary

**For detailed instructions** including [topics], see [Part Y, Section](./series-partY.md#section).
```

**Series Part Pattern:**
- Provide complete, detailed instructions
- Include all necessary context and explanations
- Can be followed standalone or as part of series

## Script Reusability

### Principles

1. **No hard-coded paths**
   - Use environment variables (`$LIQUIBASE_TUTORIAL_DIR`, `$LIQUIBASE_TUTORIAL_DATA_DIR`)
   - Allow configuration via environment variables
   - Support different deployment scenarios

2. **Container runtime detection**
   - Auto-detect Docker vs Podman
   - Support both without code duplication
   - Use helper scripts (`cr.sh`) for runtime abstraction

3. **Idempotent operations**
   - Scripts should be safe to run multiple times
   - Check for existing resources before creating
   - Use `IF NOT EXISTS` patterns in SQL

4. **Clear error messages**
   - Indicate what failed
   - Suggest how to fix
   - Provide next steps

5. **Success indicators**
   - Use colored output (✓/✗) for quick feedback
   - Show what was accomplished
   - Provide next steps

### Script Template

```bash
#!/usr/bin/env bash
# Script Name (Descriptive)
# Brief description of what the script does
# Reusable across all tutorial parts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUTORIAL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Tutorial - Script Purpose"
echo "========================================"
echo

# Check prerequisites
if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi

# Detect container runtime
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    CR_CMD="docker"
elif command -v podman &>/dev/null; then
    CR_CMD="podman"
else
    echo -e "${RED}ERROR: No container runtime found${NC}"
    exit 1
fi

# Perform operation
# ...

# Success message
echo
echo "========================================"
echo -e "${GREEN}Operation Complete${NC}"
echo "========================================"
echo "Next: Run next_script.sh"
```

## Documentation Consistency

### Cross-References

1. **Use relative links**
   - `./series-part1-baseline.md` (same directory)
   - `../scripts/README.md` (parent directory)
   - Avoid absolute paths

2. **Link to specific sections**
   - Use anchor links: `#section-name`
   - Point users to exact location
   - Reduce navigation overhead

3. **Consistent terminology**
   - Use same variable names across all docs
   - Use same script names across all docs
   - Use same container names across all docs

### Update Checklist

When adding/modifying scripts or tutorials:

- [ ] Update script name if renaming
- [ ] Update all references in tutorial docs
- [ ] Update scripts README.md
- [ ] Verify links work
- [ ] Check for consistency in terminology
- [ ] Ensure scripts are executable (`chmod +x`)

## Benefits of Modularity

1. **Maintainability**
   - Changes in one place propagate automatically
   - Less duplication = fewer inconsistencies
   - Easier to update and fix bugs

2. **Reusability**
   - Scripts can be used across multiple tutorials
   - Tutorials can reference each other
   - Reduces code/documentation bloat

3. **Clarity**
   - Clear separation of concerns
   - Each tutorial has a focused purpose
   - Users can find what they need quickly

4. **Flexibility**
   - Users can follow full series or individual parts
   - End-to-end guide provides navigation
   - Scripts work in different contexts

## Migration Guide

When migrating from step-numbered to descriptive names:

1. **Create new scripts** with descriptive names
2. **Update all references** in documentation
3. **Keep old scripts temporarily** (for backward compatibility)
4. **Add deprecation notices** to old scripts
5. **Remove old scripts** after migration period

## Examples

### Good: Modular Reference

```markdown
## Phase 1: Local Setup

Follow [Part 1: Baseline](./series-part1-baseline.md) to set up your local environment.

**Quick start:**
```bash
$LIQUIBASE_TUTORIAL_DIR/scripts/setup_liquibase_environment.sh
$LIQUIBASE_TUTORIAL_DIR/scripts/start_mssql_containers.sh
```

**For detailed explanations**, see [Part 1, Step 0](./series-part1-baseline.md#step-0-configure-environment-and-aliases).
```

### Bad: Duplicated Content

```markdown
## Phase 1: Local Setup

### Step 1: Setup Environment

[50 lines of duplicated setup instructions]

### Step 2: Start Containers

[50 lines of duplicated container instructions]
```

## Conclusion

Following these best practices ensures:
- ✅ Consistent user experience across all tutorials
- ✅ Easier maintenance and updates
- ✅ Clear navigation and structure
- ✅ Reusable, well-documented scripts
- ✅ Reduced duplication and inconsistencies
