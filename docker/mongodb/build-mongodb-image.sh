#!/bin/bash
# Build MongoDB Docker image with standardized naming
# Image tag format: gds-mongodb-{version}:{build_version}
#
# Usage: ./build-mongodb-image.sh <mongodb_version> <build_version>
#
# Example:
#   ./build-mongodb-image.sh 8.0.1 1.0.1
#   Creates image: gds-mongodb-8.0.1:1.0.1

set -e

MONGODB_VERSION=${1:-8.0.1}
BUILD_VERSION=${2:-1.0.1}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Standardized image tag: gds-mongodb-version:build_version
IMAGE_TAG="gds-mongodb-${MONGODB_VERSION}:${BUILD_VERSION}"

echo "Building GDS MongoDB Docker image..."
echo "  MongoDB Version: ${MONGODB_VERSION}"
echo "  Build Version: ${BUILD_VERSION}"
echo "  Image Tag: ${IMAGE_TAG}"
echo ""

# Build Docker image
docker build \
    --build-arg MONGODB_VERSION="${MONGODB_VERSION}" \
    --build-arg BUILD_VERSION="${BUILD_VERSION}" \
    -t "${IMAGE_TAG}" \
    -f "${SCRIPT_DIR}/Dockerfile" \
    "${SCRIPT_DIR}"

echo ""
echo "✅ Successfully built image: ${IMAGE_TAG}"
echo ""
echo "Example: Run with custom container name"
echo "  docker run -d \\"
echo "    --name auscl090041 \\"
echo "    -p 27017:27017 \\"
echo "    -v /data/mongodb:/data/mongodb \\"
echo "    -v /logs/mongodb:/logs/mongodb \\"
echo "    ${IMAGE_TAG}"
