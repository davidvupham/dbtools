#!/usr/bin/env bash
# Deploy Liquibase Baseline
# Deploys baseline to selected environments (default: all).
# - dev: changelogSync (mark as executed, don't run)
# - stg/prd: update (actually execute)
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

print_usage() {
  cat <<'EOF'
Usage:
  deploy_liquibase_baseline.sh [--envs dev,stg,prd]

Options:
  -e, --envs, --servers   Comma-separated list of targets to deploy to.
                          Defaults to "dev,stg,prd" when omitted.
  -h, --help              Show help

Examples:
  # Deploy to all (default)
  deploy_liquibase_baseline.sh

  # Deploy to one
  deploy_liquibase_baseline.sh --envs dev

  # Deploy to multiple
  deploy_liquibase_baseline.sh --envs dev,stg

Notes:
  - "stage" and "prod" are accepted as aliases for "stg" and "prd".
EOF
}

TARGET_ENVS_CSV=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -e|--envs|--servers)
      TARGET_ENVS_CSV="${2:-}"
      shift 2
      ;;
    --envs=*|--servers=*)
      TARGET_ENVS_CSV="${1#*=}"
      shift
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo -e "${RED}ERROR: Unknown option: $1${NC}" >&2
      print_usage >&2
      exit 2
      ;;
  esac
done

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi
export MSSQL_LIQUIBASE_TUTORIAL_PWD

normalize_env() {
  local env="${1//[[:space:]]/}"
  case "$env" in
    stage) echo "stg" ;;
    prod)  echo "prd" ;;
    *)     echo "$env" ;;
  esac
}

pretty_env() {
  case "$1" in
    dev) echo "Development" ;;
    stg) echo "Staging" ;;
    prd) echo "Production" ;;
    *)   echo "$1" ;;
  esac
}

declare -a TARGET_ENVS=()
if [[ -z "$TARGET_ENVS_CSV" ]]; then
  TARGET_ENVS=("dev" "stg" "prd")
else
  IFS=',' read -r -a TARGET_ENVS <<<"$TARGET_ENVS_CSV"
  # Normalize entries and drop empties
  for i in "${!TARGET_ENVS[@]}"; do
    TARGET_ENVS[$i]="$(normalize_env "${TARGET_ENVS[$i]}")"
  done
  # Remove empty entries (e.g. trailing commas)
  declare -a _filtered=()
  for env in "${TARGET_ENVS[@]}"; do
    if [[ -n "$env" ]]; then
      _filtered+=("$env")
    fi
  done
  TARGET_ENVS=("${_filtered[@]}")
  if [[ ${#TARGET_ENVS[@]} -eq 0 ]]; then
    echo -e "${RED}ERROR: --envs/--servers provided but no targets were parsed${NC}" >&2
    print_usage >&2
    exit 2
  fi
fi

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
if [[ ! -f "platform/mssql/database/orderdb/changelog/changelog.xml" ]]; then
    echo -e "${RED}ERROR: changelog.xml not found${NC}"
    echo "Run setup_liquibase_environment.sh first to create properties and changelog"
    exit 1
fi

# Check baseline file exists
if [[ ! -f "platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql" ]]; then
    echo -e "${RED}ERROR: Baseline file not found${NC}"
    echo "Run generate_liquibase_baseline.sh first"
    exit 1
fi

# Helper function to tag idempotently (handles case where tag already exists)
# Returns: 0 on success, 1 on error
# Sets TAG_STATUS: "new" if tag was created, "exists" if tag already existed
tag_baseline_idempotent() {
    local env=$1
    local tag_output
    TAG_STATUS=""
    tag_output=$("$LB_CMD" -e "$env" -- tag baseline 2>&1) || {
        local exit_code=$?
        # Check if the error is because the tag already exists
        if echo "$tag_output" | grep -qiE "(already exists|already.*tag|tag.*exists)"; then
            echo -e "${YELLOW}ℹ Tag 'baseline' already exists in $env (idempotent: skipping)${NC}"
            TAG_STATUS="exists"
            return 0
        else
            # Some other error occurred
            echo "$tag_output" >&2
            TAG_STATUS="error"
            return $exit_code
        fi
    }
    # Tag succeeded (newly created)
    echo "$tag_output"
    TAG_STATUS="new"
    return 0
}

declare -a SUMMARY_LINES=()
for env in "${TARGET_ENVS[@]}"; do
  pretty="$(pretty_env "$env")"
  action="update"
  action_desc="update - actually execute"
  success_word="deployed"
  if [[ "$env" == "dev" ]]; then
    action="changelogSync"
    action_desc="changelogSync - mark as executed, don't run"
    success_word="synced"
  fi

  echo "Deploying to $pretty ($action_desc)..."
  echo
  if "$LB_CMD" -e "$env" -- "$action" 2>&1; then
    if tag_baseline_idempotent "$env"; then
      if [[ "$TAG_STATUS" == "new" ]]; then
        echo -e "${GREEN}✓ $pretty: Baseline $success_word and tagged${NC}"
      elif [[ "$TAG_STATUS" == "exists" ]]; then
        echo -e "${GREEN}✓ $pretty: Baseline $success_word (tag already existed)${NC}"
      fi
    else
      echo -e "${YELLOW}Warning: Failed to tag baseline in $env${NC}"
    fi
  else
    echo -e "${RED}✗ Failed to $action baseline in $env${NC}"
    exit 1
  fi
  SUMMARY_LINES+=("  - $pretty: Changes $success_word ($action)")
  echo
done

echo
echo "========================================"
echo -e "${GREEN}Baseline Deployed${NC}"
echo "========================================"
echo "Baseline deployed to selected environments:"
printf '%s\n' "${SUMMARY_LINES[@]}"
echo
echo "All environments tagged with 'baseline'"
echo
echo "Next: Continue with Part 2 (Manual Lifecycle)"
echo "  Or run: validate_liquibase_deploy.sh --db mssql_dev,mssql_stg,mssql_prd to verify deployment"
