#!/usr/bin/env bash
set -euo pipefail
IMAGE_NAME=${IMAGE_NAME:-dbtools-dev}
IMAGE_TAG=${IMAGE_TAG:-latest}
WORKDIR=${WORKDIR:-/workspaces/dbtools}
KRB5_CONF=${KRB5_CONF:-.devcontainer/krb5/krb5.conf}

if ! docker image inspect "${IMAGE_NAME}:${IMAGE_TAG}" >/dev/null 2>&1; then
  echo "Image ${IMAGE_NAME}:${IMAGE_TAG} not found. Building it first..."
  docker build -f .devcontainer/Dockerfile -t "${IMAGE_NAME}:${IMAGE_TAG}" .
fi

echo "Starting container ${IMAGE_NAME}..."
docker run --rm -d \
  --name "${IMAGE_NAME}" \
  -v "$(pwd)":"${WORKDIR}" \
  -v "$(pwd)/${KRB5_CONF}":/etc/krb5.conf:ro \
  -e KRB5_CONFIG=/etc/krb5.conf \
  -w "${WORKDIR}" \
  "${IMAGE_NAME}:${IMAGE_TAG}" tail -f /dev/null

echo "Container started. Attach with: docker exec -it ${IMAGE_NAME} bash"
