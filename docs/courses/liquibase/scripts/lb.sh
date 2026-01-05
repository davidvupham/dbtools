#!/usr/bin/env bash
set -euo pipefail

# Liquibase Docker wrapper for the tutorial
# Usage examples:
#   lb.sh -e dev -- status --verbose
#   lb.sh -e stage -- update
#   lb.sh -e prod -- tag release-v1.2
#   LB_PROJECT_DIR=/some/dir lb.sh -e dev -- updateSQL
#
# Requirements:
#   - Docker image 'liquibase:latest' built via the repo's docker/liquibase directory
#   - SQL Server container running on network 'liquibase_tutorial'
#   - env files at $LB_PROJECT_DIR/env/liquibase.<env>.properties
#   - MSSQL_LIQUIBASE_TUTORIAL_PWD exported in the shell

ENVIRONMENT=""
EXTRA_DOCKER_OPTS=()
PASS_ARGS=()

print_usage() {
  cat <<'EOF'
Usage:
  lb.sh -e <dev|stage|prod> -- <liquibase-args>

Examples:
  lb.sh -e dev -- status --verbose
  lb.sh -e dev -- update
  lb.sh -e stage -- updateSQL
  lb.sh -e prod -- tag release-v1.2

Options before '--' apply to docker run:
  -e, --env <name>   Environment (dev|stage|prod) [required]
  --net <network>    Docker network (default: liquibase_tutorial)
  --image <name>     Liquibase image (default: liquibase:latest)
  --project <dir>    Project dir to mount (default: /data/liquibase-tutorial)
  -h, --help         Show help

Environment variables:
  MSSQL_LIQUIBASE_TUTORIAL_PWD   Required. SA password used by CLI
  LB_PROJECT_DIR                 Optional. Overrides --project
  LB_IMAGE                       Optional. Overrides --image
  LB_NETWORK                     Optional. Overrides --net
EOF
}

# Defaults
LB_PROJECT_DIR_DEFAULT="${LB_PROJECT_DIR:-/data/liquibase-tutorial}"
LB_IMAGE_DEFAULT="${LB_IMAGE:-liquibase:latest}"
LB_NETWORK_DEFAULT="${LB_NETWORK:-liquibase_tutorial}"

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
      LB_PROJECT_DIR_DEFAULT="$2"; shift 2;;
    -h|--help)
      print_usage; exit 0;;
    --)
      shift; PASS_ARGS=("$@"); break;;
    *)
      echo "Unknown option: $1" >&2; print_usage; exit 2;;
  esac
done

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
PROJECT_DIR="${LB_PROJECT_DIR_DEFAULT}"
if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Error: Project directory not found: $PROJECT_DIR" >&2
  exit 1
fi

# Validate env properties file exists
PROP_FILE="$PROJECT_DIR/env/liquibase.${ENVIRONMENT}.properties"
if [[ ! -f "$PROP_FILE" ]]; then
  echo "Error: Properties file not found: $PROP_FILE" >&2
  exit 1
fi

# docker run invocation
exec docker run --rm \
  --user "$(id -u):$(id -g)" \
  --network="${LB_NETWORK_DEFAULT}" \
  -v "${PROJECT_DIR}:/workspace" \
  "${LB_IMAGE_DEFAULT}" \
  --defaults-file="/workspace/env/liquibase.${ENVIRONMENT}.properties" \
  --password="${MSSQL_LIQUIBASE_TUTORIAL_PWD}" \
  "${PASS_ARGS[@]}"
