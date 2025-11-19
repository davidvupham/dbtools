#!/usr/bin/env bash
# Source this file to create convenient aliases and environment variables for the tutorial
# Usage: source /path/to/repo/docs/tutorials/liquibase/scripts/setup_aliases.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Derive repository root and tutorial directory robustly relative to this file
# Resolve repository root (four levels up from scripts directory)
export LIQUIBASE_TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"

# Default Liquibase project directory (where changelog/env live)
# Can be overridden before sourcing or later in the shell
export LB_PROJECT_DIR="${LB_PROJECT_DIR:-/data/liquibase-tutorial}"

# Aliases for convenience
alias sqlcmd-tutorial="${SCRIPT_DIR}/sqlcmd_tutorial.sh"
alias lb="${SCRIPT_DIR}/lb.sh"

echo "Tutorial environment configured."
echo "Variables:"
echo "  LIQUIBASE_TUTORIAL_DIR=${LIQUIBASE_TUTORIAL_DIR}"
echo "  LB_PROJECT_DIR=${LB_PROJECT_DIR}  (override by: export LB_PROJECT_DIR=/your/path)"
echo "Aliases: sqlcmd-tutorial, lb"
echo "Examples:"
echo "  sqlcmd-tutorial -Q 'SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime;'"
echo "  lb -e dev -- status --verbose"
