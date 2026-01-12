#!/usr/bin/env bash
################################################################################
# deploy.sh - Liquibase Deployment Orchestrator with Auto-Snapshots
################################################################################
#
# PURPOSE:
#   This script provides a unified interface for all Liquibase deployment
#   operations (baseline, update, rollback) and automatically creates
#   timestamped snapshots after every successful operation.
#
# WHY SNAPSHOTS?
#   Snapshots capture the exact database schema state at a point in time.
#   They are essential for:
#   - Drift Detection: Compare current DB against snapshot to find unauthorized changes
#   - Audit Trail: Historical record of all schema states
#   - Rollback Reference: Know exactly what state you're rolling back to
#
# SNAPSHOT STRATEGY:
#   - Every successful deployment creates a new timestamped snapshot
#   - Snapshots are NEVER deleted - they form an audit trail
#   - Each snapshot filename includes: environment, action, and timestamp
#   - Drift detection compares against the most recent snapshot
#
# SUPPORTED ACTIONS:
#   baseline       - Deploy baseline changelog (changelogSync for dev, update for stg/prd)
#                    Tags the deployment as "baseline"
#   update         - Deploy all pending changesets
#   rollback       - Rollback to a specific tag (requires --tag)
#   rollback-count - Rollback the last N changesets (requires --count)
#   status         - Show pending changesets (no snapshot taken)
#
# USAGE:
#   deploy.sh --action <action> [--env <env>] [options]
#
# OPTIONS:
#   -a, --action <action>   Action to perform (required)
#                           Values: baseline, update, rollback, rollback-count, status
#   -e, --env <env>         Target environment(s) - comma-separated
#                           Values: dev, stg, prd (default: dev)
#                           For baseline: defaults to dev,stg,prd
#   -t, --tag <tag>         Tag name for rollback action (required for rollback)
#   -c, --count <n>         Number of changesets for rollback-count (required for rollback-count)
#   --no-snapshot           Skip snapshot creation (not recommended)
#   -h, --help              Show this help message
#
# EXAMPLES:
#   # Deploy baseline to all environments (dev, stg, prd)
#   deploy.sh --action baseline
#
#   # Deploy baseline to dev only
#   deploy.sh --action baseline --env dev
#
#   # Deploy pending changesets to dev
#   deploy.sh --action update --env dev
#
#   # Deploy to multiple environments
#   deploy.sh --action update --env dev,stg
#
#   # Rollback dev to baseline tag
#   deploy.sh --action rollback --env dev --tag baseline
#
#   # Rollback last 1 changeset in dev
#   deploy.sh --action rollback-count --env dev --count 1
#
#   # Check pending changesets (no snapshot)
#   deploy.sh --action status --env dev
#
# SNAPSHOT NAMING:
#   Format: {env}_{action}_{YYYYMMDD}_{HHMMSS}.json
#   Examples:
#     dev_baseline_20260112_050000.json
#     dev_update_20260112_053000.json
#     stg_rollback_20260112_060000.json
#
# SNAPSHOT LOCATION:
#   $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/snapshots/
#
# REQUIREMENTS:
#   - MSSQL_LIQUIBASE_TUTORIAL_PWD environment variable must be set
#   - lb.sh script must be available (Liquibase wrapper)
#   - SQL Server containers must be running (mssql_dev, mssql_stg, mssql_prd)
#
# EXIT CODES:
#   0 - Success
#   1 - General error
#   2 - Invalid arguments
#
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

################################################################################
# Helper Functions
################################################################################

print_usage() {
    # Extract usage from script header
    sed -n '/^# USAGE:/,/^# REQUIREMENTS:/p' "$0" | grep -E "^#" | sed 's/^# //' | head -n -1
}

print_help() {
    # Extract full documentation from script header
    sed -n '/^# PURPOSE:/,/^# EXIT CODES:/p' "$0" | sed 's/^# //' | sed 's/^#$//'
    echo "  0 - Success"
    echo "  1 - General error"
    echo "  2 - Invalid arguments"
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
    echo -e "${RED}✗${NC} $*" >&2
}

# Normalize environment names (stage -> stg, prod -> prd)
normalize_env() {
    local env="${1//[[:space:]]/}"
    case "$env" in
        stage) echo "stg" ;;
        prod)  echo "prd" ;;
        *)     echo "$env" ;;
    esac
}

# Get human-readable environment name
pretty_env() {
    case "$1" in
        dev) echo "Development" ;;
        stg) echo "Staging" ;;
        prd) echo "Production" ;;
        *)   echo "$1" ;;
    esac
}

################################################################################
# Argument Parsing
################################################################################

ACTION=""
ENVS_CSV=""
TAG=""
COUNT=""
TAKE_SNAPSHOT=true

while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--action)
            ACTION="$2"
            shift 2
            ;;
        -e|--env|--envs)
            ENVS_CSV="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -c|--count)
            COUNT="$2"
            shift 2
            ;;
        --no-snapshot)
            TAKE_SNAPSHOT=false
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            print_usage
            exit 2
            ;;
    esac
done

################################################################################
# Validation
################################################################################

# Validate action
if [[ -z "$ACTION" ]]; then
    log_error "Action is required. Use --action <action>"
    print_usage
    exit 2
fi

VALID_ACTIONS="baseline update rollback rollback-count status"
if [[ ! " $VALID_ACTIONS " =~ " $ACTION " ]]; then
    log_error "Invalid action: $ACTION"
    log_error "Valid actions: $VALID_ACTIONS"
    exit 2
fi

# Validate rollback requires tag
if [[ "$ACTION" == "rollback" ]] && [[ -z "$TAG" ]]; then
    log_error "Rollback action requires --tag <tag>"
    exit 2
fi

# Validate rollback-count requires count
if [[ "$ACTION" == "rollback-count" ]] && [[ -z "$COUNT" ]]; then
    log_error "Rollback-count action requires --count <n>"
    exit 2
fi

# Set default environments
if [[ -z "$ENVS_CSV" ]]; then
    if [[ "$ACTION" == "baseline" ]]; then
        ENVS_CSV="dev,stg,prd"
    else
        ENVS_CSV="dev"
    fi
fi

# Parse environments into array
declare -a TARGET_ENVS=()
IFS=',' read -r -a TARGET_ENVS <<< "$ENVS_CSV"
for i in "${!TARGET_ENVS[@]}"; do
    TARGET_ENVS[$i]="$(normalize_env "${TARGET_ENVS[$i]}")"
done

# Validate environments
for env in "${TARGET_ENVS[@]}"; do
    if [[ ! "$env" =~ ^(dev|stg|prd)$ ]]; then
        log_error "Invalid environment: $env (must be dev, stg, or prd)"
        exit 2
    fi
done

# Validate password is set
if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    log_error "MSSQL_LIQUIBASE_TUTORIAL_PWD environment variable is not set"
    exit 1
fi

# Set up paths
LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR
export MSSQL_LIQUIBASE_TUTORIAL_PWD

SNAPSHOT_DIR="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/snapshots"
LB_CMD="$SCRIPT_DIR/lb.sh"

# Validate lb.sh exists
if [[ ! -f "$LB_CMD" ]]; then
    log_error "lb.sh not found at: $LB_CMD"
    exit 1
fi

################################################################################
# Snapshot Function
################################################################################

# Take a snapshot of the current database state
# Arguments:
#   $1 - environment (dev, stg, prd)
#   $2 - action name (for filename)
take_snapshot() {
    local env="$1"
    local action_name="$2"
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local snapshot_file="${SNAPSHOT_DIR}/${env}_${action_name}_${timestamp}.json"
    
    # Ensure snapshot directory exists
    mkdir -p "$SNAPSHOT_DIR"
    
    log_info "Taking snapshot: ${env}_${action_name}_${timestamp}.json"
    
    if "$LB_CMD" -e "$env" -- snapshot \
        --schemas=app \
        --snapshot-format=json \
        --output-file="/data/platform/mssql/database/orderdb/snapshots/${env}_${action_name}_${timestamp}.json" \
        2>&1; then
        log_success "Snapshot saved: $snapshot_file"
        return 0
    else
        log_warn "Failed to create snapshot (deployment was successful)"
        return 1
    fi
}

################################################################################
# Action Functions
################################################################################

# Deploy baseline
# - dev: changelogSync (mark as executed without running)
# - stg/prd: update (actually execute)
# - All: tag as "baseline"
do_baseline() {
    local env="$1"
    local pretty
    pretty=$(pretty_env "$env")
    
    local lb_action="update"
    local action_desc="update - execute changesets"
    
    if [[ "$env" == "dev" ]]; then
        lb_action="changelogSync"
        action_desc="changelogSync - mark as executed"
    fi
    
    log_info "Deploying baseline to $pretty ($action_desc)..."
    
    # Deploy
    if ! "$LB_CMD" -e "$env" -- "$lb_action" 2>&1; then
        log_error "Failed to deploy baseline to $pretty"
        return 1
    fi
    
    # Tag as baseline
    log_info "Tagging as 'baseline'..."
    if ! "$LB_CMD" -e "$env" -- tag baseline 2>&1; then
        # Tag might already exist (idempotent)
        log_warn "Tag 'baseline' may already exist in $pretty"
    fi
    
    log_success "Baseline deployed to $pretty"
    return 0
}

# Deploy updates (pending changesets)
do_update() {
    local env="$1"
    local pretty
    pretty=$(pretty_env "$env")
    
    log_info "Deploying updates to $pretty..."
    
    if "$LB_CMD" -e "$env" -- update 2>&1; then
        log_success "Updates deployed to $pretty"
        return 0
    else
        log_error "Failed to deploy updates to $pretty"
        return 1
    fi
}

# Rollback to a specific tag
do_rollback() {
    local env="$1"
    local tag="$2"
    local pretty
    pretty=$(pretty_env "$env")
    
    log_info "Rolling back $pretty to tag '$tag'..."
    
    if "$LB_CMD" -e "$env" -- rollback "$tag" 2>&1; then
        log_success "Rolled back $pretty to '$tag'"
        return 0
    else
        log_error "Failed to rollback $pretty to '$tag'"
        return 1
    fi
}

# Rollback last N changesets
do_rollback_count() {
    local env="$1"
    local count="$2"
    local pretty
    pretty=$(pretty_env "$env")
    
    log_info "Rolling back last $count changeset(s) in $pretty..."
    
    if "$LB_CMD" -e "$env" -- rollbackCount "$count" 2>&1; then
        log_success "Rolled back last $count changeset(s) in $pretty"
        return 0
    else
        log_error "Failed to rollback in $pretty"
        return 1
    fi
}

# Show status (pending changesets)
do_status() {
    local env="$1"
    local pretty
    pretty=$(pretty_env "$env")
    
    log_info "Checking status in $pretty..."
    
    "$LB_CMD" -e "$env" -- status --verbose 2>&1
    return $?
}

################################################################################
# Main Execution
################################################################################

echo "========================================"
echo "Liquibase Deployment"
echo "========================================"
echo
echo "Action:       $ACTION"
echo "Environment:  ${TARGET_ENVS[*]}"
if [[ -n "$TAG" ]]; then
    echo "Tag:          $TAG"
fi
if [[ -n "$COUNT" ]]; then
    echo "Count:        $COUNT"
fi
echo "Snapshot:     $TAKE_SNAPSHOT"
echo

cd "$LIQUIBASE_TUTORIAL_DATA_DIR"

# Track results
declare -a SUCCESS_ENVS=()
declare -a FAILED_ENVS=()

for env in "${TARGET_ENVS[@]}"; do
    echo "----------------------------------------"
    echo "Processing: $(pretty_env "$env")"
    echo "----------------------------------------"
    
    action_success=false
    
    case "$ACTION" in
        baseline)
            if do_baseline "$env"; then
                action_success=true
            fi
            ;;
        update)
            if do_update "$env"; then
                action_success=true
            fi
            ;;
        rollback)
            if do_rollback "$env" "$TAG"; then
                action_success=true
            fi
            ;;
        rollback-count)
            if do_rollback_count "$env" "$COUNT"; then
                action_success=true
            fi
            ;;
        status)
            do_status "$env"
            # Status doesn't trigger snapshot
            action_success=true
            TAKE_SNAPSHOT=false
            ;;
    esac
    
    if [[ "$action_success" == "true" ]]; then
        SUCCESS_ENVS+=("$env")
        
        # Take snapshot after successful action (except status)
        if [[ "$TAKE_SNAPSHOT" == "true" ]] && [[ "$ACTION" != "status" ]]; then
            take_snapshot "$env" "$ACTION" || true
        fi
    else
        FAILED_ENVS+=("$env")
    fi
    
    echo
done

################################################################################
# Summary
################################################################################

echo "========================================"
echo "Deployment Summary"
echo "========================================"

if [[ ${#SUCCESS_ENVS[@]} -gt 0 ]]; then
    echo -e "${GREEN}Successful:${NC} ${SUCCESS_ENVS[*]}"
fi

if [[ ${#FAILED_ENVS[@]} -gt 0 ]]; then
    echo -e "${RED}Failed:${NC} ${FAILED_ENVS[*]}"
fi

if [[ "$TAKE_SNAPSHOT" == "true" ]] && [[ "$ACTION" != "status" ]]; then
    echo
    echo "Snapshots saved to:"
    echo "  $SNAPSHOT_DIR/"
fi

echo

if [[ ${#FAILED_ENVS[@]} -gt 0 ]]; then
    log_error "Deployment completed with errors"
    exit 1
else
    log_success "Deployment completed successfully"
    exit 0
fi
