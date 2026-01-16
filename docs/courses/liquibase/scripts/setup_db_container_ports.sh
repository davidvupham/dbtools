#!/usr/bin/env bash
# Setup Database Container Ports (Multi-Platform)
# Configures available ports for database containers (MSSQL, PostgreSQL, MongoDB, etc.)
# Finds available ports, prompts user for confirmation, and saves to $LIQUIBASE_TUTORIAL_DATA_DIR/.ports file
# Can be sourced to get ports as environment variables or run standalone
#
# Usage:
#   # Run standalone for MSSQL (default, interactive prompt)
#   ./setup_db_container_ports.sh [start_port] [force] [skip_prompt]
#
#   # Run standalone for other platforms
#   ./setup_db_container_ports.sh postgresql [start_port] [force] [skip_prompt]
#   ./setup_db_container_ports.sh mongodb [start_port] [force] [skip_prompt]
#
#   # Source and use for MSSQL (backward compatible)
#   source ./setup_db_container_ports.sh
#   setup_mssql_ports 14331
#   echo $MSSQL_DEV_PORT $MSSQL_STG_PORT $MSSQL_PRD_PORT
#
#   # Use generic function for any platform
#   source ./setup_db_container_ports.sh
#   setup_database_ports postgresql 5432
#   setup_database_ports mongodb 27017

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# =============================================================================
# Platform Configuration
# =============================================================================

# Initialize platform configuration associative arrays
declare -A PLATFORM_CONFIG

# MSSQL configuration - environment-based naming (dev/stg/prd)
PLATFORM_CONFIG[mssql:prefix]="mssql"
PLATFORM_CONFIG[mssql:instances]="dev stg prd"
PLATFORM_CONFIG[mssql:var_prefix]="MSSQL"
PLATFORM_CONFIG[mssql:var_pattern]="env"  # env-based: MSSQL_DEV_PORT
PLATFORM_CONFIG[mssql:default_start_port]="14331"
PLATFORM_CONFIG[mssql:count]="3"
PLATFORM_CONFIG[mssql:description]="SQL Server"

# PostgreSQL configuration - numeric naming (1, 2, 3...)
PLATFORM_CONFIG[postgresql:prefix]="psql"
PLATFORM_CONFIG[postgresql:instances]="1 2 3"
PLATFORM_CONFIG[postgresql:var_prefix]="POSTGRES"
PLATFORM_CONFIG[postgresql:var_pattern]="numeric"  # numeric: POSTGRES_PORT_1
PLATFORM_CONFIG[postgresql:default_start_port]="5432"
PLATFORM_CONFIG[postgresql:count]="3"
PLATFORM_CONFIG[postgresql:description]="PostgreSQL"

# MongoDB configuration - numeric naming (1, 2, 3...)
PLATFORM_CONFIG[mongodb:prefix]="mongodb"
PLATFORM_CONFIG[mongodb:instances]="1 2 3"
PLATFORM_CONFIG[mongodb:var_prefix]="MONGODB"
PLATFORM_CONFIG[mongodb:var_pattern]="numeric"  # numeric: MONGODB_PORT_1
PLATFORM_CONFIG[mongodb:default_start_port]="27017"
PLATFORM_CONFIG[mongodb:count]="3"
PLATFORM_CONFIG[mongodb:description]="MongoDB"

# =============================================================================
# Helper Functions
# =============================================================================

# Check if a port is available
is_port_available() {
    local port=$1

    # Check if container runtime is using this port
    if command -v podman &>/dev/null; then
        if podman ps --format '{{.Ports}}' 2>/dev/null | grep -q "0.0.0.0:${port}->"; then
            return 1
        fi
    fi
    if command -v docker &>/dev/null; then
        if docker ps --format '{{.Ports}}' 2>/dev/null | grep -q "0.0.0.0:${port}->"; then
            return 1
        fi
    fi

    # Check using ss (most common on Linux)
    if command -v ss &>/dev/null; then
        if ss -tuln 2>/dev/null | grep -q ":${port} "; then
            return 1
        fi
    # Fallback to netstat
    elif command -v netstat &>/dev/null; then
        if netstat -tuln 2>/dev/null | grep -q ":${port} "; then
            return 1
        fi
    # Fallback to lsof
    elif command -v lsof &>/dev/null; then
        if lsof -i":${port}" -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 1
        fi
    fi

    return 0
}

# Find N consecutive available ports starting from a base port
# Usage: find_available_ports <start_port> <count>
# Returns: space-separated list of available ports
find_available_ports() {
    local start_port=${1:-14331}
    local count=${2:-3}
    local max_attempts=100
    local port=$start_port
    local found_ports=()

    for ((attempt=0; attempt<max_attempts; attempt++)); do
        found_ports=()
        local all_available=true

        # Check if 'count' consecutive ports are available
        for ((i=0; i<count; i++)); do
            local check_port=$((port + i))
            if is_port_available "$check_port"; then
                found_ports+=("$check_port")
            else
                all_available=false
                # Skip to the next port after the unavailable one
                port=$((check_port + 1))
                break
            fi
        done

        if [[ "$all_available" == "true" ]]; then
            echo "${found_ports[*]}"
            return 0
        fi
    done

    echo "ERROR: Could not find $count consecutive available ports after $max_attempts attempts" >&2
    return 1
}

# Generate container name based on platform and instance
# Usage: generate_container_name <platform> <instance>
# Returns: container name
generate_container_name() {
    local platform=$1
    local instance=$2
    local prefix="${PLATFORM_CONFIG[${platform}:prefix]}"

    # MSSQL uses prefix_instance (mssql_dev), others use prefix+number (psql1, mongodb1)
    if [[ "$platform" == "mssql" ]]; then
        echo "${prefix}_${instance}"
    else
        echo "${prefix}${instance}"
    fi
}

# Generate port variable name based on platform and instance
# Usage: generate_port_var_name <platform> <instance>
# Returns: variable name
generate_port_var_name() {
    local platform=$1
    local instance=$2
    local var_prefix="${PLATFORM_CONFIG[${platform}:var_prefix]}"
    local var_pattern="${PLATFORM_CONFIG[${platform}:var_pattern]}"

    if [[ "$var_pattern" == "env" ]]; then
        # Environment-based: MSSQL_DEV_PORT (uppercase instance)
        echo "${var_prefix}_$(echo "$instance" | tr '[:lower:]' '[:upper:]')_PORT"
    else
        # Numeric-based: POSTGRES_PORT_1, MONGODB_PORT_1
        echo "${var_prefix}_PORT_${instance}"
    fi
}

# Write ports to .ports file for other scripts to discover
# Usage: write_ports_file <platform> <container_port_map>
# container_port_map should be array of "container:port" entries in instance order
write_ports_file() {
    local platform=$1
    shift
    local container_port_map=("$@")
    local ports_file="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}/.ports"
    local script_name="${0##*/}"

    # Build ports content
    local description="${PLATFORM_CONFIG[${platform}:description]:-$platform}"
    local ports_content="# Auto-generated by setup_db_container_ports.sh
# Source this file to get the port assignments for this user's tutorial environment
# Platform: ${platform} (${description})
"

    # Add each port variable
    local instance_names=(${PLATFORM_CONFIG[${platform}:instances]})
    local i=0
    for port_entry in "${container_port_map[@]}"; do
        local instance="${instance_names[$i]}"
        local port="${port_entry#*:}"  # Extract port after colon
        local var_name=$(generate_port_var_name "$platform" "$instance")
        ports_content+="${var_name}=${port}"$'\n'
        ((i++)) || true
    done

    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$ports_file")"

    # Try to write directly, fall back to sudo if needed
    if echo "$ports_content" > "$ports_file" 2>/dev/null; then
        echo -e "${GREEN}✓ Saved port assignments to $ports_file${NC}"
        return 0
    elif sudo bash -c "cat > '$ports_file' && chown $USER:$USER '$ports_file'" <<< "$ports_content" 2>/dev/null; then
        echo -e "${GREEN}✓ Saved port assignments to $ports_file (using sudo)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Could not write port assignments to $ports_file${NC}"
        echo "  Platform: $platform"
        local i=0
        for port_entry in "${ports_array[@]}"; do
            local instance="${instance_names[$i]}"
            local port="${port_entry#*:}"
            echo "  ${instance}: ${port}"
            ((i++)) || true
        done
        echo "  You may need to manually create this file or fix permissions"
        return 1
    fi
}

# Validate that containers are using expected ports
# Usage: validate_container_ports <platform> <container_port_map>
# container_port_map: associative array where key is container name, value is port
validate_container_ports() {
    local platform=$1
    shift
    local container_port_map=("$@")

    # Detect container runtime
    local cr_cmd=""
    if command -v podman &>/dev/null; then
        cr_cmd="podman"
    elif command -v docker &>/dev/null; then
        cr_cmd="docker"
    fi

    if [[ -z "$cr_cmd" ]]; then
        return 1
    fi

    # Check each container
    for entry in "${container_port_map[@]}"; do
        local container="${entry%%:*}"
        local expected_port="${entry#*:}"

        # Check if container exists and is using the expected port
        if ! $cr_cmd ps --format '{{.Names}} {{.Ports}}' 2>/dev/null | grep -q "${container}.*:${expected_port}->"; then
            return 1
        fi
    done

    return 0
}

# =============================================================================
# Main Setup Function
# =============================================================================

# Main function to setup and configure ports for any database platform
# Usage: setup_database_ports <platform> [start_port] [force] [skip_prompt]
setup_database_ports() {
    local platform=${1:-mssql}
    local start_port=${2:-}
    local force=${3:-false}
    local skip_prompt=${4:-false}

    # Validate platform is supported
    if [[ -z "${PLATFORM_CONFIG[${platform}:prefix]:-}" ]]; then
        echo -e "${RED}ERROR: Unsupported platform: $platform${NC}"
        echo "Supported platforms: mssql, postgresql, mongodb"
        return 1
    fi

    # Set default start port if not provided
    if [[ -z "$start_port" ]]; then
        start_port="${PLATFORM_CONFIG[${platform}:default_start_port]}"
    fi

    LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"
    export LIQUIBASE_TUTORIAL_DATA_DIR

    PORTS_FILE="$LIQUIBASE_TUTORIAL_DATA_DIR/.ports"
    local count="${PLATFORM_CONFIG[${platform}:count]}"
    local prefix="${PLATFORM_CONFIG[${platform}:prefix]}"
    local description="${PLATFORM_CONFIG[${platform}:description]:-$platform}"
    local instances=(${PLATFORM_CONFIG[${platform}:instances]})

    # Check if we already have a .ports file with running containers (unless forced)
    if [[ "$force" != "true" ]] && [[ -f "$PORTS_FILE" ]]; then
        source "$PORTS_FILE"

        # Build container-port mapping for validation
        local container_port_map=()
        local all_ports_set=true
        local i=0

        for instance in "${instances[@]}"; do
            local container=$(generate_container_name "$platform" "$instance")
            local var_name=$(generate_port_var_name "$platform" "$instance")
            local port="${!var_name:-}"

            if [[ -z "$port" ]]; then
                all_ports_set=false
                break
            fi

            container_port_map+=("${container}:${port}")
            ((i++)) || true
        done

        # Validate containers are using these ports
        if [[ "$all_ports_set" == "true" ]] && validate_container_ports "$platform" "${container_port_map[@]}"; then
            echo -e "${YELLOW}Reusing existing port assignments from $PORTS_FILE${NC}"
            for entry in "${container_port_map[@]}"; do
                local container="${entry%%:*}"
                local port="${entry#*:}"
                echo "  ${container}:  localhost:${port}"
            done

            # Export all port variables
            for instance in "${instances[@]}"; do
                local var_name=$(generate_port_var_name "$platform" "$instance")
                # Use eval to export with dynamic variable name
                eval "export ${var_name}"
            done
            return 0
        fi
    fi

    # Configure consecutive available ports
    echo "Configuring ports for ${description} containers..."
    AVAILABLE_PORTS=$(find_available_ports "$start_port" "$count") || {
        echo -e "${RED}ERROR: Could not configure $count available ports starting from $start_port${NC}"
        return 1
    }

    # Parse the ports and build container-port mapping
    read -ra port_array <<< "$AVAILABLE_PORTS"
    local container_port_map=()
    local i=0

    for instance in "${instances[@]}"; do
        local container=$(generate_container_name "$platform" "$instance")
        local port="${port_array[$i]}"
        container_port_map+=("${container}:${port}")
        ((i++)) || true
    done

    # Display chosen ports
    echo
    echo -e "${GREEN}Dynamic ports chosen:${NC}"
    for entry in "${container_port_map[@]}"; do
        local container="${entry%%:*}"
        local port="${entry#*:}"
        echo "  ${container}:  localhost:${port}"
    done
    echo

    # Prompt user to accept or enter new starting port (only if running interactively and not skipped)
    if [[ "$skip_prompt" != "true" ]] && [[ -t 0 ]] && [[ "${SKIP_PORT_PROMPT:-}" != "true" ]]; then
        while true; do
            echo -e "${YELLOW}Options:${NC}"
            echo "  - Enter 'yes' or 'y' to accept these ports"
            echo "  - Enter 'no' or 'n' to specify a different starting port"
            echo "  - Enter a port number directly to search from that port"
            read -p "Your choice: " user_input

            if [[ -z "$user_input" ]]; then
                echo -e "${YELLOW}Please enter 'yes', 'no', or a port number${NC}"
                continue
            fi

            # Check if input is a number (new starting port)
            if [[ "$user_input" =~ ^[0-9]+$ ]]; then
                local new_start_port=$user_input
                echo "Searching for available ports starting from $new_start_port..."

                AVAILABLE_PORTS=$(find_available_ports "$new_start_port" "$count") || {
                    echo -e "${RED}ERROR: Could not find $count available ports starting from $new_start_port${NC}"
                    echo "Please try a different starting port."
                    continue
                }

                # Parse the new ports
                read -ra port_array <<< "$AVAILABLE_PORTS"
                container_port_map=()
                i=0

                for instance in "${instances[@]}"; do
                    local container=$(generate_container_name "$platform" "$instance")
                    local port="${port_array[$i]}"
                    container_port_map+=("${container}:${port}")
                    ((i++)) || true
                done

                echo
                echo -e "${GREEN}New dynamic ports chosen:${NC}"
                for entry in "${container_port_map[@]}"; do
                    local container="${entry%%:*}"
                    local port="${entry#*:}"
                    echo "  ${container}:  localhost:${port}"
                done
                echo
                continue
            fi

            # Check for yes/accept
            local user_input_lower=$(echo "$user_input" | tr '[:upper:]' '[:lower:]')
            if [[ "$user_input_lower" == "yes" ]] || [[ "$user_input_lower" == "y" ]] || \
               [[ "$user_input_lower" == "accept" ]] || [[ "$user_input_lower" == "a" ]]; then
                echo -e "${GREEN}Accepted ports.${NC}"
                break
            elif [[ "$user_input_lower" == "no" ]] || [[ "$user_input_lower" == "n" ]]; then
                read -p "Enter a new starting port number: " new_port
                if [[ -n "$new_port" ]] && [[ "$new_port" =~ ^[0-9]+$ ]]; then
                    local new_start_port=$new_port
                    echo "Searching for available ports starting from $new_start_port..."

                    AVAILABLE_PORTS=$(find_available_ports "$new_start_port" "$count") || {
                        echo -e "${RED}ERROR: Could not find $count available ports starting from $new_start_port${NC}"
                        echo "Please try a different starting port."
                        continue
                    }

                    # Parse the new ports
                    read -ra port_array <<< "$AVAILABLE_PORTS"
                    container_port_map=()
                    i=0

                    for instance in "${instances[@]}"; do
                        local container=$(generate_container_name "$platform" "$instance")
                        local port="${port_array[$i]}"
                        container_port_map+=("${container}:${port}")
                        ((i++)) || true
                    done

                    echo
                    echo -e "${GREEN}New dynamic ports chosen:${NC}"
                    for entry in "${container_port_map[@]}"; do
                        local container="${entry%%:*}"
                        local port="${entry#*:}"
                        echo "  ${container}:  localhost:${port}"
                    done
                    echo
                    continue
                else
                    echo -e "${RED}Invalid port number. Please enter a numeric port.${NC}"
                fi
            else
                echo -e "${YELLOW}Please enter 'yes', 'no', or a port number${NC}"
            fi
        done
    fi

    # Save ports to file
    write_ports_file "$platform" "${container_port_map[@]}" || return 1

    # Export ports as environment variables
    i=0
    for instance in "${instances[@]}"; do
        local var_name=$(generate_port_var_name "$platform" "$instance")
        local port="${container_port_map[$i]#*:}"
        # Use eval to export with dynamic variable name
        eval "export ${var_name}=${port}"
        ((i++)) || true
    done

    return 0
}

# =============================================================================
# Backward Compatible Wrapper
# =============================================================================

# Backward compatible wrapper for MSSQL-specific usage
# Usage: setup_mssql_ports [start_port] [force] [skip_prompt]
setup_mssql_ports() {
    local start_port=${1:-14331}
    local force=${2:-false}
    local skip_prompt=${3:-false}

    setup_database_ports "mssql" "$start_port" "$force" "$skip_prompt"
}

# If script is run directly (not sourced), execute the main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # If first argument is a platform name (postgresql, mongodb), use generic function
    # Otherwise, default to MSSQL for backward compatibility
    if [[ "${1:-}" == "postgresql" ]] || [[ "${1:-}" == "mongodb" ]]; then
        PLATFORM=${1}
        START_PORT=${2:-}
        FORCE=${3:-false}
        SKIP_PROMPT=${4:-false}
        setup_database_ports "$PLATFORM" "$START_PORT" "$FORCE" "$SKIP_PROMPT"
    else
        # Default to MSSQL for backward compatibility
        START_PORT=${1:-14331}
        FORCE=${2:-false}
        SKIP_PROMPT=${3:-false}
        setup_mssql_ports "$START_PORT" "$FORCE" "$SKIP_PROMPT"
    fi
fi
