#!/usr/bin/env bash
# Deploy Liquibase Baseline
# Deploys baseline to all environments (dev: changelogSync, stg/prd: update)
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
echo "Liquibase Tutorial - Deploy Baseline"
echo "========================================"
echo

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi
export MSSQL_LIQUIBASE_TUTORIAL_PWD

# Ensure lb command is available (use direct script path if alias not available)
LB_CMD=""
if command -v lb &>/dev/null || type lb &>/dev/null 2>&1; then
    LB_CMD="lb"
else
    echo -e "${YELLOW}Warning: lb alias not found. Sourcing setup_aliases.sh...${NC}"
    source "$TUTORIAL_ROOT/scripts/setup_aliases.sh" || true
    # Check again after sourcing
    if command -v lb &>/dev/null || type lb &>/dev/null 2>&1; then
        LB_CMD="lb"
    else
        # Use direct script path (more reliable than alias in subshells)
        LB_CMD="$TUTORIAL_ROOT/scripts/lb.sh"
        if [[ ! -f "$LB_CMD" ]]; then
            echo -e "${RED}ERROR: lb command not found and lb.sh script not found${NC}"
            exit 1
        fi
        echo "Using direct script path for lb: $LB_CMD"
    fi
fi

cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

# Check master changelog exists
if [[ ! -f "database/changelog/changelog.xml" ]]; then
    echo -e "${RED}ERROR: changelog.xml not found${NC}"
    echo "Run setup_liquibase_environment.sh first to create properties and changelog"
    exit 1
fi

# Check baseline file exists
if [[ ! -f "database/changelog/baseline/V0000__baseline.mssql.sql" ]]; then
    echo -e "${RED}ERROR: Baseline file not found${NC}"
    echo "Run generate_liquibase_baseline.sh first"
    exit 1
fi

# Deploy to Development (changelogSync - mark as executed, don't run)
echo "Deploying to Development (changelogSync)..."
echo
if "$LB_CMD" -e dev -- changelogSync 2>&1; then
    if "$LB_CMD" -e dev -- tag baseline 2>&1; then
        echo -e "${GREEN}✓ Development: Baseline synced and tagged${NC}"
    else
        echo -e "${YELLOW}Warning: Failed to tag baseline in dev${NC}"
    fi
else
    echo -e "${RED}✗ Failed to sync baseline in dev${NC}"
    exit 1
fi

echo
echo "Deploying to Staging (update - actually execute)..."
echo
if "$LB_CMD" -e stg -- update 2>&1; then
    if "$LB_CMD" -e stg -- tag baseline 2>&1; then
        echo -e "${GREEN}✓ Staging: Baseline deployed and tagged${NC}"
    else
        echo -e "${YELLOW}Warning: Failed to tag baseline in stg${NC}"
    fi
else
    echo -e "${RED}✗ Failed to deploy baseline in stg${NC}"
    exit 1
fi

echo
echo "Deploying to Production (update - actually execute)..."
echo
if "$LB_CMD" -e prd -- update 2>&1; then
    if "$LB_CMD" -e prd -- tag baseline 2>&1; then
        echo -e "${GREEN}✓ Production: Baseline deployed and tagged${NC}"
    else
        echo -e "${YELLOW}Warning: Failed to tag baseline in prd${NC}"
    fi
else
    echo -e "${RED}✗ Failed to deploy baseline in prd${NC}"
    exit 1
fi

echo
echo "========================================"
echo -e "${GREEN}Baseline Deployed${NC}"
echo "========================================"
echo "Baseline deployed to all environments:"
echo "  - Development: Changes synced (changelogSync)"
echo "  - Staging: Changes executed (update)"
echo "  - Production: Changes executed (update)"
echo
echo "All environments tagged with 'baseline'"
echo
echo "Next: Continue with Part 2 (Manual Lifecycle)"
echo "  Or run: validate_liquibase_deploy.sh to verify deployment"
