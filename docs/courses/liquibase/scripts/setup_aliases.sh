#!/usr/bin/env bash
# Source this file to create convenient aliases and environment variables for the tutorial
# Usage: source /path/to/repo/docs/courses/liquibase/scripts/setup_aliases.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Derive repository root and tutorial directory robustly relative to this file
# Resolve repository root (four levels up from scripts directory)
export LIQUIBASE_TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"

# Default Liquibase project directory (where changelog/env live)
# Uses per-user directory for shared Docker host support
# Can be overridden before sourcing or later in the shell
export LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/$(whoami)/liquibase_tutorial}"

# Aliases for convenience
alias sqlcmd-tutorial="${SCRIPT_DIR}/sqlcmd_tutorial.sh"
alias lb="${SCRIPT_DIR}/lb.sh"
alias cr="${SCRIPT_DIR}/cr.sh"   # Container runtime (auto-detects docker/podman)

echo "Tutorial environment configured."
echo "Variables:"
echo "  LIQUIBASE_TUTORIAL_DIR=${LIQUIBASE_TUTORIAL_DIR}"
echo "  LIQUIBASE_TUTORIAL_DATA_DIR=${LIQUIBASE_TUTORIAL_DATA_DIR}  (override by: export LIQUIBASE_TUTORIAL_DATA_DIR=/your/path)"
echo "Aliases: sqlcmd-tutorial, lb, cr"
echo "  cr = Container Runtime (auto-detects docker/podman based on OS)"
echo "Examples:"
echo "  sqlcmd-tutorial -Q 'SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime;'"
echo "  lb -e dev -- status --verbose"
echo "  cr ps                              # list containers (uses docker or podman)"
