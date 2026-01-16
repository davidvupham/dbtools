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
#  - LIQUIBASE_TUTORIAL_DATA_DIR (Liquibase project root mounted into container)
# Prints export lines you can paste or source in the current shell.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEFAULT_TUTORIAL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Per-user project directory for shared Docker hosts
# Uses /data/$USER to avoid conflicts between users
CURRENT_USER="$(whoami)"
DEFAULT_LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${CURRENT_USER}/liquibase_tutorial}"

echo "Configure tutorial environment variables"
echo "--------------------------------------"

# Prerequisite check: verify /data exists and user can write to it
check_data_permissions() {
  if [[ ! -d "/data" ]]; then
    echo "Warning: /data directory does not exist." >&2
    echo "  You may need to create it with: sudo mkdir -p /data && sudo chmod 1777 /data" >&2
    return 1
  fi

  if [[ ! -w "/data" ]]; then
    echo "Warning: No write permission on /data directory." >&2
    echo "  Ask your administrator to run: sudo chmod 1777 /data" >&2
    echo "  Or use a different project directory (e.g., your home directory)" >&2
    return 1
  fi

  return 0
}

# IS_SOURCED flag already set above

# Prompt for SQL password (hidden input)
if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
  while [[ -z "${INPUT_PWD:-}" ]]; do
    read -s -rp "Enter SQL Server SA password (required): " INPUT_PWD
    echo
    if [[ -z "${INPUT_PWD:-}" ]]; then
      echo "Error: Password cannot be empty." >&2
    fi
  done
else
  read -s -rp "Enter SQL Server SA password [set in env]: " INPUT_PWD || true
  echo
fi

PASSWORD_VALUE="${INPUT_PWD:-${MSSQL_LIQUIBASE_TUTORIAL_PWD}}"

if [[ -z "${PASSWORD_VALUE}" ]]; then
  echo "Error: Password is required." >&2
  exit 1
fi

# Warn about exclamation marks causing shell interpolation issues
if [[ "${PASSWORD_VALUE}" == *"!"* ]]; then
  echo "Warning: It's recommended to avoid '!' in the password to prevent shell history/interpolation issues." >&2
fi

# Tutorial root - use existing LIQUIBASE_TUTORIAL_DIR if set
if [[ -n "${LIQUIBASE_TUTORIAL_DIR:-}" ]]; then
  TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR}"
  echo "Using LIQUIBASE_TUTORIAL_DIR=${TUTORIAL_DIR}"
else
  read -rp "Tutorial directory (contains scripts/ and sql/) [${DEFAULT_TUTORIAL_DIR}]: " INPUT_TUTORIAL_DIR
  TUTORIAL_DIR="${INPUT_TUTORIAL_DIR:-$DEFAULT_TUTORIAL_DIR}"
fi

if [[ ! -d "${TUTORIAL_DIR}" ]]; then
  echo "Error: Tutorial directory not found: ${TUTORIAL_DIR}" >&2
  exit 1
fi

# Liquibase project dir - use existing LIQUIBASE_TUTORIAL_DATA_DIR if set
if [[ -n "${LIQUIBASE_TUTORIAL_DATA_DIR:-}" ]]; then
  LB_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR}"
  echo "Using LIQUIBASE_TUTORIAL_DATA_DIR=${LB_DIR}"
else
  echo ""
  echo "Shared Docker Host Support:"
  echo "  Default project dir: /data/${CURRENT_USER} (per-user isolation)"
  check_data_permissions || echo "  (continuing anyway - you can specify a different directory)"
  echo ""
  read -rp "Liquibase project root (mounted to /data) [${DEFAULT_LIQUIBASE_TUTORIAL_DATA_DIR}]: " INPUT_LB_DIR
  LB_DIR="${INPUT_LB_DIR:-$DEFAULT_LIQUIBASE_TUTORIAL_DATA_DIR}"
fi

# Create directory if it doesn't exist
if [[ ! -d "${LB_DIR}" ]]; then
  echo "Creating project directory: ${LB_DIR}"
  if ! mkdir -p "${LB_DIR}" 2>/dev/null; then
    echo "Error: Cannot create directory ${LB_DIR}" >&2
    echo "  Ensure you have write permission, or choose a different path." >&2
    if ${IS_SOURCED}; then return 1; else exit 1; fi
  fi
fi

cat <<EOF

Configuration summary:
  MSSQL_LIQUIBASE_TUTORIAL_PWD=(hidden)
  LIQUIBASE_TUTORIAL_DIR=${TUTORIAL_DIR}
  LIQUIBASE_TUTORIAL_DATA_DIR=${LB_DIR}

EOF

# Apply exports when sourced; otherwise, provide next-step guidance
if ${IS_SOURCED}; then
  # Export into current shell
  export MSSQL_LIQUIBASE_TUTORIAL_PWD="${PASSWORD_VALUE}"
  export LIQUIBASE_TUTORIAL_DIR="${TUTORIAL_DIR}"
  export LIQUIBASE_TUTORIAL_DATA_DIR="${LB_DIR}"

  # Validate by displaying effective values (mask the password)
  echo "Applied environment variables in current shell:"
  echo "  MSSQL_LIQUIBASE_TUTORIAL_PWD=(set; length ${#MSSQL_LIQUIBASE_TUTORIAL_PWD})"
  echo "  LIQUIBASE_TUTORIAL_DIR=${LIQUIBASE_TUTORIAL_DIR}"
  echo "  LIQUIBASE_TUTORIAL_DATA_DIR=${LIQUIBASE_TUTORIAL_DATA_DIR}"
  echo
  echo "Tip: persist these by adding the following to ~/.bashrc or ~/.zshrc:"
  echo "  export MSSQL_LIQUIBASE_TUTORIAL_PWD='(your password here)'"
  echo "  export LIQUIBASE_TUTORIAL_DIR=\"${LIQUIBASE_TUTORIAL_DIR}\""
  echo "  export LIQUIBASE_TUTORIAL_DATA_DIR=\"${LIQUIBASE_TUTORIAL_DATA_DIR}\""
else
  # Not sourced: cannot modify parent shell; provide ready-to-copy exports
  echo "This script was executed, not sourced; exports cannot persist to your current shell."
  echo "To apply now, run the following in your terminal:"
  echo
  echo "  export MSSQL_LIQUIBASE_TUTORIAL_PWD='${PASSWORD_VALUE}'"
  echo "  export LIQUIBASE_TUTORIAL_DIR=\"${TUTORIAL_DIR}\""
  echo "  export LIQUIBASE_TUTORIAL_DATA_DIR=\"${LB_DIR}\""
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
