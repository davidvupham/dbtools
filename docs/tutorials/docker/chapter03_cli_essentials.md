# Chapter 3: CLI Essentials and First Run

## Introduction

The Docker command-line interface (CLI) is your primary tool for interacting with Docker. In this chapter, you'll learn the essential commands for working with images and containers, from pulling images to running containers, viewing logs, and managing their lifecycle.

**What you'll learn**:

- How to work with Docker images (pull, list, inspect)
- How to run containers in different modes
- How to manage container lifecycle (start, stop, restart, remove)
- How to view container logs and execute commands inside containers
- How to map ports and set environment variables
- Essential Docker CLI patterns and best practices

## Understanding the Docker CLI

The Docker CLI follows this general pattern:

```bash
docker [OBJECT] [COMMAND] [OPTIONS]
```

**Examples**:

- `docker container run` - Run a container
- `docker image ls` - List images
- `docker network create` - Create a network

**Shorthand forms** (older style, still widely used):

- `docker run` instead of `docker container run`
- `docker ps` instead of `docker container ls`
- `docker images` instead of `docker image ls`

Both styles work identically. We'll use the shorthand forms in this chapter since they're more common.

---

## Working with Images

Images are the templates from which containers are created. Before you can run a container, you need an image.

### Pulling Images from Registries

**Pull an image from Docker Hub**:

```bash
# Pull the latest version
docker pull alpine

# Pull a specific version (tag)
docker pull alpine:3.19

# Pull from a specific registry
docker pull ghcr.io/user/myapp:v1.0
```

**What happens when you pull**:

1. Docker checks if the image exists locally
2. If not, it contacts the registry (default: Docker Hub)
3. Downloads the image layers
4. Stores them in your local image cache

**Example with output**:

```bash
$ docker pull nginx:alpine
alpine: Pulling from library/nginx
31e352740f53: Pull complete
27e3b7dfbb8f: Pull complete
b92e8ea76b3c: Pull complete
8a3f7b21e48d: Pull complete
59b3c0c2d43b: Pull complete
e05c5f16f1ef: Pull complete
Digest: sha256:a64c79f...
Status: Downloaded newer image for nginx:alpine
docker.io/library/nginx:alpine
```

**Understanding the output**:

- Each line is a **layer** of the image
- Layers are cached (if you pull another image that shares layers, they're reused)
- **Digest**: Unique identifier for this exact image version

### Listing Images

**List all local images**:

```bash
docker images

# Or the modern syntax
docker image ls
```

**Example output**:

```
REPOSITORY    TAG       IMAGE ID       CREATED        SIZE
nginx         alpine    3b25b682ea82   2 weeks ago    41MB
postgres      15        e3d42db034a0   3 weeks ago    376MB
redis         alpine    f4e6aa3f7a7e   1 month ago    32MB
alpine        3.19      c1aabb73d233   2 months ago   7.3MB
alpine        latest    c1aabb73d233   2 months ago   7.3MB
```

**Column explanations**:

- **REPOSITORY**: Image name
- **TAG**: Version/variant (default: `latest`)
- **IMAGE ID**: Unique identifier (first 12 chars of full hash)
- **CREATED**: When the image was built
- **SIZE**: Disk space used

**Filtering and formatting**:

```bash
# Show only nginx images
docker images nginx

# Show image IDs only
docker images -q

# Filter by name pattern
docker images "nginx:*"

# Custom format
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Show dangling images (untagged, usually old layers)
docker images -f "dangling=true"
```

### Inspecting Images

**Get detailed information about an image**:

```bash
docker inspect nginx:alpine

# Or extract specific fields
docker inspect nginx:alpine --format '{{.Architecture}}'
docker inspect nginx:alpine --format '{{.Os}}'
docker inspect nginx:alpine --format '{{.Config.Env}}'
```

**View image history (layers)**:

```bash
docker history nginx:alpine
```

**Example output**:

```
IMAGE          CREATED        CREATED BY                                      SIZE
3b25b682ea82   2 weeks ago    /bin/sh -c #(nop)  CMD ["nginx" "-g" "daemon…   0B
<missing>      2 weeks ago    /bin/sh -c #(nop)  EXPOSE 80                    0B
<missing>      2 weeks ago    /bin/sh -c #(nop) COPY file:...                 1.96kB
<missing>      2 weeks ago    /bin/sh -c apk add --no-cache nginx             15.2MB
<missing>      2 weeks ago    /bin/sh -c #(nop)  CMD ["/bin/sh"]              0B
<missing>      2 weeks ago    /bin/sh -c #(nop) ADD file:...                  7.3MB
```

This shows every instruction that was used to build the image.

### Searching for Images

**Search Docker Hub for images**:

```bash
docker search postgres

# Limit results
docker search postgres --limit 5

# Filter official images only
docker search postgres --filter "is-official=true"
```

**Example output**:

```
NAME                DESCRIPTION                                     STARS     OFFICIAL
postgres            The PostgreSQL object-relational database       12000     [OK]
postgres-postgis    PostGIS spatial database extension              500
timescale/timescaledb  Time-series database built on PostgreSQL     300
```

---

## Running Containers

The `docker run` command is the heart of Docker. It creates and starts a container from an image.

### Basic Container Execution

**Run a simple command**:

```bash
# Run a command and exit
docker run alpine echo "Hello from Alpine!"

# Expected output:
# Hello from Alpine!
```

**What happened**:

1. Docker looked for `alpine:latest` image locally
2. Didn't find it, so pulled from Docker Hub
3. Created a container from the image
4. Ran the command `echo "Hello from Alpine!"`
5. Container exited when command finished

### Interactive Containers

**Run an interactive shell**:

```bash
# -i = interactive (keep STDIN open)
# -t = allocate a pseudo-TTY (terminal)
docker run -it alpine sh

# You're now inside the container!
/ # ls
bin    dev    etc    home   lib    media  mnt    opt    proc   root   run    sbin   srv    sys    tmp    usr    var

/ # whoami
root

/ # cat /etc/os-release
NAME="Alpine Linux"
ID=alpine
VERSION_ID=3.19.0
PRETTY_NAME="Alpine Linux v3.19"

/ # exit
```

**Key points**:

- You're root inside the container (but isolated from host)
- The filesystem is the container's filesystem, not your host
- Changes inside the container are lost when it's removed (unless you save them)

### Detached Containers (Background Mode)

**Run a container in the background**:

```bash
# -d = detached (run in background)
docker run -d --name my-nginx nginx:alpine

# Returns container ID:
# 5f8c9d2e3a1b...
```

**Verify it's running**:

```bash
docker ps

# Output:
# CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS     NAMES
# 5f8c9d2e3a1b   nginx:alpine   "/docker-entrypoint.…"   10 seconds ago  Up 9 seconds   80/tcp    my-nginx
```

### Port Mapping

Containers have their own network stack. To access services running inside containers, you need to map ports.

**Map container port to host port**:

```bash
# -p HOST_PORT:CONTAINER_PORT
docker run -d --name web -p 8080:80 nginx:alpine

# Now nginx (port 80 in container) is accessible on localhost:8080
```

**Test it**:

```bash
curl http://localhost:8080

# You should see the nginx welcome page HTML
```

**Multiple port mappings**:

```bash
docker run -d \
  --name multi-port \
  -p 8080:80 \
  -p 8443:443 \
  nginx:alpine
```

**Let Docker choose a random port**:

```bash
docker run -d -p 80 nginx:alpine

# Check which port was assigned
docker ps
# Look in the PORTS column: 0.0.0.0:55000->80/tcp
```

**Bind to specific interface**:

```bash
# Only accessible on localhost
docker run -d -p 127.0.0.1:8080:80 nginx:alpine

# Accessible on all interfaces (default)
docker run -d -p 0.0.0.0:8080:80 nginx:alpine
```

### Environment Variables

**Set environment variables**:

```bash
# -e KEY=VALUE
docker run -e MY_VAR="Hello" alpine env | grep MY_VAR

# Output:
# MY_VAR=Hello
```

**Multiple environment variables**:

```bash
docker run -d \
  --name db \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_DB=mydb \
  postgres:15
```

**Load from file**:

```bash
# Create .env file
cat > app.env << EOF
DATABASE_URL=postgres://localhost/mydb
API_KEY=abc123
DEBUG=true
EOF

# Use the file
docker run --env-file app.env alpine env
```

### Container Names

**Give containers memorable names**:

```bash
# Without --name, Docker assigns a random name
docker run -d nginx:alpine
# Name might be: "quirky_tesla"

# With --name
docker run -d --name my-web nginx:alpine
# Name is: "my-web"
```

**Why use names?**

- Easier to reference: `docker logs my-web` vs `docker logs quirky_tesla`
- More readable: `docker stop my-web`
- Required for linking containers in Docker Compose

### Automatic Cleanup

**Remove container when it exits**:

```bash
# --rm = automatically remove container when it exits
docker run --rm alpine echo "This container will be removed after running"

# Verify (should not appear)
docker ps -a
```

**When to use `--rm`**:

- Short-lived containers
- Testing and development
- One-off tasks

**When NOT to use `--rm`**:

- Production services (you want to inspect logs/state after failure)
- Containers with important data
- When debugging

---

## Managing Container Lifecycle

### Listing Containers

**List running containers**:

```bash
docker ps

# Or modern syntax
docker container ls
```

**List all containers (including stopped)**:

```bash
docker ps -a
```

**Example output**:

```
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS                     PORTS                  NAMES
5f8c9d2e3a1b   nginx:alpine   "/docker-entrypoint.…"   5 minutes ago   Up 5 minutes               0.0.0.0:8080->80/tcp   web
3a2b1c4d5e6f   alpine         "sh"                     1 hour ago      Exited (0) 59 minutes ago                         test-container
```

**Column explanations**:

- **CONTAINER ID**: First 12 chars of unique ID
- **IMAGE**: Image used to create the container
- **COMMAND**: Command running in the container
- **CREATED**: When container was created
- **STATUS**: Current state (Up = running, Exited = stopped)
- **PORTS**: Port mappings
- **NAMES**: Container name

**Useful filtering**:

```bash
# Show only container IDs
docker ps -q

# Show last created container
docker ps -l

# Filter by status
docker ps -f "status=exited"

# Filter by name
docker ps -f "name=web"

# Custom format
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Stopping Containers

**Stop a running container gracefully**:

```bash
docker stop web

# Stop with timeout (default is 10 seconds)
docker stop --time=30 web
```

**What happens**:

1. Docker sends SIGTERM to the main process
2. Waits for timeout (default 10 seconds)
3. If still running, sends SIGKILL (force stop)

**Force stop immediately**:

```bash
docker kill web
```

**Stop multiple containers**:

```bash
docker stop web db cache

# Stop all running containers
docker stop $(docker ps -q)
```

### Starting Stopped Containers

**Start a stopped container**:

```bash
docker start web

# Start and attach to output
docker start -a web

# Start in interactive mode
docker start -i my-alpine-shell
```

**Difference between `docker run` and `docker start`**:

- `docker run`: Creates a NEW container from an image
- `docker start`: Starts an EXISTING stopped container

### Restarting Containers

**Restart a container**:

```bash
docker restart web

# With timeout
docker restart --time=30 web
```

**Restart policies** (automatic restart on failure):

```bash
# Never restart (default)
docker run --restart=no nginx:alpine

# Always restart (even after host reboot)
docker run -d --restart=always --name web nginx:alpine

# Restart only on failure
docker run -d --restart=on-failure nginx:alpine

# Restart on failure, max 3 times
docker run -d --restart=on-failure:3 nginx:alpine

# Restart unless stopped explicitly
docker run -d --restart=unless-stopped nginx:alpine
```

**When to use restart policies**:

- `always`: Production services
- `unless-stopped`: Services you want to stay up, but respect manual stops
- `on-failure`: Services that might have transient failures
- `no`: Development, testing

### Pausing and Unpausing

**Pause a running container** (freezes all processes):

```bash
docker pause web
```

**Unpause**:

```bash
docker unpause web
```

**Use case**: Temporarily freeze a container without stopping it (preserves connections, state).

### Removing Containers

**Remove a stopped container**:

```bash
docker rm my-container
```

**Force remove a running container**:

```bash
docker rm -f my-container
```

**Remove multiple containers**:

```bash
docker rm container1 container2 container3

# Remove all stopped containers
docker container prune

# Remove all containers (running and stopped)
docker rm -f $(docker ps -aq)
```

**Remove container and its volumes**:

```bash
docker rm -v my-container
```

---

## Viewing Container Output and Logs

### Viewing Logs

**View container logs**:

```bash
docker logs web
```

**Follow logs in real-time** (like `tail -f`):

```bash
docker logs -f web
```

**Show timestamps**:

```bash
docker logs -t web
```

**Show only last N lines**:

```bash
docker logs --tail 50 web
```

**Show logs since a specific time**:

```bash
# Since 10 minutes ago
docker logs --since 10m web

# Since specific timestamp
docker logs --since 2024-01-01T10:00:00 web
```

**Combined example**:

```bash
# Follow last 100 lines with timestamps
docker logs -f --tail 100 -t web
```

### Attaching to Running Containers

**Attach to a container's output**:

```bash
docker attach web
```

**Detach without stopping** (keyboard shortcut):

- Press `Ctrl+P` then `Ctrl+Q`

### Executing Commands in Running Containers

**Run a command inside a running container**:

```bash
docker exec web ls /usr/share/nginx/html

# Output:
# 50x.html
# index.html
```

**Start an interactive shell**:

```bash
docker exec -it web sh

# Now you're inside the running container
/ # ps aux
PID   USER     TIME  COMMAND
    1 root      0:00 nginx: master process
   29 nginx     0:00 nginx: worker process
   30 root      0:00 sh
/ # exit
```

**Common use cases**:

```bash
# Debug a running container
docker exec -it web sh

# Check logs inside container
docker exec web tail /var/log/nginx/access.log

# Run database command
docker exec db psql -U postgres -c "SELECT version();"

# Check environment
docker exec web env

# Check running processes
docker exec web ps aux

# Update a file (not recommended for production!)
docker exec web sh -c "echo 'Hello' > /usr/share/nginx/html/hello.txt"
```

**Difference between `docker exec` and `docker attach`**:

- `docker exec`: Runs a NEW command in the container
- `docker attach`: Attaches to the EXISTING main process

---

## Container Inspection and Statistics

### Inspecting Containers

**Get detailed container information**:

```bash
docker inspect web
```

**Extract specific fields**:

```bash
# Get IP address
docker inspect web --format '{{.NetworkSettings.IPAddress}}'

# Get status
docker inspect web --format '{{.State.Status}}'

# Get environment variables
docker inspect web --format '{{.Config.Env}}'

# Get port mappings
docker inspect web --format '{{.NetworkSettings.Ports}}'
```

### Real-Time Statistics

**View resource usage**:

```bash
docker stats

# For specific containers
docker stats web db cache

# One-time snapshot (no streaming)
docker stats --no-stream
```

**Example output**:

```
CONTAINER ID   NAME   CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
5f8c9d2e3a1b   web    0.01%     4.5MiB / 7.5GiB      0.06%     1.2kB / 800B      0B / 0B           5
```

**Column explanations**:

- **CPU %**: CPU usage percentage
- **MEM USAGE / LIMIT**: Current memory / maximum allowed
- **MEM %**: Memory usage percentage
- **NET I/O**: Network bytes in / out
- **BLOCK I/O**: Disk bytes read / write
- **PIDS**: Number of processes

### Viewing Container Processes

**See processes running in a container**:

```bash
docker top web
```

**Example output**:

```
UID      PID      PPID     C    STIME   TTY   TIME       CMD
root     1234     1200     0    10:30   ?     00:00:00   nginx: master process
nginx    1250     1234     0    10:30   ?     00:00:00   nginx: worker process
```

---

## Copying Files To/From Containers

**Copy file from host to container**:

```bash
docker cp myfile.txt web:/tmp/

# Copy directory
docker cp mydir web:/opt/
```

**Copy file from container to host**:

```bash
docker cp web:/etc/nginx/nginx.conf ./nginx.conf

# Copy directory
docker cp web:/var/log/nginx ./nginx-logs
```

**Use cases**:

- Debugging: Extract logs or config files
- Hot fixes: Copy updated files (not recommended for production!)
- Backup: Extract data from containers

---

## Common Workflow Patterns

### Pattern 1: Quick Testing

```bash
# Pull image, run command, clean up
docker run --rm -it python:3.11 python --version
docker run --rm node:20 node --version
docker run --rm golang:1.21 go version
```

### Pattern 2: Development Web Server

```bash
# Run web server, map port, auto-remove
docker run --rm -p 8080:80 -v $(pwd):/usr/share/nginx/html nginx:alpine

# Access: http://localhost:8080
# Stop with Ctrl+C
```

### Pattern 3: Database for Development

```bash
# Start PostgreSQL
docker run -d \
  --name dev-postgres \
  --restart unless-stopped \
  -e POSTGRES_PASSWORD=dev123 \
  -e POSTGRES_DB=myapp \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15

# Connect from host
psql -h localhost -U postgres -d myapp

# Stop when done
docker stop dev-postgres

# Remove when no longer needed
docker rm dev-postgres
docker volume rm pgdata
```

### Pattern 4: One-Off Tasks

```bash
# Run a Python script
docker run --rm -v $(pwd):/app -w /app python:3.11 python myscript.py

# Compile C code
docker run --rm -v $(pwd):/src -w /src gcc:latest gcc -o myapp main.c

# Process data with jq
echo '{"name":"Docker"}' | docker run --rm -i stedolan/jq .name
```

### Pattern 5: Debugging Running Container

```bash
# 1. Check logs
docker logs -f web

# 2. Check processes
docker top web

# 3. Check stats
docker stats web --no-stream

# 4. Enter container
docker exec -it web sh

# 5. Inspect configuration
docker inspect web

# 6. Copy logs out for analysis
docker cp web:/var/log/nginx/error.log ./error.log
```

---

## Essential CLI Tips and Tricks

### Tab Completion

**Enable Docker tab completion** (Bash):

```bash
# Ubuntu/Debian
sudo apt-get install bash-completion
sudo curl -L https://raw.githubusercontent.com/docker/docker-ce/master/components/cli/contrib/completion/bash/docker \
    -o /etc/bash_completion.d/docker
source /etc/bash_completion.d/docker

# macOS (with Homebrew)
brew install bash-completion
# Add to ~/.bashrc:
# [[ -r "/usr/local/etc/profile.d/bash_completion.sh" ]] && . "/usr/local/etc/profile.d/bash_completion.sh"
```

### Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
# Container management
alias dps='docker ps'
alias dpsa='docker ps -a'
alias dimg='docker images'
alias dstop='docker stop'
alias drm='docker rm'
alias drmi='docker rmi'

# Logs
alias dlogs='docker logs -f'

# Cleanup
alias dprune='docker system prune -af'

# Get into a container
alias dexec='docker exec -it'

# Quick run
alias drun='docker run --rm -it'
```

### Command Chaining

**Stop and remove in one line**:

```bash
docker stop web && docker rm web

# Or force remove
docker rm -f web
```

**Stop all, remove all**:

```bash
docker stop $(docker ps -q) && docker rm $(docker ps -aq)
```

**Build, tag, push**:

```bash
docker build -t myapp:latest . && \
docker tag myapp:latest username/myapp:latest && \
docker push username/myapp:latest
```

---

## Hands-On Exercises

### Exercise 1: Basic Container Operations

```bash
# 1. Pull Alpine Linux
docker pull alpine:3.19

# 2. Run a command
docker run alpine:3.19 echo "Hello Docker!"

# 3. Run interactive shell
docker run -it alpine:3.19 sh
# Inside: ls, whoami, exit

# 4. Run in background
docker run -d --name my-alpine alpine:3.19 sleep 3600

# 5. List containers
docker ps

# 6. Execute command in running container
docker exec my-alpine cat /etc/os-release

# 7. Stop container
docker stop my-alpine

# 8. Remove container
docker rm my-alpine
```

### Exercise 2: Web Server

```bash
# 1. Run nginx in background
docker run -d --name web -p 8080:80 nginx:alpine

# 2. Test it
curl http://localhost:8080

# 3. View logs
docker logs web

# 4. Enter container
docker exec -it web sh
# Inside: cat /etc/nginx/nginx.conf, exit

# 5. Create custom page
echo "<h1>Hello from Docker!</h1>" | docker exec -i web sh -c 'cat > /usr/share/nginx/html/index.html'

# 6. Test again
curl http://localhost:8080

# 7. Check stats
docker stats web --no-stream

# 8. Clean up
docker rm -f web
```

### Exercise 3: Environment Variables and Ports

```bash
# 1. Run PostgreSQL with environment variables
docker run -d \
  --name db \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 \
  postgres:15-alpine

# 2. Wait for startup
sleep 5

# 3. Check logs
docker logs db

# 4. Connect to database
docker exec -it db psql -U myuser -d testdb

# Inside psql:
# \l                              -- list databases
# CREATE TABLE test (id INT);     -- create table
# \dt                             -- list tables
# \q                              -- quit

# 5. Clean up
docker rm -f db
```

---

---

### Exercise 4: Environment Variable Challenge (Advanced)

**Goal**: Understand environment isolation and how to configure containers securely.

**The Challenge**:
Many developers assume variables from their host shell (like `AWS_ACCESS_KEY_ID`) automatically exist in the container. They don't. Containers are isolated. You must explicitly pass them.

**Steps**:

1. **Verify Isolation**:
   Set a variable on your host:

   ```bash
   export SECRET_KEY="my_secret_value"
   ```

   Run a container and try to print it:

   ```bash
   docker run --rm alpine printenv SECRET_KEY
   # Output is empty! The container doesn't know about host variables.
   ```

2. **Pass Explicitly**:
   Pass it securely using `-e`:

   ```bash
   docker run --rm -e SECRET_KEY alpine printenv SECRET_KEY
   # Output: my_secret_value
   ```

   *Note: If you don't provide a value (like `-e SECRET_KEY` instead of `-e SECRET_KEY=value`), Docker passes the current host value.*

3. **Production Challenge (Postgres)**:
   Launch a Postgres container with a custom user and password. If you fail to pass these, the container will exit (Postgres 15+ requires a password or a specific config).

   ```bash
   # Challenge: Run this command and make it work
   docker run -d \
     --name challenge-db \
     -e POSTGRES_USER=admin \
     -e POSTGRES_PASSWORD=production_secret \
     postgres:15-alpine
   ```

   **Verify it works**:

   ```bash
   # Check logs (should show "database system is ready to accept connections")
   docker logs challenge-db

   # Verify environment inside
   docker exec challenge-db env | grep POSTGRES
   ```

4. **Clean up**:

   ```bash
   docker rm -f challenge-db
   ```

---

## Quick Reference

### Most Used Commands

```bash
# Images
docker pull <image>              # Download image
docker images                    # List images
docker rmi <image>               # Remove image

# Containers
docker run <image>               # Create and start container
docker ps                        # List running containers
docker ps -a                     # List all containers
docker stop <container>          # Stop container
docker start <container>         # Start stopped container
docker restart <container>       # Restart container
docker rm <container>            # Remove container

# Information
docker logs <container>          # View logs
docker logs -f <container>       # Follow logs
docker exec -it <container> sh   # Shell into container
docker inspect <container>       # Detailed info
docker stats                     # Resource usage

# Cleanup
docker system prune              # Remove unused data
docker container prune           # Remove stopped containers
docker image prune               # Remove unused images
```

### Common Flags

```bash
-d              # Detached (background)
-it             # Interactive + TTY (terminal)
--rm            # Remove on exit
--name NAME     # Give container a name
-p HOST:CONT    # Port mapping
-e KEY=VALUE    # Environment variable
-v HOST:CONT    # Volume mount
--restart       # Restart policy
```

---

## Summary

You've learned:

✅ How to pull and manage Docker images
✅ How to run containers in different modes (interactive, detached)
✅ How to map ports and set environment variables
✅ How to manage container lifecycle (start, stop, restart, remove)
✅ How to view logs and execute commands in running containers
✅ How to inspect containers and monitor resource usage
✅ Essential Docker CLI patterns and best practices

**Next steps**:

1. Practice these commands with different images
2. Experiment with port mapping and environment variables
3. Try the hands-on exercises
4. Create your own container workflows

---

**Next Chapter**: [Chapter 4: Dockerfile Basics](./chapter04_dockerfile_basics.md)
