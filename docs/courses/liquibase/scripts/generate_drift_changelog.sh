#!/usr/bin/env bash
# Generate Drift Changelog - Create a changelog file from detected drift
# Usage: generate_drift_changelog.sh -e <dev|stg|prd> -o <output-file> [OPTIONS]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_usage() {
    cat <<'EOF'
Usage: generate_drift_changelog.sh -e <dev|stg|prd> -o <output-file> [OPTIONS]

Generate a changelog file capturing database drift compared to a snapshot.

Options:
  -e, --env <name>       Environment to check (dev|stg|prd) [required]
  -o, --output <file>    Output changelog file path (relative to /data) [required]
  -s, --snapshot <path>  Specific snapshot file (default: latest for environment)
  --schemas <list>       Schemas to compare (default: app)
  -h, --help             Show this help message

Examples:
  generate_drift_changelog.sh -e dev -o platform/mssql/database/orderdb/changelog/changes/V0002__drift.xml
  generate_drift_changelog.sh -e dev -o changelog/drift.xml --schemas "app,dbo"

EOF
}

# Defaults
LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR
ENVIRONMENT=""
SNAPSHOT_PATH=""
OUTPUT_FILE=""
SCHEMAS="app"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -e|--env)
            ENVIRONMENT="$2"; shift 2;;
        -s|--snapshot)
            SNAPSHOT_PATH="$2"; shift 2;;
        -o|--output)
            OUTPUT_FILE="$2"; shift 2;;
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

# Validate environment
case "$ENVIRONMENT" in
    stage) ENVIRONMENT="stg";;
    prod)  ENVIRONMENT="prd";;
esac

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "stg" && "$ENVIRONMENT" != "prd" ]]; then
    echo -e "${RED}Error: Environment must be dev|stg|prd${NC}" >&2
    print_usage
    exit 2
fi

# Validate output file
if [[ -z "$OUTPUT_FILE" ]]; then
    echo -e "${RED}Error: Output file is required (-o)${NC}" >&2
    print_usage
    exit 2
fi

SNAPSHOTS_DIR="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/snapshots"

# Find or validate snapshot
if [[ -z "$SNAPSHOT_PATH" ]]; then
    # Find latest snapshot for environment
    SNAPSHOT_PATH=$(ls -t "$SNAPSHOTS_DIR/${ENVIRONMENT}"_*.json 2>/dev/null | head -1 || true)
    
    if [[ -z "$SNAPSHOT_PATH" ]]; then
        echo -e "${RED}Error: No snapshots found for environment '$ENVIRONMENT'${NC}" >&2
        echo "Expected pattern: $SNAPSHOTS_DIR/${ENVIRONMENT}_*.json"
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
echo "Liquibase Tutorial - Generate Drift Changelog"
echo "========================================"
echo
echo -e "Environment:  ${CYAN}$ENVIRONMENT${NC}"
echo -e "Snapshot:     ${CYAN}$SNAPSHOT_PATH${NC}"
echo -e "Output:       ${CYAN}$OUTPUT_FILE${NC}"
echo -e "Schemas:      ${CYAN}$SCHEMAS${NC}"
echo

# Convert host path to relative path for Liquibase
# The search-path in properties is /data/platform/mssql/database/orderdb
# Snapshot path must be relative to search-path
SEARCH_PATH_BASE="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb"
RELATIVE_SNAPSHOT_PATH="${SNAPSHOT_PATH#"$SEARCH_PATH_BASE/"}"

echo -e "${YELLOW}Generating changelog from drift...${NC}"
echo

# Run the diffChangeLog command
"$SCRIPT_DIR/lb.sh" -e "$ENVIRONMENT" -- diffChangeLog \
    --schemas="$SCHEMAS" \
    --referenceUrl="offline:mssql?snapshot=$RELATIVE_SNAPSHOT_PATH" \
    --changelog-file="$OUTPUT_FILE"

# Show full path of generated file
FULL_OUTPUT_PATH="$LIQUIBASE_TUTORIAL_DATA_DIR/$OUTPUT_FILE"
if [[ -f "$FULL_OUTPUT_PATH" ]]; then
    echo
    echo -e "${GREEN}Changelog generated successfully!${NC}"
    echo
    echo "File: $FULL_OUTPUT_PATH"
    echo
    echo "Next steps:"
    echo "  1. Review the generated changelog"
    echo "  2. Edit changeset IDs and add comments as needed"
    echo "  3. Include in master changelog.xml if keeping the drift"
else
    echo
    echo -e "${YELLOW}Changelog command completed. Check output for generated file location.${NC}"
fi
