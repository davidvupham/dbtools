#!/usr/bin/env bash

# find_tutorial_dir.sh
# Automatically locates the docs/courses/liquibase directory and exports LIQUIBASE_TUTORIAL_DIR.
#
# This script searches for the tutorial directory in several locations:
#   1. If already set in environment, validates and uses it
#   2. Relative to this script's location (if script is in the repo)
#   3. Current working directory or its parents (up to git root)
#   4. Common repository locations ($HOME/src/dbtools, /data/dbtools, etc.)
#
# IMPORTANT: This script must be SOURCED so the export applies to your shell.
#            Example:  source find_tutorial_dir.sh
#            Or:       . find_tutorial_dir.sh

# Detect if script is being sourced or executed
IS_SOURCED=false
if [[ "${BASH_SOURCE[0]:-}" != "${0:-}" ]]; then
  IS_SOURCED=true
fi

# Function to validate a tutorial directory
validate_tutorial_dir() {
  local dir="$1"
  # Check for expected subdirectories that confirm this is the tutorial dir
  [[ -d "${dir}/scripts" ]] && [[ -d "${dir}/sql" ]] && [[ -f "${dir}/scripts/setup_tutorial.sh" ]]
}

# Function to search upward from a directory to find docs/courses/liquibase
find_in_parents() {
  local start_dir="$1"
  local current_dir="$start_dir"
  local max_depth=10
  local depth=0

  while [[ "$depth" -lt "$max_depth" ]]; do
    # Check if docs/courses/liquibase exists relative to current_dir
    local candidate="${current_dir}/docs/courses/liquibase"
    if validate_tutorial_dir "$candidate"; then
      echo "$candidate"
      return 0
    fi

    # Move up one directory
    local parent_dir="$(dirname "$current_dir")"
    if [[ "$parent_dir" == "$current_dir" ]]; then
      # Reached filesystem root
      break
    fi
    current_dir="$parent_dir"
    ((depth++))
  done

  return 1
}

# Function to get git repository root
get_git_root() {
  git rev-parse --show-toplevel 2>/dev/null
}

# Main logic to find the tutorial directory
find_tutorial_directory() {
  local found_dir=""

  # 1. Check if LIQUIBASE_TUTORIAL_DIR is already set and valid
  if [[ -n "${LIQUIBASE_TUTORIAL_DIR:-}" ]]; then
    if validate_tutorial_dir "$LIQUIBASE_TUTORIAL_DIR"; then
      echo "$LIQUIBASE_TUTORIAL_DIR"
      return 0
    else
      echo "Warning: LIQUIBASE_TUTORIAL_DIR is set but invalid: $LIQUIBASE_TUTORIAL_DIR" >&2
    fi
  fi

  # 2. If this script is in the repo, use its location
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
  if [[ -n "$script_dir" ]]; then
    # Script should be in docs/courses/liquibase/scripts
    local candidate="$(dirname "$script_dir")"
    if validate_tutorial_dir "$candidate"; then
      echo "$candidate"
      return 0
    fi
  fi

  # 3. Search from current working directory upward
  found_dir="$(find_in_parents "$(pwd)")"
  if [[ -n "$found_dir" ]]; then
    echo "$found_dir"
    return 0
  fi

  # 4. Try git repository root
  local git_root
  git_root="$(get_git_root)"
  if [[ -n "$git_root" ]]; then
    local candidate="${git_root}/docs/courses/liquibase"
    if validate_tutorial_dir "$candidate"; then
      echo "$candidate"
      return 0
    fi
  fi

  # 5. Check common repository locations
  local common_locations=(
    "$HOME/src/dbtools/docs/courses/liquibase"
    "$HOME/dbtools/docs/courses/liquibase"
    "/data/dbtools/docs/courses/liquibase"
    "/opt/dbtools/docs/courses/liquibase"
    "/data/$(whoami)/dbtools/docs/courses/liquibase"
  )

  for location in "${common_locations[@]}"; do
    if validate_tutorial_dir "$location"; then
      echo "$location"
      return 0
    fi
  done

  return 1
}

# Execute the search
FOUND_DIR="$(find_tutorial_directory)"

if [[ -n "$FOUND_DIR" ]]; then
  if $IS_SOURCED; then
    export LIQUIBASE_TUTORIAL_DIR="$FOUND_DIR"
    echo "✓ LIQUIBASE_TUTORIAL_DIR=$LIQUIBASE_TUTORIAL_DIR"
  else
    echo "Found tutorial directory: $FOUND_DIR"
    echo ""
    echo "To export this variable, source this script instead of executing it:"
    echo "  source ${BASH_SOURCE[0]}"
    echo ""
    echo "Or manually run:"
    echo "  export LIQUIBASE_TUTORIAL_DIR=\"$FOUND_DIR\""
  fi
else
  echo "Error: Could not find docs/courses/liquibase directory." >&2
  echo "" >&2
  echo "Searched locations:" >&2
  echo "  - Current directory and parents" >&2
  echo "  - Git repository root (if in a git repo)" >&2
  echo "  - \$HOME/src/dbtools/docs/courses/liquibase" >&2
  echo "  - \$HOME/dbtools/docs/courses/liquibase" >&2
  echo "  - /data/dbtools/docs/courses/liquibase" >&2
  echo "" >&2
  echo "Please set LIQUIBASE_TUTORIAL_DIR manually:" >&2
  echo "  export LIQUIBASE_TUTORIAL_DIR=\"/path/to/your/repo/docs/courses/liquibase\"" >&2

  if $IS_SOURCED; then
    return 1
  else
    exit 1
  fi
fi

if $IS_SOURCED; then
  return 0
fi
