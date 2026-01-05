#!/usr/bin/env bash

# If sourced, capture current shell options to restore later
IS_SOURCED=false
if [[ "${BASH_SOURCE[0]:-}" != "${0:-}" ]]; then
  IS_SOURCED=true
  ORIG_SHELL_OPTS="$(set +o)"
fi

set -euo pipefail

# setup_environment.sh
# Interactive helper to set up environment variables for the Liquibase tutorial.
# Prompts for:
#  - MSSQL_LIQUIBASE_TUTORIAL_PWD (SQL Server SA password)
#  - LIQUIBASE_TUTORIAL_DIR (tutorial root containing scripts/ and sql/)
#  - LB_PROJECT_DIR (Liquibase project root mounted into container)
# Prints export lines you can paste or source in the current shell.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEFAULT_TUTORIAL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_LB_PROJECT_DIR="${LB_PROJECT_DIR:-/data/liquibase-tutorial}"

echo "Configure tutorial environment variables"
echo "--------------------------------------"

# IS_SOURCED flag already set above

# Prompt for SQL password (hidden input)
if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
  read -s -rp "Enter SQL Server SA password (MSSQL_LIQUIBASE_TUTORIAL_PWD): " INPUT_PWD
  echo
else
  read -s -rp "Enter SQL Server SA password (MSSQL_LIQUIBASE_TUTORIAL_PWD) [set in env]: " INPUT_PWD || true
  echo
fi

PASSWORD_VALUE="${INPUT_PWD:-${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}}"

if [[ -z "${PASSWORD_VALUE}" ]]; then
  echo "Error: Password is required." >&2
  exit 1
fi

# Warn about exclamation marks causing shell interpolation issues
if [[ "${PASSWORD_VALUE}" == *"!"* ]]; then
  echo "Warning: It's recommended to avoid '!' in the password to prevent shell history/interpolation issues." >&2
fi

# Tutorial root
read -rp "Tutorial directory (contains scripts/ and sql/) [${DEFAULT_TUTORIAL_DIR}]: " INPUT_TUTORIAL_DIR
TUTORIAL_DIR="${INPUT_TUTORIAL_DIR:-$DEFAULT_TUTORIAL_DIR}"

if [[ ! -d "${TUTORIAL_DIR}" ]]; then
  echo "Error: Tutorial directory not found: ${TUTORIAL_DIR}" >&2
  exit 1
fi

# Liquibase project dir
read -rp "Liquibase project root (mounted to /workspace) [${DEFAULT_LB_PROJECT_DIR}]: " INPUT_LB_DIR
LB_DIR="${INPUT_LB_DIR:-$DEFAULT_LB_PROJECT_DIR}"

mkdir -p "${LB_DIR}" || true

cat <<EOF

Configuration summary:
  MSSQL_LIQUIBASE_TUTORIAL_PWD=(hidden)
  LIQUIBASE_TUTORIAL_DIR=${TUTORIAL_DIR}
  LB_PROJECT_DIR=${LB_DIR}

EOF

# Apply exports when sourced; otherwise, provide next-step guidance
if ${IS_SOURCED}; then
  # Export into current shell
  export MSSQL_LIQUIBASE_TUTORIAL_PWD="${PASSWORD_VALUE}"
  export LIQUIBASE_TUTORIAL_DIR="${TUTORIAL_DIR}"
  export LB_PROJECT_DIR="${LB_DIR}"

  # Validate by displaying effective values (mask the password)
  echo "Applied environment variables in current shell:"
  echo "  MSSQL_LIQUIBASE_TUTORIAL_PWD=(set; length ${#MSSQL_LIQUIBASE_TUTORIAL_PWD})"
  echo "  LIQUIBASE_TUTORIAL_DIR=${LIQUIBASE_TUTORIAL_DIR}"
  echo "  LB_PROJECT_DIR=${LB_PROJECT_DIR}"
  echo
  echo "Tip: persist these by adding the following to ~/.bashrc or ~/.zshrc:"
  echo "  export MSSQL_LIQUIBASE_TUTORIAL_PWD='(your password here)'"
  echo "  export LIQUIBASE_TUTORIAL_DIR=\"${LIQUIBASE_TUTORIAL_DIR}\""
  echo "  export LB_PROJECT_DIR=\"${LB_PROJECT_DIR}\""
else
  # Not sourced: cannot modify parent shell; provide ready-to-copy exports
  echo "This script was executed, not sourced; exports cannot persist to your current shell."
  echo "To apply now, run the following in your terminal:"
  echo
  echo "  export MSSQL_LIQUIBASE_TUTORIAL_PWD='${PASSWORD_VALUE}'"
  echo "  export LIQUIBASE_TUTORIAL_DIR=\"${TUTORIAL_DIR}\""
  echo "  export LB_PROJECT_DIR=\"${LB_DIR}\""
  echo
  echo "Or re-run as:"
  echo "  source \"${BASH_SOURCE[0]}\""
fi

# Restore caller shell options if sourced
if ${IS_SOURCED}; then
  # Only restore if variable exists
  if [[ -n "${ORIG_SHELL_OPTS:-}" ]]; then
    eval "${ORIG_SHELL_OPTS}"
  fi
  return 0
else
  exit 0
fi
