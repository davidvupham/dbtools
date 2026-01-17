#!/usr/bin/env bash
set -euo pipefail

echo "Stopping all containers..."
docker ps -aq | xargs -r docker stop || true

echo "Removing all containers..."
docker ps -aq | xargs -r docker rm || true

echo "Pruning unused Docker data..."
docker system prune -f

echo "Pruning build cache..."
docker builder prune -af || true

echo "Done."
