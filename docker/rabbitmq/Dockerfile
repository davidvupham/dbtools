# ==============================================================================
# RabbitMQ Docker Image for Local Development & Testing
# ==============================================================================
#
# PURPOSE:
# This Dockerfile builds a RabbitMQ image tailored for local development. It
# layers explicit defaults, persistent storage locations, and clear documentation
# on top of the official RabbitMQ Management image so the broker is ready to use
# immediately after `docker compose up`.
#
# WHO IS THIS FOR?
# - Developers who want a predictable RabbitMQ instance with the management UI
# - Learners seeking to understand each Docker instruction in a practical setup
# - Teams standardising broker configuration across environments
#
# WHAT YOU GET:
# - RabbitMQ 3.13 with the management plugin enabled
# - Opinionated defaults for username, password, and virtual host
# - Persistent data and log directories mapped to host volumes
# - Comprehensive inline comments explaining every build step
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Base Image: rabbitmq:3.13-management
# ------------------------------------------------------------------------------
# FROM defines the starting point for our image. We choose the official RabbitMQ
# image that includes the management plugin so the web UI and HTTP API are
# available out-of-the-box. Version 3.13 is the current LTS stream, delivering
# the latest feature set and security updates.
FROM rabbitmq:3.13-management

# ------------------------------------------------------------------------------
# Environment Defaults for Development
# ------------------------------------------------------------------------------
# ENV sets key/value pairs baked into the image. They can be overridden at
# runtime via `docker run -e` or the `environment:` section in Compose.
# - RABBITMQ_DEFAULT_USER / RABBITMQ_DEFAULT_PASS create a bootstrap account.
#   These defaults are intentionally simple for local dev; change them before
#   exposing the broker beyond localhost.
# - RABBITMQ_DEFAULT_VHOST seeds the broker with a vhost so client libraries can
#   connect without additional provisioning steps.
# - RABBITMQ_NODE_PORT and RABBITMQ_DIST_PORT define the main AMQP port and the
#   Erlang distribution port respectively. We keep the defaults but document
#   them for visibility.
ENV RABBITMQ_DEFAULT_USER=devuser \
    RABBITMQ_DEFAULT_PASS=devpassword \
    RABBITMQ_DEFAULT_VHOST=/ \
    RABBITMQ_NODE_PORT=5672 \
    RABBITMQ_DIST_PORT=25672

# ------------------------------------------------------------------------------
# Switch to root for filesystem preparation
# ------------------------------------------------------------------------------
# USER changes the active user for subsequent RUN/COPY commands. The base image
# runs as the non-root `rabbitmq` user by default. We temporarily escalate to
# `root` so we can create host-mounted directories and adjust ownership.
USER root

# ------------------------------------------------------------------------------
# Prepare Host-Mount Friendly Directories
# ------------------------------------------------------------------------------
# RUN executes shell commands during the image build. Each RUN creates a new
# immutable image layer. Here we:
# 1. Create /data/rabbitmq and /logs/rabbitmq as parent directories for bind
#    mounts. (RabbitMQ stores runtime data in /var/lib/rabbitmq and logs in
#    /var/log/rabbitmq; we'll symlink into these later.)
# 2. Create the actual RabbitMQ data/log directories if they don't exist.
# 3. Align ownership with the `rabbitmq` user so the broker can write to them.
RUN set -eux; \
    mkdir -p /data/rabbitmq /logs/rabbitmq; \
    mkdir -p /var/lib/rabbitmq /var/log/rabbitmq; \
    chown -R rabbitmq:rabbitmq /data/rabbitmq /logs/rabbitmq /var/lib/rabbitmq /var/log/rabbitmq

# ------------------------------------------------------------------------------
# Symlink Host Paths into RabbitMQ Defaults
# ------------------------------------------------------------------------------
# Many teams prefer mounting host directories under /data and /logs for
# consistency across services. To honour that convention while still letting
# RabbitMQ use its standard locations, we create symbolic links:
# - /var/lib/rabbitmq -> /data/rabbitmq
# - /var/log/rabbitmq -> /logs/rabbitmq
# This allows bind mounts to target /data/* while RabbitMQ keeps its defaults.
RUN set -eux; \
    rm -rf /var/lib/rabbitmq; \
    ln -s /data/rabbitmq /var/lib/rabbitmq; \
    rm -rf /var/log/rabbitmq; \
    ln -s /logs/rabbitmq /var/log/rabbitmq

# ------------------------------------------------------------------------------
# Declare Persistent Volumes
# ------------------------------------------------------------------------------
# VOLUME tells Docker which paths contain mutable state that should persist
# outside the container lifecycle. When using Docker Compose we will bind these
# to host directories so messages, queues, and logs survive restarts.
VOLUME ["/data/rabbitmq", "/logs/rabbitmq"]

# ------------------------------------------------------------------------------
# Expose Ports for Clients and Tooling
# ------------------------------------------------------------------------------
# EXPOSE documents which ports the container listens on:
# - 5672: AMQP 0-9-1 and AMQP 1.0 client connections
# - 15672: HTTP management UI & REST API
# - 15692: Prometheus metrics endpoint (enabled by management build)
# - 4369: Erlang Port Mapper Daemon (epmd) for clustering discovery
# - 25672: Inter-node communication (Erlang distribution)
# Publishing these ports remains the caller's responsibility via `docker run -p`
# or Compose's `ports:` section.
EXPOSE 5672 15672 15692 4369 25672

# ------------------------------------------------------------------------------
# Drop Privileges for Runtime
# ------------------------------------------------------------------------------
# USER switches us back to the `rabbitmq` user so the broker runs with the
# least privileges necessary. This is a standard container security practice.
USER rabbitmq

# ------------------------------------------------------------------------------
# Entrypoint & CMD
# ------------------------------------------------------------------------------
# We intentionally do not override the base image's entrypoint or CMD. The
# official image already ships with a robust startup script that enables
# plugins, applies environment overrides, and launches the Erlang VM in the
# foreground. Leaving it untouched keeps maintenance simple.

# ==============================================================================
# BUILDING THIS IMAGE:
#   docker build -t gds-rabbitmq:latest .
#
# RUNTIME OVERRIDES (examples):
#   docker run -e RABBITMQ_DEFAULT_USER=myuser -e RABBITMQ_DEFAULT_PASS=mypassword ...
# ==============================================================================
