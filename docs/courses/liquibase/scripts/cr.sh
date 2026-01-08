#!/usr/bin/env bash
# Container Runtime Helper - Auto-detects docker/podman based on OS
# 
# Usage:
#   cr run --rm liquibase:latest --version
#   cr ps
#   cr build -t myimage .
#
# Override detection: export CONTAINER_RUNTIME=docker  (or podman)

detect_runtime() {
  # 1. Allow override via env var
  if [[ -n "${CONTAINER_RUNTIME:-}" ]]; then
    echo "$CONTAINER_RUNTIME"
    return
  fi

  # 2. Check OS preference from /etc/os-release
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

  # 3. Fallback: check which binary exists
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

# Pass all arguments to detected runtime
exec "$CR" "$@"
