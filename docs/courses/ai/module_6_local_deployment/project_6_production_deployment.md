# Project 6: Production LLM Deployment

**[← Back to Course Index](../README.md)**

> **Difficulty:** Advanced
> **Estimated Time:** 8-10 hours
> **Prerequisites:** All previous modules completed

## Overview

Deploy a production-ready local LLM infrastructure with high availability, monitoring, and security. This capstone project integrates all concepts from the course.

## Learning objectives

By completing this project, you will:

1. Deploy Ollama with high availability
2. Implement comprehensive monitoring and alerting
3. Set up security controls and audit logging
4. Create operational runbooks and disaster recovery procedures

## Requirements

### Infrastructure requirements

1. **High availability**: Multiple Ollama nodes with load balancing
2. **Monitoring**: Prometheus metrics, Grafana dashboards, alerting
3. **Security**: API authentication, input validation, audit logs
4. **Operations**: Health checks, model management, maintenance procedures

### Deliverables

| Deliverable | Description |
|:------------|:------------|
| Docker Compose | Multi-node deployment configuration |
| Monitoring stack | Prometheus + Grafana + AlertManager |
| API gateway | Authentication and rate limiting |
| Runbooks | Operational procedures documentation |
| Load tests | Performance benchmarks |

## Architecture

```text
PRODUCTION ARCHITECTURE
═══════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                        Internet                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    API Gateway                                   │
│              (Auth, Rate Limiting, Logging)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    Load Balancer                                 │
│                 (HAProxy / Nginx)                                │
└────────────┬────────────┬────────────┬──────────────────────────┘
             │            │            │
     ┌───────▼───┐  ┌─────▼─────┐  ┌───▼───────┐
     │ Ollama #1 │  │ Ollama #2 │  │ Ollama #3 │
     │   (GPU)   │  │   (GPU)   │  │   (GPU)   │
     └───────────┘  └───────────┘  └───────────┘
             │            │            │
             └────────────┼────────────┘
                          │
     ┌────────────────────▼────────────────────┐
     │              Monitoring                  │
     │    Prometheus → Grafana → AlertManager  │
     └─────────────────────────────────────────┘
```

## Implementation guide

### Part 1: Docker Compose deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Ollama nodes
  ollama-1:
    image: ollama/ollama:latest
    container_name: ollama-1
    volumes:
      - ollama-1-data:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=60m
      - OLLAMA_MAX_LOADED_MODELS=2
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
    networks:
      - llm-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

  ollama-2:
    image: ollama/ollama:latest
    container_name: ollama-2
    volumes:
      - ollama-2-data:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=60m
      - OLLAMA_MAX_LOADED_MODELS=2
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['1']
              capabilities: [gpu]
    networks:
      - llm-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Load balancer
  haproxy:
    image: haproxy:latest
    container_name: haproxy
    ports:
      - "11434:11434"
      - "8404:8404"
    volumes:
      - ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
    depends_on:
      - ollama-1
      - ollama-2
    networks:
      - llm-network

  # API Gateway
  api-gateway:
    build: ./api-gateway
    container_name: api-gateway
    ports:
      - "8080:8080"
    environment:
      - OLLAMA_URL=http://haproxy:11434
      - REDIS_URL=redis://redis:6379
    depends_on:
      - haproxy
      - redis
    networks:
      - llm-network

  # Redis for rate limiting
  redis:
    image: redis:alpine
    container_name: redis
    networks:
      - llm-network

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - llm-network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - llm-network

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    networks:
      - llm-network

networks:
  llm-network:
    driver: bridge

volumes:
  ollama-1-data:
  ollama-2-data:
  prometheus-data:
  grafana-data:
```

### Part 2: API Gateway

```python
# api-gateway/main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import aiohttp
import redis.asyncio as redis
import hashlib
import time
import json

app = FastAPI(title="LLM API Gateway")
security = HTTPBearer()

# Configuration
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

redis_client = None


@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = await redis.from_url(REDIS_URL)


# API Key verification
API_KEYS = {}  # Load from secure storage in production


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    key_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    if key_hash not in API_KEYS:
        raise HTTPException(401, "Invalid API key")
    return API_KEYS[key_hash]


# Rate limiting
async def check_rate_limit(client_id: str, limit: int = 100) -> bool:
    key = f"rate_limit:{client_id}:{int(time.time() // 60)}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 60)
    return count <= limit


# Audit logging
async def log_request(client_id: str, endpoint: str, request_data: dict):
    entry = {
        "timestamp": time.time(),
        "client_id": client_id,
        "endpoint": endpoint,
        "request_size": len(json.dumps(request_data))
    }
    await redis_client.lpush("audit_log", json.dumps(entry))


@app.post("/api/generate")
async def generate(
    request: Request,
    client: dict = Depends(verify_api_key)
):
    # Rate limiting
    if not await check_rate_limit(client["id"], client.get("rate_limit", 100)):
        raise HTTPException(429, "Rate limit exceeded")

    # Get request data
    data = await request.json()

    # Audit log
    await log_request(client["id"], "/api/generate", data)

    # Forward to Ollama
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{OLLAMA_URL}/api/generate",
            json=data
        ) as response:
            result = await response.json()
            return result


@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### Part 3: Monitoring configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/rules/*.yml'

scrape_configs:
  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama-1:11434', 'ollama-2:11434']

  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8080']

  - job_name: 'haproxy'
    static_configs:
      - targets: ['haproxy:8404']
```

```yaml
# alertmanager.yml
global:
  slack_api_url: 'YOUR_SLACK_WEBHOOK'

route:
  receiver: 'slack-notifications'
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#llm-alerts'
        title: 'LLM Alert'
        text: '{{ .CommonAnnotations.summary }}'
```

### Part 4: Operational runbooks

Create runbooks for:

1. **Model deployment**: Steps to deploy new models
2. **Scaling**: Adding/removing Ollama nodes
3. **Incident response**: Handling outages
4. **Maintenance**: Regular maintenance tasks

## Implementation tasks

### Part 1: Infrastructure (30%)

- [ ] Docker Compose with multiple Ollama nodes
- [ ] HAProxy load balancer configuration
- [ ] Health checks and automatic failover
- [ ] Persistent volume configuration

### Part 2: API Gateway (25%)

- [ ] FastAPI gateway with authentication
- [ ] Rate limiting with Redis
- [ ] Request validation
- [ ] Audit logging

### Part 3: Monitoring (25%)

- [ ] Prometheus metrics collection
- [ ] Grafana dashboard
- [ ] AlertManager configuration
- [ ] Custom alerts for LLM-specific metrics

### Part 4: Operations (20%)

- [ ] Model preloading script
- [ ] Backup/restore procedures
- [ ] Operational runbooks
- [ ] Load testing results

## Testing

### Load testing

```python
# load_test.py
import asyncio
import aiohttp
import time
from statistics import mean, stdev

async def test_request(session, url, prompt):
    start = time.time()
    async with session.post(url, json={
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False
    }) as response:
        await response.json()
    return time.time() - start

async def run_load_test(url, concurrency, num_requests):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            tasks.append(test_request(
                session, url, f"Test prompt {i}"
            ))
            if len(tasks) >= concurrency:
                results = await asyncio.gather(*tasks)
                print(f"Batch: avg={mean(results):.2f}s, "
                      f"stdev={stdev(results):.2f}s")
                tasks = []

# Run: python load_test.py
asyncio.run(run_load_test(
    "http://localhost:8080/api/generate",
    concurrency=10,
    num_requests=100
))
```

## Evaluation criteria

| Criterion | Points |
|:----------|:-------|
| HA deployment working | 25 |
| API gateway with auth and rate limiting | 20 |
| Monitoring and alerting | 20 |
| Operational runbooks | 15 |
| Load testing and benchmarks | 10 |
| Documentation quality | 10 |
| **Total** | **100** |

## Submission

Create a git repository with:
- `docker-compose.yml` and all config files
- `api-gateway/` source code
- `monitoring/` Prometheus and Grafana configs
- `docs/runbooks/` operational documentation
- `tests/` load testing scripts
- `README.md` with deployment instructions

---

**Congratulations on completing the course!**

You now have the skills to build and deploy AI-powered database operations tools.

**[← Back to Course Index](../README.md)**
