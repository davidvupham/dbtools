#!/bin/bash
################################################################################
# query_databasechangelog.sh - Query DATABASECHANGELOG
################################################################################
#
# PURPOSE:
#   Queries DATABASECHANGELOG and displays results in a formatted table with
#   borders. Reusable across all tutorial parts.
#
# USAGE:
#   query_databasechangelog.sh --db <instance>
#
# OPTIONS:
#   -d, --db <instance>     Target database instance (required)
#                           Values: mssql_dev, mssql_stg, mssql_prd
#   -h, --help              Show this help message
#
# EXAMPLES:
#   query_databasechangelog.sh --db mssql_dev
#   query_databasechangelog.sh --db mssql_stg
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
  query_databasechangelog.sh --db <instance>

Options:
  -d, --db <instance>     Target database instance (required)
                          Values: mssql_dev, mssql_stg, mssql_prd
  -h, --help              Show this help message

Examples:
  query_databasechangelog.sh --db mssql_dev
  query_databasechangelog.sh --db mssql_stg
EOF
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

INSTANCE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--db|--database|--instance)
            INSTANCE="$2"
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

# Validate database instance (required)
if [[ -z "$INSTANCE" ]]; then
    echo -e "${RED}ERROR: Database instance required. Use --db <instance>${NC}"
    echo -e "${RED}Valid instances: mssql_dev, mssql_stg, mssql_prd${NC}"
    print_usage
    exit 2
fi

# Validate instance name
VALID_INSTANCES="mssql_dev mssql_stg mssql_prd"
if [[ ! " $VALID_INSTANCES " =~ " $INSTANCE " ]]; then
    echo -e "${RED}ERROR: Invalid database instance: $INSTANCE${NC}"
    echo -e "${RED}Valid instances: $VALID_INSTANCES${NC}"
    exit 2
fi

echo "========================================"
echo "Querying DATABASECHANGELOG"
echo "========================================"
echo
echo "Instance: $(pretty_instance "$INSTANCE")"
echo

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
    echo -e "${RED}ERROR: No container runtime found (docker or podman)${NC}"
    exit 1
fi

CONTAINER_NAME="$INSTANCE"

# Check container is running
if ! $CR_CMD ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}ERROR: Container $CONTAINER_NAME is not running${NC}"
    exit 1
fi

echo "Container: $CONTAINER_NAME"
echo

# Query DATABASECHANGELOG
QUERY="USE orderdb;
SELECT
    ID,
    AUTHOR,
    FILENAME,
    DATEEXECUTED,
    TAG,
    EXECTYPE
FROM DATABASECHANGELOG
ORDER BY ORDEREXECUTED DESC;"

echo "Querying DATABASECHANGELOG..."
echo

# Execute query and format output with borders
# Use -s "|" for pipe separator, -h -1 to suppress headers, -W to remove trailing spaces
QUERY_RESULT=$($CR_CMD exec "$CONTAINER_NAME" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
    -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
    -d orderdb \
    -Q "$QUERY" \
    -s "|" -h -1 -W 2>&1)

# Check if query succeeded
if echo "$QUERY_RESULT" | grep -qE "^[A-Z0-9-]+\|"; then
    # Format and display as table with borders
    echo "DATABASECHANGELOG entries:"
    echo "$QUERY_RESULT" | \
        grep -v "^Warning:" | grep -v "^Msg" | grep -v "rows affected" | grep -v "^---" | grep -v "^$" | \
        grep -v "^+" | grep -vE "^[[:space:]]*\|.*ID.*\|.*AUTHOR.*\|" | grep -vE "^[[:space:]]*\|.*--.*\|" | \
        awk -F'|' 'BEGIN {
            header_printed=0
            yellow="\033[1;33m"
            nc="\033[0m"
        }
        NF>=6 {
            id=$1; gsub(/^[ \t]+|[ \t]+$/, "", id); if (length(id) > 25) id = substr(id, 1, 22) "..."
            author=$2; gsub(/^[ \t]+|[ \t]+$/, "", author)
            filename=$3; gsub(/^[ \t]+|[ \t]+$/, "", filename); if (length(filename) > 50) filename = substr(filename, 1, 47) "..."
            date=$4; gsub(/^[ \t]+|[ \t]+$/, "", date)
            tag=$5; gsub(/^[ \t]+|[ \t]+$/, "", tag); if (tag == "NULL" || tag == "") tag = ""
            exectype=$6; gsub(/^[ \t]+|[ \t]+$/, "", exectype)
            # Skip header-like lines, separator lines, and empty lines
            if (id == "ID" || author == "AUTHOR" || id ~ /^--/ || author ~ /^--/ || id == "" || author == "") {
                next
            }
            # Print header only once before first data row
            if (header_printed == 0) {
                printf "+%s+%s+%s+%s+%s+%s+\n", "-------------------------", "--------------------", "--------------------------------------------------", "-------------------------", "---------------", "----------"
                printf "|%-25s|%-20s|%-50s|%-25s|%-15s|%-10s|\n", "ID", "AUTHOR", "FILENAME", "DATEEXECUTED", "TAG", "EXECTYPE"
                printf "+%s+%s+%s+%s+%s+%s+\n", "-------------------------", "--------------------", "--------------------------------------------------", "-------------------------", "---------------", "----------"
                header_printed=1
            }
            # Check if row has a release tag (highlight only release tags, not baseline)
            is_release_tag = (tag != "" && tag != "NULL" && tag ~ /^release-/)
            # Format the row first (without color codes affecting width)
            formatted_row = sprintf("|%-25s|%-20s|%-50s|%-25s|%-15s|%-10s|", id, author, filename, date, tag, exectype)
            # Print with highlighting if it is a release tag
            if (is_release_tag) {
                printf "%s%s%s\n", yellow, formatted_row, nc
            } else {
                printf "%s\n", formatted_row
            }
        }
        END {
            if (header_printed == 1) {
                printf "+%s+%s+%s+%s+%s+%s+\n", "-------------------------", "--------------------", "--------------------------------------------------", "-------------------------", "---------------", "----------"
            }
        }'
    
    # Count entries
    ENTRY_COUNT=$(echo "$QUERY_RESULT" | grep -E "^[A-Z0-9-]+\|" | wc -l | tr -d ' ')
    echo
    echo "Total entries: $ENTRY_COUNT"
else
    echo -e "${RED}ERROR: Failed to query DATABASECHANGELOG${NC}"
    echo "Query output:"
    echo "$QUERY_RESULT"
    exit 1
fi

echo
echo "========================================"
echo -e "${GREEN}QUERY COMPLETE${NC}"
echo "========================================"
