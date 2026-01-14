#!/usr/bin/env bash
################################################################################
# detect_drift.sh - Compare database against a known-good snapshot
################################################################################
#
# PURPOSE:
#   Detects drift by comparing a database instance against a known-good snapshot.
#
# USAGE:
#   detect_drift.sh --dbi <instance> [OPTIONS]
#
# OPTIONS:
#   -d, --dbi <instance>   Target database instance (required)
#                          Values: mssql_dev, mssql_stg, mssql_prd
#   -s, --snapshot <path>  Specific snapshot file (default: latest for instance)
#   --schemas <list>       Schemas to compare (default: app)
#   -h, --help             Show this help message
#
# EXAMPLES:
#   detect_drift.sh --dbi mssql_dev
#   detect_drift.sh --dbi mssql_dev --schemas "app,dbo"
#   detect_drift.sh --dbi mssql_prd -s /path/to/snapshot.json
#
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

print_usage() {
    cat <<'EOF'
Usage: detect_drift.sh --dbi <instance> [OPTIONS]

Compare a database against a known-good snapshot to detect drift.

Options:
  -d, --dbi <instance>   Target database instance (required)
                         Values: mssql_dev, mssql_stg, mssql_prd
  -s, --snapshot <path>  Specific snapshot file (default: latest for instance)
  --schemas <list>       Schemas to compare (default: app)
  -h, --help             Show this help message

Examples:
  detect_drift.sh --dbi mssql_dev
  detect_drift.sh --dbi mssql_dev --schemas "app,dbo"
  detect_drift.sh --dbi mssql_prd -s /path/to/snapshot.json

EOF
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

# Defaults
LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR
INSTANCE=""
SNAPSHOT_PATH=""
SCHEMAS="app"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--dbi|--database|--instance)
            INSTANCE="$2"; shift 2;;
        -s|--snapshot)
            SNAPSHOT_PATH="$2"; shift 2;;
        --schemas)
            SCHEMAS="$2"; shift 2;;
        -h|--help)
            print_usage; exit 0;;
        *)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            print_usage
            exit 2;;
    esac
done

# Validate database instance (required)
if [[ -z "$INSTANCE" ]]; then
    echo -e "${RED}Error: Database instance required. Use --dbi <instance>${NC}" >&2
    echo -e "${RED}Valid instances: mssql_dev, mssql_stg, mssql_prd${NC}" >&2
    print_usage
    exit 2
fi

# Validate instance name
VALID_INSTANCES="mssql_dev mssql_stg mssql_prd"
if [[ ! " $VALID_INSTANCES " =~ " $INSTANCE " ]]; then
    echo -e "${RED}Error: Invalid database instance '$INSTANCE'${NC}" >&2
    echo -e "${RED}Valid instances: $VALID_INSTANCES${NC}" >&2
    exit 2
fi

SNAPSHOTS_DIR="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/snapshots"

# Find or validate snapshot
if [[ -z "$SNAPSHOT_PATH" ]]; then
    # Find latest snapshot for instance
    SNAPSHOT_PATH=$(ls -t "$SNAPSHOTS_DIR/${INSTANCE}"_*.json 2>/dev/null | head -1 || true)
    
    if [[ -z "$SNAPSHOT_PATH" ]]; then
        echo -e "${RED}Error: No snapshots found for instance '$INSTANCE'${NC}" >&2
        echo "Expected pattern: $SNAPSHOTS_DIR/${INSTANCE}_*.json"
        echo
        echo "Available snapshots:"
        ls -la "$SNAPSHOTS_DIR"/*.json 2>/dev/null || echo "  (none)"
        exit 1
    fi
else
    # Validate provided snapshot exists
    if [[ ! -f "$SNAPSHOT_PATH" ]]; then
        echo -e "${RED}Error: Snapshot not found: $SNAPSHOT_PATH${NC}" >&2
        exit 1
    fi
fi

echo "========================================"
echo "Liquibase Tutorial - Detect Drift"
echo "========================================"
echo
echo -e "Instance:     ${CYAN}$(pretty_instance "$INSTANCE")${NC}"
echo -e "Snapshot:     ${CYAN}$SNAPSHOT_PATH${NC}"
echo -e "Schemas:      ${CYAN}$SCHEMAS${NC}"
echo

# Convert host path to relative path for Liquibase
# The search-path in properties is /data/platform/mssql/database/orderdb
# Snapshot path must be relative to search-path
SEARCH_PATH_BASE="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb"
RELATIVE_SNAPSHOT_PATH="${SNAPSHOT_PATH#"$SEARCH_PATH_BASE/"}"

echo -e "${YELLOW}Running diff against snapshot...${NC}"
echo

# Create temp file for output
TEMP_OUTPUT=$(mktemp)
trap "rm -f $TEMP_OUTPUT" EXIT

# Run the diff command and capture output
"$SCRIPT_DIR/lb.sh" --dbi "$INSTANCE" -- diff \
    --schemas="$SCHEMAS" \
    --referenceUrl="offline:mssql?snapshot=$RELATIVE_SNAPSHOT_PATH" 2>&1 | tee "$TEMP_OUTPUT"

echo
echo "========================================"
echo -e "${CYAN}Drift Summary${NC}"
echo "========================================"
echo

DRIFT_FOUND=false

# Parse drift using awk - handles the Liquibase output format:
#   "Unexpected Column(s): " followed by indented items on next lines
#   vs "Missing Column(s): NONE" on same line

# Extract Missing items (in snapshot but not in database)
MISSING_ITEMS=$(awk '
    /^Missing [^:]+: *$/ { category=$0; getline; if (/^     /) print category "\n" $0; next }
    /^Missing [^:]+:/ && !/NONE/ { print }
' "$TEMP_OUTPUT" | grep -v "NONE" || true)

if [[ -n "$MISSING_ITEMS" ]]; then
    DRIFT_FOUND=true
    echo -e "${RED}▼ MISSING (in snapshot, not in database):${NC}"
    # Get just the indented items
    awk '
        /^Missing [^:]+: *$/ { category=gensub(/Missing ([^:]+):.*/, "\\1", "g"); in_section=1; next }
        in_section && /^     / { print "  [" category "] " gensub(/^     /, "", "g"); next }
        /^[^ ]/ { in_section=0 }
    ' "$TEMP_OUTPUT" | while IFS= read -r line; do
        echo -e "${RED}$line${NC}"
    done
    echo
fi

# Extract Unexpected items (in database but not in snapshot - drift added)
UNEXPECTED_ITEMS=$(awk '
    /^Unexpected [^:]+: *$/ { category=$0; getline; if (/^     /) print category "\n" $0; next }
    /^Unexpected [^:]+:/ && !/NONE/ { print }
' "$TEMP_OUTPUT" | grep -v "NONE" || true)

if [[ -n "$UNEXPECTED_ITEMS" ]]; then
    DRIFT_FOUND=true
    echo -e "${MAGENTA}▲ UNEXPECTED (in database, not in snapshot):${NC}"
    awk '
        /^Unexpected [^:]+: *$/ { category=gensub(/Unexpected ([^:]+):.*/, "\\1", "g"); in_section=1; next }
        in_section && /^     / { print "  [" category "] " gensub(/^     /, "", "g"); next }
        /^[^ ]/ { in_section=0 }
    ' "$TEMP_OUTPUT" | while IFS= read -r line; do
        echo -e "${MAGENTA}$line${NC}"
    done
    echo
fi

# Extract Changed items
CHANGED_ITEMS=$(awk '
    /^Changed [^:]+: *$/ { category=$0; getline; if (/^     /) print category "\n" $0; next }
    /^Changed [^:]+:/ && !/NONE/ { print }
' "$TEMP_OUTPUT" | grep -v "NONE" || true)

if [[ -n "$CHANGED_ITEMS" ]]; then
    DRIFT_FOUND=true
    echo -e "${YELLOW}● CHANGED (modified since snapshot):${NC}"
    awk '
        /^Changed [^:]+: *$/ { category=gensub(/Changed ([^:]+):.*/, "\\1", "g"); in_section=1; next }
        in_section && /^     / { print "  [" category "] " gensub(/^     /, "", "g"); next }
        /^[^ ]/ { in_section=0 }
    ' "$TEMP_OUTPUT" | while IFS= read -r line; do
        echo -e "${YELLOW}$line${NC}"
    done
    echo
fi

echo "========================================"
if [[ "$DRIFT_FOUND" == "true" ]]; then
    echo -e "${RED}⚠  DRIFT DETECTED${NC}"
    echo "========================================"
    echo
    echo "Legend:"
    echo -e "  ${RED}▼ Missing${NC}    = removed from database (could break app)"
    echo -e "  ${MAGENTA}▲ Unexpected${NC} = added without authorization"
    echo -e "  ${YELLOW}● Changed${NC}    = modified since snapshot"
else
    echo -e "${GREEN}✓  NO DRIFT - database matches snapshot${NC}"
    echo "========================================"
fi
