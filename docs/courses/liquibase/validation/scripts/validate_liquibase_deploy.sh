#!/bin/bash
# Validate Liquibase Baseline Deployment
# Validates that baseline is deployed to all environments and tracked in Liquibase
# Reusable across all tutorial parts

set -u

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Validating Liquibase Baseline Deployment"
echo "========================================"
echo

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"

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

# Check each environment
for env in dev stg prd; do
    port=$((14331 + $(echo "dev stg prd" | tr ' ' '\n' | grep -n "^${env}$" | cut -d: -f1) - 1))

    echo "Checking $env environment (port $port)..."

    # Check if DATABASECHANGELOG table exists first
    table_check=$($CR_CMD exec "mssql_${env}" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -d orderdb \
        -Q "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'DATABASECHANGELOG';" \
        -h -1 -W 2>&1 | grep -E '^[0-9]+$' | head -1)

    # Check DATABASECHANGELOG table exists and baseline is tracked
    if [[ "$table_check" == "1" ]]; then
        # Table exists, check if any changesets are tracked (baseline should have multiple changesets)
        total_changesets=$($CR_CMD exec "mssql_${env}" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
            -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
            -d orderdb \
            -Q "SELECT COUNT(*) FROM DATABASECHANGELOG;" \
            -h -1 -W 2>&1 | grep -E '^[0-9]+$' | head -1)

        # Baseline should have at least 4 changesets (table, constraints, index, view, etc.)
        if [[ "${total_changesets:-0}" -ge 4 ]]; then
            pass "  $env: Baseline tracked in DATABASECHANGELOG ($total_changesets changesets)"
        elif [[ "${total_changesets:-0}" -gt 0 ]]; then
            # Some changesets exist but might not be complete
            fail "  $env: DATABASECHANGELOG exists but baseline incomplete ($total_changesets changesets, expected >= 4)"
        else
            fail "  $env: DATABASECHANGELOG exists but baseline not tracked (0 changesets)"
        fi
    else
        fail "  $env: DATABASECHANGELOG table not found"
    fi

    # Check objects exist in database (baseline was actually applied)
    echo -n "    Checking baseline objects exist... "
    customer_exists=$($CR_CMD exec "mssql_${env}" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
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
        tag_query_result=$($CR_CMD exec "mssql_${env}" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
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
    echo "  ✓ DATABASECHANGELOG table exists in all environments"
    echo "  ✓ Baseline changesets tracked in all environments"
    echo "  ✓ Baseline objects (app.customer) exist in all environments"
    echo "  ✓ Baseline tag created in all environments"
    echo
    echo "For dev: Changes marked as EXECUTED (changelogSync)"
    echo "For stg/prd: Changes executed (update)"
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
    echo "  $LIQUIBASE_TUTORIAL_DIR/scripts/deploy_liquibase_baseline.sh"
    echo
    echo "Or deploy manually:"
    echo "  1. Dev: lb -e dev -- changelogSync && lb -e dev -- tag baseline"
    echo "  2. Stg: lb -e stg -- update && lb -e stg -- tag baseline"
    echo "  3. Prd: lb -e prd -- update && lb -e prd -- tag baseline"
    echo
    exit 1
fi
