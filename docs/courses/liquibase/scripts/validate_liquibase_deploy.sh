#!/bin/bash
################################################################################
# validate_liquibase_deploy.sh - Validate Liquibase Baseline Deployment
################################################################################
#
# PURPOSE:
#   Validates that baseline is deployed to specified database instances and
#   tracked in Liquibase. Reusable across all tutorial parts.
#
# USAGE:
#   validate_liquibase_deploy.sh --db <instances>
#
# OPTIONS:
#   -d, --db <instances>    Target database instance(s) - comma-separated (required)
#                           Values: mssql_dev, mssql_stg, mssql_prd
#   -h, --help              Show this help message
#
# EXAMPLES:
#   # Validate all database instances
#   validate_liquibase_deploy.sh --db mssql_dev,mssql_stg,mssql_prd
#
#   # Validate specific instance
#   validate_liquibase_deploy.sh --db mssql_dev
#
################################################################################

set -u

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

################################################################################
# Helper Functions
################################################################################

print_usage() {
    cat <<'EOF'
Usage:
  validate_liquibase_deploy.sh --db <instances>

Options:
  -d, --db <instances>    Target database instance(s) - comma-separated (required)
                          Values: mssql_dev, mssql_stg, mssql_prd
  -h, --help              Show this help message

Examples:
  validate_liquibase_deploy.sh --db mssql_dev,mssql_stg,mssql_prd
  validate_liquibase_deploy.sh --db mssql_dev
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

################################################################################
# Argument Parsing
################################################################################

INSTANCES_CSV=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--db|--database|--instances)
            INSTANCES_CSV="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}ERROR: Unknown option: $1${NC}"
            print_usage
            exit 2
            ;;
    esac
done

################################################################################
# Validation
################################################################################

# Validate database instances (required)
if [[ -z "$INSTANCES_CSV" ]]; then
    echo -e "${RED}ERROR: Database instance(s) required. Use --db <instances>${NC}"
    echo -e "${RED}Valid instances: mssql_dev, mssql_stg, mssql_prd${NC}"
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
        echo -e "${RED}ERROR: Invalid database instance: $instance${NC}"
        echo -e "${RED}Valid instances: $VALID_INSTANCES${NC}"
        exit 2
    fi
done

echo "========================================"
echo "Validating Liquibase Baseline Deployment"
echo "========================================"
echo
echo "Instances: ${TARGET_INSTANCES[*]}"
echo

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"

# Load port assignments from .ports file if it exists
PORTS_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
if [[ -f "$PORTS_FILE" ]]; then
    source "$PORTS_FILE"
fi

# Use ports from .ports file, or fall back to defaults
MSSQL_DEV_PORT="${MSSQL_DEV_PORT:-14331}"
MSSQL_STG_PORT="${MSSQL_STG_PORT:-14332}"
MSSQL_PRD_PORT="${MSSQL_PRD_PORT:-14333}"

# Check if baseline file exists (prerequisite)
BASELINE_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/baseline/V0000__baseline.mssql.sql"
if [[ ! -f "$BASELINE_FILE" ]]; then
    echo -e "${RED}ERROR: Baseline file not found: $BASELINE_FILE${NC}"
    echo "Run generate_liquibase_baseline.sh first"
    exit 1
fi

# Check if master changelog exists (prerequisite)
CHANGELOG_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml"
if [[ ! -f "$CHANGELOG_FILE" ]]; then
    echo -e "${RED}ERROR: Master changelog not found: $CHANGELOG_FILE${NC}"
    echo "Run setup_liquibase_environment.sh first"
    exit 1
fi

FAILURES=0

pass() { echo -e "[${GREEN}PASS${NC}] $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; FAILURES=$((FAILURES+1)); }

# Detect container runtime
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    CR_CMD="docker"
    NETWORK_ARGS="--network=host"
    DB_HOST="localhost"
elif command -v podman &>/dev/null; then
    CR_CMD="podman"
    NETWORK_ARGS="--network slirp4netns:port_handler=slirp4netns"
    DB_HOST="host.containers.internal"
else
    fail "No container runtime found (docker or podman)"
    exit 1
fi

# Volume mount flags: Docker doesn't support :z,U, Podman needs it for SELinux
VOLUME_MOUNT="${LIQUIBASE_TUTORIAL_DATA_DIR}:/data"
if [[ "$CR_CMD" == "podman" ]]; then
    VOLUME_MOUNT="${LIQUIBASE_TUTORIAL_DATA_DIR}:/data:z,U"
fi

echo "Checking Liquibase tracking tables..."
echo

# Check each database instance
for instance in "${TARGET_INSTANCES[@]}"; do
    env=$(instance_to_env "$instance")
    case "$instance" in
        mssql_dev) port="$MSSQL_DEV_PORT";;
        mssql_stg) port="$MSSQL_STG_PORT";;
        mssql_prd) port="$MSSQL_PRD_PORT";;
    esac

    echo "Checking $(pretty_instance "$instance") (port $port)..."

    # Check if DATABASECHANGELOG table exists first
    table_check=$($CR_CMD exec "$instance" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -d orderdb \
        -Q "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'DATABASECHANGELOG';" \
        -h -1 -W 2>&1 | grep -E '^[0-9]+$' | head -1)

    # Check DATABASECHANGELOG table exists and baseline is tracked
    if [[ "$table_check" == "1" ]]; then
        # Table exists, check if any changesets are tracked (baseline should have multiple changesets)
        total_changesets=$($CR_CMD exec "$instance" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
            -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
            -d orderdb \
            -Q "SELECT COUNT(*) FROM DATABASECHANGELOG;" \
            -h -1 -W 2>&1 | grep -E '^[0-9]+$' | head -1)

        # Baseline should have at least 4 changesets (table, constraints, index, view, etc.)
        if [[ "${total_changesets:-0}" -ge 4 ]]; then
            pass "  $instance: Baseline tracked in DATABASECHANGELOG ($total_changesets changesets)"
        elif [[ "${total_changesets:-0}" -gt 0 ]]; then
            # Some changesets exist but might not be complete
            fail "  $instance: DATABASECHANGELOG exists but baseline incomplete ($total_changesets changesets, expected >= 4)"
        else
            fail "  $instance: DATABASECHANGELOG exists but baseline not tracked (0 changesets)"
        fi
    else
        fail "  $instance: DATABASECHANGELOG table not found"
    fi

    # Check objects exist in database (baseline was actually applied)
    echo -n "    Checking baseline objects exist... "
    customer_exists=$($CR_CMD exec "$instance" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -d orderdb \
        -Q "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'app' AND TABLE_NAME = 'customer';" \
        -h -1 -W 2>&1 | grep -E '^[0-9]+$' | head -1)

    if [[ "$customer_exists" == "1" ]]; then
        pass "app.customer table exists"
    else
        fail "app.customer table missing (baseline not deployed)"
    fi

    # Check for baseline tag (only if DATABASECHANGELOG table exists)
    echo -n "    Checking baseline tag... "
    if [[ "$table_check" == "1" ]]; then
        # Get tag data from DATABASECHANGELOG - show the changeset with the tag
        # Use -h -1 to suppress headers, -s "|" for pipe separator, and -W to remove trailing spaces
        tag_query_result=$($CR_CMD exec "$instance" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
            -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
            -d orderdb \
            -Q "SELECT TOP 1 ID, AUTHOR, FILENAME, TAG, DATEEXECUTED, EXECTYPE FROM DATABASECHANGELOG WHERE TAG IS NOT NULL AND TAG = 'baseline' ORDER BY ORDEREXECUTED DESC;" \
            -h -1 -s "|" -W 2>&1)

        # Check if baseline tag exists in the result
        if echo "$tag_query_result" | grep -qi "baseline"; then
            pass "Baseline tag found"
            # Format and display as a table with headers
            echo "      Tag data from DATABASECHANGELOG:"
            # Clean up output (remove warnings, metadata, separator lines, sqlcmd box-drawing table) and format as table using awk
            echo "$tag_query_result" | \
                grep -v "^Warning:" | grep -v "^Msg" | grep -v "rows affected" | grep -v "^---" | grep -v "^$" | \
                grep -v "^+" | grep -vE "^[[:space:]]*\|.*ID.*\|.*AUTHOR.*\|" | grep -vE "^[[:space:]]*\|.*--.*\|" | \
                awk -F'|' 'BEGIN {
                    header_printed=0
                }
                NF>=6 {
                    id=$1; gsub(/^[ \t]+|[ \t]+$/, "", id)
                    author=$2; gsub(/^[ \t]+|[ \t]+$/, "", author)
                    filename=$3; gsub(/^[ \t]+|[ \t]+$/, "", filename); if (length(filename) > 50) filename = substr(filename, 1, 47) "..."
                    tag=$4; gsub(/^[ \t]+|[ \t]+$/, "", tag)
                    date=$5; gsub(/^[ \t]+|[ \t]+$/, "", date)
                    exectype=$6; gsub(/^[ \t]+|[ \t]+$/, "", exectype)
                    # Skip header-like lines, separator lines, and empty lines
                    if (id == "ID" || author == "AUTHOR" || id ~ /^--/ || author ~ /^--/ || id == "" || author == "") {
                        next
                    }
                    # Print header only once before first data row
                    if (header_printed == 0) {
                        printf "        +%s+%s+%s+%s+%s+%s+\n", "--------------------", "--------------------", "--------------------------------------------------", "----------", "-------------------------", "----------"
                        printf "        |%-20s|%-20s|%-50s|%-10s|%-25s|%-10s|\n", "ID", "AUTHOR", "FILENAME", "TAG", "DATEEXECUTED", "EXECTYPE"
                        printf "        +%s+%s+%s+%s+%s+%s+\n", "--------------------", "--------------------", "--------------------------------------------------", "----------", "-------------------------", "----------"
                        header_printed=1
                    }
                    # Print data row
                    printf "        |%-20s|%-20s|%-50s|%-10s|%-25s|%-10s|\n", id, author, filename, tag, date, exectype
                }
                END {
                    # Print bottom border if we printed any data
                    if (header_printed == 1) {
                        printf "        +%s+%s+%s+%s+%s+%s+\n", "--------------------", "--------------------", "--------------------------------------------------", "----------", "-------------------------", "----------"
                    }
                }'
        else
            # Baseline is tracked but not tagged - suggest tagging
            fail "Baseline tag not found. Baseline changesets are tracked, but tag is missing. Run: lb -e $env -- tag baseline"
        fi
    else
        fail "Baseline tag not found (run: lb -e $env -- tag baseline)"
    fi

    echo
done

echo "========================================"
if [[ "$FAILURES" -eq 0 ]]; then
    echo -e "${GREEN}VALIDATION SUCCESSFUL${NC}"
    echo "========================================"
    echo
    echo "Expected output summary:"
    echo "  ✓ DATABASECHANGELOG table exists in all validated instances"
    echo "  ✓ Baseline changesets tracked in all validated instances"
    echo "  ✓ Baseline objects (app.customer) exist in all validated instances"
    echo "  ✓ Baseline tag created in all validated instances"
    echo
    echo "For mssql_dev: Changes marked as EXECUTED (changelogSync)"
    echo "For mssql_stg/mssql_prd: Changes executed (update)"
    echo
    exit 0
else
    echo -e "${RED}VALIDATION FAILED ($FAILURES errors)${NC}"
    echo "========================================"
    echo
    echo "Common issues and fixes:"
    echo
    echo "If baseline changesets are tracked but tags are missing:"
    echo "  lb -e dev -- tag baseline"
    echo "  lb -e stg -- tag baseline"
    echo "  lb -e prd -- tag baseline"
    echo
    echo "If baseline is not deployed yet:"
    echo "  \$LIQUIBASE_TUTORIAL_DIR/scripts/deploy.sh --action baseline --db mssql_dev,mssql_stg,mssql_prd"
    echo
    echo "Or deploy manually:"
    echo "  1. mssql_dev: lb -e dev -- changelogSync && lb -e dev -- tag baseline"
    echo "  2. mssql_stg: lb -e stg -- update && lb -e stg -- tag baseline"
    echo "  3. mssql_prd: lb -e prd -- update && lb -e prd -- tag baseline"
    echo
    exit 1
fi
