# RabbitMQ Docker Setup Guide

This guide walks you through building and operating the custom RabbitMQ image located in `docker/rabbitmq`. Follow along to spin up a fully featured broker with persistent storage and the management UI enabled.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Directory Structure](#directory-structure)
- [Prepare Host Directories](#prepare-host-directories)
- [Build the Docker Image](#build-the-docker-image)
- [Start and Stop with Docker Compose](#start-and-stop-with-docker-compose)
- [Access the Management UI](#access-the-management-ui)
- [Verify the Broker](#verify-the-broker)
- [Customise Credentials and VHosts](#customise-credentials-and-vhosts)
- [Log Files and Data Persistence](#log-files-and-data-persistence)
- [Troubleshooting](#troubleshooting)
- [Reference Commands](#reference-commands)

## Overview

The RabbitMQ setup delivers:

- RabbitMQ 3.13 with the management plugin (HTTP UI, REST API, Prometheus metrics)
- Secure configuration requiring explicit credentials (no hardcoded defaults)
- Persistent data and log directories on the host (`/data/rabbitmq`, `/logs/rabbitmq`)
- Health checks and restart policy baked into Compose

## Prerequisites

- Docker Engine 24+ (Docker Desktop, Docker for Linux, or equivalent)
- Access to `/data` and `/logs` paths on the host (requires sudo the first time)
- Optional: VS Code Dev Containers if you want to manage containers from the dev container

## Directory Structure

```
/home/dpham/src/dbtools/docker/rabbitmq
├── Dockerfile             # Builds the customised RabbitMQ image
├── docker-compose.yml     # Orchestrates build/start/stop
└── rabbitmq-docker-setup.md
```

## Prepare Host Directories

Create folders for data and logs and grant ownership to the RabbitMQ UID (999 in the official image):

```bash
sudo mkdir -p /data/rabbitmq
sudo mkdir -p /logs/rabbitmq
sudo chown -R 999:999 /data/rabbitmq /logs/rabbitmq
sudo chmod -R 775 /data/rabbitmq /logs/rabbitmq
```

> Tip: Re-run the `chown` command whenever you clean the directories to avoid permission issues.

## Set RabbitMQ Credentials

**IMPORTANT:** You must set the RabbitMQ credentials as environment variables before starting the container. There are no default credentials for security reasons.

**Set the credentials:**

```bash
export RABBITMQ_DEFAULT_USER='your_admin_user'
export RABBITMQ_DEFAULT_PASS='YourStrong@Passw0rd123'
```

**Password Requirements:**

- At least 8 characters long
- Contains uppercase letters
- Contains lowercase letters
- Contains numbers
- Contains special characters

**Verify the credentials are set:**

```bash
echo $RABBITMQ_DEFAULT_USER
echo $RABBITMQ_DEFAULT_PASS
```

**Note:** These credentials will be used to create the RabbitMQ administrator account for accessing the Management UI and connecting clients.

## Build the Docker Image

1. Navigate to the RabbitMQ directory:

   ```bash
   cd /home/dpham/src/dbtools/docker/rabbitmq
   ```

2. Build the image:

   ```bash
   docker build -t gds-rabbitmq:latest .
   ```

   - `-t gds-rabbitmq:latest` tags the image for easy reuse.
   - `.` uses the current directory (where the Dockerfile lives) as build context.

3. Alternatively, use Docker Compose to build (recommended for consistency):

   ```bash
   docker compose build rabbitmq1
   ```

   - Reuses the settings defined in `docker-compose.yml`.
   - Ensures the exact same context is used for subsequent `docker compose up`.

4. Verify the image exists:

   ```bash
   docker images | grep gds-rabbitmq
   ```

## Run the Built Image and Confirm Health

After building, start the stack and wait for the health check to succeed:

```bash
docker compose up -d --wait
```

- `-d` runs the service in the background.
- `--wait` blocks until the RabbitMQ health check reports `healthy` (requires Docker Compose v2.20+).
- If your Compose version does not support `--wait`, run `docker compose up -d` followed by the commands in the next section.

You can inspect the health status at any time:

```bash
docker compose ps
docker inspect --format='{{.State.Health.Status}}' rabbitmq1
```

A status of `healthy` confirms both the image build and the container startup completed successfully.

## Start and Stop with Docker Compose

From `/home/dpham/src/dbtools/docker/rabbitmq`:

```bash
# Build image (if needed) and start container in the background
docker compose up -d

# Stop and remove the container (data persists on host)
docker compose down
```

What Compose does:

- Builds `gds-rabbitmq:latest` if it is missing or Dockerfile changed
- Starts the container named `rabbitmq1`
- Publishes ports `5672`, `15672`, `15692` to localhost
- Mounts `/data/rabbitmq` and `/logs/rabbitmq` into the container
- Applies a health check (`rabbitmq-diagnostics ping`)

### Restart policy

The compose file sets `restart: unless-stopped`, so RabbitMQ automatically restarts after crashes or host reboots unless you deliberately stop it with `docker compose down`.

## Access the Management UI

- URL: <http://localhost:15672>
- Username: The value you set for `RABBITMQ_DEFAULT_USER`
- Password: The value you set for `RABBITMQ_DEFAULT_PASS`

The UI provides queue management, message tracing, metrics, and plugin administration.

## Verify the Broker

Check container status and health:

```bash
docker compose ps
docker inspect --format='{{.State.Health.Status}}' rabbitmq1
```

If `docker compose up -d --wait` was used earlier, this status should already be `healthy`.

Publish a test message and consume it with `rabbitmqadmin` (installed inside the container):

```bash
docker exec -it rabbitmq1 rabbitmqadmin --username="$RABBITMQ_DEFAULT_USER" --password="$RABBITMQ_DEFAULT_PASS" declare queue name=test-queue durable=false
docker exec -it rabbitmq1 rabbitmqadmin --username="$RABBITMQ_DEFAULT_USER" --password="$RABBITMQ_DEFAULT_PASS" publish routing_key=test-queue payload="hello world"
docker exec -it rabbitmq1 rabbitmqadmin --username="$RABBITMQ_DEFAULT_USER" --password="$RABBITMQ_DEFAULT_PASS" get queue=test-queue requeue=false
```

Expected output shows the message payload in the `get` command response.

## Customise Credentials and VHosts

The credentials must be set before starting the container. You can also customize the virtual host:

```bash
export RABBITMQ_DEFAULT_USER=myuser
export RABBITMQ_DEFAULT_PASS=myS3cret!
export RABBITMQ_DEFAULT_VHOST=/development
docker compose up -d
```

You can also adjust ports or mount paths in `docker-compose.yml` to fit your environment.

## Log Files and Data Persistence

- Message store, queues, and runtime metadata live in `/data/rabbitmq` on the host.
- Broker logs (including startup diagnostics) land in `/logs/rabbitmq`.

Inspect logs without entering the container:

```bash
tail -f /logs/rabbitmq/rabbit@<hostname>.log
```

Or stream directly from Docker:

```bash
docker logs -f rabbitmq1
```

## Troubleshooting

| Symptom | Checks | Fix |
| ------- | ------ | --- |
| Container exits immediately | `docker logs rabbitmq1` | Ensure `/data/rabbitmq` and `/logs/rabbitmq` exist and are owned by UID 999 |
| Management UI inaccessible | `curl -I http://localhost:15672` | Confirm container is running; ensure no firewall blocks the port |
| Health check failing | `docker inspect rabbitmq1 --format '{{json .State.Health}}'` | Look at logs for Erlang crash reports; verify disk space on host |
| Password rejected | `docker inspect rabbitmq1 | grep RABBITMQ_DEFAULT_PASS` | Stop container, clear `/data/rabbitmq`, and restart to regenerate defaults |

## Reference Commands

```bash
# Start in foreground (useful for first run)
docker compose up

# Restart while preserving data
docker compose restart rabbitmq1

# Execute rabbitmqctl commands
docker exec -it rabbitmq1 rabbitmqctl status

# List queues via rabbitmqadmin
docker exec -it rabbitmq1 rabbitmqadmin --username="$RABBITMQ_DEFAULT_USER" --password="$RABBITMQ_DEFAULT_PASS" list queues

# Remove all persisted data (WARNING: deletes queues/messages)
sudo rm -rf /data/rabbitmq/* /logs/rabbitmq/*
```

Happy messaging!
