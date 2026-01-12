# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
# REGISTRY_PREFIX: Allows the base image to be pulled from a corporate proxy
#                  (e.g., JFrog Artifactory).
#
# USAGE:
#   Corporate proxy:
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ -t prometheus:latest .
#       (requires ~/.docker/config.json configured with JFrog token via: docker login xyz.jfrog.io)
#     podman build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ -t prometheus:latest --format docker .
#       (requires authentication via: podman login xyz.jfrog.io)
#
#   Default (Docker Hub):
#     docker build -t prometheus:latest .
#
# NOTE: The trailing slash is required in the prefix!
#
ARG REGISTRY_PREFIX=docker.io/library/
FROM ${REGISTRY_PREFIX}prom/prometheus:v2.47.0

COPY config/prometheus.yml /etc/prometheus/prometheus.yml
