# SQL Server Docker Setup Guide

This guide provides step-by-step instructions for setting up Microsoft SQL Server in Docker with persistent storage, including integration with VS Code dev containers.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Directory Structure](#directory-structure)
- [Building the Docker Image](#building-the-docker-image)
- [Starting SQL Server](#starting-sql-server)
- [Connecting from Dev Container](#connecting-from-dev-container)
- [Connecting from WSL Host](#connecting-from-wsl-host)
- [VS Code Health Check Task](#vs-code-health-check-task)
- [Docker Commands Reference](#docker-commands-reference)
- [Troubleshooting](#troubleshooting)

## Overview

This setup creates a SQL Server 2022 Developer Edition instance with:

- Persistent data storage in `/data/mssql/mssql1`
- Persistent logs in `/logs/mssql`
- Port 1433 exposed for database connections
- Integration with VS Code dev containers
- Access from both dev container and WSL host

## Prerequisites

- Docker installed and running
- WSL2 (if on Windows)
- VS Code with Dev Containers extension (for dev container setup)
- `/data` and `/logs` directory structure on your host system

## Directory Structure

Before starting, ensure these directories exist on your WSL host:

```bash
# Create the directory structure on WSL host
sudo mkdir -p /data/mssql/mssql1
sudo mkdir -p /logs/mssql

# Set ownership for SQL Server
# SQL Server runs as UID 10001
sudo chown -R 10001:0 /data/mssql
sudo chown -R 10001:0 /logs/mssql
```

The project structure looks like this:

```
/workspaces/dbtools/docker/mssql/
├── Dockerfile              # Defines the SQL Server image
├── docker-compose.yml      # Orchestrates the mssql1 container
└── SETUP_GUIDE.md         # This file
```

## Building the Docker Image

### Step 1: Navigate to the MSSQL directory

```bash
cd /workspaces/dbtools/docker/mssql
```

### Step 2: Build the Docker image

```bash
docker build -t gds-mssql:latest .
```

**What this does:**

- `-t gds-mssql:latest` - Tags the image as `gds-mssql` with version `latest`
- `.` - Uses the current directory as build context (where Dockerfile is located)

**Expected output:**

```
[+] Building 45.2s (7/7) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.23kB
 => [internal] load .dockerignore
 => [1/2] FROM mcr.microsoft.com/mssql/server:2022-latest
 => [2/2] RUN mkdir -p /data/mssql /logs/mssql && chown -R mssql:0 /data /logs
 => exporting to image
 => => naming to docker.io/library/gds-mssql:latest
```

### Step 3: Verify the image was created

```bash
docker images | grep gds-mssql
```

**Expected output:**

```
gds-mssql    latest    abc123def456    2 minutes ago    2.15GB
```

## Starting SQL Server

### Step 1: Set the SA Password

**IMPORTANT:** The `MSSQL_SA_PASSWORD` environment variable must be set before starting the container. There is no default password for security reasons.

**Option A: Use the password prompt script (Recommended)**

```bash
# From the workspace root
. scripts/prompt_mssql_password.sh
```

This script will:

- Prompt you to enter the password twice for confirmation
- Validate password strength (minimum 8 characters, complexity requirements)
- Export `MSSQL_SA_PASSWORD` to your current shell session
- Optionally save it to `~/.bashrc` for future sessions

**Option B: Set manually**

```bash
export MSSQL_SA_PASSWORD='YourStrong@Passw0rd123'
```

**Password Requirements:**

- At least 8 characters long
- Contains uppercase letters
- Contains lowercase letters
- Contains numbers
- Contains special characters (@, !, #, $, etc.)

**Verify the password is set:**

```bash
echo $MSSQL_SA_PASSWORD
```

### Step 2: Start the Container

### Method 1: Using Docker Compose (Recommended)

```bash
# From /workspaces/dbtools/docker/mssql directory
docker-compose up -d
```

**What this does:**

- `up` - Creates and starts the container
- `-d` - Runs in detached mode (background)

**Expected output:**

```
[+] Running 2/2
 ✔ Network mssql_mssql-network  Created
 ✔ Container mssql1             Started
```

### Method 2: Using Docker Run (Manual)

```bash
docker run -d \
  --name mssql1 \
  -e ACCEPT_EULA=Y \
  -e MSSQL_PID=Developer \
  -e MSSQL_SA_PASSWORD="${MSSQL_SA_PASSWORD}" \
  -p 1433:1433 \
  -v /data/mssql:/data/mssql \
  -v /logs/mssql:/logs/mssql \
  -v /data/mssql/mssql1:/var/opt/mssql \
  --restart unless-stopped \
  gds-mssql:latest
```

**Note:** Make sure `MSSQL_SA_PASSWORD` is set in your environment before running this command.

### Step 3: Verify the container is running

```bash
docker ps --filter name=mssql1
```

**Expected output:**

```
CONTAINER ID   IMAGE                COMMAND                  CREATED          STATUS          PORTS                    NAMES
abc123def456   gds-mssql:latest     "/opt/mssql/bin/perm…"   10 seconds ago   Up 9 seconds    0.0.0.0:1433->1433/tcp   mssql1
```

### Step 4: Check container logs

```bash
docker logs mssql1
```

**Look for these success messages:**

```
SQL Server 2022 will run as non-root by default.
This container is running as user mssql.
Your master database file is owned by mssql.
...
SQL Server is now ready for client connections.
```

**If you see an error about missing `MSSQL_SA_PASSWORD`:**

```
ERROR: The variable MSSQL_SA_PASSWORD is not set. Defaulting to a blank string.
```

This means you forgot to set the password. Stop the container, set the password, and restart:

```bash
docker-compose down
export MSSQL_SA_PASSWORD='YourStrong@Passw0rd123'
docker-compose up -d
```

## Connecting from Dev Container

### Prerequisites

The dev container must have SQL Server tools installed (already configured in this project).

### Step 1: Open a terminal in VS Code (inside dev container)

Press `` Ctrl+` `` or go to Terminal → New Terminal

### Step 2: Connect using sqlcmd

```bash
sqlcmd -C -S localhost -U SA -P "$MSSQL_SA_PASSWORD"
```

**Parameter explanation:**

- `-C` - Trust server certificate (required for SQL Server 2022)
- `-S localhost` - Server address (container accessible via localhost)
- `-U SA` - Username (System Administrator)
- `-P "$MSSQL_SA_PASSWORD"` - Password from environment variable

### Step 3: Test the connection

Once connected, you'll see the `1>` prompt. Try these commands:

```sql
-- Check server name and time
SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime;
GO

-- List databases
SELECT name FROM sys.databases;
GO

-- Exit
QUIT
```

## Connecting from WSL Host

To connect from WSL (outside the dev container), you need:

1. SQL Server tools installed on WSL host
2. Dev container configured to publish port 1433

### Step 1: Install SQL Server tools on WSL host

Open a WSL terminal (not in VS Code) and run:

```bash
# Add Microsoft repository
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc

# Add package source (adjust for your Ubuntu version)
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Update package list
sudo apt-get update

# Install SQL Server tools (accept EULA when prompted)
sudo ACCEPT_EULA=Y apt-get install -y mssql-tools18

# Add to PATH (add this to ~/.bashrc for persistence)
export PATH="$PATH:/opt/mssql-tools18/bin"
```

### Step 2: Configure dev container port publishing

The dev container must publish port 1433 to the WSL host. This is configured in `.devcontainer/devcontainer.json`:

```jsonc
"runArgs": [
  "--env",
  "PYTHONUNBUFFERED=1",
  "--mount",
  "type=volume,source=vscode-server-cache,target=/home/gds/.vscode-server,consistency=cached",
  "-p",
  "1433:1433"  // This publishes SQL Server port
],
```

**After modifying devcontainer.json:**

1. Press `F1` or `Ctrl+Shift+P`
2. Type "Dev Containers: Rebuild Container"
3. Wait for rebuild to complete

### Step 3: Connect from WSL host

From a WSL terminal (outside VS Code):

```bash
sqlcmd -C -S localhost,1433 -U SA -P 'YourStrong!Passw0rd'
```

**Connection flow:**

```
WSL Host → Port 1433
    ↓
Dev Container → Port 1433 (via runArgs -p 1433:1433)
    ↓
mssql1 Container → Port 1433 (via docker-compose ports: "1433:1433")
    ↓
SQL Server Process
```

## VS Code Health Check Task

A VS Code task is configured to quickly check SQL Server health.

### Task Configuration

The task is defined in `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "MSSQL: Health Check",
      "type": "shell",
      "command": "docker",
      "args": [
        "exec",
        "mssql1",
        "bash",
        "-lc",
        "/opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P \"$MSSQL_SA_PASSWORD\" -Q \"SELECT @@SERVERNAME AS ServerName, GETDATE() AS CurrentTime, DB_NAME() AS CurrentDB;\" -W -s \",\""
      ],
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      },
      "problemMatcher": []
    }
  ]
}
```

### Running the Health Check

**Method 1: Command Palette**

1. Press `F1` or `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "MSSQL: Health Check"

**Method 2: Terminal Menu**

1. Go to Terminal → Run Task
2. Select "MSSQL: Health Check"

**Expected output:**

```
ServerName,CurrentTime,CurrentDB
abc123def456,2025-11-11 14:23:45.123,master
```

## Docker Commands Reference

### Container Management

```bash
# Start the mssql1 container
docker-compose up -d

# Stop the mssql1 container
docker-compose down

# Restart the container
docker restart mssql1

# View container status
docker ps --filter name=mssql1

# View container logs
docker logs mssql1

# Follow logs in real-time
docker logs -f mssql1

# View last 50 log lines
docker logs --tail 50 mssql1
```

### Interactive Access

```bash
# Execute sqlcmd interactively inside the container
docker exec -it mssql1 bash -lc '/opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P "$MSSQL_SA_PASSWORD"'

# Get a bash shell inside the container
docker exec -it mssql1 bash

# Run a one-off SQL query
docker exec mssql1 bash -lc '/opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P "$MSSQL_SA_PASSWORD" -Q "SELECT @@VERSION;"'
```

### Inspection and Debugging

```bash
# Inspect container configuration
docker inspect mssql1

# Check port mappings
docker port mssql1

# View container resource usage
docker stats mssql1

# List volumes used by container
docker inspect -f '{{ range .Mounts }}{{ .Source }} -> {{ .Destination }}{{ println }}{{ end }}' mssql1
```

### Image Management

```bash
# List SQL Server images
docker images | grep mssql

# Remove the custom image (container must be stopped first)
docker rmi gds-mssql:latest

# Rebuild the image
docker build -t gds-mssql:latest .

# Pull latest official SQL Server image
docker pull mcr.microsoft.com/mssql/server:2022-latest
```

### Data and Cleanup

```bash
# Stop and remove container (data persists in /data and /logs volumes)
docker-compose down

# Stop and remove container with volumes (DELETES ALL DATA!)
docker-compose down -v

# View disk usage by container
docker system df

# Clean up unused Docker resources
docker system prune
```

## Troubleshooting

### Container won't start

**Check logs:**

```bash
docker logs mssql1
```

**Common issues:**

- **Permission denied on /.system**: Ensure `/data/mssql/mssql1` is owned by UID 10001

  ```bash
  sudo chown -R 10001:0 /data/mssql/mssql1
  ```

- **Password doesn't meet requirements**: SA password must be at least 8 characters with uppercase, lowercase, numbers, and special characters

### Can't connect from dev container

**Verify container is running:**

```bash
docker ps --filter name=mssql1
```

**Test from inside container:**

```bash
docker exec mssql1 bash -lc '/opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P "$MSSQL_SA_PASSWORD" -Q "SELECT 1;"'
```

**Check if sqlcmd is in PATH:**

```bash
which sqlcmd
```

Expected: `/opt/mssql-tools18/bin/sqlcmd`

### Can't connect from WSL host

**Verify dev container is publishing port:**

```bash
# From WSL, check if dev container exists
docker ps | grep devcontainer

# Check if port 1433 is listening on WSL host
netstat -tuln | grep 1433
```

**Verify port forwarding in devcontainer.json:**
Check that `runArgs` includes `-p 1433:1433`

**Rebuild dev container** if you modified devcontainer.json

### Port 1433 already in use

```bash
# Find what's using port 1433
sudo lsof -i :1433

# Or on some systems
sudo netstat -tulnp | grep 1433
```

**Solution:** Stop the other service or change the port in docker-compose.yml:

```yaml
ports:
  - "1434:1433"  # Map host port 1434 to container port 1433
```

### Data not persisting

**Verify volume mounts:**

```bash
docker inspect mssql1 | grep -A 10 Mounts
```

**Check directory ownership:**

```bash
ls -ld /data/mssql/mssql1
```

Should show: `drwxr-xr-x 10001 root`

### Container keeps restarting

```bash
# Check restart policy
docker inspect --format='{{.HostConfig.RestartPolicy.Name}}' mssql1

# View recent container events
docker events --filter container=mssql1 --since 1h
```

## Additional Resources

- [SQL Server on Docker - Official Documentation](https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker)
- [SQL Server Environment Variables](https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-configure-environment-variables)
- [sqlcmd Utility Reference](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)

## Security Notes

⚠️ **Important Security Considerations:**

1. **Default Password**: The default password `YourStrong!Passw0rd` is for development only. Change it for production:

   ```bash
   export MSSQL_SA_PASSWORD='YourProductionPassword123!'
   docker-compose up -d
   ```

2. **Environment Variables**: Never commit `.env` files with passwords to version control

3. **Network Exposure**: The current setup exposes port 1433 to localhost only. For remote access, configure firewall rules carefully

4. **SSL/TLS**: The `-C` flag bypasses certificate validation. For production, use proper certificates

5. **SA Account**: Create dedicated login accounts instead of using SA for applications
