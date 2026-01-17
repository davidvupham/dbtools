#!/usr/bin/env bash
# ==============================================================================
# Container Image Build Tests
# ==============================================================================
#
# PURPOSE:
# Automated tests for building and verifying all container images in the
# docker/tools/ and docker/ directories.
#
# FEATURES:
# - OS-aware container runtime detection (Docker for Ubuntu, Podman for RHEL)
# - Builds all tool images and service images
# - Health check verification for each image
# - Detailed logging with pass/fail tracking
# - Support for corporate proxy builds via REGISTRY_PREFIX
#
# USAGE:
#   ./scripts/test/test_container_builds.sh [OPTIONS]
#
# OPTIONS:
#   -h, --help          Show help message
#   -v, --verbose       Show detailed build output
#   -k, --keep-images   Keep images after tests (default: cleanup)
#   --tools-only        Only test tool images (docker/tools/)
#   --services-only     Only test service images (docker/)
#   --image NAME        Test only the specified image
#
# EXAMPLES:
#   ./scripts/test/test_container_builds.sh
#   ./scripts/test/test_container_builds.sh --verbose
#   ./scripts/test/test_container_builds.sh --image psql
#   REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ ./scripts/test/test_container_builds.sh
#
# ==============================================================================

set -euo pipefail

# ------------------------------------------------------------------------------
# Script Configuration
# ------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Test configuration
VERBOSE="${VERBOSE:-false}"
KEEP_IMAGES="${KEEP_IMAGES:-false}"
TOOLS_ONLY="${TOOLS_ONLY:-false}"
SERVICES_ONLY="${SERVICES_ONLY:-false}"
declare -a SELECTED_IMAGES=()

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Logging
LOG_FILE="/tmp/container_build_test_$(date +%Y%m%d_%H%M%S).log"
touch "$LOG_FILE"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Container runtime (detected later)
CONTAINER_RUNTIME=""

# Image prefix for test builds
TEST_IMAGE_PREFIX="test-build"

# ------------------------------------------------------------------------------
# Tool Images Configuration
# ------------------------------------------------------------------------------
declare -A TOOL_IMAGES=(
    ["psql"]="docker/tools/psql"
    ["snowsql"]="docker/tools/snowsql"
    ["mongosh"]="docker/tools/mongosh"
    ["mssql-tools"]="docker/tools/mssql-tools"
    ["clickhouse-client"]="docker/tools/clickhouse-client"
    ["db-tools"]="docker/tools/db-tools"
)

# Health check commands for each tool image
declare -A TOOL_HEALTH_CHECKS=(
    ["psql"]="psql --version"
    ["snowsql"]="snowsql --version"
    ["mongosh"]="mongosh --version"
    ["mssql-tools"]="sqlcmd -?"
    ["clickhouse-client"]="clickhouse-client --version"
    ["db-tools"]="psql --version && sqlcmd -? && mongosh --version && test -f /opt/snowsql/snowsql"
)

# ------------------------------------------------------------------------------
# Service Images Configuration
# ------------------------------------------------------------------------------
declare -A SERVICE_IMAGES=(
    ["grafana"]="docker/grafana"
    ["clickhouse"]="docker/clickhouse"
)

# Health check commands for each service image
declare -A SERVICE_HEALTH_CHECKS=(
    ["grafana"]="grafana-cli --version"
    ["clickhouse"]="clickhouse-server --version"
)

# ------------------------------------------------------------------------------
# Logging Functions
# ------------------------------------------------------------------------------
# All log output goes to stderr and log file, keeping stdout clean for return values
log() {
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "[$timestamp] $*" >> "$LOG_FILE"
    echo -e "[$timestamp] $*" >&2
}

log_info() {
    log "${BLUE}[INFO]${NC} $*"
}

log_pass() {
    log "${GREEN}[PASS]${NC} $*"
}

log_fail() {
    log "${RED}[FAIL]${NC} $*"
}

log_skip() {
    log "${YELLOW}[SKIP]${NC} $*"
}

log_section() {
    log ""
    log "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    log "${CYAN} $*${NC}"
    log "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
}

# ------------------------------------------------------------------------------
# Usage
# ------------------------------------------------------------------------------
usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Automated tests for building and verifying container images.

OPTIONS:
  -h, --help          Show this help message
  -v, --verbose       Show detailed build output
  -k, --keep-images   Keep images after tests (default: cleanup)
  --tools-only        Only test tool images (docker/tools/)
  --services-only     Only test service images (docker/)
  --image NAME        Test specified image(s) - can be used multiple times

ENVIRONMENT VARIABLES:
  REGISTRY_PREFIX     Override registry prefix for proxy builds
  CONTAINER_RUNTIME   Override container runtime (docker or podman)

EXAMPLES:
  $(basename "$0")                                    # Run all tests
  $(basename "$0") --verbose                          # Run with detailed output
  $(basename "$0") --image psql                       # Test only psql image
  $(basename "$0") --image psql --image mongosh       # Test multiple images
  $(basename "$0") --tools-only                       # Test only tool images

LOG FILE:
  Results are logged to: $LOG_FILE

EOF
    exit 0
}

# ------------------------------------------------------------------------------
# OS and Container Runtime Detection
# ------------------------------------------------------------------------------
detect_os_family() {
    local os_family="unknown"

    if [[ -f /etc/os-release ]]; then
        # shellcheck source=/dev/null
        source /etc/os-release

        local id_lower="${ID,,}"
        local id_like_lower="${ID_LIKE,,}"

        # RHEL family (RHEL, CentOS, Fedora, Rocky, Alma, Oracle Linux)
        if [[ "$id_lower" =~ ^(rhel|centos|fedora|rocky|almalinux|ol)$ ]] || \
           [[ "$id_like_lower" =~ rhel|fedora ]]; then
            os_family="rhel"
        # Debian family (Debian, Ubuntu, Mint, Pop!_OS)
        elif [[ "$id_lower" =~ ^(debian|ubuntu|linuxmint|pop)$ ]] || \
             [[ "$id_like_lower" =~ debian|ubuntu ]]; then
            os_family="debian"
        fi
    elif [[ -f /etc/redhat-release ]]; then
        os_family="rhel"
    elif [[ -f /etc/debian_version ]]; then
        os_family="debian"
    fi

    echo "$os_family"
}

detect_container_runtime() {
    # Allow explicit override
    if [[ -n "${CONTAINER_RUNTIME:-}" ]]; then
        if command -v "$CONTAINER_RUNTIME" &>/dev/null; then
            log_info "Using CONTAINER_RUNTIME from environment: $CONTAINER_RUNTIME"
            echo "$CONTAINER_RUNTIME"
            return 0
        else
            log_fail "CONTAINER_RUNTIME=$CONTAINER_RUNTIME not found"
            return 1
        fi
    fi

    local os_family
    os_family=$(detect_os_family)

    local preferred_runtime fallback_runtime
    case "$os_family" in
        rhel)
            preferred_runtime="podman"
            fallback_runtime="docker"
            log_info "Detected RHEL-family OS, preferring Podman"
            ;;
        debian)
            preferred_runtime="docker"
            fallback_runtime="podman"
            log_info "Detected Debian-family OS, preferring Docker"
            ;;
        *)
            preferred_runtime="docker"
            fallback_runtime="podman"
            log_info "Unknown OS family, trying Docker first"
            ;;
    esac

    if command -v "$preferred_runtime" &>/dev/null; then
        echo "$preferred_runtime"
        return 0
    fi

    if command -v "$fallback_runtime" &>/dev/null; then
        log_info "$preferred_runtime not found, using $fallback_runtime"
        echo "$fallback_runtime"
        return 0
    fi

    log_fail "Neither docker nor podman found in PATH"
    return 1
}

# ------------------------------------------------------------------------------
# Test Functions
# ------------------------------------------------------------------------------
run_test() {
    local test_name="$1"
    local test_cmd="$2"
    local allow_fail="${3:-false}"

    TESTS_RUN=$((TESTS_RUN + 1))

    log_info "Running: $test_name"

    local output
    local exit_code=0

    if [[ "$VERBOSE" == "true" ]]; then
        # Use process substitution and PIPESTATUS to capture exit code through tee
        eval "$test_cmd" 2>&1 | tee -a "$LOG_FILE"
        exit_code=${PIPESTATUS[0]}
    else
        if output=$(eval "$test_cmd" 2>&1); then
            exit_code=0
        else
            exit_code=$?
        fi
        echo "$output" >> "$LOG_FILE"
    fi

    if [[ $exit_code -eq 0 ]]; then
        log_pass "$test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        if [[ "$allow_fail" == "true" ]]; then
            log_skip "$test_name (allowed failure)"
            TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
            return 0
        else
            log_fail "$test_name (exit code: $exit_code)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            if [[ "$VERBOSE" != "true" && -n "${output:-}" ]]; then
                echo "$output" | tail -20 >&2
            fi
            return 1
        fi
    fi
}

build_image() {
    local image_name="$1"
    local context_dir="$2"
    local full_image_name="${TEST_IMAGE_PREFIX}-${image_name}:test"

    local build_cmd="$CONTAINER_RUNTIME build"

    # Add registry prefix if set
    if [[ -n "${REGISTRY_PREFIX:-}" ]]; then
        build_cmd+=" --build-arg REGISTRY_PREFIX=${REGISTRY_PREFIX}"
    fi

    # Add --format docker for podman (required for HEALTHCHECK)
    if [[ "$CONTAINER_RUNTIME" == "podman" ]]; then
        build_cmd+=" --format docker"
    fi

    build_cmd+=" -t $full_image_name"
    build_cmd+=" $REPO_ROOT/$context_dir"

    run_test "Build $image_name" "$build_cmd"
}

run_health_check() {
    local image_name="$1"
    local health_cmd="$2"
    local full_image_name="${TEST_IMAGE_PREFIX}-${image_name}:test"

    # For db-tools, we need to run bash -c with the compound command
    if [[ "$image_name" == "db-tools" ]]; then
        local check_cmd="$CONTAINER_RUNTIME run --rm $full_image_name -c '$health_cmd'"
    else
        local check_cmd="$CONTAINER_RUNTIME run --rm --entrypoint sh $full_image_name -c '$health_cmd'"
    fi

    run_test "Health check $image_name" "$check_cmd"
}

cleanup_image() {
    local image_name="$1"
    local full_image_name="${TEST_IMAGE_PREFIX}-${image_name}:test"

    if [[ "$KEEP_IMAGES" != "true" ]]; then
        log_info "Cleaning up $full_image_name"
        $CONTAINER_RUNTIME rmi -f "$full_image_name" &>/dev/null || true
    fi
}

test_tool_image() {
    local image_name="$1"
    local context_dir="${TOOL_IMAGES[$image_name]}"
    local health_cmd="${TOOL_HEALTH_CHECKS[$image_name]}"

    log_section "Testing Tool Image: $image_name"

    # Check if Dockerfile exists
    if [[ ! -f "$REPO_ROOT/$context_dir/Dockerfile" ]]; then
        log_skip "$image_name - Dockerfile not found at $context_dir/Dockerfile"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
        return 0
    fi

    # Build
    if ! build_image "$image_name" "$context_dir"; then
        return 1
    fi

    # Health check
    if ! run_health_check "$image_name" "$health_cmd"; then
        cleanup_image "$image_name"
        return 1
    fi

    # Cleanup
    cleanup_image "$image_name"
    return 0
}

test_service_image() {
    local image_name="$1"
    local context_dir="${SERVICE_IMAGES[$image_name]}"
    local health_cmd="${SERVICE_HEALTH_CHECKS[$image_name]}"

    log_section "Testing Service Image: $image_name"

    # Check if Dockerfile exists
    if [[ ! -f "$REPO_ROOT/$context_dir/Dockerfile" ]]; then
        log_skip "$image_name - Dockerfile not found at $context_dir/Dockerfile"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
        return 0
    fi

    # Build
    if ! build_image "$image_name" "$context_dir"; then
        return 1
    fi

    # Health check
    if ! run_health_check "$image_name" "$health_cmd"; then
        cleanup_image "$image_name"
        return 1
    fi

    # Cleanup
    cleanup_image "$image_name"
    return 0
}

# ------------------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------------------
print_summary() {
    log_section "Test Summary"

    log ""
    log "Container Runtime: $CONTAINER_RUNTIME"
    log "Registry Prefix:   ${REGISTRY_PREFIX:-<default>}"
    log ""
    log "Tests Run:     $TESTS_RUN"
    log "${GREEN}Tests Passed:  $TESTS_PASSED${NC}"
    log "${RED}Tests Failed:  $TESTS_FAILED${NC}"
    log "${YELLOW}Tests Skipped: $TESTS_SKIPPED${NC}"
    log ""
    log "Log file: $LOG_FILE"
    log ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        log "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
        log "${GREEN} ALL TESTS PASSED${NC}"
        log "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
        return 0
    else
        log "${RED}═══════════════════════════════════════════════════════════════════${NC}"
        log "${RED} SOME TESTS FAILED${NC}"
        log "${RED}═══════════════════════════════════════════════════════════════════${NC}"
        return 1
    fi
}

# ------------------------------------------------------------------------------
# Argument Parsing
# ------------------------------------------------------------------------------
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -k|--keep-images)
                KEEP_IMAGES="true"
                shift
                ;;
            --tools-only)
                TOOLS_ONLY="true"
                shift
                ;;
            --services-only)
                SERVICES_ONLY="true"
                shift
                ;;
            --image)
                SELECTED_IMAGES+=("$2")
                shift 2
                ;;
            *)
                log_fail "Unknown option: $1"
                usage
                ;;
        esac
    done
}

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
main() {
    parse_args "$@"

    log_section "Container Image Build Tests"
    log_info "Starting test run at $(date)"
    log_info "Log file: $LOG_FILE"

    # Detect container runtime
    CONTAINER_RUNTIME=$(detect_container_runtime) || exit 1
    log_info "Using container runtime: $CONTAINER_RUNTIME"

    # Show registry prefix if set
    if [[ -n "${REGISTRY_PREFIX:-}" ]]; then
        log_info "Using registry prefix: $REGISTRY_PREFIX"
    fi

    # Test selected images if specified
    if [[ ${#SELECTED_IMAGES[@]} -gt 0 ]]; then
        log_info "Testing selected images: ${SELECTED_IMAGES[*]}"
        for image_name in "${SELECTED_IMAGES[@]}"; do
            if [[ -n "${TOOL_IMAGES[$image_name]:-}" ]]; then
                test_tool_image "$image_name" || true
            elif [[ -n "${SERVICE_IMAGES[$image_name]:-}" ]]; then
                test_service_image "$image_name" || true
            else
                log_fail "Unknown image: $image_name"
                log_info "Available tool images: ${!TOOL_IMAGES[*]}"
                log_info "Available service images: ${!SERVICE_IMAGES[*]}"
                TESTS_FAILED=$((TESTS_FAILED + 1))
            fi
        done
        print_summary
        exit $?
    fi

    # Test tool images
    if [[ "$SERVICES_ONLY" != "true" ]]; then
        log_section "Tool Images"
        for image_name in "${!TOOL_IMAGES[@]}"; do
            test_tool_image "$image_name" || true
        done
    fi

    # Test service images
    if [[ "$TOOLS_ONLY" != "true" ]]; then
        log_section "Service Images"
        for image_name in "${!SERVICE_IMAGES[@]}"; do
            test_service_image "$image_name" || true
        done
    fi

    # Print summary
    print_summary
}

# Run main
main "$@"
