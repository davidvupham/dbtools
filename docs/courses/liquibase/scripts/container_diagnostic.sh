#!/usr/bin/env bash
# Diagnostic script to troubleshoot container detection issues
# in sqlcmd_tutorial.sh, especially in corporate environments.

set -euo pipefail

detect_runtime() {
  if [[ -n "${CONTAINER_RUNTIME:-}" ]]; then
    echo "$CONTAINER_RUNTIME"
    return
  fi

  local os_id=""
  if [[ -f /etc/os-release ]]; then
    os_id="$(source /etc/os-release && echo "${ID} ${ID_LIKE:-}")"
  fi

  if [[ "$os_id" =~ (rhel|fedora|centos|rocky|almalinux) ]]; then
    if command -v podman &> /dev/null; then
      echo "podman"
      return
    fi
  fi

  if [[ "$os_id" =~ (ubuntu|debian) ]]; then
    if command -v docker &> /dev/null; then
      echo "docker"
      return
    fi
  fi

  if command -v docker &> /dev/null; then
    echo "docker"
  elif command -v podman &> /dev/null; then
    echo "podman"
  else
    echo "none"
  fi
}

CR="$(detect_runtime)"
CONTAINER_NAME="${CONTAINER_NAME:-mssql_dev}"

echo "=== Container Detection Diagnostic ==="
echo ""
echo "--- Environment ---"
echo "Runtime detected:    $CR"
echo "CONTAINER_RUNTIME:   ${CONTAINER_RUNTIME:-<not set>}"
echo "CONTAINER_NAME:      $CONTAINER_NAME"
echo "Current user:        $(whoami)"
echo "User ID:             $(id -u)"
echo ""

if [[ "$CR" == "none" ]]; then
  echo "ERROR: No container runtime (docker/podman) found."
  exit 1
fi

echo "--- Runtime Info ---"
echo "Runtime version:"
$CR --version
echo ""

if [[ "$CR" == "docker" ]]; then
  echo "Docker context:"
  docker context ls 2>/dev/null || echo "  (docker context not available)"
  echo ""
  echo "DOCKER_HOST: ${DOCKER_HOST:-<not set>}"
  echo ""
elif [[ "$CR" == "podman" ]]; then
  echo "Podman connections:"
  podman system connection list 2>/dev/null || echo "  (no remote connections configured)"
  echo ""
  echo "Podman info (rootless check):"
  podman info --format '{{.Host.Security.Rootless}}' 2>/dev/null && echo " (rootless mode)" || echo "  (could not determine)"
  echo ""
fi

echo "--- All Running Containers ---"
$CR ps --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null || $CR ps
echo ""

echo "--- Raw Container Names ---"
echo "(Showing exact output with visible whitespace)"
$CR ps --format '{{.Names}}' | while IFS= read -r name; do
  # Show length and hex dump of any non-printable chars
  printf "  Found: '%s' (length: %d)\n" "$name" "${#name}"
done
echo ""

echo "--- Container Name Match Test ---"
echo "Looking for exact match: '^${CONTAINER_NAME}\$'"
if $CR ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "  RESULT: MATCH FOUND - Container '$CONTAINER_NAME' detected correctly"
else
  echo "  RESULT: NO MATCH"
  echo ""
  echo "  Trying partial/substring match..."
  partial_matches=$($CR ps --format '{{.Names}}' | grep "$CONTAINER_NAME" 2>/dev/null || true)
  if [[ -n "$partial_matches" ]]; then
    echo "  Partial matches found:"
    echo "$partial_matches" | while read -r match; do
      echo "    - '$match'"
    done
    echo ""
    echo "  SUGGESTION: The container name may have a prefix (e.g., docker-compose project name)."
    echo "  Try running sqlcmd_tutorial.sh with: --container <full-name>"
  else
    echo "  No partial matches found either."
    echo ""
    echo "  SUGGESTION: The container may be:"
    echo "    - Not running (check: $CR ps -a)"
    echo "    - Running under a different user (try: sudo $CR ps)"
    echo "    - On a remote host (check DOCKER_HOST or podman connections)"
  fi
fi
echo ""

echo "--- All Containers (including stopped) ---"
$CR ps -a --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null | head -20 || $CR ps -a | head -20
echo ""

echo "=== Diagnostic Complete ==="
