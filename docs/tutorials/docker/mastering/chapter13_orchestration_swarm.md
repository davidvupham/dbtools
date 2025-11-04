# Chapter 13: Orchestration 101 (Docker Swarm)

- Services vs containers
- Desired state and scheduling
- Overlay networks

```bash
# Init swarm (single node demo)
docker swarm init
# Deploy a replicated service
docker service create --name web --replicas 3 -p 8080:80 nginx:alpine
```

Note: For production orchestration, most teams use Kubernetes today.
