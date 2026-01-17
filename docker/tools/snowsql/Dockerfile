# ==============================================================================
# Snowflake SnowSQL CLI - Docker Image
# ==============================================================================
#
# PURPOSE:
# Container with Snowflake's SnowSQL command-line client for interacting
# with Snowflake data warehouses.
#
# TOOLS INCLUDED:
# - snowsql: Snowflake command-line interface
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
ARG REGISTRY_PREFIX=docker.io/library/

# ------------------------------------------------------------------------------
# Base Image
# ------------------------------------------------------------------------------
# Using Debian slim because SnowSQL requires glibc (not available in Alpine musl)
#
FROM ${REGISTRY_PREFIX}debian:bookworm-slim

# ------------------------------------------------------------------------------
# Version Configuration
# ------------------------------------------------------------------------------
ARG SNOWSQL_VERSION=1.3.2

# ------------------------------------------------------------------------------
# Labels
# ------------------------------------------------------------------------------
LABEL org.opencontainers.image.title="Snowflake SnowSQL" \
      org.opencontainers.image.description="Snowflake command-line client (snowsql)" \
      org.opencontainers.image.version="${SNOWSQL_VERSION}"

# ------------------------------------------------------------------------------
# Install SnowSQL
# ------------------------------------------------------------------------------
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        unzip; \
    # Download SnowSQL installer
    mkdir -p /opt/snowsql; \
    curl -fsSL -o /tmp/snowsql.bash \
        "https://sfc-repo.snowflakecomputing.com/snowsql/bootstrap/1.3/linux_x86_64/snowsql-${SNOWSQL_VERSION}-linux_x86_64.bash"; \
    # Run installer - creates wrapper at SNOWSQL_DEST, binary downloads to ~/.snowsql
    SNOWSQL_DEST=/opt/snowsql SNOWSQL_LOGIN_SHELL=/dev/null \
        bash /tmp/snowsql.bash; \
    # Create symlink
    ln -sf /opt/snowsql/snowsql /usr/local/bin/snowsql; \
    # Cleanup (keep ~/.snowsql as snowsql needs it)
    rm -f /tmp/snowsql.bash; \
    apt-get purge -y --auto-remove curl unzip; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*; \
    # Note: snowsql --version requires connection to Snowflake, skip verification
    ls -la /opt/snowsql/

# ------------------------------------------------------------------------------
# Environment Variables
# ------------------------------------------------------------------------------
# SNOWSQL_DEST: Where the snowsql binary is installed
# SNOWSQL_CONFIG_PATH: Where snowsql looks for config files (can be overridden)
#
ENV SNOWSQL_DEST=/opt/snowsql \
    PATH="/opt/snowsql:${PATH}"

# ------------------------------------------------------------------------------
# Working Directory
# ------------------------------------------------------------------------------
WORKDIR /data

# ------------------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------------------
# Note: snowsql --version requires internet to download binary on first run
# Using file existence check instead
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["test", "-f", "/opt/snowsql/snowsql"]

# ------------------------------------------------------------------------------
# Non-Root User
# ------------------------------------------------------------------------------
RUN useradd --uid 1001 --gid 0 --create-home snowsql \
    && mkdir -p /home/snowsql/.snowsql \
    && cp -r /root/.snowsql/* /home/snowsql/.snowsql/ 2>/dev/null || true \
    && chown -R 1001:0 /data /opt/snowsql /home/snowsql/.snowsql

USER snowsql

# ------------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------------
ENTRYPOINT ["snowsql"]
CMD ["--version"]

# ==============================================================================
# BUILD:
#   docker build -t snowsql:latest .
#   podman build -t snowsql:latest --format docker .
#
# CONFIGURATION:
#   SnowSQL stores config/credentials in ~/.snowsql/ which includes:
#   - config: Connection settings and credentials
#   - history: Command history
#   - logs/: Log files
#
#   Mount your host's ~/.snowsql directory for persistent settings.
#   The mount requires read-write access so SnowSQL can:
#   - Read your connection configurations and credentials
#   - Write command history
#   - Write log files
#
# DOCKER EXAMPLES:
#   # Verify installation
#   docker run --rm snowsql:latest --version
#
#   # Connect using a named connection from your config
#   docker run --rm -it \
#     -v ~/.snowsql:/home/snowsql/.snowsql \
#     snowsql:latest -c myconnection
#
#   # Interactive connection (will prompt for credentials)
#   docker run --rm -it \
#     -v ~/.snowsql:/home/snowsql/.snowsql \
#     snowsql:latest -a <account> -u <user>
#
#   # Run SQL file with mounted scripts directory
#   docker run --rm \
#     -v ~/.snowsql:/home/snowsql/.snowsql \
#     -v ./scripts:/data \
#     snowsql:latest -c myconnection -f /data/script.sql
#
#   # Pass credentials via environment (less secure, useful for CI)
#   docker run --rm \
#     -e SNOWSQL_ACCOUNT=myaccount \
#     -e SNOWSQL_USER=myuser \
#     -e SNOWSQL_PWD=mypass \
#     snowsql:latest
#
# PODMAN EXAMPLES:
#   # Verify installation
#   podman run --rm snowsql:latest --version
#
#   # Connect using a named connection from your config
#   podman run --rm -it \
#     -v ~/.snowsql:/home/snowsql/.snowsql \
#     snowsql:latest -c myconnection
#
#   # Interactive connection (will prompt for credentials)
#   podman run --rm -it \
#     -v ~/.snowsql:/home/snowsql/.snowsql \
#     snowsql:latest -a <account> -u <user>
#
#   # Run SQL file with mounted scripts directory
#   podman run --rm \
#     -v ~/.snowsql:/home/snowsql/.snowsql \
#     -v ./scripts:/data \
#     snowsql:latest -c myconnection -f /data/script.sql
#
#   # Pass credentials via environment (less secure, useful for CI)
#   podman run --rm \
#     -e SNOWSQL_ACCOUNT=myaccount \
#     -e SNOWSQL_USER=myuser \
#     -e SNOWSQL_PWD=mypass \
#     snowsql:latest
# ==============================================================================
