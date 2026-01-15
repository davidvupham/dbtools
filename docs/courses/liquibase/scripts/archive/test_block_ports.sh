#!/usr/bin/env bash
# Test Helper: Block/Unblock Default Ports
# Temporarily blocks ports 14331, 14332, 14333 for testing dynamic port assignment
#
# Usage:
#   ./test_block_ports.sh start   - Block ports 14331-14333
#   ./test_block_ports.sh stop    - Unblock ports (cleanup)
#   ./test_block_ports.sh status  - Check if ports are blocked

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PORTS=(14331 14332 14333)
PID_FILE="$SCRIPT_DIR/.test_block_ports.pids"

# Check if a port is already in use
is_port_in_use() {
    local port=$1
    
    # Check using ss (most common on Linux)
    if command -v ss &>/dev/null; then
        if ss -tuln 2>/dev/null | grep -q ":${port} "; then
            return 0
        fi
    # Fallback to netstat
    elif command -v netstat &>/dev/null; then
        if netstat -tuln 2>/dev/null | grep -q ":${port} "; then
            return 0
        fi
    # Fallback to lsof
    elif command -v lsof &>/dev/null; then
        if lsof -i":${port}" -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 0
        fi
    fi
    
    # Check if container runtime is using this port
    if command -v podman &>/dev/null; then
        if podman ps --format '{{.Ports}}' 2>/dev/null | grep -q "0.0.0.0:${port}->"; then
            return 0
        fi
    fi
    if command -v docker &>/dev/null; then
        if docker ps --format '{{.Ports}}' 2>/dev/null | grep -q "0.0.0.0:${port}->"; then
            return 0
        fi
    fi
    
    return 1
}

# Block ports using socat (preferred)
block_with_socat() {
    local port=$1
    local pid
    
    # Create a TCP listener that accepts connections but does nothing
    socat TCP-LISTEN:${port},fork,reuseaddr /dev/null 2>/dev/null &
    pid=$!
    echo "$pid"
}

# Block ports using nc (netcat) - less reliable but common
block_with_nc() {
    local port=$1
    local pid
    
    # nc -l listens and exits after first connection, so we need a loop
    while true; do
        nc -l -p ${port} >/dev/null 2>&1 || true
    done &
    pid=$!
    echo "$pid"
}

# Block ports using Python (fallback)
block_with_python() {
    local port=$1
    local pid
    
    python3 -c "
import socket
import sys
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', ${port}))
s.listen(5)

# Keep accepting connections
while True:
    try:
        conn, addr = s.accept()
        conn.close()
    except:
        pass
" >/dev/null 2>&1 &
    pid=$!
    echo "$pid"
}

start_blockers() {
    echo "Blocking ports ${PORTS[*]}..."
    
    # Check if ports are already blocked
    for port in "${PORTS[@]}"; do
        if is_port_in_use "$port"; then
            echo -e "${YELLOW}Warning: Port $port is already in use${NC}"
        fi
    done
    
    # Choose blocking method
    local method=""
    local pids=()
    
    if command -v socat &>/dev/null; then
        method="socat"
        echo "Using socat to block ports..."
        for port in "${PORTS[@]}"; do
            if ! is_port_in_use "$port"; then
                pid=$(block_with_socat "$port")
                pids+=("$pid")
                echo "  Blocked port $port (PID: $pid)"
            else
                echo "  Port $port already blocked, skipping"
            fi
        done
    elif command -v nc &>/dev/null; then
        method="nc"
        echo "Using netcat (nc) to block ports..."
        for port in "${PORTS[@]}"; do
            if ! is_port_in_use "$port"; then
                pid=$(block_with_nc "$port")
                pids+=("$pid")
                echo "  Blocked port $port (PID: $pid)"
            else
                echo "  Port $port already blocked, skipping"
            fi
        done
    elif command -v python3 &>/dev/null; then
        method="python"
        echo "Using Python to block ports..."
        for port in "${PORTS[@]}"; do
            if ! is_port_in_use "$port"; then
                pid=$(block_with_python "$port")
                pids+=("$pid")
                echo "  Blocked port $port (PID: $pid)"
            else
                echo "  Port $port already blocked, skipping"
            fi
        done
    else
        echo -e "${RED}ERROR: No suitable tool found to block ports${NC}"
        echo "Install one of: socat, nc (netcat), or python3"
        exit 1
    fi
    
    # Save PIDs to file
    if [[ ${#pids[@]} -gt 0 ]]; then
        printf "%s\n" "${pids[@]}" > "$PID_FILE"
        echo -e "${GREEN}✓ Ports blocked (${#pids[@]} processes)${NC}"
        echo "PIDs saved to: $PID_FILE"
    else
        echo -e "${YELLOW}⚠ All ports were already blocked${NC}"
    fi
}

stop_blockers() {
    echo "Unblocking ports ${PORTS[*]}..."
    
    if [[ ! -f "$PID_FILE" ]]; then
        echo -e "${YELLOW}No PID file found - ports may not be blocked by this script${NC}"
        return 0
    fi
    
    local killed=0
    while IFS= read -r pid; do
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            echo "  Killed process $pid"
            ((killed++)) || true
        fi
    done < "$PID_FILE"
    
    rm -f "$PID_FILE"
    
    if [[ $killed -gt 0 ]]; then
        echo -e "${GREEN}✓ Unblocked ports (killed $killed processes)${NC}"
    else
        echo -e "${YELLOW}⚠ No processes found to kill${NC}"
    fi
}

check_status() {
    echo "Checking port status..."
    for port in "${PORTS[@]}"; do
        if is_port_in_use "$port"; then
            echo -e "  Port $port: ${RED}BLOCKED${NC}"
        else
            echo -e "  Port $port: ${GREEN}AVAILABLE${NC}"
        fi
    done
    
    if [[ -f "$PID_FILE" ]]; then
        echo
        echo "Active blocker processes:"
        while IFS= read -r pid; do
            if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
                echo "  PID $pid: running"
            else
                echo "  PID $pid: not running (stale)"
            fi
        done < "$PID_FILE"
    fi
}

# Cleanup function
cleanup() {
    if [[ -f "$PID_FILE" ]]; then
        stop_blockers
    fi
}

# Main
case "${1:-}" in
    start)
        # Start blockers and leave them running (no cleanup on exit)
        # Only trap signals to clean up on interruption
        trap cleanup INT TERM
        start_blockers
        # Don't trap EXIT so blockers persist after script exits
        trap - EXIT
        ;;
    stop)
        stop_blockers
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        echo
        echo "  start  - Block ports 14331-14333 for testing"
        echo "  stop   - Unblock ports (cleanup blockers)"
        echo "  status - Check current port status"
        exit 1
        ;;
esac
