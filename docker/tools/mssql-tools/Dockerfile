# ==============================================================================
# Microsoft SQL Server Tools - Docker Image
# ==============================================================================
#
# PURPOSE:
# Container with Microsoft SQL Server command-line tools and ODBC driver
# for interacting with SQL Server databases.
#
# TOOLS INCLUDED:
# - sqlcmd: Command-line query utility
# - bcp: Bulk copy program for data import/export
# - msodbcsql18: Microsoft ODBC Driver 18 for SQL Server
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
ARG REGISTRY_PREFIX=docker.io/

# ------------------------------------------------------------------------------
# Base Image
# ------------------------------------------------------------------------------
# Red Hat UBI 9 Minimal: Microsoft's supported platform for mssql-tools
# Matches the devcontainer base image for consistency
# NOTE: UBI images are under docker.io/redhat/ not docker.io/library/
#
FROM ${REGISTRY_PREFIX}redhat/ubi9-minimal:latest

# ------------------------------------------------------------------------------
# Version Configuration
# ------------------------------------------------------------------------------
ARG MSSQL_TOOLS_VERSION=18

# ------------------------------------------------------------------------------
# Labels
# ------------------------------------------------------------------------------
LABEL org.opencontainers.image.title="Microsoft SQL Server Tools" \
      org.opencontainers.image.description="SQL Server command-line tools (sqlcmd, bcp) with ODBC driver" \
      org.opencontainers.image.version="${MSSQL_TOOLS_VERSION}"

# ------------------------------------------------------------------------------
# Install Microsoft SQL Server Tools
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
    # Install prerequisites (ca-certificates only, curl-minimal is pre-installed)
    $INSTALL_CMD ca-certificates; \
    # Add Microsoft repository (use curl-minimal which is pre-installed)
    curl -fsSL https://packages.microsoft.com/config/rhel/9/prod.repo \
        -o /etc/yum.repos.d/mssql-release.repo; \
    # Install ODBC driver and tools (accept EULA)
    ACCEPT_EULA=Y $INSTALL_CMD \
        msodbcsql${MSSQL_TOOLS_VERSION} \
        mssql-tools${MSSQL_TOOLS_VERSION} \
        unixODBC-devel; \
    # Cleanup
    $CLEAN_CMD; \
    rm -rf /var/cache/yum /var/cache/dnf; \
    # Verify installation
    /opt/mssql-tools${MSSQL_TOOLS_VERSION}/bin/sqlcmd -?

# ------------------------------------------------------------------------------
# Environment Variables
# ------------------------------------------------------------------------------
ENV PATH="/opt/mssql-tools${MSSQL_TOOLS_VERSION}/bin:${PATH}"

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
RUN useradd --uid 1001 --gid 0 --create-home mssql \
    && chown -R 1001:0 /data

USER mssql

# ------------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------------
ENTRYPOINT ["sqlcmd"]
CMD ["-?"]

# ==============================================================================
# BUILD:
#   docker build -t mssql-tools:latest .
#   podman build -t mssql-tools:latest --format docker .
#
# RUN:
#   docker run --rm mssql-tools:latest -?
#
# EXAMPLES:
#   # Connect to SQL Server
#   docker run --rm -it mssql-tools:latest -S host.docker.internal -U sa -P 'YourPassword'
#
#   # Run SQL query
#   docker run --rm mssql-tools:latest -S myserver -U myuser -P 'pass' -Q "SELECT @@VERSION"
#
#   # Run SQL file
#   docker run --rm -v ./scripts:/data mssql-tools:latest -S myserver -U myuser -P 'pass' -i /data/script.sql
#
#   # Bulk copy (bcp)
#   docker run --rm --entrypoint bcp -v ./data:/data mssql-tools:latest mydb.dbo.mytable in /data/data.csv -S myserver -U myuser -P 'pass' -c -t ','
# ==============================================================================
