#!/bin/bash
# Monitor container build and startup with detailed logging

LOG_FILE="/home/dpham/src/dbtools/.devcontainer/container_test.log"

echo "=== Dev Container Test Log ===" | tee "$LOG_FILE"
echo "Date: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Monitoring for new containers..." | tee -a "$LOG_FILE"
echo "Rebuild your dev container now in VS Code" | tee -a "$LOG_FILE"
echo "Press Ctrl+C to stop monitoring" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Watch for new containers
while true; do
  container_id=$(docker ps -a --filter "label=devcontainer.local_folder=/home/dpham/src/dbtools" --format "{{.ID}}" --latest 2>/dev/null | head -1)

  if [ -n "$container_id" ]; then
    echo "=== Container detected: $container_id ===" | tee -a "$LOG_FILE"
    echo "Status:" | tee -a "$LOG_FILE"
    docker ps -a --filter "id=$container_id" --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Logs:" | tee -a "$LOG_FILE"
    docker logs "$container_id" 2>&1 | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
  fi

  sleep 5
done
