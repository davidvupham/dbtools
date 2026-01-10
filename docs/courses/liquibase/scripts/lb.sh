#!/usr/bin/env bash
set -euo pipefail

# Liquibase Docker wrapper for the tutorial
# Usage examples:
#   lb.sh -e dev -- status --verbose
#   lb.sh -e stg -- update
#   lb.sh -e prd -- tag release-v1.2
#   LIQUIBASE_TUTORIAL_DATA_DIR=/some/dir lb.sh -e dev -- updateSQL
#
# Requirements:
#   - Docker image 'liquibase:latest' built via the repo's docker/liquibase directory
#   - SQL Server containers running (mssql_dev/mssql_stg/mssql_prd)
#   - env files at $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env/liquibase.mssql_<env>.properties
#   - MSSQL_LIQUIBASE_TUTORIAL_PWD exported in the shell
#
# Runtime detection:
#   Checks CONTAINER_RUNTIME env var, then searches for docker, then podman.

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

ENVIRONMENT=""
EXTRA_DOCKER_OPTS=()
PASS_ARGS=()

print_usage() {
  cat <<'EOF'
Usage:
  lb.sh -e <dev|stg|prd> -- <liquibase-args>

Examples:
  lb.sh -e dev -- status --verbose
  lb.sh -e dev -- update
  lb.sh -e stg -- updateSQL
  lb.sh -e prd -- tag release-v1.2

Options before '--' apply to docker run:
  -e, --env <name>   Environment (dev|stg|prd) [required]
  --net <network>    Container network (default: auto)
  --image <name>     Liquibase image (default: liquibase:latest)
  --project <dir>    Project dir to mount (default: /data/$USER/liquibase_tutorial)
  -h, --help         Show help

Environment variables:
  MSSQL_LIQUIBASE_TUTORIAL_PWD   Required. SA password used by CLI
  LIQUIBASE_TUTORIAL_DATA_DIR                 Optional. Overrides --project
  LB_IMAGE                       Optional. Overrides --image
  LB_NETWORK                     Optional. Overrides --net
EOF
}

# Defaults
LIQUIBASE_TUTORIAL_DATA_DIR_DEFAULT="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/$(whoami)/liquibase_tutorial}"
LB_IMAGE_DEFAULT="${LB_IMAGE:-liquibase:latest}"
LB_NETWORK_DEFAULT="${LB_NETWORK:-}"

# Parse args until '--'
while [[ $# -gt 0 ]]; do
  case "$1" in
    -e|--env)
      ENVIRONMENT="$2"; shift 2;;
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

# Backward compatibility: accept stage/prod as aliases
case "$ENVIRONMENT" in
  stage) ENVIRONMENT="stg";;
  prod)  ENVIRONMENT="prd";;
esac

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "stg" && "$ENVIRONMENT" != "prd" ]]; then
  echo "Error: invalid environment '$ENVIRONMENT' (expected dev|stg|prd)." >&2
  print_usage
  exit 2
fi

if [[ -z "$ENVIRONMENT" ]]; then
  echo "Error: environment not specified. Use -e dev|stage|prod" >&2
  print_usage
  exit 2
fi

if [[ -z "${MSSQL_LIQUIBASE_TUTORIAL_PWD:-}" ]]; then
  echo "Error: MSSQL_LIQUIBASE_TUTORIAL_PWD is not set." >&2
  echo "Export it, e.g.: export MSSQL_LIQUIBASE_TUTORIAL_PWD='YourStrong@Passw0rd'" >&2
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

# Compute connection URL (avoid runtime-specific hostnames in the properties files)
case "$ENVIRONMENT" in
  dev) PORT=14331;;
  stg) PORT=14332;;
  prd) PORT=14333;;
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

# Volume mount flags: Docker doesn't support :z,U, Podman needs it for SELinux
VOLUME_MOUNT="${PROJECT_DIR}:/data"
if [[ "$CR" == "podman" ]]; then
  VOLUME_MOUNT="${PROJECT_DIR}:/data:z,U"
fi

# docker run invocation
exec "$CR" run --rm \
  --user "$(id -u):$(id -g)" \
  "${NETWORK_ARG[@]}" \
  -v "${VOLUME_MOUNT}" \
  "${LB_IMAGE_DEFAULT}" \
  --defaults-file="/data/platform/mssql/database/orderdb/env/liquibase.mssql_${ENVIRONMENT}.properties" \
  --url="${JDBC_URL}" \
  --username=sa \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  "${PASS_ARGS[@]}"
