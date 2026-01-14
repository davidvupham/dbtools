#!/usr/bin/env bash
# ==============================================================================
# Container Image Build Script with Corporate Proxy Support
# ==============================================================================
#
# PURPOSE:
# Build Docker/Podman images with automatic detection of corporate registry
# proxy (JFrog Artifactory) configuration. Works with any Dockerfile that
# uses the REGISTRY_PREFIX build argument pattern.
#
# FEATURES:
# - Auto-detects JFrog authentication in ~/.docker/config.json
# - Auto-detects registry mirrors in Docker daemon configuration
# - Falls back to Docker Hub if no corporate proxy is configured
# - Supports manual override via environment variables
# - OS-aware container runtime selection:
#   - RHEL/CentOS/Fedora: prefers Podman (standard on Red Hat systems)
#   - Ubuntu/Debian: prefers Docker (standard on Debian-based systems)
#   - Override with CONTAINER_RUNTIME=docker or CONTAINER_RUNTIME=podman
#
# USAGE:
#   build_container_image.sh <context_dir> [image_name:tag] [-- extra_args...]
#
# EXAMPLES:
#   # Build liquibase image (auto-detect registry, default name from directory)
#   ./scripts/build_container_image.sh docker/liquibase
#
#   # Build with custom image name and tag
#   ./scripts/build_container_image.sh docker/liquibase myregistry/liquibase:v1.0
#
#   # Pass additional docker build arguments
#   ./scripts/build_container_image.sh docker/liquibase liquibase:latest -- --no-cache --progress=plain
#
#   # Override registry prefix manually
#   REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ ./scripts/build_container_image.sh docker/liquibase
#
#   # Specify JFrog domain pattern
#   JFROG_REGISTRY=mycompany.jfrog.io ./scripts/build_container_image.sh docker/liquibase
#
# DOCKERFILE REQUIREMENTS:
#   Your Dockerfile should include the REGISTRY_PREFIX ARG pattern:
#
#     ARG REGISTRY_PREFIX=docker.io/library/
#     FROM ${REGISTRY_PREFIX}eclipse-temurin:21-jre-ubi9-minimal
#
# ==============================================================================

set -euo pipefail

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# JFrog configuration
# Override JFROG_REGISTRY to match your corporate JFrog domain
JFROG_REGISTRY="${JFROG_REGISTRY:-jfrog.io}"
JFROG_PROXY_PATH="${JFROG_PROXY_PATH:-docker-proxy/library}"

# Default registry (Docker Hub)
DEFAULT_REGISTRY_PREFIX="docker.io/library/"

# Docker config file locations
DOCKER_USER_CONFIG="${HOME}/.docker/config.json"
DOCKER_DAEMON_CONFIG="/etc/docker/daemon.json"
DOCKER_ROOTLESS_CONFIG="${HOME}/.config/docker/daemon.json"

# Podman config locations (for RHEL/Fedora users)
PODMAN_AUTH_CONFIG="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/containers/auth.json"
PODMAN_USER_AUTH="${HOME}/.config/containers/auth.json"

# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <context_dir> [image_name:tag] [-- extra_args...]

Build a container image with automatic JFrog proxy detection and OS-aware
container runtime selection.

OPTIONS:
  -h, --help        Show this help message and exit

ARGUMENTS:
  context_dir       Directory containing the Dockerfile (required)
  image_name:tag    Image name and optional tag (default: directory name:latest)
  extra_args        Additional arguments passed to docker/podman build (after --)

ENVIRONMENT VARIABLES:
  CONTAINER_RUNTIME Override container runtime (docker or podman)
                    Auto-detected based on OS if not set
  REGISTRY_PREFIX   Override the registry prefix for base images
                    Example: xyz.jfrog.io/docker-proxy/library/
  JFROG_REGISTRY    JFrog domain pattern to search for (default: jfrog.io)
  JFROG_PROXY_PATH  Path within JFrog for Docker Hub proxy (default: docker-proxy/library)
  IMAGE_NAME        Override image name
  IMAGE_TAG         Override image tag

OS-AWARE RUNTIME SELECTION:
  The script automatically selects the container runtime based on OS:
    • RHEL/CentOS/Fedora/Rocky/Alma  →  podman (Red Hat standard)
    • Ubuntu/Debian/Mint             →  docker (Debian standard)
    • Other/Unknown                  →  docker (fallback)

JFROG AUTO-DETECTION:
  The script checks for JFrog Artifactory configuration in:
    • ~/.docker/config.json          (Docker auth)
    • /etc/docker/daemon.json        (Docker daemon mirrors)
    • ~/.config/containers/auth.json (Podman auth)

  If JFrog auth is found, REGISTRY_PREFIX is automatically set to pull
  base images through your corporate proxy.

DOCKERFILE REQUIREMENTS:
  Your Dockerfile should include the REGISTRY_PREFIX ARG pattern:

    ARG REGISTRY_PREFIX=docker.io/library/
    FROM \${REGISTRY_PREFIX}eclipse-temurin:21-jre-ubi9-minimal

EXAMPLES:
  # Basic build (auto-detect everything)
  $(basename "$0") docker/liquibase

  # Custom image name and tag
  $(basename "$0") docker/liquibase myregistry/liquibase:v1.0

  # Pass extra arguments to docker/podman build
  $(basename "$0") docker/liquibase liquibase:latest -- --no-cache --progress=plain

  # Force specific container runtime
  CONTAINER_RUNTIME=podman $(basename "$0") docker/liquibase

  # Override registry prefix (skip auto-detection)
  REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ $(basename "$0") docker/liquibase

  # Build from absolute path
  $(basename "$0") /path/to/my/dockerfile/dir myimage:latest

EOF
    exit 0
}

log_info() {
    echo "[INFO] $*" >&2
}

log_warn() {
    echo "[WARN] $*" >&2
}

log_error() {
    echo "[ERROR] $*" >&2
}

log_success() {
    echo "[✓] $*" >&2
}

# Check if a file contains JFrog registry reference
check_file_for_jfrog() {
    local file="$1"
    if [[ -f "$file" ]] && grep -q "$JFROG_REGISTRY" "$file" 2>/dev/null; then
        return 0
    fi
    return 1
}

# Extract the full JFrog registry URL from config
extract_jfrog_url() {
    local file="$1"
    # Extract the JFrog URL from the auths section
    # Handles formats like: "xyz.jfrog.io": { or "https://xyz.jfrog.io": {
    if [[ -f "$file" ]]; then
        grep -oE "[a-zA-Z0-9.-]+\.${JFROG_REGISTRY}[^\"]*" "$file" 2>/dev/null | head -1 || true
    fi
}

# Detect if JFrog proxy is configured
detect_jfrog_config() {
    local jfrog_url=""

    # Check Docker user config (authentication)
    if check_file_for_jfrog "$DOCKER_USER_CONFIG"; then
        jfrog_url=$(extract_jfrog_url "$DOCKER_USER_CONFIG")
        if [[ -n "$jfrog_url" ]]; then
            log_info "JFrog authentication found in $DOCKER_USER_CONFIG"
            log_info "  Registry: $jfrog_url"
            echo "$jfrog_url"
            return 0
        fi
    fi

    # Check Docker daemon config (registry mirrors)
    if check_file_for_jfrog "$DOCKER_DAEMON_CONFIG"; then
        jfrog_url=$(extract_jfrog_url "$DOCKER_DAEMON_CONFIG")
        if [[ -n "$jfrog_url" ]]; then
            log_info "JFrog registry mirror found in $DOCKER_DAEMON_CONFIG"
            echo "$jfrog_url"
            return 0
        fi
    fi

    # Check rootless Docker daemon config
    if check_file_for_jfrog "$DOCKER_ROOTLESS_CONFIG"; then
        jfrog_url=$(extract_jfrog_url "$DOCKER_ROOTLESS_CONFIG")
        if [[ -n "$jfrog_url" ]]; then
            log_info "JFrog registry mirror found in $DOCKER_ROOTLESS_CONFIG"
            echo "$jfrog_url"
            return 0
        fi
    fi

    # Check Podman auth configs
    for podman_config in "$PODMAN_AUTH_CONFIG" "$PODMAN_USER_AUTH"; do
        if check_file_for_jfrog "$podman_config"; then
            jfrog_url=$(extract_jfrog_url "$podman_config")
            if [[ -n "$jfrog_url" ]]; then
                log_info "JFrog authentication found in $podman_config"
                echo "$jfrog_url"
                return 0
            fi
        fi
    done

    return 1
}

# Detect if we're building a Microsoft SQL Server image
# Checks the Dockerfile for Microsoft Container Registry references
is_microsoft_sql_server_image() {
    local dockerfile="$1"
    if [[ -f "$dockerfile" ]]; then
        # Check if Dockerfile uses mcr.microsoft.com or mssql/server
        if grep -qE "(mcr\.microsoft\.com|mssql/server)" "$dockerfile" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# Build the registry prefix from JFrog URL
build_registry_prefix() {
    local jfrog_url="$1"
    local proxy_path="$2"

    # Remove protocol if present
    jfrog_url="${jfrog_url#https://}"
    jfrog_url="${jfrog_url#http://}"

    # Remove trailing slash
    jfrog_url="${jfrog_url%/}"

    # If URL doesn't include proxy path, add the specified proxy path
    if [[ ! "$jfrog_url" =~ $proxy_path ]]; then
        echo "${jfrog_url}/${proxy_path}/"
    else
        echo "${jfrog_url}/"
    fi
}

# Detect the Linux distribution family
# Returns: rhel, debian, or unknown
detect_os_family() {
    local os_family="unknown"

    # Check /etc/os-release (standard on modern Linux)
    if [[ -f /etc/os-release ]]; then
        # shellcheck source=/dev/null
        source /etc/os-release

        # ID_LIKE contains parent distros (e.g., "rhel fedora" or "debian")
        # ID contains the specific distro (e.g., "ubuntu", "rhel", "fedora")
        local id_lower="${ID,,}"
        local id_like_lower="${ID_LIKE,,}"

        # Check for RHEL family (RHEL, CentOS, Fedora, Rocky, Alma, Oracle Linux)
        if [[ "$id_lower" =~ ^(rhel|centos|fedora|rocky|almalinux|ol)$ ]] || \
           [[ "$id_like_lower" =~ rhel|fedora ]]; then
            os_family="rhel"
        # Check for Debian family (Debian, Ubuntu, Mint, Pop!_OS)
        elif [[ "$id_lower" =~ ^(debian|ubuntu|linuxmint|pop)$ ]] || \
             [[ "$id_like_lower" =~ debian|ubuntu ]]; then
            os_family="debian"
        fi
    # Fallback: check for distro-specific files
    elif [[ -f /etc/redhat-release ]]; then
        os_family="rhel"
    elif [[ -f /etc/debian_version ]]; then
        os_family="debian"
    fi

    echo "$os_family"
}

# Detect container runtime (docker or podman)
# Priority:
#   1. CONTAINER_RUNTIME environment variable (explicit override)
#   2. OS-based preference (podman for RHEL, docker for Ubuntu/Debian)
#   3. Whatever is available
# Note: This function returns the runtime via stdout, so all log messages
#       must go to stderr to avoid corrupting the return value.
detect_container_runtime() {
    # Allow explicit override via environment variable
    if [[ -n "${CONTAINER_RUNTIME:-}" ]]; then
        if command -v "$CONTAINER_RUNTIME" &>/dev/null; then
            echo "[INFO] Using CONTAINER_RUNTIME from environment: $CONTAINER_RUNTIME" >&2
            echo "$CONTAINER_RUNTIME"
            return 0
        else
            log_warn "CONTAINER_RUNTIME=$CONTAINER_RUNTIME not found, auto-detecting..."
        fi
    fi

    local os_family
    os_family=$(detect_os_family)

    local preferred_runtime fallback_runtime
    case "$os_family" in
        rhel)
            # RHEL/CentOS/Fedora: Podman is the standard container runtime
            preferred_runtime="podman"
            fallback_runtime="docker"
            echo "[INFO] Detected RHEL-family OS, preferring Podman" >&2
            ;;
        debian)
            # Ubuntu/Debian: Docker is more commonly used
            preferred_runtime="docker"
            fallback_runtime="podman"
            echo "[INFO] Detected Debian-family OS, preferring Docker" >&2
            ;;
        *)
            # Unknown OS: try docker first (more common in general)
            preferred_runtime="docker"
            fallback_runtime="podman"
            echo "[INFO] Unknown OS family, trying Docker first" >&2
            ;;
    esac

    # Try preferred runtime first
    if command -v "$preferred_runtime" &>/dev/null; then
        echo "$preferred_runtime"
        return 0
    fi

    # Try fallback runtime
    if command -v "$fallback_runtime" &>/dev/null; then
        log_warn "$preferred_runtime not found, using $fallback_runtime"
        echo "$fallback_runtime"
        return 0
    fi

    # Neither found
    log_error "Neither docker nor podman found in PATH"
    log_error "Please install Docker or Podman:"
    log_error "  Ubuntu/Debian: sudo apt install docker.io"
    log_error "  RHEL/Fedora:   sudo dnf install podman"
    exit 1
}

# ------------------------------------------------------------------------------
# Argument Parsing
# ------------------------------------------------------------------------------

parse_args() {
    CONTEXT_DIR=""
    IMAGE_SPEC=""
    EXTRA_ARGS=()

    # Parse positional arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                ;;
            --)
                shift
                EXTRA_ARGS=("$@")
                break
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                ;;
            *)
                if [[ -z "$CONTEXT_DIR" ]]; then
                    CONTEXT_DIR="$1"
                elif [[ -z "$IMAGE_SPEC" ]]; then
                    IMAGE_SPEC="$1"
                else
                    log_error "Unexpected argument: $1"
                    usage
                fi
                shift
                ;;
        esac
    done

    # Validate context directory
    if [[ -z "$CONTEXT_DIR" ]]; then
        log_error "Context directory is required"
        usage
    fi

    # Resolve context directory (support both absolute and relative paths)
    if [[ ! "$CONTEXT_DIR" = /* ]]; then
        # Relative path - resolve from current directory or repo root
        if [[ -d "$CONTEXT_DIR" ]]; then
            CONTEXT_DIR="$(cd "$CONTEXT_DIR" && pwd)"
        elif [[ -d "$REPO_ROOT/$CONTEXT_DIR" ]]; then
            CONTEXT_DIR="$(cd "$REPO_ROOT/$CONTEXT_DIR" && pwd)"
        else
            log_error "Context directory not found: $CONTEXT_DIR"
            exit 1
        fi
    fi

    # Verify Dockerfile exists
    if [[ ! -f "$CONTEXT_DIR/Dockerfile" ]]; then
        log_error "No Dockerfile found in: $CONTEXT_DIR"
        exit 1
    fi

    # Parse image spec or use defaults
    if [[ -n "$IMAGE_SPEC" ]]; then
        if [[ "$IMAGE_SPEC" == *:* ]]; then
            IMAGE_NAME="${IMAGE_NAME:-${IMAGE_SPEC%:*}}"
            IMAGE_TAG="${IMAGE_TAG:-${IMAGE_SPEC##*:}}"
        else
            IMAGE_NAME="${IMAGE_NAME:-$IMAGE_SPEC}"
            IMAGE_TAG="${IMAGE_TAG:-latest}"
        fi
    else
        # Default to directory name
        IMAGE_NAME="${IMAGE_NAME:-$(basename "$CONTEXT_DIR")}"
        IMAGE_TAG="${IMAGE_TAG:-latest}"
    fi
}

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

main() {
    parse_args "$@"

    log_info "Container Image Builder"
    log_info "======================="
    log_info "Context: $CONTEXT_DIR"

    # Detect container runtime (OS-aware: podman on RHEL, docker on Ubuntu)
    CONTAINER_RUNTIME=$(detect_container_runtime)
    log_success "Using: $CONTAINER_RUNTIME"

    # Determine registry prefix
    if [[ -n "${REGISTRY_PREFIX:-}" ]]; then
        # Manual override via environment variable
        log_info "Using REGISTRY_PREFIX from environment: $REGISTRY_PREFIX"
    else
        # Auto-detect JFrog configuration
        log_info "Checking for JFrog proxy configuration..."

        if jfrog_url=$(detect_jfrog_config); then
            # Detect if this is a Microsoft SQL Server image
            local proxy_path="$JFROG_PROXY_PATH"
            if is_microsoft_sql_server_image "$CONTEXT_DIR/Dockerfile"; then
                proxy_path="docker-microsoft-proxy"
                log_info "Microsoft SQL Server image detected, using docker-microsoft-proxy"
            fi
            REGISTRY_PREFIX=$(build_registry_prefix "$jfrog_url" "$proxy_path")
            log_success "JFrog proxy detected!"
        else
            REGISTRY_PREFIX=""
            log_info "No JFrog proxy detected, using Dockerfile defaults"
        fi
    fi

    if [[ -n "$REGISTRY_PREFIX" ]]; then
        log_info "Registry prefix: $REGISTRY_PREFIX"
    else
        log_info "Registry prefix: (using Dockerfile default)"
    fi
    log_info ""

    # Build the image
    log_info "Building image: ${IMAGE_NAME}:${IMAGE_TAG}"
    log_info "------------------------------"

    # Construct build command
    BUILD_CMD=(
        "$CONTAINER_RUNTIME" build
        -t "${IMAGE_NAME}:${IMAGE_TAG}"
    )

    # Only add REGISTRY_PREFIX if explicitly set (JFrog detected or manual override)
    if [[ -n "$REGISTRY_PREFIX" ]]; then
        BUILD_CMD+=(--build-arg "REGISTRY_PREFIX=${REGISTRY_PREFIX}")
    fi

    # Add --format docker for podman (required for HEALTHCHECK)
    if [[ "$CONTAINER_RUNTIME" == "podman" ]]; then
        BUILD_CMD+=(--format docker)
    fi

    # Add any extra arguments
    if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
        BUILD_CMD+=("${EXTRA_ARGS[@]}")
    fi

    # Add build context
    BUILD_CMD+=("$CONTEXT_DIR")

    # Execute build
    log_info "Running: ${BUILD_CMD[*]}"
    "${BUILD_CMD[@]}"

    log_info ""
    log_success "Build complete: ${IMAGE_NAME}:${IMAGE_TAG}"
    log_info ""
    log_info "To run:"
    log_info "  $CONTAINER_RUNTIME run --rm ${IMAGE_NAME}:${IMAGE_TAG}"
}

# Run main with all script arguments
main "$@"
