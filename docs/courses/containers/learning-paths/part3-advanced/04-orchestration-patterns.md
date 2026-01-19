# Orchestration patterns

> **Module:** Part 3 - Advanced | **Level:** Advanced | **Time:** 30 minutes

## Learning objectives

By the end of this section, you will be able to:

- Implement common deployment patterns
- Design for high availability
- Handle stateful services
- Implement service discovery patterns

---

## Deployment patterns

### Blue-green deployment

Deploy new version alongside old, then switch traffic:

```yaml
# blue stack (current)
services:
  api-blue:
    image: myapi:v1.0.0
    deploy:
      replicas: 3
    networks:
      - backend

# green stack (new version)
services:
  api-green:
    image: myapi:v1.1.0
    deploy:
      replicas: 3
    networks:
      - backend
```

```bash
# 1. Deploy green alongside blue
docker stack deploy -c stack-green.yaml myapp

# 2. Test green deployment
curl http://green.internal/health

# 3. Update load balancer to point to green
# 4. Remove blue after verification
docker service rm myapp_api-blue
```

### Canary deployment

Gradually shift traffic to new version:

```yaml
services:
  api-stable:
    image: myapi:v1.0.0
    deploy:
      replicas: 9
    networks:
      - backend

  api-canary:
    image: myapi:v1.1.0
    deploy:
      replicas: 1  # 10% of traffic
    networks:
      - backend
```

```bash
# Increase canary percentage
docker service scale myapp_api-stable=8 myapp_api-canary=2  # 20%
docker service scale myapp_api-stable=5 myapp_api-canary=5  # 50%
docker service scale myapp_api-stable=0 myapp_api-canary=10 # 100%
```

### Rolling updates (default)

```yaml
services:
  api:
    image: myapi:v1.0.0
    deploy:
      replicas: 6
      update_config:
        parallelism: 2      # Update 2 at a time
        delay: 30s          # Wait between batches
        failure_action: rollback
        monitor: 60s        # Monitor for failures
        max_failure_ratio: 0.1
        order: start-first  # Start new before stopping old
```

---

## High availability patterns

### Multi-manager setup

```bash
# Initialize swarm with multiple managers
docker swarm init --advertise-addr 192.168.1.10

# Add manager nodes (3 or 5 total for HA)
docker swarm join-token manager
# Run output on other manager nodes
```

**Manager node count:**
| Managers | Fault Tolerance |
|----------|-----------------|
| 1 | 0 (no HA) |
| 3 | 1 manager failure |
| 5 | 2 manager failures |
| 7 | 3 manager failures |

### Service distribution

```yaml
services:
  api:
    deploy:
      replicas: 6
      placement:
        preferences:
          - spread: node.labels.zone  # Spread across zones
        constraints:
          - node.role == worker
```

### Drain and maintenance

```bash
# Drain node for maintenance
docker node update --availability drain node1

# Perform maintenance...

# Return to active
docker node update --availability active node1
```

---

## Stateful service patterns

### Single-instance with constraint

```yaml
services:
  postgres:
    image: postgres:15-alpine
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.postgres == primary
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### Primary-replica pattern

```yaml
services:
  postgres-primary:
    image: postgres:15-alpine
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.postgres == primary
    environment:
      - POSTGRES_REPLICATION_MODE=master
    volumes:
      - postgres_primary_data:/var/lib/postgresql/data

  postgres-replica:
    image: postgres:15-alpine
    deploy:
      replicas: 2
      placement:
        preferences:
          - spread: node.labels.zone
    environment:
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_MASTER_HOST=postgres-primary
```

### Distributed storage

For truly stateful services at scale, use distributed storage:

```yaml
volumes:
  postgres_data:
    driver: portworx
    driver_opts:
      repl: 3
      io_priority: high
```

---

## Service discovery patterns

### DNS-based discovery

Services automatically register in Swarm DNS:

```bash
# Service name resolves to VIP
ping myapp_api  # Returns VIP

# Tasks endpoint for individual IPs
dig tasks.myapp_api
```

### Load balancer integration

```yaml
services:
  api:
    image: myapi:latest
    deploy:
      replicas: 3
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.api.rule=Host(`api.example.com`)"
        - "traefik.http.services.api.loadbalancer.server.port=5000"

  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker.swarmMode=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    deploy:
      placement:
        constraints:
          - node.role == manager
```

### Sidecar pattern

```yaml
services:
  api:
    image: myapi:latest
    networks:
      - backend

  api-proxy:
    image: envoyproxy/envoy:v1.28
    configs:
      - source: envoy_config
        target: /etc/envoy/envoy.yaml
    networks:
      - backend
      - frontend
    depends_on:
      - api
```

---

## Batch processing patterns

### Job queue

```yaml
services:
  # Job queue
  redis:
    image: redis:7-alpine
    networks:
      - backend

  # API that enqueues jobs
  api:
    image: myapi:latest
    environment:
      - REDIS_URL=redis://redis:6379
    networks:
      - frontend
      - backend

  # Workers that process jobs
  worker:
    image: myworker:latest
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
    environment:
      - REDIS_URL=redis://redis:6379
    networks:
      - backend
```

### Scheduled tasks

```yaml
services:
  scheduler:
    image: mcuadros/ofelia:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    deploy:
      placement:
        constraints:
          - node.role == manager
    configs:
      - source: ofelia_config
        target: /etc/ofelia/config.ini

configs:
  ofelia_config:
    file: |
      [job-exec "cleanup"]
      schedule = 0 0 * * *
      container = myapp_cleanup
      command = /app/cleanup.sh
```

---

## Event-driven patterns

### Message broker

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "15672:15672"  # Management UI
    deploy:
      replicas: 1
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - backend

  producer:
    image: myproducer:latest
    environment:
      - RABBITMQ_URL=amqp://rabbitmq:5672
    networks:
      - backend

  consumer:
    image: myconsumer:latest
    deploy:
      replicas: 3
    environment:
      - RABBITMQ_URL=amqp://rabbitmq:5672
    networks:
      - backend
```

### Event sourcing

```yaml
services:
  eventstore:
    image: eventstore/eventstore:latest
    deploy:
      replicas: 3
    environment:
      - EVENTSTORE_CLUSTER_SIZE=3
      - EVENTSTORE_GOSSIP_SEED=eventstore:2113
    networks:
      - backend

  projection-service:
    image: myprojection:latest
    deploy:
      replicas: 2
    environment:
      - EVENTSTORE_URL=tcp://eventstore:1113
    networks:
      - backend
```

---

## Observability patterns

### Metrics collection

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    configs:
      - source: prometheus_config
        target: /etc/prometheus/prometheus.yml
    volumes:
      - prometheus_data:/prometheus
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    deploy:
      mode: global
    networks:
      - monitoring
```

### Centralized logging

```yaml
services:
  fluentd:
    image: fluent/fluentd:v1.16
    configs:
      - source: fluentd_config
        target: /fluentd/etc/fluent.conf
    deploy:
      mode: global
    networks:
      - logging

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - logging

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    networks:
      - logging
```

---

## Anti-patterns to avoid

### Don't do this

```yaml
# Anti-pattern: Single point of failure
services:
  db:
    deploy:
      replicas: 1
    # No volume persistence
    # No health check
    # No resource limits

# Anti-pattern: Manager-only deployment
services:
  api:
    deploy:
      placement:
        constraints:
          - node.role == manager  # Overloads managers

# Anti-pattern: Hardcoded secrets
services:
  api:
    environment:
      - DATABASE_PASSWORD=mysecret  # Should use secrets
```

---

## Key takeaways

1. **Blue-green** for instant rollback capability
2. **Canary** for gradual rollout with validation
3. **Spread placement** for high availability
4. **Constraints** for stateful service pinning
5. **Global mode** for per-node services

---

## What's next

Learn about container security in depth.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Docker Stacks](03-docker-stacks.md) | [Part 3 Overview](../../course_overview.md#part-3-advanced) | [Security Deep Dive](05-security-deep-dive.md) |
