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
#   - Each snapshot filename includes: instance, action, and timestamp
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
#   deploy.sh --action <action> --db <instances> [options]
#
# OPTIONS:
#   -a, --action <action>   Action to perform (required)
#                           Values: baseline, update, rollback, rollback-count, status
#   -d, --db <instances>    Target database instance(s) - comma-separated (required)
#                           Values: mssql_dev, mssql_stg, mssql_prd
#   -t, --tag <tag>         Tag name for rollback action (required for rollback)
#   -c, --count <n>         Number of changesets for rollback-count (required for rollback-count)
#   --no-snapshot           Skip snapshot creation (not recommended)
#   -h, --help              Show this help message
#
# EXAMPLES:
#   # Deploy baseline to all database instances
#   deploy.sh --action baseline --db mssql_dev,mssql_stg,mssql_prd
#
#   # Deploy baseline to dev only
#   deploy.sh --action baseline --db mssql_dev
#
#   # Deploy pending changesets to dev
#   deploy.sh --action update --db mssql_dev
#
#   # Deploy to multiple instances
#   deploy.sh --action update --db mssql_dev,mssql_stg
#
#   # Rollback dev to baseline tag
#   deploy.sh --action rollback --db mssql_dev --tag baseline
#
#   # Rollback last 1 changeset in dev
#   deploy.sh --action rollback-count --db mssql_dev --count 1
#
#   # Check pending changesets (no snapshot)
#   deploy.sh --action status --db mssql_dev
#
# SNAPSHOT NAMING:
#   Format: {instance}_{action}_{YYYYMMDD}_{HHMMSS}.json
#   Examples:
#     mssql_dev_baseline_20260112_050000.json
#     mssql_dev_update_20260112_053000.json
#     mssql_stg_rollback_20260112_060000.json
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

# Extract environment from database instance name (mssql_dev -> dev)
instance_to_env() {
    local instance="${1//[[:space:]]/}"
    case "$instance" in
        mssql_dev) echo "dev" ;;
        mssql_stg) echo "stg" ;;
        mssql_prd) echo "prd" ;;
        *)         echo "" ;;
    esac
}

# Get human-readable instance name
pretty_instance() {
    case "$1" in
        mssql_dev) echo "Development (mssql_dev)" ;;
        mssql_stg) echo "Staging (mssql_stg)" ;;
        mssql_prd) echo "Production (mssql_prd)" ;;
        *)         echo "$1" ;;
    esac
}

################################################################################
# Argument Parsing
################################################################################

ACTION=""
INSTANCES_CSV=""
TAG=""
COUNT=""
TAKE_SNAPSHOT=true

while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--action)
            ACTION="$2"
            shift 2
            ;;
        -d|--db|--database|--instances)
            INSTANCES_CSV="$2"
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

# Validate database instances (required)
if [[ -z "$INSTANCES_CSV" ]]; then
    log_error "Database instance(s) required. Use --db <instances>"
    log_error "Valid instances: mssql_dev, mssql_stg, mssql_prd"
    print_usage
    exit 2
fi

# Parse instances into array
declare -a TARGET_INSTANCES=()
IFS=',' read -r -a TARGET_INSTANCES <<< "$INSTANCES_CSV"

# Validate database instances
VALID_INSTANCES="mssql_dev mssql_stg mssql_prd"
for instance in "${TARGET_INSTANCES[@]}"; do
    # Trim whitespace
    instance="${instance//[[:space:]]/}"
    if [[ ! " $VALID_INSTANCES " =~ " $instance " ]]; then
        log_error "Invalid database instance: $instance"
        log_error "Valid instances: $VALID_INSTANCES"
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
#   $1 - database instance (mssql_dev, mssql_stg, mssql_prd)
#   $2 - action name (for filename)
take_snapshot() {
    local instance="$1"
    local action_name="$2"
    local env
    env=$(instance_to_env "$instance")
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local snapshot_file="${SNAPSHOT_DIR}/${instance}_${action_name}_${timestamp}.json"
    
    # Ensure snapshot directory exists
    mkdir -p "$SNAPSHOT_DIR"
    
    log_info "Taking snapshot: ${instance}_${action_name}_${timestamp}.json"
    
    if "$LB_CMD" --db "$instance" -- snapshot \
        --schemas=app \
        --snapshot-format=json \
        --output-file="/data/platform/mssql/database/orderdb/snapshots/${instance}_${action_name}_${timestamp}.json" \
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
# - mssql_dev: changelogSync (mark as executed without running)
# - mssql_stg/mssql_prd: update (actually execute)
# - All: tag as "baseline"
do_baseline() {
    local instance="$1"
    local pretty
    pretty=$(pretty_instance "$instance")
    
    local lb_action="update"
    local action_desc="update - execute changesets"
    
    if [[ "$instance" == "mssql_dev" ]]; then
        lb_action="changelogSync"
        action_desc="changelogSync - mark as executed"
    fi
    
    log_info "Deploying baseline to $pretty ($action_desc)..."
    
    # Deploy
    if ! "$LB_CMD" --db "$instance" -- "$lb_action" 2>&1; then
        log_error "Failed to deploy baseline to $pretty"
        return 1
    fi
    
    # Tag as baseline
    log_info "Tagging as 'baseline'..."
    if ! "$LB_CMD" --db "$instance" -- tag baseline 2>&1; then
        # Tag might already exist (idempotent)
        log_warn "Tag 'baseline' may already exist in $pretty"
    fi
    
    log_success "Baseline deployed to $pretty"
    return 0
}

# Deploy updates (pending changesets)
do_update() {
    local instance="$1"
    local pretty
    pretty=$(pretty_instance "$instance")
    
    log_info "Deploying updates to $pretty..."
    
    if "$LB_CMD" --db "$instance" -- update 2>&1; then
        log_success "Updates deployed to $pretty"
        return 0
    else
        log_error "Failed to deploy updates to $pretty"
        return 1
    fi
}

# Rollback to a specific tag
do_rollback() {
    local instance="$1"
    local tag="$2"
    local pretty
    pretty=$(pretty_instance "$instance")
    
    log_info "Rolling back $pretty to tag '$tag'..."
    
    if "$LB_CMD" --db "$instance" -- rollback "$tag" 2>&1; then
        log_success "Rolled back $pretty to '$tag'"
        return 0
    else
        log_error "Failed to rollback $pretty to '$tag'"
        return 1
    fi
}

# Rollback last N changesets
do_rollback_count() {
    local instance="$1"
    local count="$2"
    local pretty
    pretty=$(pretty_instance "$instance")
    
    log_info "Rolling back last $count changeset(s) in $pretty..."
    
    if "$LB_CMD" --db "$instance" -- rollbackCount "$count" 2>&1; then
        log_success "Rolled back last $count changeset(s) in $pretty"
        return 0
    else
        log_error "Failed to rollback in $pretty"
        return 1
    fi
}

# Show status (pending changesets)
do_status() {
    local instance="$1"
    local pretty
    pretty=$(pretty_instance "$instance")
    
    log_info "Checking status in $pretty..."
    
    "$LB_CMD" --db "$instance" -- status --verbose 2>&1
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
echo "Instances:    ${TARGET_INSTANCES[*]}"
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
declare -a SUCCESS_INSTANCES=()
declare -a FAILED_INSTANCES=()

for instance in "${TARGET_INSTANCES[@]}"; do
    echo "----------------------------------------"
    echo "Processing: $(pretty_instance "$instance")"
    echo "----------------------------------------"
    
    action_success=false
    
    case "$ACTION" in
        baseline)
            if do_baseline "$instance"; then
                action_success=true
            fi
            ;;
        update)
            if do_update "$instance"; then
                action_success=true
            fi
            ;;
        rollback)
            if do_rollback "$instance" "$TAG"; then
                action_success=true
            fi
            ;;
        rollback-count)
            if do_rollback_count "$instance" "$COUNT"; then
                action_success=true
            fi
            ;;
        status)
            do_status "$instance"
            # Status doesn't trigger snapshot
            action_success=true
            TAKE_SNAPSHOT=false
            ;;
    esac
    
    if [[ "$action_success" == "true" ]]; then
        SUCCESS_INSTANCES+=("$instance")
        
        # Take snapshot after successful action (except status)
        if [[ "$TAKE_SNAPSHOT" == "true" ]] && [[ "$ACTION" != "status" ]]; then
            take_snapshot "$instance" "$ACTION" || true
        fi
    else
        FAILED_INSTANCES+=("$instance")
    fi
    
    echo
done

################################################################################
# Summary
################################################################################

echo "========================================"
echo "Deployment Summary"
echo "========================================"

if [[ ${#SUCCESS_INSTANCES[@]} -gt 0 ]]; then
    echo -e "${GREEN}Successful:${NC} ${SUCCESS_INSTANCES[*]}"
fi

if [[ ${#FAILED_INSTANCES[@]} -gt 0 ]]; then
    echo -e "${RED}Failed:${NC} ${FAILED_INSTANCES[*]}"
fi

if [[ "$TAKE_SNAPSHOT" == "true" ]] && [[ "$ACTION" != "status" ]]; then
    echo
    echo "Snapshots saved to:"
    echo "  $SNAPSHOT_DIR/"
fi

echo

if [[ ${#FAILED_INSTANCES[@]} -gt 0 ]]; then
    log_error "Deployment completed with errors"
    exit 1
else
    log_success "Deployment completed successfully"
    exit 0
fi
