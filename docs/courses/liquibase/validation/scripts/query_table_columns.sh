#!/bin/bash
# Query Table Columns
# Queries columns for a specified table and displays results in a formatted table with borders
# Optionally highlights a specific column

set -u

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 [-e <dev|stg|prd>] [-h <highlight_column>] <schema.table>"
    echo
    echo "Options:"
    echo "  -e <env>              Environment (dev|stg|prd), default: dev"
    echo "  -h <column_name>      Column name to highlight"
    echo
    echo "Examples:"
    echo "  $0 app.customer"
    echo "  $0 -e dev app.customer"
    echo "  $0 -e dev -h loyalty_points app.customer"
}

ENV="dev"
HIGHLIGHT_COLUMN=""

# Parse options
while getopts "e:h:" opt; do
    case $opt in
        e) ENV="$OPTARG" ;;
        h) HIGHLIGHT_COLUMN="$OPTARG" ;;
        *) print_usage; exit 1 ;;
    esac
done
shift $((OPTIND-1))

# Check for table argument
if [[ $# -lt 1 ]]; then
    echo -e "${RED}ERROR: Table name required${NC}"
    print_usage
    exit 1
fi

TABLE_NAME="$1"

# Parse schema and table
if [[ "$TABLE_NAME" == *.* ]]; then
    SCHEMA_NAME="${TABLE_NAME%%.*}"
    TABLE_ONLY="${TABLE_NAME##*.}"
else
    SCHEMA_NAME="dbo"
    TABLE_ONLY="$TABLE_NAME"
fi

echo "========================================"
echo "Querying Table Columns"
echo "========================================"
echo

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
echo "Table: $SCHEMA_NAME.$TABLE_ONLY"
if [[ -n "$HIGHLIGHT_COLUMN" ]]; then
    echo "Highlight: $HIGHLIGHT_COLUMN"
fi
echo

# Query table columns
QUERY="USE orderdb;
SELECT
    c.name AS COLUMN_NAME,
    t.name AS DATA_TYPE,
    CASE WHEN c.is_nullable = 1 THEN 'YES' ELSE 'NO' END AS NULLABLE,
    ISNULL(CAST(c.max_length AS VARCHAR), '') AS MAX_LENGTH,
    ISNULL(d.definition, '') AS DEFAULT_VALUE
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
JOIN sys.tables tb ON c.object_id = tb.object_id
JOIN sys.schemas s ON tb.schema_id = s.schema_id
LEFT JOIN sys.default_constraints d ON c.default_object_id = d.object_id
WHERE s.name = '$SCHEMA_NAME' AND tb.name = '$TABLE_ONLY'
ORDER BY c.column_id;"

echo "Querying columns..."
echo

# Execute query
QUERY_RESULT=$($CR_CMD exec "$CONTAINER_NAME" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
    -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
    -d orderdb \
    -Q "$QUERY" \
    -s "|" -h -1 -W 2>&1)

# Check if query succeeded
if echo "$QUERY_RESULT" | grep -qE "^[a-zA-Z_]+\|"; then
    echo "Columns in $SCHEMA_NAME.$TABLE_ONLY:"
    echo "$QUERY_RESULT" | \
        grep -v "^Warning:" | grep -v "^Msg" | grep -v "rows affected" | grep -v "^---" | grep -v "^$" | \
        grep -v "^+" | grep -vE "^[[:space:]]*\|.*COLUMN_NAME.*\|" | grep -vE "^[[:space:]]*\|.*--.*\|" | \
        awk -F'|' -v highlight="$HIGHLIGHT_COLUMN" 'BEGIN {
            header_printed=0
            yellow="\033[1;33m"
            nc="\033[0m"
        }
        NF>=5 {
            col=$1; gsub(/^[ \t]+|[ \t]+$/, "", col)
            dtype=$2; gsub(/^[ \t]+|[ \t]+$/, "", dtype)
            nullable=$3; gsub(/^[ \t]+|[ \t]+$/, "", nullable)
            maxlen=$4; gsub(/^[ \t]+|[ \t]+$/, "", maxlen)
            defval=$5; gsub(/^[ \t]+|[ \t]+$/, "", defval); if (length(defval) > 30) defval = substr(defval, 1, 27) "..."
            # Skip header-like lines
            if (col == "COLUMN_NAME" || col ~ /^--/ || col == "") {
                next
            }
            # Print header only once before first data row
            if (header_printed == 0) {
                printf "+%s+%s+%s+%s+%s+\n", "----------------------", "---------------", "----------", "------------", "--------------------------------"
                printf "|%-22s|%-15s|%-10s|%-12s|%-32s|\n", "COLUMN_NAME", "DATA_TYPE", "NULLABLE", "MAX_LENGTH", "DEFAULT_VALUE"
                printf "+%s+%s+%s+%s+%s+\n", "----------------------", "---------------", "----------", "------------", "--------------------------------"
                header_printed=1
            }
            # Check if this column should be highlighted
            is_highlight = (highlight != "" && col == highlight)
            # Format the row
            formatted_row = sprintf("|%-22s|%-15s|%-10s|%-12s|%-32s|", col, dtype, nullable, maxlen, defval)
            # Print with highlighting if matched
            if (is_highlight) {
                printf "%s%s%s\n", yellow, formatted_row, nc
            } else {
                printf "%s\n", formatted_row
            }
        }
        END {
            if (header_printed == 1) {
                printf "+%s+%s+%s+%s+%s+\n", "----------------------", "---------------", "----------", "------------", "--------------------------------"
            }
        }'
    
    # Count columns
    COL_COUNT=$(echo "$QUERY_RESULT" | grep -E "^[a-zA-Z_]+\|" | wc -l | tr -d ' ')
    echo
    echo "Total columns: $COL_COUNT"
else
    echo -e "${RED}ERROR: Failed to query table columns${NC}"
    echo "Query output:"
    echo "$QUERY_RESULT"
    exit 1
fi

echo
echo "========================================"
echo -e "${GREEN}QUERY COMPLETE${NC}"
echo "========================================"
