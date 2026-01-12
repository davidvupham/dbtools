# ==============================================================================
# Apache Kafka Docker Image with Persistent Storage
# ==============================================================================
#
# PURPOSE:
# This Dockerfile creates a customized Apache Kafka image with support for
# persistent storage volumes and proper configuration for development use.
#
# LEARNING OBJECTIVES FOR BEGINNERS:
# 1. How to extend official Confluent Kafka images
# 2. User and permission management in containers
# 3. Volume configuration for data persistence
# 4. Environment variable usage for Kafka configuration
# 5. Multi-stage permission handling (root vs. application user)
# 6. Understanding Kafka's relationship with Zookeeper/KRaft
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
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/ -t kafka:latest .
#       (requires ~/.docker/config.json configured with JFrog token via: docker login xyz.jfrog.io)
#     podman build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/ -t kafka:latest --format docker .
#       (requires authentication via: podman login xyz.jfrog.io)
#
#   Default (Docker Hub):
#     docker build -t kafka:latest .
#
# NOTE: The trailing slash is required in the prefix!
#
ARG REGISTRY_PREFIX=docker.io/
# ------------------------------------------------------------------------------
# Base Image Selection
# ------------------------------------------------------------------------------
# FROM: Specifies the base image to build upon
# - We use Confluent's official Kafka image (community version)
# - Confluent provides well-maintained, production-ready Kafka images
# - Version 7.6.0 includes Kafka 3.6.x with KRaft support
#
# WHAT YOU GET:
# - Apache Kafka broker with all core features
# - Java Runtime Environment (JRE) pre-installed
# - Kafka tools (kafka-topics, kafka-console-producer, etc.)
# - Confluent utilities and configurations
# - User 'appuser' (UID 1000) for running Kafka
#
FROM ${REGISTRY_PREFIX}confluentinc/cp-kafka:7.6.0

# ------------------------------------------------------------------------------
# Environment Variables - Kafka Core Configuration
# ------------------------------------------------------------------------------
# ENV: Sets environment variables that persist in the container
# These can be overridden when starting the container
#
# KAFKA_BROKER_ID=1:
#   - Unique identifier for this Kafka broker
#   - Required in multi-broker clusters
#   - Each broker must have a different ID
#
# KAFKA_LISTENERS:
#   - Defines the addresses Kafka listens on
#   - Format: <protocol>://<host>:<port>
#   - PLAINTEXT = No encryption (for development)
#   - 0.0.0.0:9092 = Listen on all network interfaces
#
# KAFKA_ADVERTISED_LISTENERS:
#   - Address that clients use to connect
#   - Must be reachable from client machines
#   - PLAINTEXT://localhost:9092 = Clients connect to localhost:9092
#   - Change this if connecting from outside the container
#
# KAFKA_LISTENER_SECURITY_PROTOCOL_MAP:
#   - Maps listener names to security protocols
#   - PLAINTEXT:PLAINTEXT = No encryption for PLAINTEXT listener
#   - For production, consider SASL_SSL or SSL protocols
#
# KAFKA_INTER_BROKER_LISTENER_NAME:
#   - Protocol used for broker-to-broker communication
#   - Should match one of the defined listeners
#   - PLAINTEXT = No encryption between brokers (dev only)
#
ENV KAFKA_BROKER_ID=1 \
    KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092 \
    KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
    KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT \
    KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT

# ------------------------------------------------------------------------------
# Environment Variables - Zookeeper/KRaft Configuration
# ------------------------------------------------------------------------------
# KAFKA_ZOOKEEPER_CONNECT:
#   - Address of Zookeeper ensemble (legacy mode)
#   - Format: <host>:<port>
#   - zookeeper:2181 = Connects to Zookeeper container
#   - NOTE: Kafka is transitioning to KRaft (Kafka Raft) mode
#   - This variable is used when running with Zookeeper
#
# WHY ZOOKEEPER:
#   - Historically, Kafka used Zookeeper for:
#     * Cluster coordination and metadata management
#     * Leader election for partitions
#     * Configuration management
#   - KRaft mode (introduced in Kafka 2.8) removes Zookeeper dependency
#   - Many production systems still use Zookeeper mode
#
ENV KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181

# ------------------------------------------------------------------------------
# Environment Variables - Topic and Log Configuration
# ------------------------------------------------------------------------------
# KAFKA_AUTO_CREATE_TOPICS_ENABLE:
#   - Automatically creates topics when producers send messages
#   - true = Convenient for development
#   - false = Better for production (explicit topic creation)
#
# KAFKA_DELETE_TOPIC_ENABLE:
#   - Allows deletion of topics
#   - true = Topics can be deleted via admin commands
#   - false = Topics cannot be deleted (safety measure)
#
# KAFKA_LOG_DIRS:
#   - Directory where Kafka stores log segments (message data)
#   - /data/kafka/logs = Custom path we'll create
#   - Each partition's data is stored in subdirectories
#   - This is mapped to persistent storage
#
# KAFKA_LOG_RETENTION_HOURS:
#   - How long to keep messages before deletion
#   - 168 hours = 7 days
#   - After this, old log segments are deleted
#   - Can also use log.retention.bytes for size-based retention
#
# KAFKA_LOG_SEGMENT_BYTES:
#   - Maximum size of a single log segment file
#   - 1073741824 bytes = 1 GB
#   - When segment reaches this size, Kafka creates a new one
#   - Smaller segments = more frequent rotation, faster deletions
#
ENV KAFKA_AUTO_CREATE_TOPICS_ENABLE=true \
    KAFKA_DELETE_TOPIC_ENABLE=true \
    KAFKA_LOG_DIRS=/data/kafka/logs \
    KAFKA_LOG_RETENTION_HOURS=168 \
    KAFKA_LOG_SEGMENT_BYTES=1073741824

# ------------------------------------------------------------------------------
# Environment Variables - Replication and Performance
# ------------------------------------------------------------------------------
# KAFKA_DEFAULT_REPLICATION_FACTOR:
#   - Default number of replicas for each partition
#   - 1 = No replication (single broker, development only)
#   - 3 = Recommended for production (survives 2 broker failures)
#
# KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR:
#   - Replication factor for __consumer_offsets topic
#   - Stores consumer group offsets
#   - 1 = Single broker setup (development)
#
# KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR:
#   - Replication for transaction state log
#   - Used by transactional producers
#   - 1 = Single broker setup
#
# KAFKA_TRANSACTION_STATE_LOG_MIN_ISR:
#   - Minimum In-Sync Replicas for transaction log
#   - 1 = At least 1 replica must be in sync
#   - Lower than replication factor allows progress during failures
#
# KAFKA_NUM_PARTITIONS:
#   - Default number of partitions for new topics
#   - 3 = Good starting point for parallelism
#   - More partitions = more parallelism but more overhead
#
ENV KAFKA_DEFAULT_REPLICATION_FACTOR=1 \
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
    KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1 \
    KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1 \
    KAFKA_NUM_PARTITIONS=3

# ------------------------------------------------------------------------------
# User Context Switch: root
# ------------------------------------------------------------------------------
# USER root:
#   - Switches to root user for administrative tasks
#   - Required for: creating directories, changing ownership
#   - The base image runs as 'appuser', so we temporarily elevate privileges
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
# mkdir -p /data/kafka/logs /logs/kafka:
#   - Creates directories for persistent storage
#   - -p flag creates parent directories if they don't exist
#   - /data/kafka/logs = Kafka log segments (message data, partitions)
#   - /logs/kafka = Kafka server logs (operational logs, errors)
#
# chown -R appuser:appuser /data /logs:
#   - Changes ownership recursively (-R)
#   - appuser = user that runs Kafka (UID 1000 in base image)
#   - First appuser = user, second appuser = group
#   - WHY: Kafka runs as 'appuser' and needs write access
#
# chmod -R 755 /data /logs:
#   - Changes permissions recursively
#   - 755 = rwxr-xr-x (owner: read/write/execute, others: read/execute)
#   - Owner (appuser) has full access
#   - Group and others can read and list directories
#
RUN mkdir -p /data/kafka/logs /logs/kafka && \
    chown -R appuser:appuser /data /logs && \
    chmod -R 755 /data /logs

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
#   - Example: /data/kafka on host → /data/kafka in container
#
# DATA STORED HERE:
#   - /data/kafka/logs: Topic partitions, log segments, index files
#   - /logs/kafka: Server logs, controller logs, state-change logs
#
# WHY PERSISTENT STORAGE:
#   - Prevents data loss when container restarts
#   - Allows inspection of Kafka state and logs
#   - Enables backup and recovery procedures
#
VOLUME ["/data/kafka/logs", "/logs/kafka"]

# ------------------------------------------------------------------------------
# Port Exposure
# ------------------------------------------------------------------------------
# EXPOSE: Documents which ports the container listens on
#
# PORT 9092:
#   - Default Kafka broker port for client connections
#   - Used by producers, consumers, and admin clients
#   - This doesn't actually publish the port (that's done at runtime)
#   - Think of it as documentation for users of this image
#
# TO ACCESS FROM OUTSIDE:
#   - Use -p flag with docker run: -p 9092:9092
#   - Or use ports section in docker-compose.yml
#   - Format: <host-port>:<container-port>
#
# ADDITIONAL PORTS (not exposed by default):
#   - 9093: Often used for inter-broker communication
#   - 9094: Often used for external/public access
#   - 9021: Confluent Control Center (if used)
#
EXPOSE 9092

# ------------------------------------------------------------------------------
# User Context Switch: Application User
# ------------------------------------------------------------------------------
# USER appuser:
#   - Switches from root back to 'appuser' user
#   - Kafka will run as this non-privileged user
#
# SECURITY BEST PRACTICE:
#   - Never run applications as root in production
#   - Limits damage if container is compromised
#   - 'appuser' (UID 1000) has only necessary permissions
#   - Can write to /data and /logs directories (we set ownership above)
#   - Cannot modify system files or other users' data
#
USER appuser

# ------------------------------------------------------------------------------
# Container Startup Command
# ------------------------------------------------------------------------------
# CMD: Specifies the default command to run when container starts
#
# /etc/confluent/docker/run:
#   - Confluent's entrypoint script for Kafka
#   - Handles configuration file generation
#   - Starts Kafka broker in foreground
#   - Processes environment variables into server.properties
#
# WHAT IT DOES:
#   1. Validates required environment variables
#   2. Generates server.properties from env vars
#   3. Starts Kafka broker (kafka-server-start)
#   4. Monitors the process
#
# CONTAINER LIFECYCLE:
#   - When Kafka process stops, the container stops
#   - Docker monitors this process for health
#   - Logs go to stdout/stderr (visible via 'docker logs')
#
# CAN BE OVERRIDDEN:
#   - docker run <image> /bin/bash (overrides CMD)
#   - Useful for debugging or running Kafka tools manually
#
CMD ["/etc/confluent/docker/run"]

# ==============================================================================
# BUILD INSTRUCTIONS:
# ==============================================================================
# From /workspaces/dbtools/docker/kafka directory:
#
#   docker build -t gds-kafka:latest .
#
# EXPLANATION:
#   - docker build: Build an image from this Dockerfile
#   - -t gds-kafka:latest: Tag the image with name:version
#   - .: Use current directory as build context
#
# ==============================================================================
# RUN INSTRUCTIONS:
# ==============================================================================
# See docker-compose.yml or use:
#
#   docker run -d \
#     --name kafka1 \
#     -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
#     -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
#     -p 9092:9092 \
#     -v /data/kafka:/data/kafka \
#     -v /logs/kafka:/logs/kafka \
#     gds-kafka:latest
#
# NOTE: Kafka requires Zookeeper (or KRaft mode). See docker-compose.yml
#       for complete setup with both Kafka and Zookeeper.
#
# ==============================================================================
