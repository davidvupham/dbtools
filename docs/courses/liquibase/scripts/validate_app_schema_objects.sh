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
#   validate_app_schema_objects.sh --dbi <instances>
#
# OPTIONS:
#   -d, --dbi <instances>    Target database instance(s) - comma-separated (required)
#                           Values: mssql_dev, mssql_stg, mssql_prd
#   -h, --help              Show this help message
#
# EXAMPLES:
#   validate_app_schema_objects.sh --dbi mssql_dev
#   validate_app_schema_objects.sh --dbi mssql_dev,mssql_stg,mssql_prd
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
  validate_app_schema_objects.sh --dbi <instances>

Options:
  -d, --dbi <instances>    Target database instance(s) - comma-separated (required)
                          Values: mssql_dev, mssql_stg, mssql_prd
  -h, --help              Show this help message

Examples:
  validate_app_schema_objects.sh --dbi mssql_dev
  validate_app_schema_objects.sh --dbi mssql_dev,mssql_stg,mssql_prd
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
# Validation Function
################################################################################

validate_instance() {
    local instance="$1"
    local container_name="$instance"
    local failures=0

    pass() { echo -e "[${GREEN}PASS${NC}] $1"; }
    fail() { echo -e "[${RED}FAIL${NC}] $1"; failures=$((failures+1)); }
    warn() { echo -e "[${YELLOW}WARN${NC}] $1"; }

    echo "========================================"
    echo "Validating App Schema Objects"
    echo "========================================"
    echo
    echo "Instance: $(pretty_instance "$instance")"
    echo

    # Check container is running
    if ! $CR_CMD ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        fail "Container $container_name is not running"
        return 1
    fi

    echo "Container: $container_name"
    echo

    # Query objects in app schema
    local query="USE orderdb;
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
    local query_result
    query_result=$($CR_CMD exec "$container_name" /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
        -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
        -d orderdb \
        -Q "$query" \
        -s "|" -h -1 -W 2>&1)

    # Check if query succeeded (look for expected output patterns)
    if echo "$query_result" | grep -qE "^app\|"; then
        # Format and display as table with borders
        echo "Objects in app schema:"
        echo "$query_result" | \
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
        local object_count
        object_count=$(echo "$query_result" | grep -E "^app\|" | wc -l | tr -d ' ')
        echo
        echo "Total objects: $object_count"

        # Check for expected objects (basic validation)
        if echo "$query_result" | grep -q "customer"; then
            pass "customer table found"
        else
            fail "customer table not found"
        fi

        if echo "$query_result" | grep -q "orders"; then
            pass "orders table found"
        else
            warn "orders table not found (may not be deployed yet)"
        fi
    else
        fail "Failed to query objects in app schema"
        echo "Query output:"
        echo "$query_result"
        return 1
    fi

    echo
    if [[ "$failures" -eq 0 ]]; then
        echo -e "${GREEN}VALIDATION SUCCESSFUL${NC}"
        return 0
    else
        echo -e "${RED}VALIDATION FAILED ($failures errors)${NC}"
        return 1
    fi
}

################################################################################
# Main Execution
################################################################################

TOTAL_FAILURES=0
declare -a SUCCESS_INSTANCES=()
declare -a FAILED_INSTANCES=()

for instance in "${TARGET_INSTANCES[@]}"; do
    # Trim whitespace
    instance="${instance//[[:space:]]/}"

    if validate_instance "$instance"; then
        SUCCESS_INSTANCES+=("$instance")
    else
        FAILED_INSTANCES+=("$instance")
        TOTAL_FAILURES=$((TOTAL_FAILURES+1))
    fi

    echo
done

################################################################################
# Summary
################################################################################

if [[ ${#TARGET_INSTANCES[@]} -gt 1 ]]; then
    echo "========================================"
    echo "Validation Summary"
    echo "========================================"

    if [[ ${#SUCCESS_INSTANCES[@]} -gt 0 ]]; then
        echo -e "${GREEN}Successful:${NC} ${SUCCESS_INSTANCES[*]}"
    fi

    if [[ ${#FAILED_INSTANCES[@]} -gt 0 ]]; then
        echo -e "${RED}Failed:${NC} ${FAILED_INSTANCES[*]}"
    fi
fi

if [[ "$TOTAL_FAILURES" -eq 0 ]]; then
    exit 0
else
    exit 1
fi
