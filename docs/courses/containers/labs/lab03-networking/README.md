# Lab 03: Container Networking

> **Level:** Intermediate | **Time:** 60-75 minutes | **Prerequisites:** Labs 01-02 completed

## Lab Overview

In this lab, you will practice container networking concepts including creating custom networks, connecting containers, and troubleshooting network issues.

---

## Learning Objectives

By completing this lab, you will be able to:

- Create and manage custom bridge networks
- Connect containers to multiple networks
- Use DNS for service discovery
- Debug network connectivity issues
- Implement network isolation patterns

---

## Prerequisites

- Completed Labs 01 and 02
- Docker or Podman installed
- curl available on host

---

## Part 1: Default Bridge Network

### Task 1.1: Explore Default Network

```bash
# List default networks
docker network ls

# Inspect the bridge network
docker network inspect bridge
```

### Task 1.2: Test Default Bridge Limitations

```bash
# Run two containers
docker run -d --name container1 alpine sleep 3600
docker run -d --name container2 alpine sleep 3600

# Get IP addresses
docker inspect --format '{{.NetworkSettings.IPAddress}}' container1
docker inspect --format '{{.NetworkSettings.IPAddress}}' container2

# Test connectivity by IP (works)
docker exec container1 ping -c 3 <container2-ip>

# Test connectivity by name (fails on default bridge!)
docker exec container1 ping -c 3 container2
# ping: bad address 'container2'

# Cleanup
docker rm -f container1 container2
```

---

## Part 2: Custom Bridge Networks

### Task 2.1: Create Custom Network

```bash
# Create a custom bridge network
docker network create myapp-network

# Inspect the network
docker network inspect myapp-network

# View network settings
docker network inspect myapp-network --format '{{.IPAM.Config}}'
```

### Task 2.2: DNS Resolution on Custom Networks

```bash
# Run containers on custom network
docker run -d --name web --network myapp-network nginx:alpine
docker run -d --name app --network myapp-network alpine sleep 3600

# DNS resolution works!
docker exec app ping -c 3 web
docker exec app nslookup web

# Containers can access each other by name
docker exec app wget -qO- http://web
```

### Task 2.3: Custom Network with Specific Subnet

```bash
# Create network with specific subnet
docker network create \
    --subnet 172.28.0.0/16 \
    --gateway 172.28.0.1 \
    custom-subnet

# Run container with specific IP
docker run -d --name fixed-ip \
    --network custom-subnet \
    --ip 172.28.0.100 \
    nginx:alpine

# Verify IP
docker inspect --format '{{.NetworkSettings.Networks}}' fixed-ip
```

---

## Part 3: Multi-Network Setup

### Task 3.1: Create Isolated Networks

```bash
# Create frontend and backend networks
docker network create frontend
docker network create backend
```

### Task 3.2: Deploy Multi-Tier Application

```bash
# Database on backend only
docker run -d --name db \
    --network backend \
    -e POSTGRES_PASSWORD=secret \
    postgres:15-alpine

# API on both networks
docker run -d --name api \
    --network backend \
    nginx:alpine

# Connect API to frontend too
docker network connect frontend api

# Web server on frontend only
docker run -d --name web \
    --network frontend \
    nginx:alpine
```

### Task 3.3: Test Connectivity

```bash
# Web can reach API
docker exec web ping -c 2 api

# API can reach DB
docker exec api ping -c 2 db

# Web CANNOT reach DB (network isolation!)
docker exec web ping -c 2 db
# ping: bad address 'db'

# Verify network memberships
docker inspect api --format '{{json .NetworkSettings.Networks}}' | jq
```

---

## Part 4: Port Publishing

### Task 4.1: Different Port Publishing Methods

```bash
# Publish to all interfaces
docker run -d --name web1 -p 8080:80 nginx:alpine

# Publish to localhost only
docker run -d --name web2 -p 127.0.0.1:8081:80 nginx:alpine

# Publish to random port
docker run -d --name web3 -p 80 nginx:alpine

# View assigned port
docker port web3
```

### Task 4.2: Test Port Access

```bash
# All interfaces - accessible from anywhere
curl http://localhost:8080

# Localhost only
curl http://localhost:8081

# From another machine (if applicable)
# curl http://<host-ip>:8080  # Works
# curl http://<host-ip>:8081  # Fails (localhost only)

# Find random port
random_port=$(docker port web3 80 | cut -d: -f2)
curl http://localhost:$random_port
```

---

## Part 5: Network Troubleshooting

### Task 5.1: Create Test Environment

```bash
# Create network
docker network create debug-net

# Run containers
docker run -d --name server \
    --network debug-net \
    nginx:alpine

docker run -d --name client \
    --network debug-net \
    alpine sleep 3600
```

### Task 5.2: Debugging Tools

```bash
# Install network tools in client
docker exec client apk add --no-cache curl bind-tools iputils netcat-openbsd

# Test DNS resolution
docker exec client nslookup server

# Test HTTP connectivity
docker exec client curl -I http://server

# Test port connectivity
docker exec client nc -zv server 80

# Check routing
docker exec client ip route

# Check network interfaces
docker exec client ip addr
```

### Task 5.3: Debug Network Container

Use a dedicated debugging container:

```bash
# Run nicolaka/netshoot for debugging
docker run -it --rm --network debug-net nicolaka/netshoot

# Inside netshoot:
nslookup server
curl http://server
ping server
tcpdump -i eth0
# Exit when done
```

---

## Part 6: Network Aliases

### Task 6.1: Create Service Aliases

```bash
# Create network
docker network create alias-net

# Run container with alias
docker run -d --name main-db \
    --network alias-net \
    --network-alias database \
    --network-alias db \
    postgres:15-alpine \
    -e POSTGRES_PASSWORD=secret

# Test different aliases
docker run --rm --network alias-net alpine ping -c 2 main-db
docker run --rm --network alias-net alpine ping -c 2 database
docker run --rm --network alias-net alpine ping -c 2 db
# All three resolve to the same container!
```

### Task 6.2: Round-Robin DNS

```bash
# Create multiple backends with same alias
docker run -d --name backend1 \
    --network alias-net \
    --network-alias backend \
    nginx:alpine

docker run -d --name backend2 \
    --network alias-net \
    --network-alias backend \
    nginx:alpine

docker run -d --name backend3 \
    --network alias-net \
    --network-alias backend \
    nginx:alpine

# DNS returns all IPs
docker run --rm --network alias-net alpine nslookup backend
# Returns 3 IP addresses (round-robin)
```

---

## Part 7: Real-World Scenario

### Task 7.1: Deploy a Web Application Stack

```bash
# Create application network
docker network create webapp

# Deploy PostgreSQL
docker run -d --name postgres \
    --network webapp \
    -e POSTGRES_DB=myapp \
    -e POSTGRES_USER=appuser \
    -e POSTGRES_PASSWORD=secret \
    -v pgdata:/var/lib/postgresql/data \
    postgres:15-alpine

# Wait for PostgreSQL
sleep 5

# Deploy Redis
docker run -d --name redis \
    --network webapp \
    redis:7-alpine

# Deploy API (simulated with nginx)
docker run -d --name api \
    --network webapp \
    -e DATABASE_URL=postgres://appuser:secret@postgres:5432/myapp \
    -e REDIS_URL=redis://redis:6379 \
    nginx:alpine

# Deploy Frontend
docker run -d --name frontend \
    --network webapp \
    -p 80:80 \
    nginx:alpine
```

### Task 7.2: Verify Connectivity

```bash
# API can reach PostgreSQL
docker exec api ping -c 2 postgres

# API can reach Redis
docker exec api ping -c 2 redis

# Frontend can reach API
docker exec frontend ping -c 2 api

# Test external access
curl http://localhost
```

---

## Part 8: Challenge Exercises

### Challenge 1: DMZ Architecture

Create a network setup with:
- Public network (accessible from host)
- Private network (isolated)
- Only one container bridging both

### Challenge 2: Network Debugging

Given this error scenario:
```bash
docker run --name broken --network nonexistent nginx
# Error: network nonexistent not found
```

Write a script that:
1. Checks if a network exists
2. Creates it if missing
3. Runs the container

### Challenge 3: Service Discovery

Create a setup where:
- 3 web servers share an alias "webservers"
- A client container can access any of them via the alias
- Demonstrate round-robin load distribution

---

## Verification Checklist

- [ ] Created custom bridge network
- [ ] Demonstrated DNS resolution on custom networks
- [ ] Connected a container to multiple networks
- [ ] Implemented network isolation
- [ ] Used network aliases
- [ ] Debugged network connectivity

---

## Cleanup

```bash
# Stop all containers
docker stop $(docker ps -q)

# Remove containers
docker rm $(docker ps -aq)

# Remove custom networks
docker network rm myapp-network custom-subnet frontend backend debug-net alias-net webapp

# Remove volumes
docker volume rm pgdata
```

---

## Solutions

See [solutions.md](solutions.md) for detailed solutions.

---

## Next Lab

Continue to: [Lab 04: Volumes and Storage](../lab04-volumes-storage/)
