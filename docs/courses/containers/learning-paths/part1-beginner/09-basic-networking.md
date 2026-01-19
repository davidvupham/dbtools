# Introduction to Container Networking

> **Module:** Part 1 - Beginner | **Level:** Foundation | **Time:** 30 minutes

## Learning Objectives

By the end of this section, you will be able to:

- Understand how containers communicate with networks
- Publish container ports to the host
- Create and use custom networks
- Connect containers to each other
- Use DNS for container discovery

---

## Networking Overview

Containers need networking for:
- Exposing services to users (web servers, APIs)
- Communicating with other containers (app → database)
- Accessing external resources (APIs, databases)

```mermaid
flowchart TB
    subgraph Host["Host Machine"]
        subgraph Docker["Container Runtime"]
            C1[Web Container<br>:3000]
            C2[API Container<br>:8080]
            C3[DB Container<br>:5432]
        end
        HP[Host Ports<br>80, 8080]
    end

    Internet[Internet] --> HP
    HP --> C1
    C1 --> C2
    C2 --> C3
```

---

## Port Publishing

### Exposing Container Ports

Containers are isolated by default. Use `-p` to publish ports:

```bash
# Syntax: -p HOST_PORT:CONTAINER_PORT
docker run -d -p 8080:80 nginx

# Access: http://localhost:8080
```

### Port Publishing Options

```bash
# Map to specific host port
docker run -d -p 8080:80 nginx

# Map to random host port
docker run -d -p 80 nginx
docker port <container>  # See assigned port

# Bind to specific interface
docker run -d -p 127.0.0.1:8080:80 nginx   # localhost only
docker run -d -p 0.0.0.0:8080:80 nginx     # all interfaces (default)

# Multiple ports
docker run -d -p 80:80 -p 443:443 nginx

# Port range
docker run -d -p 8080-8090:80-90 nginx

# UDP port
docker run -d -p 53:53/udp dns-server
```

### Viewing Published Ports

```bash
# Show port mappings
docker port mycontainer

# Output:
80/tcp -> 0.0.0.0:8080
443/tcp -> 0.0.0.0:8443

# In docker ps output
docker ps
# PORTS column shows: 0.0.0.0:8080->80/tcp
```

---

## Network Types

### Default Networks

Docker/Podman provides several default network types:

```bash
# List networks
docker network ls

# Output:
NETWORK ID     NAME      DRIVER    SCOPE
abc123         bridge    bridge    local
def456         host      host      local
ghi789         none      null      local
```

| Network | Driver | Description |
|---------|--------|-------------|
| **bridge** | bridge | Default. Isolated network with NAT |
| **host** | host | Share host's network stack |
| **none** | null | No networking |

### Bridge Network (Default)

```mermaid
flowchart TB
    subgraph Host
        subgraph Bridge["bridge (docker0)"]
            C1[Container 1<br>172.17.0.2]
            C2[Container 2<br>172.17.0.3]
        end
        ETH[eth0<br>Host IP]
    end

    Internet <--> ETH
    ETH <-->|NAT| Bridge
```

```bash
# Containers on default bridge
docker run -d --name web1 nginx
docker run -d --name web2 nginx

# They get IPs in 172.17.0.0/16 range
docker inspect --format '{{.NetworkSettings.IPAddress}}' web1
# 172.17.0.2
```

### Host Network

Container shares the host's network namespace:

```bash
# Use host network
docker run -d --network host nginx

# nginx now listens on host's port 80 directly
# No port mapping needed
curl http://localhost:80
```

**Pros:** Best performance, no port mapping needed
**Cons:** Port conflicts possible, less isolation

### None Network

Container has no network access:

```bash
docker run -d --network none alpine sleep infinity

# Container can only use loopback
docker exec <container> ip addr
# Only lo interface
```

---

## Custom Bridge Networks

Custom networks provide DNS resolution and better isolation:

### Creating Custom Networks

```bash
# Create a custom bridge network
docker network create mynet

# Create with options
docker network create \
    --driver bridge \
    --subnet 192.168.100.0/24 \
    --gateway 192.168.100.1 \
    mynet
```

### Using Custom Networks

```bash
# Run container on custom network
docker run -d --name web --network mynet nginx
docker run -d --name api --network mynet myapi
docker run -d --name db --network mynet postgres:15

# Containers can reach each other by name!
docker exec web curl http://api:8080
docker exec api psql -h db -U postgres
```

### DNS Resolution

Custom networks provide automatic DNS:

```mermaid
flowchart LR
    subgraph mynet["Custom Network: mynet"]
        web[web<br>192.168.100.2]
        api[api<br>192.168.100.3]
        db[db<br>192.168.100.4]
    end

    web -->|"curl api:8080"| api
    api -->|"psql -h db"| db
```

```bash
# DNS works automatically
docker exec web ping api
# PING api (192.168.100.3): 56 data bytes

# Using hostname
docker exec web curl http://api:8080/health
```

**Note:** DNS doesn't work on the default bridge network!

---

## Network Commands

### List and Inspect

```bash
# List networks
docker network ls

# Inspect network
docker network inspect mynet

# See connected containers
docker network inspect mynet --format '{{range .Containers}}{{.Name}} {{end}}'
```

### Connect and Disconnect

```bash
# Connect running container to network
docker network connect mynet existingcontainer

# Disconnect from network
docker network disconnect mynet existingcontainer

# Connect with alias
docker network connect --alias webserver mynet web
```

### Remove Networks

```bash
# Remove specific network
docker network rm mynet

# Remove unused networks
docker network prune

# Force remove
docker network rm -f mynet
```

---

## Container-to-Container Communication

### Same Custom Network (Recommended)

```bash
# Create network
docker network create appnet

# Run services
docker run -d --name postgres --network appnet \
    -e POSTGRES_PASSWORD=secret postgres:15

docker run -d --name api --network appnet \
    -e DATABASE_URL=postgres://postgres:secret@postgres:5432/postgres \
    myapi

# API can reach postgres by hostname
```

### Multiple Networks

Containers can be on multiple networks:

```bash
# Create networks
docker network create frontend
docker network create backend

# Web server on frontend
docker run -d --name web --network frontend nginx

# API on both networks
docker run -d --name api --network frontend myapi
docker network connect backend api

# Database on backend only
docker run -d --name db --network backend postgres:15

# web -> api (frontend)
# api -> db (backend)
# web cannot reach db
```

```mermaid
flowchart LR
    subgraph frontend
        web[web]
        api1[api]
    end

    subgraph backend
        api2[api]
        db[db]
    end

    web --> api1
    api2 --> db
```

---

## Practical Examples

### Example 1: Web Application Stack

```bash
# Create network
docker network create webapp

# Database
docker run -d --name db --network webapp \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_DB=myapp \
    -v pgdata:/var/lib/postgresql/data \
    postgres:15

# Backend API
docker run -d --name api --network webapp \
    -e DATABASE_URL=postgres://postgres:secret@db:5432/myapp \
    -p 3000:3000 \
    myapi

# Frontend (if separate)
docker run -d --name web --network webapp \
    -e API_URL=http://api:3000 \
    -p 80:80 \
    myfrontend
```

### Example 2: Development Environment

```bash
# Create network
docker network create devnet

# Start services
docker run -d --name redis --network devnet redis:7
docker run -d --name mongo --network devnet mongo:7

# Run your app with access to all services
docker run -it --network devnet \
    -v $(pwd):/app -w /app \
    -e REDIS_URL=redis://redis:6379 \
    -e MONGO_URL=mongodb://mongo:27017 \
    node:20 npm run dev
```

### Example 3: Inspect Container Networking

```bash
# Run a container
docker run -d --name myapp -p 8080:80 nginx

# Check network settings
docker inspect myapp --format '{{json .NetworkSettings}}' | jq

# Get IP address
docker inspect myapp --format '{{.NetworkSettings.IPAddress}}'

# Check port bindings
docker inspect myapp --format '{{json .NetworkSettings.Ports}}' | jq
```

---

## Network Troubleshooting

### Common Commands

```bash
# Check container can reach another
docker exec container1 ping container2

# Check DNS resolution
docker exec container1 nslookup container2

# Check connectivity to port
docker exec container1 nc -zv container2 5432

# Install network tools (if needed)
docker exec container1 apt update && apt install -y iputils-ping netcat-openbsd

# Check container's network config
docker exec container1 ip addr
docker exec container1 ip route
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Can't reach container by name | Using default bridge | Use custom network |
| Port already in use | Another process on host port | Use different host port |
| Connection refused | Service not running or wrong port | Check container logs |
| No route to host | Network isolation | Connect to same network |

---

## Docker vs Podman Networking

### Podman-Specific

```bash
# Podman uses different default network
podman network ls
# podman (default network)

# Create network
podman network create mynet

# Rootless Podman networking
# Uses slirp4netns or pasta by default
podman run -p 8080:80 nginx
# Works but with some performance overhead

# Check network backend
podman info | grep -A5 network
```

### CNI vs Netavark

Podman 4.0+ uses Netavark by default:
- Better performance than CNI
- DNS with aardvark-dns
- Native to containers

```bash
# Check which network backend
podman info | grep networkBackend
```

---

## Key Takeaways

1. **Containers are isolated by default** - use `-p` to publish ports
2. **Custom networks enable DNS** - containers can reach each other by name
3. **Use custom networks for multi-container apps** - not the default bridge
4. **Port publishing syntax:** `-p HOST:CONTAINER`
5. **Multiple networks** enable network isolation between services
6. **DNS only works on custom networks** - not on the default bridge

---

## What's Next

Congratulations! You've completed Part 1: Beginner. You now understand:
- Container basics and lifecycle
- Building and managing images
- Persisting data with volumes
- Basic networking

Continue to: [Part 2: Intermediate](../part2-intermediate/01-docker-compose-basics.md)

Or practice with: [Exercises](exercises/beginner-exercises.md)

---

## Quick Quiz

1. What does `-p 8080:80` do?
   - [ ] Pauses container for 80 seconds
   - [x] Maps host port 8080 to container port 80
   - [ ] Opens port 8080 in the container
   - [ ] Publishes port 80 to random host port

2. Why should you use custom networks instead of the default bridge?
   - [ ] They are faster
   - [ ] They use less memory
   - [x] They provide DNS resolution by container name
   - [ ] They are required for port publishing

3. How can containers on the same custom network reach each other?
   - [x] By container name (DNS)
   - [ ] Only by IP address
   - [ ] They can't communicate
   - [ ] Only through the host

4. What network type shares the host's network stack?
   - [ ] bridge
   - [x] host
   - [ ] none
   - [ ] overlay

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Basic Volumes](08-basic-volumes.md) | [Part 1 Overview](../../course_overview.md#part-1-beginner) | [Part 1 Quiz](quiz.md) |
