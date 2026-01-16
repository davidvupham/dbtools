#!/usr/bin/env bash
# Container Runtime Helper - Auto-detects docker/podman based on OS
#
# Usage:
#   cr run --rm liquibase:latest --version
#   cr ps
#   cr build -t myimage .
#   cr build -t myimage:tag /path/to/context
#
# For 'build' commands, delegates to build_container_image.sh which provides:
#   - JFrog proxy auto-detection
#   - OS-aware container runtime selection
#   - Proper --format docker for Podman (HEALTHCHECK support)
#
# Override detection: export CONTAINER_RUNTIME=docker  (or podman)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_SCRIPT="$SCRIPT_DIR/build_container_image.sh"

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

# Handle 'build' command specially - delegate to build_container_image.sh
handle_build() {
  local image_name=""
  local context_dir=""
  local extra_args=()

  # Parse build arguments to extract -t/--tag and context directory
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -t|--tag)
        image_name="$2"
        shift 2
        ;;
      -t=*|--tag=*)
        image_name="${1#*=}"
        shift
        ;;
      -f|--file)
        # Pass through Dockerfile path as extra arg
        extra_args+=("$1" "$2")
        shift 2
        ;;
      -f=*|--file=*)
        extra_args+=("$1")
        shift
        ;;
      --format)
        # Skip --format flag - build_container_image.sh handles this automatically
        # (adds --format docker for podman to support HEALTHCHECK)
        shift 2
        ;;
      --format=*)
        # Skip --format=value - handled automatically
        shift
        ;;
      --)
        shift
        extra_args+=("$@")
        break
        ;;
      -*)
        # Other flags - pass through as extra args
        extra_args+=("$1")
        shift
        ;;
      *)
        # Positional argument - should be context directory
        context_dir="$1"
        shift
        ;;
    esac
  done

  # Validate we have required arguments
  if [[ -z "$context_dir" ]]; then
    echo "Error: No build context directory specified" >&2
    echo "Usage: cr build -t image:tag /path/to/context" >&2
    exit 1
  fi

  # Check if build_container_image.sh exists
  if [[ ! -x "$BUILD_SCRIPT" ]]; then
    echo "Warning: build_container_image.sh not found, falling back to direct $CR build" >&2
    CR="$(detect_runtime)"
    exec "$CR" build ${image_name:+-t "$image_name"} "${extra_args[@]}" "$context_dir"
  fi

  # Delegate to build_container_image.sh
  # Format: build_container_image.sh <context_dir> [image_name:tag] [-- extra_args...]
  local build_args=("$context_dir")
  if [[ -n "$image_name" ]]; then
    build_args+=("$image_name")
  fi
  if [[ ${#extra_args[@]} -gt 0 ]]; then
    build_args+=("--" "${extra_args[@]}")
  fi

  exec "$BUILD_SCRIPT" "${build_args[@]}"
}

# Main logic
if [[ $# -eq 0 ]]; then
  echo "Usage: cr <command> [args...]" >&2
  echo "Commands are passed to docker/podman (auto-detected)" >&2
  echo "Build commands use build_container_image.sh for JFrog proxy support" >&2
  exit 1
fi

case "$1" in
  build)
    shift
    handle_build "$@"
    ;;
  *)
    # Pass all other commands to detected runtime
    CR="$(detect_runtime)"
    exec "$CR" "$@"
    ;;
esac
