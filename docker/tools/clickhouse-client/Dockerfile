# ==============================================================================
# ClickHouse Client - Docker Image
# ==============================================================================
#
# PURPOSE:
# Minimal container with ClickHouse command-line client for interacting
# with ClickHouse databases.
#
# TOOLS INCLUDED:
# - clickhouse-client: ClickHouse native CLI client
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
ARG REGISTRY_PREFIX=docker.io/library/

# ------------------------------------------------------------------------------
# Base Image
# ------------------------------------------------------------------------------
# Using Debian slim because ClickHouse provides official packages for Debian
#
FROM ${REGISTRY_PREFIX}debian:bookworm-slim

# ------------------------------------------------------------------------------
# Version Configuration
# ------------------------------------------------------------------------------
ARG CLICKHOUSE_VERSION=24.12.3.47

# ------------------------------------------------------------------------------
# Labels
# ------------------------------------------------------------------------------
LABEL org.opencontainers.image.title="ClickHouse Client" \
      org.opencontainers.image.description="ClickHouse command-line client" \
      org.opencontainers.image.version="${CLICKHOUSE_VERSION}"

# ------------------------------------------------------------------------------
# Install ClickHouse Client
# ------------------------------------------------------------------------------
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg; \
    # Add ClickHouse repository
    curl -fsSL https://packages.clickhouse.com/rpm/lts/repodata/repomd.xml.key | \
        gpg --dearmor -o /usr/share/keyrings/clickhouse-keyring.gpg; \
    echo "deb [signed-by=/usr/share/keyrings/clickhouse-keyring.gpg] https://packages.clickhouse.com/deb stable main" \
        > /etc/apt/sources.list.d/clickhouse.list; \
    apt-get update; \
    # Install only the client package
    apt-get install -y --no-install-recommends \
        clickhouse-client; \
    # Cleanup
    apt-get purge -y --auto-remove curl gnupg; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*; \
    # Verify installation
    clickhouse-client --version

# ------------------------------------------------------------------------------
# Working Directory
# ------------------------------------------------------------------------------
WORKDIR /data

# ------------------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["clickhouse-client", "--version"]

# ------------------------------------------------------------------------------
# Non-Root User
# ------------------------------------------------------------------------------
RUN useradd --uid 1001 --gid 0 --create-home clickhouse \
    && chown -R 1001:0 /data

USER clickhouse

# ------------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------------
ENTRYPOINT ["clickhouse-client"]
CMD ["--help"]

# ==============================================================================
# BUILD:
#   docker build -t clickhouse-client:latest .
#   podman build -t clickhouse-client:latest --format docker .
#
# RUN:
#   docker run --rm clickhouse-client:latest --version
#
# EXAMPLES:
#   # Connect to ClickHouse
#   docker run --rm -it clickhouse-client:latest --host host.docker.internal
#
#   # Connect with authentication
#   docker run --rm -it clickhouse-client:latest --host myhost --user myuser --password mypass
#
#   # Run query
#   docker run --rm clickhouse-client:latest --host myhost --query "SELECT 1"
#
#   # Run SQL file
#   docker run --rm -v ./scripts:/data clickhouse-client:latest --host myhost --queries-file /data/script.sql
# ==============================================================================
