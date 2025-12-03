#!/bin/bash
# Verification script for Liquibase tutorial self-hosted GitHub Actions environment
# Checks:
#  - Docker available
#  - Required network exists
#  - Runner + SQL Server containers running (supports both compose and manual names)
#  - Runner registration status (log scan)
#  - Connectivity: runner -> SQL Server (ping + port test)
#  - GitHub CLI auth (optional)
#  - Environment file presence (runner.env.local or external path)
#
# Exit codes:
#  0 = All critical checks passed
#  1 = One or more critical failures
#  2 = Script usage error

set -o pipefail

show_help() {
  cat <<'EOF'
Usage: verify-self-hosted-env.sh [options]

Options:
  --runner <name>            Runner container name AND registered runner name (shortcut)
  --runner-container <name>  Runner container name (if different from registered name)
  --runner-registered <name> Registered GitHub Actions runner name
  --sql <name>               Override SQL Server container name (default auto-detect list)
  --network <name>           Docker network to validate (default: liquibase_tutorial)
  -h, --help                 Show this help and exit

Environment Overrides:
  RUNNER_NAME                Registered runner name (same as --runner-registered)
  RUNNER_CONTAINER_NAME      Runner container name (same as --runner-container)
  NET_NAME                   Network name
  SQL_CONTAINER_NAME         SQL Server container name

Auto-detection:
  If runner container name not provided, script will attempt to find a single running
  container whose name matches /runner/i. If multiple are found you must specify one.

Exit Codes:
  0 Success; 1 critical failures; 2 usage error
EOF
}

# Defaults
NET_NAME="${NET_NAME:-liquibase_tutorial}"
RUNNER_NAME="${RUNNER_NAME:-}"            # Registered runner name (API list)
CONTAINER_RUNNER_NAME="${RUNNER_CONTAINER_NAME:-}"  # Docker container name
SQL_CANDIDATES=(mssql_liquibase_tutorial sqlserver)

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --runner)
      [[ -z "$2" ]] && echo "Missing value for --runner" >&2 && exit 2
      RUNNER_NAME="$2"; CONTAINER_RUNNER_NAME="$2"; shift 2;;
    --runner-container)
      [[ -z "$2" ]] && echo "Missing value for --runner-container" >&2 && exit 2
      CONTAINER_RUNNER_NAME="$2"; shift 2;;
    --runner-registered)
      [[ -z "$2" ]] && echo "Missing value for --runner-registered" >&2 && exit 2
      RUNNER_NAME="$2"; shift 2;;
    --sql)
      [[ -z "$2" ]] && echo "Missing value for --sql" >&2 && exit 2
      SQL_CANDIDATES=("$2"); shift 2;;
    --network)
      [[ -z "$2" ]] && echo "Missing value for --network" >&2 && exit 2
      NET_NAME="$2"; shift 2;;
    -h|--help)
      show_help; exit 0;;
    *) echo "Unknown argument: $1" >&2; exit 2;;
  esac
done

CRITICAL_FAIL=0
WARNINGS=()
PASS=()
FAIL=()

color() { # $1=color $2=text
  local c="$1"; shift
  local t="$*"
  case "$c" in green) printf "\e[32m%s\e[0m" "$t";; red) printf "\e[31m%s\e[0m" "$t";; yellow) printf "\e[33m%s\e[0m" "$t";; cyan) printf "\e[36m%s\e[0m" "$t";; *) printf "%s" "$t";; esac
}

header() { echo ""; color cyan "==== $* ===="; }
status_line() { # $1=ok|fail|warn $2=message
  case "$1" in
    ok) PASS+=("$2"); printf "  ["; color green "PASS"; printf "] %s\n" "$2" ;;
    fail) FAIL+=("$2"); printf "  ["; color red "FAIL"; printf "] %s\n" "$2" ; CRITICAL_FAIL=1 ;;
    warn) WARNINGS+=("$2"); printf "  ["; color yellow "WARN"; printf "] %s\n" "$2" ;;
  esac
}

header "Docker Availability"
if command -v docker >/dev/null 2>&1; then
  status_line ok "docker present ($(docker --version | awk '{print $3}' | tr -d ,))"
else
  status_line fail "docker not found in PATH"
fi

header "Network Check"
if docker network ls --format '{{.Name}}' | grep -q "^${NET_NAME}$"; then
  status_line ok "Network ${NET_NAME} exists"
else
  status_line fail "Network ${NET_NAME} missing"
fi

header "Container Presence"
# Resolve runner container name if not provided
if [[ -z "$CONTAINER_RUNNER_NAME" ]]; then
  mapfile -t AUTO_RUNNERS < <(docker ps --format '{{.Names}}' | grep -i 'runner' || true)
  if (( ${#AUTO_RUNNERS[@]} == 1 )); then
    CONTAINER_RUNNER_NAME="${AUTO_RUNNERS[0]}"
    [[ -z "$RUNNER_NAME" ]] && RUNNER_NAME="$CONTAINER_RUNNER_NAME"
    status_line ok "Auto-detected runner container: $CONTAINER_RUNNER_NAME"
  elif (( ${#AUTO_RUNNERS[@]} > 1 )); then
    status_line warn "Multiple possible runner containers found: ${AUTO_RUNNERS[*]} (specify with --runner-container)"
  else
    status_line fail "No runner containers found (name match /runner/)"
  fi
fi
[[ -z "$RUNNER_NAME" && -n "$CONTAINER_RUNNER_NAME" ]] && RUNNER_NAME="$CONTAINER_RUNNER_NAME"

SQL_FOUND=""
for name in "${SQL_CANDIDATES[@]}"; do
  if docker ps --format '{{.Names}}' | grep -q "^${name}$"; then SQL_FOUND="$name"; break; fi
done
if [[ -n "$SQL_FOUND" ]]; then
  status_line ok "SQL Server container running: $SQL_FOUND"
else
  status_line fail "No SQL Server container running (checked: ${SQL_CANDIDATES[*]})"
fi
if [[ -n "$CONTAINER_RUNNER_NAME" ]]; then
  if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_RUNNER_NAME}$"; then
    status_line ok "Runner container running: ${CONTAINER_RUNNER_NAME}"
  else
    status_line fail "Runner container ${CONTAINER_RUNNER_NAME} not running"
  fi
fi

header "Runner Registration Log Scan"
if [[ -n "$CONTAINER_RUNNER_NAME" ]] && docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_RUNNER_NAME}$"; then
  LOG=$(docker logs --tail 400 "$CONTAINER_RUNNER_NAME" 2>/dev/null)
  if echo "$LOG" | grep -q "Runner successfully added"; then
    status_line ok "Runner log shows successful registration"
  else
    status_line fail "Registration success string not found in last 400 log lines"
  fi
  if echo "$LOG" | grep -q "Connected to GitHub"; then
    status_line ok "Runner log shows connection to GitHub"
  else
    status_line warn "Connection confirmation string not found"
  fi
fi

header "Environment File Check"
ENV_LOCAL="docs/tutorials/liquibase/runner_config/runner.env.local"
ENV_EXTERNAL="/data/github-runner-config/runner.env"
ENV_USED=""
if [[ -f "$ENV_LOCAL" ]]; then
  ENV_USED="$ENV_LOCAL"; status_line ok "Found local env file: $ENV_LOCAL"
elif [[ -f "$ENV_EXTERNAL" ]]; then
  ENV_USED="$ENV_EXTERNAL"; status_line ok "Found external env file: $ENV_EXTERNAL"
else
  status_line warn "No env file found at expected locations"
fi
if [[ -n "$ENV_USED" ]]; then
  if grep -q '^REPO_URL=' "$ENV_USED"; then
    REPO=$(grep '^REPO_URL=' "$ENV_USED" | head -1 | cut -d= -f2-)
    [[ -n "$REPO" ]] && status_line ok "REPO_URL present (${REPO})" || status_line fail "REPO_URL empty"
  else
    status_line fail "REPO_URL not defined in env file"
  fi
fi

header "GitHub CLI Auth (Optional)"
if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    USER=$(gh auth status 2>/dev/null | grep -i 'Logged in to' | head -1 | awk '{print $4}')
    status_line ok "gh authenticated as ${USER:-(unknown)}"
  else
    status_line warn "gh installed but not authenticated"
  fi
else
  status_line warn "gh CLI not installed"
fi

header "GitHub Runner API Status"
if command -v gh >/dev/null 2>&1 && [[ -n "$RUNNER_NAME" ]]; then
  if gh auth status >/dev/null 2>&1; then
    OWNER=""; REPO_NAME=""
    if [[ -n "$REPO" ]]; then
      OWNER=$(echo "$REPO" | sed -E 's#https?://github.com/([^/]+)/([^/]+).*#\1#')
      REPO_NAME=$(echo "$REPO" | sed -E 's#https?://github.com/([^/]+)/([^/]+).*#\2#' | sed 's/.git$//')
    fi
    if [[ -z "$OWNER" || -z "$REPO_NAME" ]]; then
      status_line warn "Could not parse owner/repo from REPO_URL ($REPO)"
    else
      API_JSON=$(gh api -H 'Accept: application/vnd.github+json' repos/$OWNER/$REPO_NAME/actions/runners 2>/dev/null)
      if [[ $? -ne 0 || -z "$API_JSON" ]]; then
        status_line warn "GitHub API call failed for $OWNER/$REPO_NAME (scopes or repo)"
      else
        if echo "$API_JSON" | grep -q '"name":"'$RUNNER_NAME'"'; then
          status_line ok "API lists registered runner '$RUNNER_NAME'"
        else
          COUNT=$(echo "$API_JSON" | sed -n 's/.*"total_count":\([0-9]*\).*/\1/p')
          status_line fail "API does not list registered runner '$RUNNER_NAME' (total runners: ${COUNT:-unknown})"
        fi
      fi
    fi
  else
    status_line warn "Skipping API runner check (gh not authenticated)"
  fi
elif [[ -z "$RUNNER_NAME" ]]; then
  status_line warn "Runner registered name unknown (set with --runner-registered or RUNNER_NAME)"
else
  status_line warn "gh CLI not installed; skipping API runner check"
fi

header "Connectivity: Runner -> SQL Server"
if [[ -n "$CONTAINER_RUNNER_NAME" ]] && docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_RUNNER_NAME}$" && [[ -n "$SQL_FOUND" ]]; then
  if docker exec "$CONTAINER_RUNNER_NAME" ping -c 1 "$SQL_FOUND" >/dev/null 2>&1; then
    status_line ok "Ping from runner container to $SQL_FOUND successful"
  else
    status_line fail "Ping from runner container to $SQL_FOUND failed"
  fi
  if docker exec "$CONTAINER_RUNNER_NAME" bash -c "timeout 3 bash -c '>/dev/tcp/$SQL_FOUND/1433'" 2>/dev/null; then
    status_line ok "Port 1433 reachable using /dev/tcp from runner container"
  else
    status_line fail "Port 1433 not reachable via /dev/tcp from runner container"
  fi
fi

header "Summary"
TOTAL_PASS=${#PASS[@]}; TOTAL_FAIL=${#FAIL[@]}; TOTAL_WARN=${#WARNINGS[@]}
printf "Passed: %s  Failed: %s  Warnings: %s\n" "$TOTAL_PASS" "$TOTAL_FAIL" "$TOTAL_WARN"

if (( CRITICAL_FAIL )); then
  color red "\nOne or more critical checks failed."
  echo ""; color yellow "Recommended actions:"; echo ""
  for f in "${FAIL[@]}"; do echo " - $f"; done
  exit 1
else
  color green "\nAll critical checks passed."
  echo ""; color cyan "Environment looks healthy."; echo ""
  exit 0
fi
