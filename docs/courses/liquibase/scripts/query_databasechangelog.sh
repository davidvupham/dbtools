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
#   query_databasechangelog.sh --dbi <instances>
#
# OPTIONS:
#   -d, --dbi <instances>    Target database instance(s) - comma-separated (required)
#                           Values: mssql_dev, mssql_stg, mssql_prd
#   -h, --help              Show this help message
#
# EXAMPLES:
#   query_databasechangelog.sh --dbi mssql_dev
#   query_databasechangelog.sh --dbi mssql_dev,mssql_stg,mssql_prd
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
  query_databasechangelog.sh --dbi <instances>

Options:
  -d, --dbi <instances>    Target database instance(s) - comma-separated (required)
                          Values: mssql_dev, mssql_stg, mssql_prd
  -h, --help              Show this help message

Examples:
  query_databasechangelog.sh --dbi mssql_dev
  query_databasechangelog.sh --dbi mssql_dev,mssql_stg,mssql_prd
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

INSTANCES_CSV=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--dbi|--database|--instances)
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
    echo -e "${RED}ERROR: Database instance(s) required. Use --dbi <instances>${NC}"
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

################################################################################
# Query Function
################################################################################

query_instance() {
    local instance="$1"
    local container_name="$instance"
    
    echo "========================================"
    echo "Querying DATABASECHANGELOG"
    echo "========================================"
    echo
    echo "Instance: $(pretty_instance "$instance")"
    echo
    
    # Check container is running
    if ! $CR_CMD ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        echo -e "${RED}ERROR: Container $container_name is not running${NC}"
        return 1
    fi
    
    echo "Container: $container_name"
    echo
    
    # Query DATABASECHANGELOG
    local query="USE orderdb;
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
    local query_result
    query_result=$($CR_CMD exec "$container_name" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -d orderdb \
        -Q "$query" \
        -s "|" -h -1 -W 2>&1)
    
    # Check if query succeeded
    if echo "$query_result" | grep -qE "^[A-Z0-9-]+\|"; then
        # Format and display as table with borders
        echo "DATABASECHANGELOG entries:"
        echo "$query_result" | \
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
        local entry_count
        entry_count=$(echo "$query_result" | grep -E "^[A-Z0-9-]+\|" | wc -l | tr -d ' ')
        echo
        echo "Total entries: $entry_count"
        echo
        echo -e "${GREEN}QUERY COMPLETE${NC}"
        return 0
    else
        echo -e "${RED}ERROR: Failed to query DATABASECHANGELOG${NC}"
        echo "Query output:"
        echo "$query_result"
        return 1
    fi
}

################################################################################
# Main Execution
################################################################################

FAILURES=0

for instance in "${TARGET_INSTANCES[@]}"; do
    # Trim whitespace
    instance="${instance//[[:space:]]/}"
    
    if ! query_instance "$instance"; then
        FAILURES=$((FAILURES+1))
    fi
    
    echo
done

################################################################################
# Summary
################################################################################

if [[ ${#TARGET_INSTANCES[@]} -gt 1 ]]; then
    echo "========================================"
    echo "Query Summary"
    echo "========================================"
    if [[ "$FAILURES" -eq 0 ]]; then
        echo -e "${GREEN}All instances queried successfully${NC}"
    else
        echo -e "${RED}$FAILURES instance(s) failed${NC}"
    fi
fi

exit $FAILURES
