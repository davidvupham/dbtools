# Container command reference

> Quick reference for Docker and Podman commands.

---

## Container lifecycle

### Run containers

```bash
# Basic run
docker run nginx
podman run nginx

# Common options
docker run -d nginx                    # Detached (background)
docker run -it alpine sh               # Interactive terminal
docker run --rm nginx                  # Remove on exit
docker run --name mycontainer nginx    # Named container
docker run -p 8080:80 nginx            # Port mapping
docker run -v data:/data nginx         # Volume mount
docker run -e VAR=value nginx          # Environment variable
docker run --network mynet nginx       # Specific network
docker run -m 512m nginx               # Memory limit
docker run --cpus 2 nginx              # CPU limit
docker run --restart unless-stopped nginx  # Restart policy
```

### Manage containers

```bash
# List containers
docker ps                   # Running only
docker ps -a                # All containers

# Start/stop
docker start mycontainer
docker stop mycontainer
docker restart mycontainer

# Remove
docker rm mycontainer
docker rm -f mycontainer    # Force remove running

# Logs
docker logs mycontainer
docker logs -f mycontainer  # Follow
docker logs --tail 100 mycontainer

# Execute
docker exec mycontainer ls
docker exec -it mycontainer sh

# Inspect
docker inspect mycontainer
docker top mycontainer
docker stats mycontainer
```

---

## Images

### Build and manage

```bash
# Build
docker build -t myapp .
docker build -t myapp:v1 .
docker build -f Dockerfile.prod -t myapp .
docker build --no-cache -t myapp .
docker build --target stage -t myapp .

# Tag
docker tag myapp myapp:v1
docker tag myapp registry.com/myapp:v1

# Push/pull
docker push myapp:v1
docker pull nginx:alpine

# List
docker images
docker images -a

# Remove
docker rmi myapp:v1
docker image prune

# Inspect
docker history myapp
docker inspect myapp
```

---

## Volumes

```bash
# Create
docker volume create myvolume

# List
docker volume ls

# Inspect
docker volume inspect myvolume

# Remove
docker volume rm myvolume
docker volume prune

# Mount types
docker run -v myvolume:/data nginx         # Named volume
docker run -v /host/path:/data nginx       # Bind mount
docker run -v /host/path:/data:ro nginx    # Read-only
docker run --tmpfs /tmp nginx              # tmpfs
```

---

## Networks

```bash
# Create
docker network create mynet
docker network create --driver overlay mynet

# List
docker network ls

# Inspect
docker network inspect mynet

# Connect/disconnect
docker network connect mynet mycontainer
docker network disconnect mynet mycontainer

# Remove
docker network rm mynet
docker network prune
```

---

## Docker Compose

```bash
# Start services
docker compose up
docker compose up -d
docker compose up --build

# Stop services
docker compose down
docker compose down -v          # Remove volumes

# Manage
docker compose ps
docker compose logs
docker compose logs -f api
docker compose exec api sh
docker compose restart

# Build
docker compose build
docker compose build --no-cache

# Scale
docker compose up -d --scale worker=3
```

---

## Docker Swarm

### Cluster management

```bash
# Initialize
docker swarm init
docker swarm init --advertise-addr IP

# Join
docker swarm join --token TOKEN IP:2377
docker swarm join-token worker
docker swarm join-token manager

# Leave
docker swarm leave
docker swarm leave --force

# Nodes
docker node ls
docker node inspect node1
docker node update --availability drain node1
docker node rm node1
```

### Services

```bash
# Create
docker service create --name api nginx
docker service create --name api --replicas 3 nginx
docker service create --name api -p 80:80 nginx
docker service create --name api --secret mysecret nginx

# Manage
docker service ls
docker service ps api
docker service logs api
docker service inspect api

# Update
docker service update --replicas 5 api
docker service update --image nginx:latest api
docker service rollback api

# Remove
docker service rm api
```

### Stacks

```bash
# Deploy
docker stack deploy -c stack.yaml myapp

# Manage
docker stack ls
docker stack services myapp
docker stack ps myapp

# Remove
docker stack rm myapp
```

### Secrets

```bash
# Create
echo "password" | docker secret create mysecret -
docker secret create mysecret file.txt

# List
docker secret ls

# Inspect
docker secret inspect mysecret

# Remove
docker secret rm mysecret
```

---

## System

```bash
# Info
docker info
docker version

# Disk usage
docker system df
docker system df -v

# Clean up
docker system prune
docker system prune -a --volumes

# Events
docker events
docker events --filter type=container
```

---

## Inspection formats

```bash
# Container IP
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mycontainer

# Port bindings
docker inspect -f '{{json .HostConfig.PortBindings}}' mycontainer

# Environment variables
docker inspect -f '{{json .Config.Env}}' mycontainer

# Mounts
docker inspect -f '{{json .Mounts}}' mycontainer

# Health status
docker inspect -f '{{.State.Health.Status}}' mycontainer
```

---

## Podman-specific

```bash
# Pods
podman pod create --name mypod -p 8080:80
podman run --pod mypod nginx
podman pod ls
podman pod rm mypod

# Generate
podman generate kube mycontainer > pod.yaml
podman generate systemd --name mycontainer

# Play
podman play kube pod.yaml

# Rootless info
podman unshare cat /proc/self/uid_map
```
