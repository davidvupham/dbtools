# ==============================================================================
# ClickHouse Server - Docker Image
# ==============================================================================
#
# PURPOSE:
# ClickHouse is an open-source column-oriented database management system
# for online analytical processing (OLAP).
#
# FEATURES:
# - Columnar storage for fast analytical queries
# - Real-time query processing
# - Linear scalability
# - SQL support with extensions
# - High compression ratios
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
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/ -t clickhouse:latest .
#
#   Default (Docker Hub):
#     docker build -t clickhouse:latest .
#
# NOTE: The trailing slash is required in the prefix!
# NOTE: ClickHouse images are under clickhouse/ not library/
#
ARG REGISTRY_PREFIX=docker.io/

# ------------------------------------------------------------------------------
# Base Image
# ------------------------------------------------------------------------------
FROM ${REGISTRY_PREFIX}clickhouse/clickhouse-server:24.12

# ------------------------------------------------------------------------------
# Labels
# ------------------------------------------------------------------------------
LABEL org.opencontainers.image.title="ClickHouse Server" \
      org.opencontainers.image.description="ClickHouse column-oriented OLAP database server" \
      org.opencontainers.image.version="24.12"

# ------------------------------------------------------------------------------
# Ports
# ------------------------------------------------------------------------------
# 8123 - HTTP interface
# 9000 - Native TCP interface (clickhouse-client)
# 9009 - Interserver HTTP (for replication)
#
EXPOSE 8123 9000 9009

# ------------------------------------------------------------------------------
# Volumes
# ------------------------------------------------------------------------------
# /var/lib/clickhouse - Database data
# /var/log/clickhouse-server - Server logs
#
VOLUME ["/var/lib/clickhouse", "/var/log/clickhouse-server"]

# ------------------------------------------------------------------------------
# Non-Root User
# ------------------------------------------------------------------------------
# The official ClickHouse image already runs as non-root (user clickhouse).
# This explicit USER directive ensures security compliance and documents the
# expected runtime user.
#
# SECURITY:
#   - Limits blast radius if container is compromised
#   - Required by CKV_DOCKER_3 security policy
#   - Best practice for production containers
#
USER clickhouse

# ------------------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------------------
# ClickHouse provides a /ping endpoint on the HTTP interface (port 8123)
#
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD ["wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8123/ping"]

# ==============================================================================
# BUILD:
#   docker build -t clickhouse:latest .
#   podman build -t clickhouse:latest --format docker .
#
# RUN:
#   docker run -d -p 8123:8123 -p 9000:9000 clickhouse:latest
#
# EXAMPLES:
#   # Run with persistent storage
#   docker run -d \
#     -p 8123:8123 -p 9000:9000 \
#     -v clickhouse-data:/var/lib/clickhouse \
#     -v clickhouse-logs:/var/log/clickhouse-server \
#     clickhouse:latest
#
#   # Connect with clickhouse-client
#   docker run --rm -it --network host clickhouse-client:latest --host localhost
#
#   # HTTP API query
#   curl 'http://localhost:8123/?query=SELECT%201'
#
# PORTS:
#   8123 - HTTP interface (REST API, web UI)
#   9000 - Native TCP (clickhouse-client connections)
#   9009 - Inter-server HTTP (replication)
# ==============================================================================
