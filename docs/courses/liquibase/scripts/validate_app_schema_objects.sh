#!/bin/bash
################################################################################
# validate_app_schema_objects.sh - Validate App Schema Objects
################################################################################
#
# PURPOSE:
#   Validates objects in the app schema and displays them in a formatted table
#   with borders. Reusable across all tutorial parts.
#
# USAGE:
#   validate_app_schema_objects.sh --db <instance>
#
# OPTIONS:
#   -d, --db <instance>     Target database instance (required)
#                           Values: mssql_dev, mssql_stg, mssql_prd
#   -h, --help              Show this help message
#
# EXAMPLES:
#   validate_app_schema_objects.sh --db mssql_dev
#   validate_app_schema_objects.sh --db mssql_stg
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
  validate_app_schema_objects.sh --db <instance>

Options:
  -d, --db <instance>     Target database instance (required)
                          Values: mssql_dev, mssql_stg, mssql_prd
  -h, --help              Show this help message

Examples:
  validate_app_schema_objects.sh --db mssql_dev
  validate_app_schema_objects.sh --db mssql_stg
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
echo "Validating App Schema Objects"
echo "========================================"
echo
echo "Instance: $(pretty_instance "$INSTANCE")"
echo

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    echo -e "${RED}ERROR: MSSQL_LIQUIBASE_TUTORIAL_PWD not set${NC}"
    exit 1
fi

FAILURES=0

pass() { echo -e "[${GREEN}PASS${NC}] $1"; }
fail() { echo -e "[${RED}FAIL${NC}] $1"; FAILURES=$((FAILURES+1)); }
warn() { echo -e "[${YELLOW}WARN${NC}] $1"; }

# Detect container runtime
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    CR_CMD="docker"
elif command -v podman &>/dev/null; then
    CR_CMD="podman"
else
    fail "No container runtime found (docker or podman)"
    exit 1
fi

CONTAINER_NAME="$INSTANCE"

# Check container is running
if ! $CR_CMD ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    fail "Container $CONTAINER_NAME is not running"
    exit 1
fi

echo "Container: $CONTAINER_NAME"
echo

# Query objects in app schema
QUERY="USE orderdb;
SELECT
    SCHEMA_NAME(schema_id) AS SchemaName,
    name AS ObjectName,
    type_desc AS ObjectType
FROM sys.objects
WHERE schema_id = SCHEMA_ID('app')
ORDER BY type_desc, name;"

echo "Querying objects in app schema..."
echo

# Execute query and format output with borders
# Use -s "|" for pipe separator, -h -1 to suppress headers, -W to remove trailing spaces
QUERY_RESULT=$($CR_CMD exec "$CONTAINER_NAME" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
    -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
    -d orderdb \
    -Q "$QUERY" \
    -s "|" -h -1 -W 2>&1)

# Check if query succeeded (look for expected output patterns)
if echo "$QUERY_RESULT" | grep -qE "^app\|"; then
    # Format and display as table with borders
    echo "Objects in app schema:"
    echo "$QUERY_RESULT" | \
        grep -v "^Warning:" | grep -v "^Msg" | grep -v "rows affected" | grep -v "^---" | grep -v "^$" | \
        grep -v "^+" | grep -vE "^[[:space:]]*\|.*SchemaName.*\|.*ObjectName.*\|" | grep -vE "^[[:space:]]*\|.*--.*\|" | \
        awk -F'|' 'BEGIN {
            header_printed=0
        }
        NF>=3 {
            schema=$1; gsub(/^[ \t]+|[ \t]+$/, "", schema)
            objname=$2; gsub(/^[ \t]+|[ \t]+$/, "", objname)
            objtype=$3; gsub(/^[ \t]+|[ \t]+$/, "", objtype)
            # Skip header-like lines, separator lines, and empty lines
            if (schema == "SchemaName" || objname == "ObjectName" || schema ~ /^--/ || objname ~ /^--/ || schema == "" || objname == "") {
                next
            }
            # Truncate long object names for display
            if (length(objname) > 40) objname = substr(objname, 1, 37) "..."
            # Print header only once before first data row
            if (header_printed == 0) {
                printf "+%-13s+%-43s+%-30s+\n", "-------------", "-------------------------------------------", "------------------------------"
                printf "|%-13s|%-43s|%-30s|\n", "SchemaName", "ObjectName", "ObjectType"
                printf "+%-13s+%-43s+%-30s+\n", "-------------", "-------------------------------------------", "------------------------------"
                header_printed=1
            }
            # Print data row
            printf "|%-13s|%-43s|%-30s|\n", schema, objname, objtype
        }
        END {
            if (header_printed == 1) {
                printf "+%-13s+%-43s+%-30s+\n", "-------------", "-------------------------------------------", "------------------------------"
            }
        }'
    
    # Count objects
    OBJECT_COUNT=$(echo "$QUERY_RESULT" | grep -E "^app\|" | wc -l | tr -d ' ')
    echo
    echo "Total objects: $OBJECT_COUNT"
    
    # Check for expected objects (basic validation)
    if echo "$QUERY_RESULT" | grep -q "customer"; then
        pass "customer table found"
    else
        fail "customer table not found"
    fi
    
    if echo "$QUERY_RESULT" | grep -q "orders"; then
        pass "orders table found"
    else
        warn "orders table not found (may not be deployed yet)"
    fi
else
    fail "Failed to query objects in app schema"
    echo "Query output:"
    echo "$QUERY_RESULT"
    exit 1
fi

echo
echo "========================================"
if [[ "$FAILURES" -eq 0 ]]; then
    echo -e "${GREEN}VALIDATION SUCCESSFUL${NC}"
    echo "========================================"
    exit 0
else
    echo -e "${RED}VALIDATION FAILED ($FAILURES errors)${NC}"
    echo "========================================"
    exit 1
fi
