#!/bin/bash
# Query DATABASECHANGELOG
# Queries DATABASECHANGELOG and displays results in a formatted table with borders
# Reusable across all tutorial parts

set -u

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "Querying DATABASECHANGELOG"
echo "========================================"
echo

ENV="${1:-dev}"

if [[ ! "$ENV" =~ ^(dev|stg|prd)$ ]]; then
    echo -e "${RED}ERROR: Invalid environment '$ENV'. Use dev, stg, or prd${NC}"
    exit 1
fi

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

CONTAINER_NAME="mssql_${ENV}"

# Check container is running
if ! $CR_CMD ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}ERROR: Container $CONTAINER_NAME is not running${NC}"
    exit 1
fi

echo "Environment: $ENV"
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
            # Print data row
            printf "|%-25s|%-20s|%-50s|%-25s|%-15s|%-10s|\n", id, author, filename, date, tag, exectype
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
