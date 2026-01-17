# Part 3 advanced exercises

> **Level:** Advanced | **Time:** 90-120 minutes

Complete these exercises to master advanced container orchestration and operations.

---

## Exercise 1: Docker Swarm cluster

**Objective:** Set up a multi-node Swarm cluster.

### Requirements

- 3 nodes (can be VMs or cloud instances)
- 1 manager, 2 workers
- Overlay network
- Deploy a replicated service

### Steps

```bash
# On manager node
docker swarm init --advertise-addr <manager-ip>

# Get worker join token
docker swarm join-token worker

# On worker nodes
docker swarm join --token <token> <manager-ip>:2377

# Verify cluster
docker node ls
```

### Validation

```bash
# Create overlay network
docker network create --driver overlay mynet

# Deploy replicated service
docker service create --name web \
    --replicas 3 \
    --network mynet \
    -p 80:80 \
    nginx:alpine

# Verify distribution
docker service ps web
```

---

## Exercise 2: Stack deployment

**Objective:** Deploy a full application stack.

### Requirements

Create a stack file with:
- API service (3 replicas)
- PostgreSQL database
- Redis cache
- Nginx load balancer
- Proper networks and secrets

### Stack file template

```yaml
# stack.yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    configs:
      - source: nginx_conf
        target: /etc/nginx/nginx.conf
    deploy:
      replicas: 2
    networks:
      - frontend

  api:
    image: myapi:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
    secrets:
      - db_password
    networks:
      - frontend
      - backend

  postgres:
    image: postgres:15-alpine
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend

  redis:
    image: redis:7-alpine
    networks:
      - backend

networks:
  frontend:
    driver: overlay
  backend:
    driver: overlay
    internal: true

volumes:
  postgres_data:

secrets:
  db_password:
    external: true

configs:
  nginx_conf:
    file: ./nginx.conf
```

### Validation

```bash
# Create secrets
echo "secretpassword" | docker secret create db_password -

# Deploy stack
docker stack deploy -c stack.yaml myapp

# Verify services
docker stack services myapp

# Test rolling update
docker service update --image myapi:v2 myapp_api
```

---

## Exercise 3: Security hardening

**Objective:** Secure a container deployment.

### Requirements

Implement:
- Non-root user
- Read-only filesystem
- Dropped capabilities
- Resource limits
- Security scanning

### Dockerfile

```dockerfile
# Create hardened image
FROM node:20-alpine

# Security: Non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /app
COPY --chown=appuser:appgroup . .

# Security: No shell
RUN rm /bin/sh

USER appuser
CMD ["node", "index.js"]
```

### Compose file

```yaml
services:
  api:
    image: myapi:hardened
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
```

### Validation

```bash
# Scan image
trivy image myapi:hardened

# Verify non-root
docker run --rm myapi:hardened id

# Test read-only
docker run --rm myapi:hardened touch /test
# Should fail
```

---

## Exercise 4: Network isolation

**Objective:** Implement zero-trust networking.

### Requirements

Create a setup where:
- Frontend can only reach API
- API can reach database and cache
- Database and cache can't reach internet
- All traffic goes through defined paths

### Implementation

```yaml
services:
  frontend:
    networks:
      - dmz

  api:
    networks:
      - dmz
      - internal

  database:
    networks:
      - internal

  cache:
    networks:
      - internal

networks:
  dmz:
    driver: overlay

  internal:
    driver: overlay
    internal: true
```

### Validation

```bash
# Frontend can reach API
docker exec frontend_container ping api

# API can reach database
docker exec api_container ping database

# Frontend CANNOT reach database
docker exec frontend_container ping database
# Should fail

# Database CANNOT reach internet
docker exec database_container ping google.com
# Should fail
```

---

## Exercise 5: Monitoring stack

**Objective:** Set up complete monitoring.

### Requirements

Deploy:
- Prometheus for metrics
- Grafana for dashboards
- cAdvisor for container metrics
- Alertmanager for alerts

### Stack file

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    deploy:
      placement:
        constraints:
          - node.role == manager

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    deploy:
      mode: global

  alertmanager:
    image: prom/alertmanager:latest
```

### Validation

- Access Grafana at :3000
- View container metrics in Prometheus
- Trigger a test alert
- Verify alert notification

---

## Exercise 6: CI/CD pipeline

**Objective:** Create automated deployment pipeline.

### Requirements

Implement:
- Build on push
- Run tests
- Security scan
- Push to registry
- Deploy to Swarm

### GitHub Actions workflow

```yaml
name: CI/CD

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build
        run: docker build -t myapp:${{ github.sha }} .

      - name: Test
        run: docker run --rm myapp:${{ github.sha }} npm test

      - name: Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          exit-code: '1'

      - name: Push
        run: |
          docker tag myapp:${{ github.sha }} ghcr.io/${{ github.repository }}:${{ github.sha }}
          docker push ghcr.io/${{ github.repository }}:${{ github.sha }}

      - name: Deploy
        run: |
          docker service update --image ghcr.io/${{ github.repository }}:${{ github.sha }} myapp_api
```

### Validation

- Push code change
- Verify build passes
- Check security scan results
- Verify deployment updates

---

## Exercise 7: Rolling update strategy

**Objective:** Implement zero-downtime deployment.

### Requirements

Configure:
- Rolling updates with parallelism
- Health checks
- Automatic rollback
- Update monitoring

### Implementation

```yaml
services:
  api:
    image: myapi:v1
    deploy:
      replicas: 6
      update_config:
        parallelism: 2
        delay: 30s
        failure_action: rollback
        monitor: 60s
        max_failure_ratio: 0.2
        order: start-first
      rollback_config:
        parallelism: 0
        delay: 0s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
```

### Validation

```bash
# Update to new version
docker service update --image myapi:v2 myapp_api

# Watch update progress
watch docker service ps myapp_api

# Test rollback (deploy bad image)
docker service update --image myapi:broken myapp_api

# Verify automatic rollback occurred
docker service ps myapp_api
```

---

## Exercise 8: Distributed storage

**Objective:** Implement persistent storage for Swarm.

### Requirements

- NFS volume for shared data
- Backup automation
- Data persistence across node failures

### Implementation

```yaml
services:
  api:
    volumes:
      - shared_data:/app/uploads

  backup:
    image: alpine
    volumes:
      - shared_data:/source:ro
      - backup_data:/backup
    command: |
      sh -c 'while true; do
        tar czf /backup/data_$(date +%Y%m%d_%H%M).tar.gz -C /source .
        find /backup -mtime +7 -delete
        sleep 86400
      done'

volumes:
  shared_data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=nfs-server,rw
      device: ":/exports/data"

  backup_data:
```

### Validation

- Upload file through API
- Verify file accessible from all replicas
- Simulate node failure
- Verify data still accessible
- Verify backup created

---

## Bonus challenges

### Challenge A: Multi-region deployment

Deploy services across multiple regions with:
- Region-specific placement
- Cross-region service discovery
- Latency-based routing

### Challenge B: Chaos engineering

Implement:
- Random container kills
- Network partition simulation
- Resource exhaustion tests
- Automated recovery verification

### Challenge C: GitOps deployment

Set up:
- Git repository as source of truth
- Automatic sync to cluster
- Drift detection
- Audit logging

---

## Solutions

Solutions are available in the `solutions/` directory. Try to complete the exercises before checking the solutions.
