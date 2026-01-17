# ==============================================================================
# Database Tools - Consolidated Docker Image
# ==============================================================================
#
# PURPOSE:
# All-in-one container with multiple database command-line clients for
# convenient access to various database platforms.
#
# TOOLS INCLUDED:
# - psql: PostgreSQL client (psql, pg_dump, pg_restore)
# - snowsql: Snowflake CLI
# - mongosh: MongoDB Shell
# - sqlcmd: Microsoft SQL Server client
# - bcp: SQL Server bulk copy utility
# - msodbcsql18: Microsoft ODBC Driver for SQL Server
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
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ -t db-tools:latest .
#
#   Default (Docker Hub):
#     docker build -t db-tools:latest .
#
# NOTE: The trailing slash is required in the prefix!
#
ARG REGISTRY_PREFIX=docker.io/

# ------------------------------------------------------------------------------
# Base Image
# ------------------------------------------------------------------------------
# Red Hat UBI 9 Minimal: Required for Microsoft SQL Server tools
# Also provides a stable base for other tools
# NOTE: UBI images are under docker.io/redhat/ not docker.io/library/
#
FROM ${REGISTRY_PREFIX}redhat/ubi9-minimal:latest

# ------------------------------------------------------------------------------
# Version Configuration
# ------------------------------------------------------------------------------
ARG SNOWSQL_VERSION=1.3.2
ARG MSSQL_TOOLS_VERSION=18

# ------------------------------------------------------------------------------
# Labels
# ------------------------------------------------------------------------------
LABEL org.opencontainers.image.title="Database Tools" \
      org.opencontainers.image.description="Consolidated database CLI tools: psql, snowsql, mongosh, sqlcmd, bcp"

# ------------------------------------------------------------------------------
# Install All Database Tools
# ------------------------------------------------------------------------------
RUN set -eux; \
    # Determine package manager
    if command -v microdnf >/dev/null 2>&1; then \
        PM="microdnf"; \
        INSTALL_CMD="$PM -y install"; \
        CLEAN_CMD="$PM clean all"; \
    else \
        PM="dnf"; \
        INSTALL_CMD="$PM -y install"; \
        CLEAN_CMD="$PM clean all"; \
    fi; \
    \
    # ==========================================================================
    # Prerequisites (curl-minimal is pre-installed in UBI 9 minimal)
    # ==========================================================================
    $INSTALL_CMD \
        ca-certificates \
        tar \
        gzip \
        findutils; \
    \
    # ==========================================================================
    # PostgreSQL Client (psql)
    # ==========================================================================
    # Use default UBI9 PostgreSQL package (psql installs to /usr/bin/)
    $INSTALL_CMD postgresql; \
    \
    # ==========================================================================
    # Microsoft SQL Server Tools (sqlcmd, bcp)
    # ==========================================================================
    # Add Microsoft repository
    curl -fsSL https://packages.microsoft.com/config/rhel/9/prod.repo \
        -o /etc/yum.repos.d/mssql-release.repo; \
    # Install ODBC driver and tools
    ACCEPT_EULA=Y $INSTALL_CMD \
        msodbcsql${MSSQL_TOOLS_VERSION} \
        mssql-tools${MSSQL_TOOLS_VERSION} \
        unixODBC-devel; \
    \
    # ==========================================================================
    # MongoDB Shell (mongosh)
    # ==========================================================================
    # Add MongoDB repository for RHEL 9
    curl -fsSL -o /etc/yum.repos.d/mongodb-org-8.0.repo \
        https://repo.mongodb.org/yum/redhat/9/mongodb-org/8.0/x86_64/RPMS/; \
    echo -e "[mongodb-org-8.0]\nname=MongoDB Repository\nbaseurl=https://repo.mongodb.org/yum/redhat/9/mongodb-org/8.0/x86_64/\ngpgcheck=1\nenabled=1\ngpgkey=https://pgp.mongodb.com/server-8.0.asc" \
        > /etc/yum.repos.d/mongodb-org-8.0.repo; \
    $INSTALL_CMD mongodb-mongosh || true; \
    \
    # ==========================================================================
    # Snowflake SnowSQL
    # ==========================================================================
    # Note: SnowSQL installer creates a bootstrap wrapper that downloads the
    # actual binary on first run. Keep ~/.snowsql as snowsql needs it.
    curl -fsSL -o /tmp/snowsql.bash \
        "https://sfc-repo.snowflakecomputing.com/snowsql/bootstrap/1.3/linux_x86_64/snowsql-${SNOWSQL_VERSION}-linux_x86_64.bash"; \
    mkdir -p /opt/snowsql; \
    SNOWSQL_DEST=/opt/snowsql SNOWSQL_LOGIN_SHELL=/dev/null \
        bash /tmp/snowsql.bash || true; \
    ln -sf /opt/snowsql/snowsql /usr/local/bin/snowsql || true; \
    rm -f /tmp/snowsql.bash; \
    # Note: Do NOT remove /root/.snowsql - snowsql needs it \
    \
    # ==========================================================================
    # Cleanup
    # ==========================================================================
    $CLEAN_CMD; \
    rm -rf /var/cache/yum /var/cache/dnf /tmp/*; \
    \
    # ==========================================================================
    # Verify Installations
    # ==========================================================================
    echo "=== Verifying installations ==="; \
    psql --version || echo "psql not found"; \
    /opt/mssql-tools${MSSQL_TOOLS_VERSION}/bin/sqlcmd -? || echo "sqlcmd check complete"; \
    mongosh --version || echo "mongosh not found"; \
    ls -la /opt/snowsql/ || echo "snowsql not found"; \
    echo "=== Verification complete ==="

# ------------------------------------------------------------------------------
# Environment Variables
# ------------------------------------------------------------------------------
ENV PATH="/opt/mssql-tools18/bin:/opt/snowsql:${PATH}" \
    SNOWSQL_DEST=/opt/snowsql

# ------------------------------------------------------------------------------
# Working Directory
# ------------------------------------------------------------------------------
WORKDIR /data

# ------------------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["sqlcmd", "-?"]

# ------------------------------------------------------------------------------
# Non-Root User
# ------------------------------------------------------------------------------
RUN useradd --uid 1001 --gid 0 --create-home dbtools \
    && mkdir -p /home/dbtools/.snowsql /home/dbtools/.mongodb \
    && cp -r /root/.snowsql/* /home/dbtools/.snowsql/ 2>/dev/null || true \
    && chown -R 1001:0 /data /opt/snowsql /home/dbtools || true

USER dbtools

# ------------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------------
# Default to bash for interactive use with all tools available
ENTRYPOINT ["/bin/bash"]
CMD ["-c", "echo 'Database Tools Container'; echo 'Available commands: psql, sqlcmd, bcp, mongosh, snowsql'; exec bash"]

# ==============================================================================
# BUILD:
#   docker build -t db-tools:latest .
#   podman build -t db-tools:latest --format docker .
#
# RUN:
#   # Interactive shell with all tools
#   docker run --rm -it db-tools:latest
#
# EXAMPLES:
#   # PostgreSQL
#   docker run --rm db-tools:latest -c "psql --version"
#   docker run --rm -it db-tools:latest -c "psql -h myhost -U myuser -d mydb"
#
#   # SQL Server
#   docker run --rm db-tools:latest -c "sqlcmd -S myserver -U myuser -P 'pass' -Q 'SELECT @@VERSION'"
#
#   # MongoDB
#   docker run --rm db-tools:latest -c "mongosh 'mongodb://host:27017' --eval 'db.version()'"
#
#   # Snowflake
#   docker run --rm db-tools:latest -c "snowsql -a myaccount -u myuser"
#
#   # Run SQL file
#   docker run --rm -v ./scripts:/data db-tools:latest -c "psql -h myhost -U myuser -f /data/script.sql"
# ==============================================================================
