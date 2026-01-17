# ==============================================================================
# MongoDB Shell (mongosh) - Docker Image
# ==============================================================================
#
# PURPOSE:
# Minimal container with MongoDB Shell for interacting with MongoDB databases.
#
# TOOLS INCLUDED:
# - mongosh: Modern MongoDB Shell (replacement for legacy mongo shell)
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
ARG REGISTRY_PREFIX=docker.io/library/

# ------------------------------------------------------------------------------
# Base Image
# ------------------------------------------------------------------------------
# Using Debian slim because mongosh requires glibc
#
FROM ${REGISTRY_PREFIX}debian:bookworm-slim

# ------------------------------------------------------------------------------
# Labels
# ------------------------------------------------------------------------------
LABEL org.opencontainers.image.title="MongoDB Shell" \
      org.opencontainers.image.description="MongoDB Shell (mongosh) command-line client"

# ------------------------------------------------------------------------------
# Install mongosh
# ------------------------------------------------------------------------------
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg; \
    # Add MongoDB repository GPG key
    curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
        gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg; \
    # Add MongoDB repository
    echo "deb [signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" \
        > /etc/apt/sources.list.d/mongodb-org-8.0.list; \
    # Install mongosh
    apt-get update; \
    apt-get install -y --no-install-recommends \
        mongodb-mongosh; \
    # Cleanup
    apt-get purge -y --auto-remove curl gnupg; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*; \
    # Verify installation
    mongosh --version

# ------------------------------------------------------------------------------
# Working Directory
# ------------------------------------------------------------------------------
WORKDIR /data

# ------------------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["mongosh", "--version"]

# ------------------------------------------------------------------------------
# Non-Root User
# ------------------------------------------------------------------------------
RUN useradd --uid 1001 --gid 0 --create-home mongosh \
    && mkdir -p /home/mongosh/.mongodb \
    && chown -R 1001:0 /data /home/mongosh/.mongodb

USER mongosh

# ------------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------------
ENTRYPOINT ["mongosh"]
CMD ["--help"]

# ==============================================================================
# BUILD:
#   docker build -t mongosh:latest .
#   podman build -t mongosh:latest --format docker .
#
# RUN:
#   docker run --rm mongosh:latest --version
#
# EXAMPLES:
#   # Connect to MongoDB
#   docker run --rm -it mongosh:latest "mongodb://host.docker.internal:27017"
#
#   # Connect with authentication
#   docker run --rm -it mongosh:latest "mongodb://user:pass@host:27017/mydb"
#
#   # Run JavaScript file
#   docker run --rm -v ./scripts:/data mongosh:latest "mongodb://host:27017" /data/script.js
# ==============================================================================
