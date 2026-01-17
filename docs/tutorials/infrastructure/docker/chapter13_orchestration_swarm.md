# Chapter 13: Orchestration 101 (Docker Swarm)

Docker Swarm is Docker's built-in orchestration tool. While Kubernetes has become the industry standard for large-scale deployments, Swarm remains useful for simpler setups and understanding orchestration concepts.

> [!NOTE]
> For most production workloads, Kubernetes is recommended. This chapter covers Swarm for learning orchestration fundamentals.

## Core Concepts

### Nodes

- **Manager nodes**: Control the cluster, schedule services, maintain state
- **Worker nodes**: Run containers (services)

### Services vs Containers

| Concept | Description |
| :--- | :--- |
| **Container** | A single running instance |
| **Service** | A definition of desired state (image, replicas, ports) |
| **Task** | A container running as part of a service |

---

## Getting Started with Swarm

### Initialize a Swarm

```bash
# Initialize on the first node (becomes manager)
docker swarm init

# Output includes a join token for workers
# docker swarm join --token SWMTKN-xxx 192.168.1.100:2377
```

### Join Worker Nodes

```bash
# On worker machines
docker swarm join --token SWMTKN-xxx MANAGER_IP:2377
```

### View Nodes

```bash
docker node ls

# Output:
# ID           HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
# abc123 *     manager1   Ready     Active         Leader
# def456       worker1    Ready     Active
```

---

## Deploying Services

### Create a Service

```bash
# Deploy 3 replicas of nginx
docker service create \
  --name web \
  --replicas 3 \
  --publish 8080:80 \
  nginx:alpine
```

### List Services

```bash
docker service ls

# Output:
# ID       NAME   MODE        REPLICAS   IMAGE
# abc123   web    replicated  3/3        nginx:alpine
```

### View Service Tasks

```bash
docker service ps web

# Shows which nodes are running each replica
```

---

## Scaling and Updates

### Scale a Service

```bash
docker service scale web=5
```

### Rolling Update

```bash
docker service update \
  --image nginx:1.25-alpine \
  --update-parallelism 1 \
  --update-delay 10s \
  web
```

### Rollback

```bash
docker service rollback web
```

---

## Overlay Networks

Swarm creates overlay networks that span all nodes.

```bash
# Create an overlay network
docker network create --driver overlay app-net

# Use it in a service
docker service create \
  --name api \
  --network app-net \
  myapi:latest
```

---

## Deploy with Stack (Compose for Swarm)

Use `docker stack deploy` with a Compose file:

```yaml
# docker-compose.yml
version: "3.8"
services:
  web:
    image: nginx:alpine
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
    ports:
      - "8080:80"
```

```bash
docker stack deploy -c docker-compose.yml myapp

docker stack ls
docker stack services myapp
docker stack rm myapp
```

---

## When to Use Swarm vs Kubernetes

| Factor | Swarm | Kubernetes |
| :--- | :--- | :--- |
| Complexity | Simple | Complex |
| Learning curve | Low | High |
| Built into Docker | Yes | No (separate install) |
| Ecosystem | Limited | Extensive |
| Production scale | Small-medium | Any scale |
| Community/Support | Smaller | Very large |

**Recommendation:** Use Swarm for simple deployments, learning, or when Kubernetes is overkill. Use Kubernetes for production at scale.

---

## Summary

```bash
# Initialize
docker swarm init

# Create service
docker service create --name web --replicas 3 -p 8080:80 nginx

# Scale
docker service scale web=5

# Update
docker service update --image nginx:1.25 web

# Remove
docker service rm web

# Leave swarm
docker swarm leave --force
```

**Next Chapter:** Learn Kubernetes concepts in **Chapter 14: Kubernetes for Docker Users**.
