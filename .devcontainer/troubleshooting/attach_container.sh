#!/bin/bash
# Attach to running dev container for debugging

echo "Looking for running dev container..."
container_id=$(docker ps --filter "label=devcontainer.local_folder=/home/dpham/src/dbtools" --format "{{.ID}}" | head -1)

if [ -n "$container_id" ]; then
  echo "Found container: $container_id"
  echo "Container status:"
  docker ps --filter "id=$container_id" --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"
  echo ""
  echo "Attaching to container (type 'exit' to detach)..."
  echo ""
  docker exec -it "$container_id" bash -l
else
  echo "No running dev container found for this workspace"
  echo ""
  echo "All VS Code containers:"
  docker ps -a | grep vsc || echo "  None found"
fi
