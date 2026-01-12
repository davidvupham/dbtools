#!/usr/bin/env bash
set -euo pipefail

# create_project_structure.sh
# Creates the Liquibase project directory structure for the tutorial.
#
# This script:
# - Removes existing Liquibase directories if starting fresh (preserves mssql-data)
# - Creates the project directory structure
# - Uses LIQUIBASE_TUTORIAL_DATA_DIR environment variable with default /data/$USER/liquibase_tutorial
#
# Usage:
#   ./create_project_structure.sh
#   # Or with custom directory:
#   export LIQUIBASE_TUTORIAL_DATA_DIR=/custom/path
#   ./create_project_structure.sh

# Default: per-user isolation for shared Docker hosts
# Uses /data/$USER to avoid conflicts between users
CURRENT_USER="$(whoami)"
LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${CURRENT_USER}/liquibase_tutorial}"

echo "Creating Liquibase project structure..."
echo "Project directory: ${LIQUIBASE_TUTORIAL_DATA_DIR}"
echo

# Remove existing Liquibase directories if starting fresh (preserves mssql-data)
if [[ -d "${LIQUIBASE_TUTORIAL_DATA_DIR}/platform" ]]; then
  echo "Removing existing platform directory (preserves mssql-data)..."
  rm -rf "${LIQUIBASE_TUTORIAL_DATA_DIR}/platform"
fi

# Create project directory (uses /data/$USER by default)
echo "Creating project directory..."
mkdir -p "${LIQUIBASE_TUTORIAL_DATA_DIR}"

# Create folder structure
echo "Creating folder structure..."
mkdir -p "${LIQUIBASE_TUTORIAL_DATA_DIR}/platform/mssql/database/orderdb/changelog/baseline"
mkdir -p "${LIQUIBASE_TUTORIAL_DATA_DIR}/platform/mssql/database/orderdb/changelog/changes"
mkdir -p "${LIQUIBASE_TUTORIAL_DATA_DIR}/platform/mssql/database/orderdb/env"
mkdir -p "${LIQUIBASE_TUTORIAL_DATA_DIR}/platform/mssql/database/orderdb/snapshots"

echo
echo "Project structure created successfully!"
echo "Location: ${LIQUIBASE_TUTORIAL_DATA_DIR}/platform/mssql/database/orderdb"
echo
echo "Created directories:"
echo "  - changelog/baseline"
echo "  - changelog/changes"
echo "  - env"
echo "  - snapshots"
