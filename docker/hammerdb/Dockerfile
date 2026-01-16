# HammerDB Benchmark Container
# Based on official HammerDB releases

# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
# REGISTRY_PREFIX: Allows the base image to be pulled from a corporate proxy
#                  (e.g., JFrog Artifactory).
#
# USAGE:
#   Corporate proxy:
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ -t hammerdb:latest .
#       (requires ~/.docker/config.json configured with JFrog token via: docker login xyz.jfrog.io)
#     podman build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/library/ -t hammerdb:latest --format docker .
#       (requires authentication via: podman login xyz.jfrog.io)
#
#   Default (Docker Hub):
#     docker build -t hammerdb:latest .
#
# NOTE: The trailing slash is required in the prefix!
#
ARG REGISTRY_PREFIX=docker.io/library/
FROM ${REGISTRY_PREFIX}ubuntu:22.04

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# HammerDB version
ARG HAMMERDB_VERSION=4.10

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    tcl \
    tcllib \
    libpq5 \
    unixodbc \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Download and install HammerDB
WORKDIR /opt
RUN wget -q https://github.com/TPC-Council/HammerDB/releases/download/v${HAMMERDB_VERSION}/HammerDB-${HAMMERDB_VERSION}-Linux.tar.gz \
    && tar -xzf HammerDB-${HAMMERDB_VERSION}-Linux.tar.gz \
    && rm HammerDB-${HAMMERDB_VERSION}-Linux.tar.gz \
    && ln -s /opt/HammerDB-${HAMMERDB_VERSION} /opt/hammerdb

# Add HammerDB to PATH
ENV PATH="/opt/hammerdb:${PATH}"
ENV HAMMERDB_CLI_PATH="/opt/hammerdb/hammerdbcli"

# Install gds_benchmark and gds_hammerdb
WORKDIR /app
COPY python/gds_benchmark/ /app/gds_benchmark/
COPY python/gds_hammerdb/ /app/gds_hammerdb/

RUN pip3 install /app/gds_benchmark && \
    pip3 install /app/gds_hammerdb

# Set working directory for scripts
WORKDIR /benchmarks

# Default entrypoint runs hammerdbcli
ENTRYPOINT ["hammerdbcli"]
CMD ["--help"]
