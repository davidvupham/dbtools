#!/usr/bin/env bash
set -euo pipefail

# Helper script to execute sqlcmd inside the tutorial SQL Server container.
# Replaces long commands like:
#   container_runtime exec -i mssql_liquibase_tutorial /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" < 04_verify_dev_objects.sql
#
# Usage examples:
#   ./sqlcmd_tutorial.sh 04_verify_dev_objects.sql
#   ./sqlcmd_tutorial.sh -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime;"
#   ./sqlcmd_tutorial.sh -d testdbdev 05_verify_dev_data.sql
#   ./sqlcmd_tutorial.sh -d testdbdev -Q "SELECT name FROM sys.tables;"

detect_runtime() {
  # 1. Allow override via env var
  if [[ -n "${CONTAINER_RUNTIME:-}" ]]; then
    echo "$CONTAINER_RUNTIME"
    return
  fi

  # 2. Check OS preference
  local os_id=""
  if [[ -f /etc/os-release ]]; then
    os_id="$(source /etc/os-release && echo "${ID} ${ID_LIKE:-}")"
  fi

  # RedHat/Fedora/CentOS -> Prefer Podman
  if [[ "$os_id" =~ (rhel|fedora|centos|rocky|almalinux) ]]; then
    if command -v podman &> /dev/null; then
      echo "podman"
      return
    fi
  fi

  # Ubuntu/Debian -> Prefer Docker
  if [[ "$os_id" =~ (ubuntu|debian) ]]; then
    if command -v docker &> /dev/null; then
      echo "docker"
      return
    fi
  fi

  # 3. Fallback: check binaries
  if command -v docker &> /dev/null; then
    echo "docker"
  elif command -v podman &> /dev/null; then
    echo "podman"
  else
    echo "Error: Neither docker nor podman found. Install one or set CONTAINER_RUNTIME." >&2
    exit 1
  fi
}

CR="$(detect_runtime)"

CONTAINER_NAME=${CONTAINER_NAME:-mssql_liquibase_tutorial}
SQLCMD_BIN=/opt/mssql-tools18/bin/sqlcmd
SERVER=${SERVER:-localhost}
USER=${USER_NAME:-SA}
DB=""
QUERY=""
SQL_FILE=""

print_usage() {
  cat <<'EOF'
Usage:
  sqlcmd_tutorial.sh [options] <sql-file.sql>
  sqlcmd_tutorial.sh [options] -Q "<query>"

Options:
  -d, --database <name>   Database name to connect to (sqlcmd -d)
  -Q, --query    <query>  Query string to execute (exclusive with <sql-file.sql>)
  --container    <name>   Container name (default: mssql_liquibase_tutorial)
  --server       <host>   SQL Server hostname (default: localhost)
  --user         <name>   SQL login user (default: SA)
  -h, --help              Show this help and exit

Environment:
  MSSQL_LIQUIBASE_TUTORIAL_PWD   Password for the SQL login (required)

Examples:
  ./sqlcmd_tutorial.sh 04_verify_dev_objects.sql
  ./sqlcmd_tutorial.sh -Q "SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime;"
  ./sqlcmd_tutorial.sh -d testdbdev 05_verify_dev_data.sql
  ./sqlcmd_tutorial.sh --container mssql_liquibase_tutorial -d testdbdev -Q "SELECT name FROM sys.tables;"
EOF
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--database)
      DB="$2"; shift 2;;
    -Q|--query)
      QUERY="$2"; shift 2;;
    --container)
      CONTAINER_NAME="$2"; shift 2;;
    --server)
      SERVER="$2"; shift 2;;
    --user)
      USER="$2"; shift 2;;
    -h|--help)
      print_usage; exit 0;;
    --)
      shift; break;;
    -*)
      echo "Unknown option: $1" >&2; print_usage; exit 2;;
    *)
      # First non-flag argument: treat as SQL file
      if [[ -z "$SQL_FILE" ]]; then
        SQL_FILE="$1"; shift
      else
        echo "Unexpected argument: $1" >&2; print_usage; exit 2
      fi
      ;;
  esac
done

# Validate inputs
if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
  echo "Error: MSSQL_LIQUIBASE_TUTORIAL_PWD environment variable is not set." >&2
  echo "Set it first, e.g.: export MSSQL_LIQUIBASE_TUTORIAL_PWD='YourStrong@Passw0rd'" >&2
  exit 1
fi

if [[ -n "$QUERY" && -n "$SQL_FILE" ]]; then
  echo "Error: Provide either a query (-Q/--query) or a SQL file, not both." >&2
  print_usage
  exit 2
fi

if [[ -z "$QUERY" && -z "$SQL_FILE" ]]; then
  echo "Error: Provide a SQL file or a query to execute." >&2
  print_usage
  exit 2
fi

# If SQL file specified, resolve its path
if [[ -n "$SQL_FILE" ]]; then
  # Get the directory where this script is located
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  # Candidate search paths for SQL files
  CANDIDATES=(
    "$SQL_FILE"
    "$PWD/$SQL_FILE"
    "$SCRIPT_DIR/$SQL_FILE"
    "$SCRIPT_DIR/../sql/$SQL_FILE"
  )
  # Prefer LIQUIBASE_TUTORIAL_DIR if set
  if [[ -n "${LIQUIBASE_TUTORIAL_DIR:-}" ]]; then
    CANDIDATES+=("$LIQUIBASE_TUTORIAL_DIR/sql/$SQL_FILE")
  fi

  RESOLVED=""
  for p in "${CANDIDATES[@]}"; do
    if [[ -f "$p" ]]; then
      RESOLVED="$p"; break
    fi
  done

  if [[ -z "$RESOLVED" ]]; then
    echo "Error: SQL file not found: $SQL_FILE" >&2
    echo "Searched in:" >&2
    printf "  - %s\n" "${CANDIDATES[@]}" >&2
    exit 1
  fi
  SQL_FILE="$RESOLVED"
fi

# Check container status
if ! "$CR" ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Error: Container '${CONTAINER_NAME}' is not running." >&2
  echo "Start it first (see tutorial Step 0)." >&2
  exit 1
fi

# Build sqlcmd args
SQLCMD_ARGS=("${SQLCMD_BIN}" -C -S "${SERVER}" -U "${USER}" -P "${MSSQL_LIQUIBASE_TUTORIAL_PWD}")
if [[ -n "$DB" ]]; then
  SQLCMD_ARGS+=( -d "$DB" )
fi

# Execute
if [[ -n "$QUERY" ]]; then
  "$CR" exec -i "${CONTAINER_NAME}" "${SQLCMD_ARGS[@]}" -Q "$QUERY"
else
  # Feed file via stdin to preserve local path semantics
  "$CR" exec -i "${CONTAINER_NAME}" "${SQLCMD_ARGS[@]}" < "$SQL_FILE"
fi
