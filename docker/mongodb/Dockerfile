# MongoDB version can be customized via build arg
ARG MONGODB_VERSION=8.0.1
ARG BUILD_VERSION=1.0.1

# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
# REGISTRY_PREFIX: Allows the base image to be pulled from a corporate proxy
#                  (e.g., JFrog Artifactory).
#
# USAGE:
#   Corporate proxy:
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ -t mongodb:latest .
#       (requires ~/.docker/config.json configured with JFrog token via: docker login xyz.jfrog.io)
#     podman build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ -t mongodb:latest --format docker .
#       (requires authentication via: podman login xyz.jfrog.io)
#
#   Default (Docker Hub):
#     docker build -t mongodb:latest .
#
# NOTE: The trailing slash is required in the prefix!
#
ARG REGISTRY_PREFIX=docker.io/library/

FROM ${REGISTRY_PREFIX}mongo:${MONGODB_VERSION}

# Add labels for image identification
LABEL image.tag="gds-mongodb-${MONGODB_VERSION}:${BUILD_VERSION}" \
      mongodb.version="${MONGODB_VERSION}" \
      build.version="${BUILD_VERSION}" \
      description="GDS MongoDB ${MONGODB_VERSION} image" \
      maintainer="dbtools"

# Create directories for persistent volumes
RUN mkdir -p /data/mongodb /logs/mongodb && \
    chown -R mongodb:mongodb /data /logs

# Generate keyfile at build time (NOT copied from repo for security)
# This is a template - actual keyfile should be mounted at runtime per environment
RUN openssl rand -base64 756 > /tmp/mongodb-keyfile.template && \
    chmod 400 /tmp/mongodb-keyfile.template && \
    chown mongodb:mongodb /tmp/mongodb-keyfile.template

# Define volumes for persistent storage
VOLUME ["/data/mongodb", "/logs/mongodb"]

EXPOSE 27017

# Use entrypoint script to handle instance-specific configuration
COPY docker-entrypoint-custom.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint-custom.sh

ENTRYPOINT ["docker-entrypoint-custom.sh"]
CMD ["mongod"]
