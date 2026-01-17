# ==============================================================================
# PostgreSQL Client (psql) - Docker Image
# ==============================================================================
#
# PURPOSE:
# Minimal container with PostgreSQL command-line tools for database operations.
#
# TOOLS INCLUDED:
# - psql: Interactive PostgreSQL terminal
# - pg_dump: Database backup utility
# - pg_restore: Database restore utility
# - pg_isready: Connection check utility
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
# REGISTRY_PREFIX: Allows the base image to be pulled from a corporate proxy
#                  (e.g., JFrog Artifactory).
#
# USAGE:
#   Corporate proxy:
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ -t psql:latest .
#
#   Default (Docker Hub):
#     docker build -t psql:latest .
#
# NOTE: The trailing slash is required in the prefix!
#
ARG REGISTRY_PREFIX=docker.io/library/

# ------------------------------------------------------------------------------
# Base Image
# ------------------------------------------------------------------------------
# Alpine Linux: Minimal base image (~5MB) with apk package manager
# PostgreSQL client tools are available in the main Alpine repository
#
FROM ${REGISTRY_PREFIX}alpine:3.21

# ------------------------------------------------------------------------------
# Version Configuration
# ------------------------------------------------------------------------------
ARG POSTGRESQL_VERSION=17

# ------------------------------------------------------------------------------
# Labels
# ------------------------------------------------------------------------------
LABEL org.opencontainers.image.title="PostgreSQL Client" \
      org.opencontainers.image.description="PostgreSQL command-line tools (psql, pg_dump, pg_restore)" \
      org.opencontainers.image.version="${POSTGRESQL_VERSION}"

# ------------------------------------------------------------------------------
# Install PostgreSQL Client Tools
# ------------------------------------------------------------------------------
RUN set -eux; \
    apk add --no-cache \
        postgresql${POSTGRESQL_VERSION}-client \
        ca-certificates; \
    # Verify installation
    psql --version

# ------------------------------------------------------------------------------
# Working Directory
# ------------------------------------------------------------------------------
WORKDIR /data

# ------------------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["psql", "--version"]

# ------------------------------------------------------------------------------
# Non-Root User
# ------------------------------------------------------------------------------
RUN adduser -D -u 1001 -g 0 psql \
    && chown -R 1001:0 /data

USER psql

# ------------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------------
ENTRYPOINT ["psql"]
CMD ["--help"]

# ==============================================================================
# BUILD:
#   docker build -t psql:latest .
#   podman build -t psql:latest --format docker .
#
# RUN:
#   docker run --rm psql:latest --version
#   docker run --rm -it psql:latest -h host.docker.internal -U postgres -d mydb
#
# EXAMPLES:
#   # Connect to PostgreSQL
#   docker run --rm -it psql:latest -h myhost -U myuser -d mydb
#
#   # Run SQL file
#   docker run --rm -v ./scripts:/data psql:latest -h myhost -U myuser -d mydb -f /data/script.sql
#
#   # Backup database
#   docker run --rm --entrypoint pg_dump -v ./backups:/data psql:latest -h myhost -U myuser mydb > backup.sql
# ==============================================================================
