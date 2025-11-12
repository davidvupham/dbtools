# ==============================================================================
# SQL Server 2022 Docker Image with Persistent Storage
# ==============================================================================
#
# PURPOSE:
# This Dockerfile creates a customized Microsoft SQL Server 2022 Developer
# Edition image with support for persistent storage volumes.
#
# LEARNING OBJECTIVES FOR BEGINNERS:
# 1. How to extend official Docker images
# 2. User and permission management in containers
# 3. Volume configuration for data persistence
# 4. Environment variable usage
# 5. Multi-stage permission handling (root vs. application user)
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Base Image Selection
# ------------------------------------------------------------------------------
# FROM: Specifies the base image to build upon
# - We use Microsoft's official SQL Server 2022 image
# - "latest" tag gets the most recent stable version
# - This image already includes SQL Server binaries and default configuration
#
# WHAT YOU GET:
# - SQL Server 2022 Developer Edition (fully featured, free for non-production)
# - Linux-based container (SQL Server on Linux)
# - Pre-configured with default settings
# - User 'mssql' (UID 10001) already created for running SQL Server
#
FROM mcr.microsoft.com/mssql/server:2022-latest

# ------------------------------------------------------------------------------
# Environment Variables
# ------------------------------------------------------------------------------
# ENV: Sets environment variables that persist in the container
# These can be overridden when starting the container
#
# ACCEPT_EULA=Y:
#   - Accepts Microsoft's End User License Agreement
#   - Required for SQL Server to start
#   - Without this, SQL Server will refuse to run
#
# MSSQL_PID=Developer:
#   - Specifies the SQL Server edition/product ID
#   - Options: Developer, Express, Standard, Enterprise, or a product key
#   - Developer = Full features, free for non-production use
#
ENV ACCEPT_EULA=Y \
    MSSQL_PID=Developer

# ------------------------------------------------------------------------------
# User Context Switch: root
# ------------------------------------------------------------------------------
# USER root:
#   - Switches to root user for administrative tasks
#   - Required for: creating directories, changing ownership, installing packages
#   - The base image runs as 'mssql' user, so we temporarily elevate privileges
#
# WHY NEEDED:
#   - Only root can create system directories and change ownership
#   - Security best practice: use root only when necessary, then switch back
#
USER root

# ------------------------------------------------------------------------------
# Directory Creation and Permissions
# ------------------------------------------------------------------------------
# RUN: Executes commands during image build (creates new layer in image)
#
# mkdir -p /data/mssql /logs/mssql:
#   - Creates directories for persistent storage
#   - -p flag creates parent directories if they don't exist
#   - /data/mssql = SQL Server database files (.mdf, .ldf)
#   - /logs/mssql = SQL Server error logs and transaction logs
#
# chown -R mssql:0 /data /logs:
#   - Changes ownership recursively (-R)
#   - mssql = user (UID 10001, created in base image)
#   - 0 = group (root group, GID 0)
#   - WHY: SQL Server runs as 'mssql' user and needs write access
#   - WHY GROUP 0: OpenShift compatibility (uses arbitrary UIDs with GID 0)
#
# chmod -R g+rwx /data /logs:
#   - Changes permissions recursively
#   - g+rwx = Give group read, write, execute permissions
#   - WHY: Allows group (GID 0) full access to directories
#   - Security: Only owner (mssql) and group (0) can access, not others
#
RUN mkdir -p /data/mssql /logs/mssql && \
    chown -R mssql:0 /data /logs && \
    chmod -R g+rwx /data /logs

# ------------------------------------------------------------------------------
# Volume Declaration
# ------------------------------------------------------------------------------
# VOLUME: Declares mount points for external storage
#
# PURPOSE:
#   - Tells Docker these directories should persist data outside the container
#   - Data in volumes survives container restarts and deletions
#   - Volumes can be shared between containers
#
# HOW IT WORKS:
#   - If not mapped at runtime, Docker creates anonymous volumes
#   - Best practice: map to host directories (bind mounts) in docker-compose.yml
#   - Example: /data/mssql on host → /data/mssql in container
#
# DATA STORED HERE:
#   - /data/mssql: System databases (master, model, msdb, tempdb)
#   - /data/mssql: User databases
#   - /logs/mssql: Error logs, agent logs, system logs
#
VOLUME ["/data/mssql", "/logs/mssql"]

# ------------------------------------------------------------------------------
# Port Exposure
# ------------------------------------------------------------------------------
# EXPOSE: Documents which ports the container listens on
#
# PORT 1433:
#   - Default SQL Server port
#   - Used for client connections (sqlcmd, SSMS, application connections)
#   - This doesn't actually publish the port (that's done at runtime)
#   - Think of it as documentation for users of this image
#
# TO ACCESS FROM OUTSIDE:
#   - Use -p flag with docker run: -p 1433:1433
#   - Or use ports section in docker-compose.yml
#   - Format: <host-port>:<container-port>
#
EXPOSE 1433

# ------------------------------------------------------------------------------
# User Context Switch: Application User
# ------------------------------------------------------------------------------
# USER mssql:
#   - Switches from root back to 'mssql' user
#   - SQL Server will run as this non-privileged user
#
# SECURITY BEST PRACTICE:
#   - Never run applications as root in production
#   - Limits damage if container is compromised
#   - 'mssql' user (UID 10001) has only necessary permissions
#   - Can write to /data and /logs directories (we set ownership above)
#   - Cannot modify system files or other users' data
#
USER mssql

# ------------------------------------------------------------------------------
# Container Startup Command
# ------------------------------------------------------------------------------
# CMD: Specifies the default command to run when container starts
#
# /opt/mssql/bin/sqlservr:
#   - The SQL Server daemon/service executable
#   - Runs in foreground (required for Docker containers)
#   - Listens on port 1433 for connections
#   - Manages database files in /var/opt/mssql (or mapped volume)
#
# CONTAINER LIFECYCLE:
#   - When this process stops, the container stops
#   - Docker monitors this process for health
#   - Logs go to stdout/stderr (visible via 'docker logs')
#
# CAN BE OVERRIDDEN:
#   - docker run <image> /bin/bash  (overrides CMD)
#   - Useful for debugging or running one-off commands
#
CMD ["/opt/mssql/bin/sqlservr"]

# ==============================================================================
# BUILD INSTRUCTIONS:
# ==============================================================================
# From /workspaces/dbtools/docker/mssql directory:
#
#   docker build -t gds-mssql:latest .
#
# EXPLANATION:
#   - docker build: Build an image from this Dockerfile
#   - -t gds-mssql:latest: Tag the image with name:version
#   - .: Use current directory as build context
#
# ==============================================================================
# RUN INSTRUCTIONS:
# ==============================================================================
# See docker-compose.yml or use:
#
#   docker run -d \
#     --name mssql1 \
#     -e MSSQL_SA_PASSWORD='YourStrong!Passw0rd' \
#     -p 1433:1433 \
#     -v /data/mssql/mssql1:/var/opt/mssql \
#     gds-mssql:latest
#
# ==============================================================================
