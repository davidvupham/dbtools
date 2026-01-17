# Container Monitoring and Logging

> **Module:** Operations | **Level:** Intermediate-Advanced | **Time:** 35 minutes

## Learning Objectives

By the end of this section, you will be able to:

- Monitor container resource usage
- Configure and manage container logs
- Set up centralized logging
- Use common monitoring tools

---

## Container Metrics

### Built-in Stats

```bash
# Real-time stats for all containers
docker stats

# Stats for specific container
docker stats mycontainer

# One-time snapshot (no streaming)
docker stats --no-stream

# Custom format
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

**Metrics Available:**

| Metric | Description |
|--------|-------------|
| CPU % | CPU usage percentage |
| MEM USAGE / LIMIT | Memory used vs limit |
| MEM % | Memory percentage |
| NET I/O | Network bytes in/out |
| BLOCK I/O | Disk read/write |
| PIDS | Number of processes |

### Inspect Resource Limits

```bash
# View container limits
docker inspect --format '{{.HostConfig.Memory}}' mycontainer
docker inspect --format '{{.HostConfig.NanoCpus}}' mycontainer

# Detailed resource info
docker inspect --format '{{json .HostConfig}}' mycontainer | jq
```

---

## Logging Basics

### View Container Logs

```bash
# All logs
docker logs mycontainer

# Follow logs
docker logs -f mycontainer

# Last N lines
docker logs --tail 100 mycontainer

# With timestamps
docker logs -t mycontainer

# Since specific time
docker logs --since 1h mycontainer
docker logs --since "2024-01-15T10:00:00" mycontainer

# Combine options
docker logs -f --tail 50 -t mycontainer
```

### Understanding Log Output

Containers have two output streams:

- **stdout** - Standard output (application logs)
- **stderr** - Standard error (error messages)

```bash
# Show only stderr
docker logs mycontainer 2>&1 1>/dev/null

# Redirect to file
docker logs mycontainer > container.log 2>&1
```

---

## Logging Drivers

Docker supports multiple logging drivers:

| Driver | Description |
|--------|-------------|
| **json-file** | Default, writes JSON files |
| **local** | Optimized local logging |
| **syslog** | Sends to syslog |
| **journald** | Sends to systemd journal |
| **fluentd** | Sends to Fluentd |
| **awslogs** | Sends to AWS CloudWatch |
| **gcplogs** | Sends to Google Cloud |
| **splunk** | Sends to Splunk |
| **none** | Disables logging |

### Configure Default Driver

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### Per-Container Logging

```bash
# Use specific driver
docker run -d \
    --log-driver json-file \
    --log-opt max-size=10m \
    --log-opt max-file=5 \
    nginx

# Disable logging
docker run -d --log-driver none nginx

# Use syslog
docker run -d \
    --log-driver syslog \
    --log-opt syslog-address=udp://logserver:514 \
    nginx
```

---

## Log Management

### Log Rotation (json-file driver)

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "compress": "true"
  }
}
```

### Log Location

```bash
# Default log location (json-file driver)
/var/lib/docker/containers/<container-id>/<container-id>-json.log

# View raw log file
sudo cat /var/lib/docker/containers/abc123*/abc123*-json.log | jq

# Check log size
sudo du -sh /var/lib/docker/containers/*/
```

### Truncate Logs

```bash
# Truncate specific container log
sudo truncate -s 0 /var/lib/docker/containers/<container-id>/*-json.log

# Script to truncate all logs
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'
```

---

## Centralized Logging

### ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
# compose.yaml for ELK
version: '3.8'
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - esdata:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  esdata:
```

### Fluentd

```bash
# Run app with fluentd logging
docker run -d \
    --log-driver fluentd \
    --log-opt fluentd-address=localhost:24224 \
    --log-opt tag="docker.{{.Name}}" \
    nginx
```

### Loki + Grafana

```yaml
# compose.yaml for Loki
version: '3.8'
services:
  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    depends_on:
      - loki

volumes:
  loki-data:
```

---

## Monitoring Solutions

### cAdvisor

Container metrics exporter:

```bash
docker run -d \
    --name cadvisor \
    --volume /:/rootfs:ro \
    --volume /var/run:/var/run:ro \
    --volume /sys:/sys:ro \
    --volume /var/lib/docker/:/var/lib/docker:ro \
    --publish 8080:8080 \
    gcr.io/cadvisor/cadvisor:latest
```

### Prometheus + Grafana

```yaml
# compose.yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"

volumes:
  prometheus-data:
  grafana-data:
```

---

## Health Checks

### Container Health

```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1
```

```bash
# In docker run
docker run -d \
    --health-cmd "curl -f http://localhost/health || exit 1" \
    --health-interval 30s \
    --health-timeout 10s \
    --health-retries 3 \
    nginx

# Check health status
docker inspect --format '{{.State.Health.Status}}' mycontainer
docker inspect --format '{{json .State.Health}}' mycontainer | jq
```

### Health States

| State | Meaning |
|-------|---------|
| starting | Health check not run yet |
| healthy | Check passing |
| unhealthy | Check failing |

---

## Alerting

### Docker Events

```bash
# Watch Docker events
docker events

# Filter events
docker events --filter type=container
docker events --filter event=die
docker events --filter container=mycontainer

# JSON format
docker events --format '{{json .}}'
```

### Simple Alert Script

```bash
#!/bin/bash
# alert-on-exit.sh

docker events --filter event=die --format '{{.Actor.Attributes.name}}' | while read container; do
    echo "Container died: $container"
    # Send notification (email, Slack, etc.)
    # curl -X POST -d "Container $container exited" https://hooks.slack.com/...
done
```

---

## Key Takeaways

1. **docker stats** provides real-time metrics
2. **Configure log rotation** to prevent disk full
3. **Use appropriate logging driver** for your environment
4. **Centralized logging** is essential for production
5. **Health checks** enable automatic detection of issues
6. **docker events** allows custom alerting

---

## What's Next

Learn about troubleshooting container issues.

Continue to: [02-troubleshooting.md](02-troubleshooting.md)

---

## Quick Quiz

1. What command shows real-time container resource usage?
   - [ ] docker resources
   - [x] docker stats
   - [ ] docker monitor
   - [ ] docker top

2. What is the default logging driver?
   - [x] json-file
   - [ ] syslog
   - [ ] journald
   - [ ] none

3. How do you limit log file size?
   - [ ] --max-log-size
   - [ ] --log-size
   - [x] --log-opt max-size=10m
   - [ ] --log-limit 10m

4. What does a health check status of "unhealthy" indicate?
   - [ ] Container is stopped
   - [ ] Container has no health check
   - [x] Health check is failing
   - [ ] Container needs restart
