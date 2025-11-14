#!/bin/bash
echo "=== Monitoring Dev Container Build - Test 4 ==="
echo "Started: $(date)"
echo ""
echo "Waiting for container to start..."
echo ""

# Wait for container to appear
for i in {1..30}; do
    CONTAINER_ID=$(docker ps -q --filter "label=devcontainer.local_folder=\\\\wsl.localhost\\Ubuntu\\home\\dpham\\src\\dbtools" --filter "label=devcontainer.config_file=/home/dpham/src/dbtools/.devcontainer/devcontainer.json")
    if [ -n "$CONTAINER_ID" ]; then
        echo "✅ Container started: $CONTAINER_ID"
        echo ""
        echo "=== Container Processes ==="
        docker top "$CONTAINER_ID" 2>&1 || echo "Cannot get process list yet"
        echo ""
        echo "=== Checking for VS Code Server ==="
        docker exec "$CONTAINER_ID" sh -c 'ps aux 2>/dev/null | grep -i "vscode\|node" || echo "No VS Code processes yet"'
        echo ""
        echo "=== Container Status ==="
        docker inspect "$CONTAINER_ID" --format='Status: {{.State.Status}} | Running: {{.State.Running}}'
        break
    fi
    sleep 1
done

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ No container found after 30 seconds"
fi
