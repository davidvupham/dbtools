# Chapter 30: Production operations

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-6_Local_Deployment-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Deploy Ollama with high availability
2. Implement proper security controls
3. Set up monitoring and alerting
4. Handle model updates and maintenance

## Table of contents

- [Introduction](#introduction)
- [High availability](#high-availability)
- [Security](#security)
- [Monitoring](#monitoring)
- [Maintenance](#maintenance)
- [Disaster recovery](#disaster-recovery)
- [Production checklist](#production-checklist)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Running LLMs in production requires the same operational rigor as any critical service. This chapter covers availability, security, monitoring, and maintenance practices for production deployments.

[↑ Back to Table of Contents](#table-of-contents)

## High availability

### Load balancer setup

```text
HIGH AVAILABILITY ARCHITECTURE
══════════════════════════════

                    ┌─────────────────┐
                    │  Load Balancer  │
                    │    (HAProxy)    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Ollama #1     │ │   Ollama #2     │ │   Ollama #3     │
│   (GPU Node)    │ │   (GPU Node)    │ │   (GPU Node)    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### HAProxy configuration

```text
# /etc/haproxy/haproxy.cfg

global
    maxconn 1000
    log stdout local0

defaults
    mode http
    timeout connect 10s
    timeout client 120s
    timeout server 120s
    option httplog
    option dontlognull

frontend ollama_frontend
    bind *:11434
    default_backend ollama_backend

backend ollama_backend
    balance roundrobin
    option httpchk GET /api/tags
    http-check expect status 200

    server ollama1 10.0.0.1:11434 check inter 5s fall 3 rise 2
    server ollama2 10.0.0.2:11434 check inter 5s fall 3 rise 2
    server ollama3 10.0.0.3:11434 check inter 5s fall 3 rise 2

listen stats
    bind *:8404
    stats enable
    stats uri /stats
```

### Kubernetes deployment

```yaml
# ollama-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        env:
        - name: OLLAMA_KEEP_ALIVE
          value: "30m"
        - name: OLLAMA_MAX_LOADED_MODELS
          value: "2"
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "32Gi"
          requests:
            memory: "16Gi"
        volumeMounts:
        - name: models
          mountPath: /root/.ollama
        readinessProbe:
          httpGet:
            path: /api/tags
            port: 11434
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /api/tags
            port: 11434
          initialDelaySeconds: 60
          periodSeconds: 30
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: ollama-models

---
apiVersion: v1
kind: Service
metadata:
  name: ollama
spec:
  selector:
    app: ollama
  ports:
  - port: 11434
    targetPort: 11434
  type: ClusterIP
```

### Model preloading

```python
#!/usr/bin/env python3
"""Preload models on startup for consistent performance."""

import asyncio
import aiohttp
import sys


REQUIRED_MODELS = [
    "llama3.1:8b",
    "nomic-embed-text",
]


async def wait_for_ollama(base_url: str, timeout: int = 300):
    """Wait for Ollama to be ready."""
    start = asyncio.get_event_loop().time()

    while asyncio.get_event_loop().time() - start < timeout:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/api/tags") as response:
                    if response.status == 200:
                        return True
        except aiohttp.ClientError:
            pass

        await asyncio.sleep(5)
        print("Waiting for Ollama...")

    return False


async def pull_model(base_url: str, model: str):
    """Pull a model if not present."""
    async with aiohttp.ClientSession() as session:
        # Check if model exists
        async with session.get(f"{base_url}/api/tags") as response:
            data = await response.json()
            existing = [m["name"] for m in data.get("models", [])]

            if model in existing:
                print(f"Model {model} already present")
                return

        # Pull model
        print(f"Pulling {model}...")
        async with session.post(
            f"{base_url}/api/pull",
            json={"name": model, "stream": False},
            timeout=aiohttp.ClientTimeout(total=3600)
        ) as response:
            if response.status == 200:
                print(f"Successfully pulled {model}")
            else:
                print(f"Failed to pull {model}: {await response.text()}")


async def warm_model(base_url: str, model: str):
    """Warm up model by running a simple inference."""
    print(f"Warming up {model}...")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": "Hello", "stream": False},
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:
            if response.status == 200:
                print(f"Model {model} warmed up")


async def main():
    base_url = "http://localhost:11434"

    if not await wait_for_ollama(base_url):
        print("Ollama did not become ready in time")
        sys.exit(1)

    for model in REQUIRED_MODELS:
        await pull_model(base_url, model)
        await warm_model(base_url, model)

    print("All models ready")


if __name__ == "__main__":
    asyncio.run(main())
```

[↑ Back to Table of Contents](#table-of-contents)

## Security

### Network isolation

```yaml
# docker-compose with network isolation
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    networks:
      - internal
    # No external port exposure

  api_gateway:
    image: nginx:alpine
    ports:
      - "443:443"
    networks:
      - internal
      - external
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro

networks:
  internal:
    internal: true  # No external access
  external:
```

### API authentication

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import secrets

app = FastAPI()
security = HTTPBearer()

# API keys (in production, use a database or secrets manager)
API_KEYS = {
    hashlib.sha256("key1".encode()).hexdigest(): {"name": "app1", "rate_limit": 100},
    hashlib.sha256("key2".encode()).hexdigest(): {"name": "app2", "rate_limit": 50},
}


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify API key and return client info."""
    key_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()

    if key_hash not in API_KEYS:
        raise HTTPException(401, "Invalid API key")

    return API_KEYS[key_hash]


@app.post("/api/generate")
async def generate(
    request: dict,
    client: dict = Depends(verify_api_key)
):
    """Authenticated generate endpoint."""
    # Rate limiting could be added here
    # Forward to Ollama
    return await forward_to_ollama(request)
```

### Input validation

```python
from pydantic import BaseModel, validator, Field
from typing import Optional


class GenerateRequest(BaseModel):
    model: str = Field(..., max_length=100)
    prompt: str = Field(..., max_length=100000)
    system: Optional[str] = Field(None, max_length=10000)
    temperature: Optional[float] = Field(0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(2048, ge=1, le=8192)

    @validator("model")
    def validate_model(cls, v):
        allowed_models = ["llama3.1:8b", "qwen2.5:7b", "nomic-embed-text"]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of: {allowed_models}")
        return v

    @validator("prompt")
    def validate_prompt(cls, v):
        # Check for potential prompt injection patterns
        suspicious_patterns = [
            "ignore previous instructions",
            "disregard all previous",
            "system prompt:",
        ]
        lower_prompt = v.lower()
        for pattern in suspicious_patterns:
            if pattern in lower_prompt:
                raise ValueError("Suspicious prompt content detected")
        return v


@app.post("/api/generate")
async def generate(request: GenerateRequest):
    """Generate with validated input."""
    return await forward_to_ollama(request.dict())
```

### Audit logging

```python
import logging
import json
from datetime import datetime
from typing import Any


class AuditLogger:
    """Security audit logger for LLM operations."""

    def __init__(self, log_path: str = "/var/log/ollama-audit.jsonl"):
        self.logger = logging.getLogger("ollama-audit")
        handler = logging.FileHandler(log_path)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_request(
        self,
        client_id: str,
        model: str,
        prompt_hash: str,
        prompt_length: int,
        source_ip: str
    ):
        """Log an inference request."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "inference_request",
            "client_id": client_id,
            "model": model,
            "prompt_hash": prompt_hash,  # Don't log actual prompt
            "prompt_length": prompt_length,
            "source_ip": source_ip
        }
        self.logger.info(json.dumps(entry))

    def log_response(
        self,
        client_id: str,
        model: str,
        response_length: int,
        latency_ms: float,
        success: bool
    ):
        """Log an inference response."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "inference_response",
            "client_id": client_id,
            "model": model,
            "response_length": response_length,
            "latency_ms": latency_ms,
            "success": success
        }
        self.logger.info(json.dumps(entry))
```

[↑ Back to Table of Contents](#table-of-contents)

## Monitoring

### Key metrics to monitor

| Metric | Alert Threshold | Action |
|:-------|:----------------|:-------|
| Request latency P95 | > 5s | Scale up or optimize |
| Error rate | > 1% | Investigate logs |
| GPU memory | > 90% | Reduce loaded models |
| GPU temperature | > 80°C | Check cooling |
| Request queue | > 10 | Scale up |
| Model load time | > 60s | Check storage |

### Grafana dashboard

```json
{
  "dashboard": {
    "title": "Ollama Production",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ollama_requests_total[5m])",
            "legendFormat": "{{model}}"
          }
        ]
      },
      {
        "title": "Latency P95",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(ollama_latency_bucket[5m]))",
            "legendFormat": "{{model}}"
          }
        ]
      },
      {
        "title": "GPU Memory",
        "type": "gauge",
        "targets": [
          {
            "expr": "ollama_gpu_memory_used_bytes / ollama_gpu_memory_total_bytes * 100"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ollama_requests_total{status='error'}[5m]) / rate(ollama_requests_total[5m]) * 100"
          }
        ]
      }
    ]
  }
}
```

### Alerting rules

```yaml
# prometheus-alerts.yml
groups:
  - name: ollama
    rules:
      - alert: OllamaHighLatency
        expr: histogram_quantile(0.95, rate(ollama_latency_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Ollama latency is high"
          description: "P95 latency is {{ $value }}s"

      - alert: OllamaHighErrorRate
        expr: rate(ollama_requests_total{status="error"}[5m]) / rate(ollama_requests_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Ollama error rate is high"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: OllamaGPUMemoryHigh
        expr: ollama_gpu_memory_used_bytes / ollama_gpu_memory_total_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GPU memory usage is high"
          description: "GPU memory at {{ $value | humanizePercentage }}"

      - alert: OllamaDown
        expr: up{job="ollama"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Ollama instance is down"
```

[↑ Back to Table of Contents](#table-of-contents)

## Maintenance

### Model updates

```python
#!/usr/bin/env python3
"""Rolling model update script."""

import asyncio
import aiohttp
from typing import List


async def update_model_rolling(
    nodes: List[str],
    model: str,
    new_version: str
):
    """Update model on all nodes with rolling deployment."""
    for node in nodes:
        print(f"Updating {model} on {node}...")

        # Remove from load balancer
        await remove_from_lb(node)
        await asyncio.sleep(30)  # Wait for drain

        # Pull new model
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"http://{node}:11434/api/pull",
                json={"name": f"{model}:{new_version}"}
            )

        # Warm up
        await warm_model(node, f"{model}:{new_version}")

        # Add back to load balancer
        await add_to_lb(node)

        # Wait before next node
        await asyncio.sleep(60)

        print(f"Node {node} updated")

    print("Rolling update complete")
```

### Backup and restore

```bash
#!/bin/bash
# backup-ollama.sh

BACKUP_DIR="/backup/ollama/$(date +%Y%m%d)"
OLLAMA_DIR="${OLLAMA_MODELS:-$HOME/.ollama}"

mkdir -p "$BACKUP_DIR"

# Backup model manifests (not the full weights)
cp -r "$OLLAMA_DIR/manifests" "$BACKUP_DIR/"

# Backup custom Modelfiles
if [ -d "/etc/ollama/modelfiles" ]; then
    cp -r /etc/ollama/modelfiles "$BACKUP_DIR/"
fi

# Create inventory
ollama list > "$BACKUP_DIR/model_inventory.txt"

echo "Backup complete: $BACKUP_DIR"
```

### Cleanup script

```bash
#!/bin/bash
# cleanup-ollama.sh

# Remove unused models
echo "Current models:"
ollama list

# Remove models not used in 30 days (based on access time)
find "${OLLAMA_MODELS:-$HOME/.ollama}/blobs" -atime +30 -type f -print

# Clear old logs
find /var/log/ollama* -mtime +7 -delete

# Clean up temporary files
rm -rf /tmp/ollama-*
```

[↑ Back to Table of Contents](#table-of-contents)

## Disaster recovery

### Backup strategy

```text
BACKUP STRATEGY
═══════════════

What to backup:
├── Model manifests (small, critical)
├── Custom Modelfiles
├── Configuration files
├── API keys/credentials
└── Audit logs

What NOT to backup (can be re-downloaded):
├── Model weights (~5-50GB per model)
└── Temporary cache files

Recovery time objective (RTO):
├── Model manifests: < 5 minutes
├── Model weights: 30-60 minutes (download)
└── Full service: < 2 hours
```

### Failover procedure

```python
#!/usr/bin/env python3
"""Disaster recovery failover script."""

import asyncio
import aiohttp
from typing import List

PRIMARY_REGION = "us-east"
FAILOVER_REGION = "us-west"

MODELS = ["llama3.1:8b", "nomic-embed-text"]


async def check_region_health(region: str) -> bool:
    """Check if region is healthy."""
    endpoints = get_region_endpoints(region)

    for endpoint in endpoints:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{endpoint}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return True
        except Exception:
            continue

    return False


async def failover_to_region(region: str):
    """Failover to specified region."""
    print(f"Initiating failover to {region}")

    # Update DNS or load balancer
    await update_dns(region)

    # Ensure models are loaded
    for model in MODELS:
        await ensure_model_loaded(region, model)

    # Verify service
    if await check_region_health(region):
        print(f"Failover to {region} successful")
        await notify_team(f"Failover to {region} complete")
    else:
        print(f"Failover verification failed!")
        await notify_team(f"CRITICAL: Failover to {region} failed!")


async def main():
    """Monitor and failover if needed."""
    while True:
        if not await check_region_health(PRIMARY_REGION):
            print(f"Primary region {PRIMARY_REGION} unhealthy")

            if await check_region_health(FAILOVER_REGION):
                await failover_to_region(FAILOVER_REGION)
            else:
                await notify_team("CRITICAL: Both regions unhealthy!")

        await asyncio.sleep(30)
```

[↑ Back to Table of Contents](#table-of-contents)

## Production checklist

```text
PRODUCTION READINESS CHECKLIST
══════════════════════════════

Infrastructure:
□ Multiple GPU nodes deployed
□ Load balancer configured with health checks
□ Persistent storage for models
□ Network isolation configured

Security:
□ API authentication implemented
□ Input validation in place
□ Audit logging enabled
□ TLS encryption for all traffic
□ Secrets management configured

Monitoring:
□ Prometheus metrics exposed
□ Grafana dashboards created
□ Alerting rules configured
□ Log aggregation set up

Operations:
□ Model preloading script ready
□ Rolling update procedure documented
□ Backup schedule configured
□ Disaster recovery plan tested
□ Runbook created for common issues

Performance:
□ Baseline benchmarks recorded
□ Capacity planning completed
□ Auto-scaling configured (if applicable)
□ Cache warming implemented
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Deploy Ollama with high availability using load balancers and multiple nodes
- Implement security controls including authentication, validation, and audit logging
- Set up comprehensive monitoring with Prometheus, Grafana, and alerting
- Handle maintenance tasks including model updates and backups
- Plan for disaster recovery with failover procedures

## Next steps

You have completed Module 6 and the entire course! To solidify your knowledge:

- **[Module 6 Exercises](./exercises/)**
- **[Module 6 Quiz](./quiz_module_6.md)**
- **[Project 6: Production LLM Deployment](./project_6_production_deployment.md)**

Continue your learning:
- Explore fine-tuning open-source models
- Build custom MCP servers for your organization
- Deploy multi-agent systems for complex workflows

[↑ Back to Table of Contents](#table-of-contents)
