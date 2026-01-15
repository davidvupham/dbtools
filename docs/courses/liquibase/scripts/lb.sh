#!/usr/bin/env bash
set -euo pipefail

################################################################################
# lb.sh - Liquibase Docker wrapper for the tutorial
################################################################################
#
# PURPOSE:
#   Wrapper script to run Liquibase commands against SQL Server database
#   instances using Docker/Podman containers.
#
# USAGE:
#   lb.sh --dbi <instance> -- <liquibase-args>
#
# OPTIONS:
#   -d, --dbi <instance>    Target database instance (required)
#                          Values: mssql_dev, mssql_stg, mssql_prd
#   --net <network>        Container network (default: auto)
#   --image <name>         Liquibase image (default: liquibase:latest)
#   --project <dir>        Project dir to mount (default: /data/$USER/liquibase_tutorial)
#   -h, --help             Show help
#
# EXAMPLES:
#   lb.sh --dbi mssql_dev -- status --verbose
#   lb.sh --dbi mssql_dev -- update
#   lb.sh --dbi mssql_stg -- updateSQL
#   lb.sh --dbi mssql_prd -- tag release-v1.2
#   LIQUIBASE_TUTORIAL_DATA_DIR=/some/dir lb.sh --dbi mssql_dev -- updateSQL
#
# ENVIRONMENT VARIABLES:
#   MSSQL_LIQUIBASE_TUTORIAL_PWD   Required. SA password used by CLI
#   LIQUIBASE_TUTORIAL_DATA_DIR    Optional. Overrides --project
#   LB_IMAGE                       Optional. Overrides --image
#   LB_NETWORK                     Optional. Overrides --net
#
# REQUIREMENTS:
#   - Docker image 'liquibase:latest' built via the repo's docker/liquibase directory
#   - SQL Server containers running (mssql_dev/mssql_stg/mssql_prd)
#   - Properties files at $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env/
#   - MSSQL_LIQUIBASE_TUTORIAL_PWD exported in the shell
#
# RUNTIME DETECTION:
#   Checks CONTAINER_RUNTIME env var, then searches for docker, then podman.
#
################################################################################

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

INSTANCE=""
EXTRA_DOCKER_OPTS=()
PASS_ARGS=()

print_usage() {
  cat <<'EOF'
Usage:
  lb.sh --dbi <instance> -- <liquibase-args>

Options:
  -d, --dbi <instance>    Target database instance (required)
                         Values: mssql_dev, mssql_stg, mssql_prd
  --net <network>        Container network (default: auto)
  --image <name>         Liquibase image (default: liquibase:latest)
  --project <dir>        Project dir to mount (default: /data/$USER/liquibase_tutorial)
  -h, --help             Show help

Examples:
  lb.sh --dbi mssql_dev -- status --verbose
  lb.sh --dbi mssql_dev -- update
  lb.sh --dbi mssql_stg -- updateSQL
  lb.sh --dbi mssql_prd -- tag release-v1.2

Environment variables:
  MSSQL_LIQUIBASE_TUTORIAL_PWD   Required. SA password used by CLI
  LIQUIBASE_TUTORIAL_DATA_DIR    Optional. Overrides --project
  LB_IMAGE                       Optional. Overrides --image
  LB_NETWORK                     Optional. Overrides --net
EOF
}

# Extract environment from database instance name (mssql_dev -> dev)
instance_to_env() {
  local instance="${1//[[:space:]]/}"
  case "$instance" in
    mssql_dev) echo "dev" ;;
    mssql_stg) echo "stg" ;;
    mssql_prd) echo "prd" ;;
    *)         echo "" ;;
  esac
}

# Defaults
LIQUIBASE_TUTORIAL_DATA_DIR_DEFAULT="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/$(whoami)/liquibase_tutorial}"
LB_IMAGE_DEFAULT="${LB_IMAGE:-liquibase:latest}"
LB_NETWORK_DEFAULT="${LB_NETWORK:-}"

# Parse args until '--'
while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--dbi|--database|--instance)
      INSTANCE="$2"; shift 2;;
    --net)
      LB_NETWORK_DEFAULT="$2"; shift 2;;
    --image)
      LB_IMAGE_DEFAULT="$2"; shift 2;;
    --project)
      LIQUIBASE_TUTORIAL_DATA_DIR_DEFAULT="$2"; shift 2;;
    -h|--help)
      print_usage; exit 0;;
    --)
      shift; PASS_ARGS=("$@"); break;;
    *)
      echo "Unknown option: $1" >&2; print_usage; exit 2;;
  esac
done

# Validate database instance (required)
if [[ -z "$INSTANCE" ]]; then
  echo "Error: Database instance required. Use --dbi <instance>" >&2
  echo "Valid instances: mssql_dev, mssql_stg, mssql_prd" >&2
  print_usage
  exit 2
fi

# Validate instance name
VALID_INSTANCES="mssql_dev mssql_stg mssql_prd"
if [[ ! " $VALID_INSTANCES " =~ " $INSTANCE " ]]; then
  echo "Error: Invalid database instance '$INSTANCE'" >&2
  echo "Valid instances: $VALID_INSTANCES" >&2
  exit 2
fi

# Extract environment from instance name
ENVIRONMENT=$(instance_to_env "$INSTANCE")

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
  echo "Error: MSSQL_LIQUIBASE_TUTORIAL_PWD is not set." >&2
  echo "Export it, e.g.: export MSSQL_LIQUIBASE_TUTORIAL_PWD='<YOUR_STRONG_PASSWORD>'" >&2
  exit 1
fi

# Resolve project dir
PROJECT_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR_DEFAULT}"
if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Error: Project directory not found: $PROJECT_DIR" >&2
  exit 1
fi

# Validate env properties file exists
PROP_FILE="$PROJECT_DIR/platform/mssql/database/orderdb/env/liquibase.mssql_${ENVIRONMENT}.properties"
if [[ ! -f "$PROP_FILE" ]]; then
  echo "Error: Properties file not found: $PROP_FILE" >&2
  exit 1
fi

# Load port assignments from .ports file (written by start_mssql_containers.sh)
PORTS_FILE="$PROJECT_DIR/.ports"
if [[ -f "$PORTS_FILE" ]]; then
  source "$PORTS_FILE"
fi

# Use ports from .ports file, or fall back to defaults
MSSQL_DEV_PORT="${MSSQL_DEV_PORT:-14331}"
MSSQL_STG_PORT="${MSSQL_STG_PORT:-14332}"
MSSQL_PRD_PORT="${MSSQL_PRD_PORT:-14333}"

# Select port based on instance
case "$INSTANCE" in
  mssql_dev) PORT="$MSSQL_DEV_PORT";;
  mssql_stg) PORT="$MSSQL_STG_PORT";;
  mssql_prd) PORT="$MSSQL_PRD_PORT";;
esac

# If network not explicitly set, pick a safe default per runtime
# - docker: host networking so liquibase can reach localhost:1433x
# - podman: slirp4netns so liquibase can reach host via host.containers.internal
HOSTNAME="localhost"
NETWORK_ARG=()
if [[ -n "${LB_NETWORK_DEFAULT}" ]]; then
  NETWORK_ARG=(--network="${LB_NETWORK_DEFAULT}")
else
  if [[ "$CR" == "docker" ]]; then
    NETWORK_ARG=(--network=host)
    HOSTNAME="localhost"
  else
    NETWORK_ARG=(--network slirp4netns:port_handler=slirp4netns)
    HOSTNAME="host.containers.internal"
  fi
fi

JDBC_URL="jdbc:sqlserver://${HOSTNAME}:${PORT};databaseName=orderdb;encrypt=true;trustServerCertificate=true"

# Volume mount flags: Docker doesn't support :z, Podman needs it for SELinux
# For Podman, use --userns=keep-id to preserve host UID (avoids UID remapping issues)
VOLUME_MOUNT="${PROJECT_DIR}:/data"
USERNS_ARG=()
if [[ "$CR" == "podman" ]]; then
  VOLUME_MOUNT="${PROJECT_DIR}:/data:z"
  USERNS_ARG=(--userns=keep-id)
fi

# docker run invocation
exec "$CR" run --rm \
  --user "$(id -u):$(id -g)" \
  "${USERNS_ARG[@]}" \
  "${NETWORK_ARG[@]}" \
  -v "${VOLUME_MOUNT}" \
  "${LB_IMAGE_DEFAULT}" \
  --defaults-file="/data/platform/mssql/database/orderdb/env/liquibase.mssql_${ENVIRONMENT}.properties" \
  --url="${JDBC_URL}" \
  --username=sa \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  "${PASS_ARGS[@]}"
