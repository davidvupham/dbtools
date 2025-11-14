#!/bin/bash
# Check if container is running and accessible

echo "=== Checking for dev containers ==="
docker ps -a --filter "label=devcontainer.local_folder=/home/dpham/src/dbtools"

echo ""
echo "=== All containers with 'dbtools' in name ==="
docker ps -a | grep -i dbtools || echo "No containers found with 'dbtools' in name"

echo ""
echo "=== All containers with 'vsc' prefix (VS Code containers) ==="
docker ps -a | grep vsc || echo "No VS Code containers found"

echo ""
echo "=== Latest logs from most recent container ==="
latest_container=$(docker ps -a --filter "label=devcontainer.local_folder=/home/dpham/src/dbtools" --format "{{.ID}}" | head -1)
if [ -n "$latest_container" ]; then
  echo "Container ID: $latest_container"
  docker logs --tail 100 "$latest_container" 2>&1
else
  echo "No dev container found for this workspace"
fi
