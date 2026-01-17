# ==============================================================================
# Grafana - Docker Image
# ==============================================================================
#
# PURPOSE:
# Grafana dashboarding and visualization platform for metrics, logs, and traces.
#
# FEATURES:
# - Data visualization and dashboards
# - Alerting and notifications
# - Plugin ecosystem
# - Multi-data source support (Prometheus, InfluxDB, PostgreSQL, etc.)
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
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/ -t grafana:latest .
#
#   Default (Docker Hub):
#     docker build -t grafana:latest .
#
# NOTE: The trailing slash is required in the prefix!
# NOTE: Grafana images are under grafana/ not library/ so adjust REGISTRY_PREFIX accordingly
#
ARG REGISTRY_PREFIX=docker.io/

# ------------------------------------------------------------------------------
# Base Image
# ------------------------------------------------------------------------------
FROM ${REGISTRY_PREFIX}grafana/grafana:11.4.0

# ------------------------------------------------------------------------------
# Labels
# ------------------------------------------------------------------------------
LABEL org.opencontainers.image.title="Grafana" \
      org.opencontainers.image.description="Grafana dashboarding and visualization platform" \
      org.opencontainers.image.version="11.4.0"

# ------------------------------------------------------------------------------
# Environment Variables
# ------------------------------------------------------------------------------
ENV GF_PATHS_PROVISIONING=/etc/grafana/provisioning \
    GF_SECURITY_ADMIN_USER=admin \
    GF_USERS_ALLOW_SIGN_UP=false

# ------------------------------------------------------------------------------
# Copy Provisioning Configuration (optional)
# ------------------------------------------------------------------------------
# Uncomment to include default provisioning configs
# COPY provisioning/ /etc/grafana/provisioning/

# ------------------------------------------------------------------------------
# Non-Root User
# ------------------------------------------------------------------------------
# The official Grafana image already runs as non-root (UID 472, user grafana).
# This explicit USER directive ensures security compliance and documents the
# expected runtime user.
#
# SECURITY:
#   - Limits blast radius if container is compromised
#   - Required by CKV_DOCKER_3 security policy
#   - Best practice for production containers
#
USER grafana

# ------------------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------------------
# Grafana provides a /api/health endpoint for health checks
#
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD ["wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/api/health"]

# ==============================================================================
# BUILD:
#   docker build -t grafana:latest .
#   podman build -t grafana:latest --format docker .
#
# RUN:
#   docker run -d -p 3000:3000 grafana:latest
#
# EXAMPLES:
#   # Run with persistent storage
#   docker run -d -p 3000:3000 -v grafana-data:/var/lib/grafana grafana:latest
#
#   # Run with custom admin password
#   docker run -d -p 3000:3000 -e GF_SECURITY_ADMIN_PASSWORD=secret grafana:latest
#
#   # Run with provisioning configs
#   docker run -d -p 3000:3000 -v ./provisioning:/etc/grafana/provisioning:ro grafana:latest
#
# ACCESS:
#   http://localhost:3000
#   Default credentials: admin / admin (change on first login)
# ==============================================================================
