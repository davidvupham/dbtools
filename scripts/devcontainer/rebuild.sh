#!/usr/bin/env bash
set -euo pipefail
IMAGE_NAME=${IMAGE_NAME:-dbtools-dev}
IMAGE_TAG=${IMAGE_TAG:-latest}

echo "Rebuilding ${IMAGE_NAME}:${IMAGE_TAG} without cache..."
docker build --no-cache -f .devcontainer/Dockerfile -t "${IMAGE_NAME}:${IMAGE_TAG}" .
echo "Done."
