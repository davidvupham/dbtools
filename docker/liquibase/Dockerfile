# ==============================================================================
# Liquibase Database Migration Tool - Docker Image
# ==============================================================================
#
# PURPOSE:
# This Dockerfile creates a containerized version of Liquibase, a database
# schema change management tool, with support for multiple database platforms.
#
# WHAT IS LIQUIBASE?
# Liquibase tracks, versions, and deploys database schema changes. It's like
# Git for your database schema - you can:
# - Version control database changes
# - Apply changes across different environments (dev, test, prod)
# - Rollback changes if needed
# - Support multiple database types from one tool
#
# DATABASES SUPPORTED IN THIS IMAGE:
# - SQL Server (Microsoft)
# - PostgreSQL
# - Snowflake
# - MongoDB
#
# LEARNING OBJECTIVES FOR BEGINNERS:
# 1. How to use build arguments (ARG) for version management
# 2. Environment variable configuration (ENV)
# 3. Multi-step RUN commands with && chaining
# 4. Downloading and extracting software in Docker
# 5. JDBC driver management for Java applications
# 6. Creating symbolic links for command availability
# 7. ENTRYPOINT vs CMD usage patterns
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Base Image Selection
# ------------------------------------------------------------------------------
# FROM: Specifies the parent image to build upon
#
# eclipse-temurin:21-jre:
#   - Eclipse Temurin is an OpenJDK distribution (open-source Java)
#   - 21 = Java version 21 (LTS - Long Term Support release)
#   - jre = Java Runtime Environment (enough to run Java apps, not compile them)
#   - JRE is smaller than JDK (no compiler/dev tools), perfect for production
#
# WHY JAVA?
#   - Liquibase is a Java application
#   - Requires Java Runtime to execute
#   - JDBC drivers (database connectors) are Java libraries
#
FROM eclipse-temurin:21-jre

# ------------------------------------------------------------------------------
# Build Arguments - Version Control
# ------------------------------------------------------------------------------
# ARG: Build-time variables (only available during image build, not runtime)
# These can be overridden when building: docker build --build-arg LIQUIBASE_VERSION=5.0.2
#
# WHY USE ARG?
#   - Easy version upgrades (change one number, rebuild)
#   - No hardcoded versions scattered throughout Dockerfile
#   - Can customize versions without editing Dockerfile
#   - Self-documenting: shows exact versions being installed
#
# VERSION MANAGEMENT STRATEGY:
#   - Keep these ARGs at the top for easy updates
#   - Use variables in URLs below (${LIQUIBASE_VERSION})
#   - To upgrade: just change the version number and rebuild
#
ARG LIQUIBASE_VERSION=5.0.1           # Liquibase core version
ARG MSSQL_DRIVER_VERSION=13.2.1       # SQL Server JDBC driver
ARG MSSQL_DRIVER_JAR=mssql-jdbc-${MSSQL_DRIVER_VERSION}.jre11.jar  # Full JAR filename
ARG POSTGRES_DRIVER_VERSION=42.7.8    # PostgreSQL JDBC driver
ARG SNOWFLAKE_DRIVER_VERSION=3.27.1   # Snowflake JDBC driver
ARG MONGODB_DRIVER_VERSION=3.12.14    # MongoDB Java driver
ARG LIQUIBASE_MONGODB_VERSION=5.0.1   # Liquibase extension for MongoDB

# ------------------------------------------------------------------------------
# Environment Variables - Runtime Configuration
# ------------------------------------------------------------------------------
# ENV: Sets environment variables that persist in the running container
# Unlike ARG, these are available when the container runs
#
# LIQUIBASE_HOME=/opt/liquibase:
#   - Installation directory for Liquibase
#   - /opt is Linux convention for optional/add-on software
#   - Other applications can reference $LIQUIBASE_HOME
#
# PATH=/opt/liquibase:${PATH}:
#   - Adds Liquibase directory to system PATH
#   - Allows running 'liquibase' command without full path
#   - ${PATH} preserves existing PATH entries
#   - Format: new_path:old_path (colon-separated on Linux)
#
ENV LIQUIBASE_HOME=/opt/liquibase \
    PATH=/opt/liquibase:${PATH}

# ------------------------------------------------------------------------------
# Software Installation - Multi-Step Process
# ------------------------------------------------------------------------------
# RUN: Executes commands during image build (creates a new layer)
#
# WHY CHAIN COMMANDS WITH && ?
#   - Each RUN creates a new layer in the Docker image
#   - More layers = larger image size
#   - && chains commands into one RUN = one layer = smaller image
#   - If any command fails, entire RUN fails (safer)
#
# CLEANUP STRATEGY:
#   - Download → Extract → Delete download in same layer
#   - Removes temporary files from the final image
#   - Keeps image size small
#
# COMMAND BREAKDOWN:
#
RUN apt-get update \
    # ----------------------------------------------------------------------
    # Update package index
    # Like refreshing the app store catalog before installing apps
    # ----------------------------------------------------------------------
    && apt-get install -y --no-install-recommends curl unzip ca-certificates \
    # ----------------------------------------------------------------------
    # Install required utilities:
    # - curl: Download files from URLs
    # - unzip: Extract .zip archives (if needed)
    # - ca-certificates: SSL/TLS certificates for HTTPS downloads
    #
    # Flags explained:
    # - -y: Automatically answer "yes" to prompts (non-interactive)
    # - --no-install-recommends: Don't install suggested packages (smaller image)
    # ----------------------------------------------------------------------
    && rm -rf /var/lib/apt/lists/* \
    # ----------------------------------------------------------------------
    # Clean up APT cache
    # After installing packages, delete the package lists
    # Saves space (package lists can be hundreds of MB)
    # We won't need them again since image is built
    # ----------------------------------------------------------------------
    && curl -fsSL -o /tmp/liquibase.tar.gz \
    https://github.com/liquibase/liquibase/releases/download/v${LIQUIBASE_VERSION}/liquibase-${LIQUIBASE_VERSION}.tar.gz \
    # ----------------------------------------------------------------------
    # Download Liquibase from GitHub releases
    #
    # curl flags:
    # - -f: Fail silently on server errors (don't download error pages)
    # - -s: Silent mode (no progress bar)
    # - -S: Show errors if -s is used
    # - -L: Follow redirects (GitHub releases often redirect)
    # - -o: Output to file (instead of stdout)
    #
    # ${LIQUIBASE_VERSION}: Substitutes ARG value (5.0.1)
    # Downloads to /tmp (temporary directory)
    # ----------------------------------------------------------------------
    && mkdir -p ${LIQUIBASE_HOME} \
    # ----------------------------------------------------------------------
    # Create Liquibase installation directory
    # -p flag: Create parent directories if needed, don't error if exists
    # ----------------------------------------------------------------------
    && tar -xzf /tmp/liquibase.tar.gz -C ${LIQUIBASE_HOME} \
    # ----------------------------------------------------------------------
    # Extract Liquibase archive
    #
    # tar flags:
    # - -x: Extract
    # - -z: Decompress with gzip
    # - -f: File to extract (next argument)
    # - -C: Change to directory (extract to ${LIQUIBASE_HOME})
    #
    # Result: Liquibase files now in /opt/liquibase/
    # ----------------------------------------------------------------------
    && rm /tmp/liquibase.tar.gz \
    # ----------------------------------------------------------------------
    # Delete the downloaded archive
    # We've extracted it, don't need the .tar.gz anymore
    # Saves space in the final image
    # ----------------------------------------------------------------------
    && curl -fsSL -o ${LIQUIBASE_HOME}/lib/${MSSQL_DRIVER_JAR} \
    https://github.com/microsoft/mssql-jdbc/releases/download/v${MSSQL_DRIVER_VERSION}/${MSSQL_DRIVER_JAR} \
    # ----------------------------------------------------------------------
    # Download SQL Server JDBC driver
    #
    # WHAT IS A JDBC DRIVER?
    # - Java Database Connectivity driver
    # - Allows Java applications to connect to databases
    # - Each database type needs its own driver (SQL Server, Postgres, etc.)
    # - Drivers are .jar files (Java archives)
    #
    # WHY IN lib/ DIRECTORY?
    # - Liquibase automatically loads drivers from lib/ directory
    # - No additional configuration needed
    #
    # Downloads to: /opt/liquibase/lib/mssql-jdbc-13.2.1.jre11.jar
    # ----------------------------------------------------------------------
    && curl -fsSL -o ${LIQUIBASE_HOME}/lib/postgresql-${POSTGRES_DRIVER_VERSION}.jar \
    https://repo1.maven.org/maven2/org/postgresql/postgresql/${POSTGRES_DRIVER_VERSION}/postgresql-${POSTGRES_DRIVER_VERSION}.jar \
    # ----------------------------------------------------------------------
    # Download PostgreSQL JDBC driver
    # From Maven Central Repository (standard Java package repository)
    # Downloads to: /opt/liquibase/lib/postgresql-42.7.8.jar
    # ----------------------------------------------------------------------
    && curl -fsSL -o ${LIQUIBASE_HOME}/lib/snowflake-jdbc-${SNOWFLAKE_DRIVER_VERSION}.jar \
    https://repo1.maven.org/maven2/net/snowflake/snowflake-jdbc/${SNOWFLAKE_DRIVER_VERSION}/snowflake-jdbc-${SNOWFLAKE_DRIVER_VERSION}.jar \
    # ----------------------------------------------------------------------
    # Download Snowflake JDBC driver
    # Snowflake is a cloud data warehouse platform
    # Downloads to: /opt/liquibase/lib/snowflake-jdbc-3.27.1.jar
    # ----------------------------------------------------------------------
    && curl -fsSL -o ${LIQUIBASE_HOME}/lib/mongo-java-driver-${MONGODB_DRIVER_VERSION}.jar \
    https://repo1.maven.org/maven2/org/mongodb/mongo-java-driver/${MONGODB_DRIVER_VERSION}/mongo-java-driver-${MONGODB_DRIVER_VERSION}.jar \
    # ----------------------------------------------------------------------
    # Download MongoDB Java driver
    # Base driver for MongoDB connectivity
    # Downloads to: /opt/liquibase/lib/mongo-java-driver-3.12.14.jar
    # ----------------------------------------------------------------------
    && mkdir -p ${LIQUIBASE_HOME}/lib/ext \
    # ----------------------------------------------------------------------
    # Create extensions directory
    # Liquibase looks in lib/ext/ for extension plugins
    # Extensions add support for non-standard databases
    # ----------------------------------------------------------------------
    && curl -fsSL -o ${LIQUIBASE_HOME}/lib/ext/liquibase-mongodb-${LIQUIBASE_MONGODB_VERSION}.jar \
    https://repo1.maven.org/maven2/org/liquibase/ext/liquibase-mongodb/${LIQUIBASE_MONGODB_VERSION}/liquibase-mongodb-${LIQUIBASE_MONGODB_VERSION}.jar \
    # ----------------------------------------------------------------------
    # Download Liquibase MongoDB extension
    # Adds MongoDB-specific functionality to Liquibase
    # Extensions go in lib/ext/ (not lib/)
    # Downloads to: /opt/liquibase/lib/ext/liquibase-mongodb-5.0.1.jar
    # ----------------------------------------------------------------------
    && ln -s ${LIQUIBASE_HOME}/liquibase /usr/local/bin/liquibase
# ----------------------------------------------------------------------
# Create symbolic link (like a Windows shortcut)
#
# ln -s source target:
# - Creates a symlink from /usr/local/bin/liquibase
#   → /opt/liquibase/liquibase
# - /usr/local/bin is in system PATH
# - Allows running 'liquibase' from anywhere
#
# WITHOUT SYMLINK:
#   Must type: /opt/liquibase/liquibase <command>
#
# WITH SYMLINK:
#   Can type: liquibase <command>
# ----------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Working Directory
# ------------------------------------------------------------------------------
# WORKDIR: Sets the default directory for subsequent commands
# - Creates the directory if it doesn't exist
# - Like "cd /liquibase" but persists
# - When you run the container, you start in this directory
# - All relative paths in commands are relative to this directory
#
# WHY /liquibase?
# - Convention: working directory for Liquibase operations
# - Users mount their changelog files here
# - Example: docker run -v ./changelogs:/liquibase liquibase update
#
WORKDIR /liquibase

# ------------------------------------------------------------------------------
# Container Entry Point and Default Command
# ------------------------------------------------------------------------------
# ENTRYPOINT vs CMD - IMPORTANT DISTINCTION:
#
# ENTRYPOINT:
#   - The main command that always runs
#   - Cannot be easily overridden (need --entrypoint flag)
#   - Arguments passed to container are appended to ENTRYPOINT
#
# CMD:
#   - Default arguments for ENTRYPOINT
#   - Easily overridden by arguments in docker run
#   - If ENTRYPOINT is set, CMD provides default parameters
#
# HOW THEY WORK TOGETHER:
#   Final command = ENTRYPOINT + CMD (or user arguments)
#
# EXAMPLES:
#   docker run liquibase
#     → Runs: liquibase --help (ENTRYPOINT + CMD)
#
#   docker run liquibase update
#     → Runs: liquibase update (ENTRYPOINT + user arg, CMD ignored)
#
#   docker run liquibase --version
#     → Runs: liquibase --version (ENTRYPOINT + user arg)
#
# WHY THIS PATTERN?
#   - Container is purpose-built to run Liquibase
#   - Users can easily pass any Liquibase command/flags
#   - Default behavior shows help (user-friendly)
#
ENTRYPOINT ["liquibase"]
CMD ["--help"]

# ==============================================================================
# BUILD INSTRUCTIONS:
# ==============================================================================
# From /workspaces/dbtools/docker/liquibase directory:
#
#   docker build -t liquibase:5.0.1 .
#
# To customize versions:
#   docker build \
#     --build-arg LIQUIBASE_VERSION=5.0.2 \
#     --build-arg POSTGRES_DRIVER_VERSION=42.7.9 \
#     -t liquibase:custom .
#
# ==============================================================================
# RUN INSTRUCTIONS:
# ==============================================================================
# Show help:
#   docker run --rm liquibase
#
# Run Liquibase update (example):
#   docker run --rm \
#     -v ./changelogs:/liquibase \
#     liquibase \
#     --url=jdbc:postgresql://host.docker.internal:5432/mydb \
#     --username=user \
#     --password=pass \
#     --changelog-file=changelog.xml \
#     update
#
# Check Liquibase version:
#   docker run --rm liquibase --version
#
# ==============================================================================
# SUPPORTED DATABASES:
# ==============================================================================
# SQL Server:
#   --url=jdbc:sqlserver://host:1433;databaseName=mydb
#
# PostgreSQL:
#   --url=jdbc:postgresql://host:5432/mydb
#
# Snowflake:
#   --url=jdbc:snowflake://account.snowflakecomputing.com/?db=mydb
#
# MongoDB:
#   --url=jdbc:mongodb://host:27017/mydb
#
# ==============================================================================
