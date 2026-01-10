#!/usr/bin/env bash
set -euo pipefail

# One-shot setup helper for the Liquibase + SQL Server tutorial.
#
# Responsibilities:
# - Source setup_environment.sh to capture/export required env vars
# - Source setup_aliases.sh to register lb/sqlcmd-tutorial helpers
# - Create missing Liquibase properties for dev/stage/prod under $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env
#
# IMPORTANT: This script must be SOURCED so that environment and aliases
#            are applied to your current shell.
#            Example:  source /path/to/repo/docs/courses/liquibase/scripts/setup_tutorial.sh

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "This script must be sourced so changes apply to your current shell." >&2
  echo "Usage: source $0" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1) Source environment setup (prompts on first run; exports values when sourced)
ENV_HELPER="${SCRIPT_DIR}/setup_environment.sh"
if [[ ! -f "${ENV_HELPER}" ]]; then
  echo "Error: Missing setup helper: ${ENV_HELPER}" >&2
  return 1
fi
source "${ENV_HELPER}"

# 2) Source aliases (lb, sqlcmd-tutorial)
ALIAS_HELPER="${SCRIPT_DIR}/setup_aliases.sh"
if [[ ! -f "${ALIAS_HELPER}" ]]; then
  # Backward-compatible fallback if someone used a different filename
  if [[ -f "${SCRIPT_DIR}/setup_alias.sh" ]]; then
    ALIAS_HELPER="${SCRIPT_DIR}/setup_alias.sh"
  else
    echo "Error: Missing aliases helper: ${ALIAS_HELPER}" >&2
    return 1
  fi
fi
source "${ALIAS_HELPER}"

# 3) Ensure required env vars are available
: "${MSSQL_LIQUIBASE_TUTORIAL_PWD:?MSSQL_LIQUIBASE_TUTORIAL_PWD must be set}"
: "${LIQUIBASE_TUTORIAL_DIR:?LIQUIBASE_TUTORIAL_DIR must be set}"

# Default: per-user isolation for shared Docker hosts
LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/$(whoami)/liquibase_tutorial}"
export LIQUIBASE_TUTORIAL_DATA_DIR

# 4) Ensure runtime project directories exist
mkdir -p "${LIQUIBASE_TUTORIAL_DATA_DIR}/platform/mssql/database/orderdb/env"
mkdir -p "${LIQUIBASE_TUTORIAL_DATA_DIR}/platform/mssql/database/orderdb/changelog/baseline" "${LIQUIBASE_TUTORIAL_DATA_DIR}/platform/mssql/database/orderdb/changelog/changes"

# 5) Summarize
echo
echo "Tutorial setup complete. Summary:"
echo "- LIQUIBASE_TUTORIAL_DATA_DIR: ${LIQUIBASE_TUTORIAL_DATA_DIR}"
echo "- Project dirs: platform/mssql/database/orderdb/env/, platform/mssql/database/orderdb/changelog/{baseline,changes}"
echo
echo "Verify helpers:"
type lb || true
type sqlcmd-tutorial || true
echo
# echo "You can now run Liquibase, e.g.:"
# echo "  lb -e dev -- status --verbose"
return 0
