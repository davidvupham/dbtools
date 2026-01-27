# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
# REGISTRY_PREFIX: Allows the base image to be pulled from a corporate proxy
#                  (e.g., JFrog Artifactory).
#
# USAGE:
#   Corporate proxy:
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/ -t vault:latest .
#       (requires ~/.docker/config.json configured with JFrog token via: docker login xyz.jfrog.io)
#     podman build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/ -t vault:latest --format docker .
#       (requires authentication via: podman login xyz.jfrog.io)
#
#   Default (Docker Hub):
#     docker build -t vault:latest .
#
# NOTE: The trailing slash is required in the prefix!
#
ARG REGISTRY_PREFIX=docker.io/
FROM ${REGISTRY_PREFIX}hashicorp/vault:latest

LABEL org.opencontainers.image.title="HashiCorp Vault" \
      org.opencontainers.image.description="Vault server configured for containerized deployments" \
      org.opencontainers.image.source="https://github.com/hashicorp/vault" \
      org.opencontainers.image.licenses="BUSL-1.1"

# Copy static configuration into the image. Using a single COPY keeps layer
# count to a minimum while enabling reproducible builds.
COPY docker/vault/config/vault.hcl /vault/config/vault.hcl

# Vault drops privileges internally; keep running as the default non-root user
# provided by the base image for better security.
USER vault

ENTRYPOINT ["vault"]
CMD ["server", "-config=/vault/config/vault.hcl"]
