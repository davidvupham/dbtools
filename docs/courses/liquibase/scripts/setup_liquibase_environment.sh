#!/usr/bin/env bash
# Setup Liquibase Environment
# Creates directories and configures environment for Liquibase tutorial
# Reusable across all tutorial parts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUTORIAL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Options
OVERWRITE=0
BACKUP=0
INTERACTIVE=0
if [[ -t 0 && -t 1 ]]; then
    INTERACTIVE=1
fi

usage() {
    cat <<'EOF'
Usage: setup_liquibase_environment.sh [--overwrite] [--backup]

Creates tutorial directories, Liquibase properties files, and a master changelog.

Options:
  --overwrite   Overwrite existing properties/changelog files without prompting
  --backup      When overwriting, create a timestamped .bak file first
  -h, --help    Show this help

Notes:
  - In interactive shells, if target files already exist you'll be prompted unless --overwrite is provided.
  - In non-interactive shells, the script will error if target files exist unless --overwrite is provided.
EOF
}

if [[ $# -gt 0 ]]; then
    for arg in "$@"; do
        case "$arg" in
            --overwrite) OVERWRITE=1 ;;
            --backup) BACKUP=1 ;;
            -h|--help) usage; exit 0 ;;
            *)
                echo "Unknown argument: $arg" >&2
                usage >&2
                exit 2
                ;;
        esac
    done
fi

# Helper: backup file if enabled
backup_file_if_needed() {
    local target="$1"
    if [[ "$BACKUP" -eq 1 && -f "$target" ]]; then
        local ts
        ts="$(date +%Y%m%d_%H%M%S)"
        cp -p "$target" "${target}.bak.${ts}"
    fi
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Liquibase Tutorial - Setup Environment"
echo "========================================"
echo

# Determine data directory
LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

echo "Data directory: $LIQUIBASE_TUTORIAL_DATA_DIR"

# Create directories
echo -n "Creating directories... "
if mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR"/{mssql_dev,mssql_stg,mssql_prd,platform/mssql/database/orderdb/changelog/{baseline,changes},platform/mssql/database/orderdb/env} 2>/dev/null; then
    echo -e "${GREEN}✓ Done${NC}"
else
    echo -e "${YELLOW}Using sudo...${NC}"
    sudo mkdir -p "$LIQUIBASE_TUTORIAL_DATA_DIR"/{mssql_dev,mssql_stg,mssql_prd,platform/mssql/database/orderdb/changelog/{baseline,changes},platform/mssql/database/orderdb/env}
    sudo chown -R "$USER:$USER" "$LIQUIBASE_TUTORIAL_DATA_DIR"
    echo -e "${GREEN}✓ Done${NC}"
fi

# Prompt for password if not set
if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
    if [[ "$INTERACTIVE" -ne 1 ]]; then
        echo
        echo -e "${RED}ERROR:${NC} MSSQL_LIQUIBASE_TUTORIAL_PWD is not set and stdin is not a TTY." >&2
        echo "Set MSSQL_LIQUIBASE_TUTORIAL_PWD in your environment and re-run." >&2
        exit 1
    fi
    echo
    echo "SQL Server password not set."
    read -sp "Enter password for SQL Server (min 8 chars, mixed case, number, special): " MSSQL_LIQUIBASE_TUTORIAL_PWD
    echo
fi
export MSSQL_LIQUIBASE_TUTORIAL_PWD

# Load port assignments if .ports file exists (from previous start_mssql_containers.sh run)
PORTS_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
if [[ -f "$PORTS_FILE" ]]; then
    source "$PORTS_FILE"
    echo -e "${GREEN}Using ports from $PORTS_FILE${NC}"
fi

# Use ports from .ports file, or fall back to defaults
MSSQL_DEV_PORT="${MSSQL_DEV_PORT:-14331}"
MSSQL_STG_PORT="${MSSQL_STG_PORT:-14332}"
MSSQL_PRD_PORT="${MSSQL_PRD_PORT:-14333}"

# Determine target files (for overwrite confirmation)
ENV_DIR="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env"
CHANGELOG_DIR="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog"
TARGET_FILES=(
    "$ENV_DIR/liquibase.mssql_dev.properties"
    "$ENV_DIR/liquibase.mssql_stg.properties"
    "$ENV_DIR/liquibase.mssql_prd.properties"
    "$CHANGELOG_DIR/changelog.xml"
)

EXISTING_FILES=()
for f in "${TARGET_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        EXISTING_FILES+=("$f")
    fi
done

if [[ "${#EXISTING_FILES[@]}" -gt 0 && "$OVERWRITE" -ne 1 ]]; then
    if [[ "$INTERACTIVE" -eq 1 ]]; then
        echo
        echo "The following files already exist and may be overwritten:"
        for f in "${EXISTING_FILES[@]}"; do
            echo "  - $f"
        done
        echo
        read -rp "Overwrite existing files? [y/N] " reply
        case "${reply:-}" in
            y|Y|yes|YES) OVERWRITE=1 ;;
            *)
                echo "Keeping existing files; will only create missing ones."
                ;;
        esac
    else
        echo -e "${RED}ERROR:${NC} Refusing to overwrite existing files in non-interactive mode." >&2
        echo "Re-run with --overwrite (optionally --backup) to proceed." >&2
        echo "Existing files:" >&2
        for f in "${EXISTING_FILES[@]}"; do
            echo "  - $f" >&2
        done
        exit 1
    fi
fi

# Create properties files for each environment
# Note: lb.sh overrides the URL at runtime, so these ports are for reference/debugging
echo -n "Creating Liquibase properties files... "
for env in dev stg prd; do
    case "$env" in
        dev) port="$MSSQL_DEV_PORT";;
        stg) port="$MSSQL_STG_PORT";;
        prd) port="$MSSQL_PRD_PORT";;
    esac
    target="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env/liquibase.mssql_${env}.properties"
    if [[ -f "$target" && "$OVERWRITE" -ne 1 ]]; then
        continue
    fi
    backup_file_if_needed "$target"
    cat > "$target" << EOF
# ${env^^} Environment - Liquibase Properties
# Note: lb.sh dynamically sets the URL based on .ports file; this is a fallback
url=jdbc:sqlserver://localhost:${port};databaseName=orderdb;encrypt=true;trustServerCertificate=true
username=sa
changelog-file=changelog/changelog.xml
search-path=/data/platform/mssql/database/orderdb
logLevel=info
EOF
done
echo -e "${GREEN}✓ Done${NC}"

# Create master changelog
echo -n "Creating master changelog... "
CHANGELOG_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/changelog.xml"
if [[ -f "$CHANGELOG_FILE" && "$OVERWRITE" -ne 1 ]]; then
    echo -e "${YELLOW}Skipped (already exists)${NC}"
else
    backup_file_if_needed "$CHANGELOG_FILE"
    cat > "$CHANGELOG_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">

    <!-- Baseline from existing database -->
    <include file="baseline/V0000__baseline.mssql.sql" relativeToChangelogFile="true"/>

    <!-- Incremental changes -->
    <!-- <include file="changes/V0001__add_orders_table.mssql.sql" relativeToChangelogFile="true"/> -->

</databaseChangeLog>
EOF
    echo -e "${GREEN}✓ Done${NC}"
fi

# Summary
echo
echo "========================================"
echo -e "${GREEN}Environment Setup Complete${NC}"
echo "========================================"
echo "Data directory:  $LIQUIBASE_TUTORIAL_DATA_DIR"
echo "Properties:      $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env/"
echo "Changelogs:      $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/changelog/"
echo
echo "Next: Run start_mssql_containers.sh"
