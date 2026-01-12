# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
# REGISTRY_PREFIX: Allows the base image to be pulled from a corporate proxy
#                  (e.g., JFrog Artifactory).
#
# USAGE:
#   Corporate proxy:
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ -t postgres:latest .
#       (requires ~/.docker/config.json configured with JFrog token via: docker login xyz.jfrog.io)
#     podman build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ -t postgres:latest --format docker .
#       (requires authentication via: podman login xyz.jfrog.io)
#
#   Default (Docker Hub):
#     docker build -t postgres:latest .
#
# NOTE: The trailing slash is required in the prefix!
#
ARG REGISTRY_PREFIX=docker.io/library/
FROM ${REGISTRY_PREFIX}postgres:latest

# Create directories for persistent volumes
RUN mkdir -p /data/postgresql /logs/postgresql && \
    chown -R postgres:postgres /data /logs

# Define volumes for persistent storage
VOLUME ["/data/postgresql", "/logs/postgresql"]

EXPOSE 5432

CMD ["postgres"]
