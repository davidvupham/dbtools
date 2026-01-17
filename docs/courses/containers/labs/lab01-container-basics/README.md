# Lab 01: Container Basics

> **Level:** Beginner | **Time:** 45-60 minutes | **Prerequisites:** Docker or Podman installed

## Lab Overview

In this lab, you will practice fundamental container operations including running containers, managing container lifecycle, and working with container data.

---

## Learning Objectives

By completing this lab, you will be able to:

- Run containers in interactive and detached modes
- Manage container lifecycle (start, stop, restart, remove)
- Execute commands inside running containers
- View container logs and inspect container details
- Understand container isolation

---

## Prerequisites

- Docker or Podman installed and running
- Terminal access
- Internet connection (for pulling images)

Verify your setup:

```bash
# Docker
docker version
docker run hello-world

# Podman
podman version
podman run hello-world
```

---

## Part 1: Running Containers

### Task 1.1: Run Your First Container

Run the official nginx web server:

```bash
docker run nginx
```

**Observe:** The container runs in the foreground and you see nginx logs. Press `Ctrl+C` to stop.

### Task 1.2: Run in Detached Mode

Run nginx in the background:

```bash
docker run -d --name webserver nginx
```

Verify it's running:

```bash
docker ps
```

### Task 1.3: Interactive Container

Run Ubuntu interactively:

```bash
docker run -it --name myubuntu ubuntu bash
```

Inside the container:

```bash
# Check the OS
cat /etc/os-release

# Check the hostname
hostname

# Check network configuration
ip addr

# Check processes
ps aux

# Exit
exit
```

### Task 1.4: Run with Port Publishing

Run nginx with port publishing:

```bash
docker run -d --name web-public -p 8080:80 nginx
```

Access the web server:

```bash
curl http://localhost:8080
# Or open http://localhost:8080 in your browser
```

---

## Part 2: Container Management

### Task 2.1: List Containers

```bash
# Show running containers
docker ps

# Show all containers (including stopped)
docker ps -a

# Show only container IDs
docker ps -aq
```

### Task 2.2: Start and Stop Containers

```bash
# Stop a running container
docker stop webserver

# Verify it stopped
docker ps -a | grep webserver

# Start the container again
docker start webserver

# Verify it's running
docker ps
```

### Task 2.3: Restart Containers

```bash
# Restart a container
docker restart webserver

# Check uptime
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Task 2.4: Remove Containers

```bash
# Remove a stopped container
docker rm myubuntu

# Force remove a running container
docker rm -f webserver

# Remove all stopped containers
docker container prune -f
```

---

## Part 3: Executing Commands

### Task 3.1: Run Commands in Container

Start a new nginx container:

```bash
docker run -d --name mynginx nginx
```

Run commands inside it:

```bash
# View nginx configuration
docker exec mynginx cat /etc/nginx/nginx.conf

# Check running processes
docker exec mynginx ps aux

# Check nginx version
docker exec mynginx nginx -v
```

### Task 3.2: Interactive Shell in Running Container

```bash
# Get a shell in the container
docker exec -it mynginx bash

# Inside the container:
ls -la /usr/share/nginx/html/
cat /usr/share/nginx/html/index.html
exit
```

### Task 3.3: Run as Different User

```bash
# Run as root explicitly
docker exec -u root mynginx whoami

# Check user ID
docker exec mynginx id
```

---

## Part 4: Logs and Inspection

### Task 4.1: View Container Logs

```bash
# Make some requests first
docker run -d --name logtest -p 8081:80 nginx
curl http://localhost:8081
curl http://localhost:8081/nonexistent

# View logs
docker logs logtest

# Follow logs in real-time
docker logs -f logtest
# Press Ctrl+C to stop following

# Show last 5 lines
docker logs --tail 5 logtest

# Show logs with timestamps
docker logs -t logtest
```

### Task 4.2: Inspect Container Details

```bash
# Full JSON inspection
docker inspect logtest

# Get specific fields
docker inspect --format '{{.State.Status}}' logtest
docker inspect --format '{{.NetworkSettings.IPAddress}}' logtest
docker inspect --format '{{.Config.Image}}' logtest
```

### Task 4.3: Monitor Resource Usage

```bash
# Real-time stats
docker stats logtest

# One-time snapshot
docker stats --no-stream logtest
# Press Ctrl+C to stop

# View processes
docker top logtest
```

---

## Part 5: Container Isolation

### Task 5.1: Filesystem Isolation

```bash
# Create a file inside a container
docker exec mynginx touch /tmp/test-file

# Verify it exists
docker exec mynginx ls /tmp/test-file

# Run a new container - file doesn't exist there
docker run --rm nginx ls /tmp/test-file
# Error: file not found
```

### Task 5.2: Process Isolation

```bash
# Check processes inside container
docker exec mynginx ps aux

# Container only sees its own processes
# PID 1 is the main process (nginx)
```

### Task 5.3: Network Isolation

```bash
# Container has its own network stack
docker exec mynginx ip addr

# Compare with host
ip addr
```

---

## Part 6: Challenge Exercises

### Challenge 1: Port Conflict Resolution

1. Run nginx on port 8080
2. Try to run another nginx on port 8080 (it will fail)
3. Find another available port and run the second nginx

### Challenge 2: Container Cleanup

1. Run 5 nginx containers with names web1 through web5
2. Stop all of them with a single command
3. Remove all of them with a single command

### Challenge 3: Log Analysis

1. Run nginx and generate some traffic
2. Find all 404 errors in the logs
3. Count the total number of requests

---

## Verification Checklist

- [ ] Successfully ran a container in detached mode
- [ ] Accessed a web server through published ports
- [ ] Executed commands inside a running container
- [ ] Viewed and followed container logs
- [ ] Inspected container configuration
- [ ] Demonstrated filesystem isolation between containers
- [ ] Removed containers properly

---

## Cleanup

```bash
# Stop all running containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -aq)

# Or use prune
docker container prune -f
```

---

## Solutions

See [solutions.md](solutions.md) for detailed solutions to all tasks and challenges.

---

## Next Lab

Continue to: [Lab 02: Building Images](../lab02-building-images/)
