# Operations guide

**[← Back to local-ai-hub Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-How--To-green)

> [!IMPORTANT]
> **Related Docs:** [Implementation Guide](./implementation-guide.md) | [Architecture](./architecture.md) | [Hardware Requirements](./hardware-requirements.md)

## Table of contents

- [Overview](#overview)
- [Day-to-day operations](#day-to-day-operations)
- [Monitoring and alerting](#monitoring-and-alerting)
- [Troubleshooting guide](#troubleshooting-guide)
- [Disaster recovery](#disaster-recovery)
- [Capacity planning](#capacity-planning)
- [User training](#user-training)
- [Incident response](#incident-response)
- [Maintenance procedures](#maintenance-procedures)

## Overview

This guide covers operational procedures for running local-ai-hub in production. It provides runbooks for common tasks, troubleshooting guides, and procedures for handling incidents.

### Operational responsibilities

| Role | Responsibilities |
|:-----|:-----------------|
| **Platform team** | Infrastructure, Ollama service, GPU management |
| **Application team** | FastAPI service, agents, MCP servers |
| **Security team** | Access controls, audit reviews, compliance |
| **Model owners** | Model validation, performance monitoring, updates |

[↑ Back to Table of Contents](#table-of-contents)

## Day-to-day operations

### Service health checks

Perform these checks daily or configure automated monitoring:

```bash
# 1. Check Ollama service status
systemctl status ollama

# 2. Verify Ollama is responding
curl -s http://localhost:11434/api/tags | jq '.models[].name'

# 3. Check FastAPI service
curl -s http://localhost:8080/health

# 4. Check GPU status
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv

# 5. Check disk space (models can be large)
df -h /usr/share/ollama  # or wherever models are stored
```

### Service management

```bash
# Start services
sudo systemctl start ollama
uvicorn local_ai_hub.api.app:app --host 0.0.0.0 --port 8080

# Stop services
sudo systemctl stop ollama

# Restart Ollama (if model loading issues)
sudo systemctl restart ollama

# View Ollama logs
journalctl -u ollama -f

# View application logs
tail -f /var/log/local-ai-hub/app.log
```

### Model management

```bash
# List installed models
ollama list

# Check model details
ollama show llama3.1:8b

# Pull/update a model
ollama pull llama3.1:8b

# Remove unused models (free disk space)
ollama rm <model-name>

# Check model disk usage
du -sh ~/.ollama/models/*
```

### Common daily tasks

| Task | Command/Procedure | Frequency |
|:-----|:------------------|:----------|
| Check service health | Run health check script | Daily |
| Review error logs | `journalctl -u ollama --since "24 hours ago" -p err` | Daily |
| Monitor GPU memory | `nvidia-smi` | As needed |
| Clear inference cache | Restart Ollama service | Weekly |
| Review audit logs | Check application logs for anomalies | Weekly |

[↑ Back to Table of Contents](#table-of-contents)

## Monitoring and alerting

### Key metrics to monitor

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONITORING DASHBOARD METRICS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INFRASTRUCTURE METRICS                                                      │
│  ──────────────────────                                                      │
│  • GPU memory utilization (%)      Alert if > 90% sustained                 │
│  • GPU compute utilization (%)     Alert if > 95% sustained                 │
│  • System RAM usage                Alert if > 85%                           │
│  • Disk space (model storage)      Alert if < 20% free                      │
│  • CPU utilization                 Alert if > 80% sustained                 │
│                                                                              │
│  SERVICE METRICS                                                             │
│  ───────────────                                                             │
│  • Ollama service status           Alert if down                            │
│  • FastAPI service status          Alert if down                            │
│  • API response time (p95)         Alert if > 30 seconds                    │
│  • Request error rate              Alert if > 5%                            │
│  • Requests per minute             Track for capacity planning              │
│                                                                              │
│  MODEL METRICS                                                               │
│  ─────────────                                                               │
│  • Tokens per second               Track for performance baseline           │
│  • Model load time                 Alert if > 60 seconds                    │
│  • Context window utilization      Track for optimization                   │
│  • Generation failures             Alert if > 2%                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Prometheus metrics (example)

If using Prometheus/Grafana, expose these metrics:

```python
# Example metrics for FastAPI service
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter('local_ai_hub_requests_total', 'Total requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('local_ai_hub_request_latency_seconds', 'Request latency', ['endpoint'])

# Model metrics
TOKENS_GENERATED = Counter('local_ai_hub_tokens_generated_total', 'Total tokens generated', ['model'])
GENERATION_TIME = Histogram('local_ai_hub_generation_seconds', 'Generation time', ['model'])

# Resource metrics
GPU_MEMORY_USED = Gauge('local_ai_hub_gpu_memory_bytes', 'GPU memory used')
ACTIVE_REQUESTS = Gauge('local_ai_hub_active_requests', 'Currently processing requests')
```

### Alert thresholds

| Metric | Warning | Critical | Action |
|:-------|:--------|:---------|:-------|
| GPU memory | > 85% | > 95% | Scale down concurrent requests or add GPU |
| API response time (p95) | > 15s | > 60s | Check model loading, reduce load |
| Error rate | > 2% | > 10% | Check logs, investigate root cause |
| Disk space | < 30% | < 10% | Remove old models, expand storage |
| Service down | - | Any downtime | Restart service, check logs |

### Health check endpoint

Implement a comprehensive health check:

```python
from fastapi import FastAPI, HTTPException
from datetime import datetime
import httpx

app = FastAPI()

@app.get("/health")
async def health_check():
    """Comprehensive health check for monitoring."""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check Ollama
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            health["checks"]["ollama"] = {
                "status": "healthy" if resp.status_code == 200 else "unhealthy",
                "models_loaded": len(resp.json().get("models", []))
            }
    except Exception as e:
        health["checks"]["ollama"] = {"status": "unhealthy", "error": str(e)}
        health["status"] = "unhealthy"

    # Check GPU (if applicable)
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            used, total = map(int, result.stdout.strip().split(", "))
            health["checks"]["gpu"] = {
                "status": "healthy",
                "memory_used_mb": used,
                "memory_total_mb": total,
                "memory_percent": round(used / total * 100, 1)
            }
    except Exception as e:
        health["checks"]["gpu"] = {"status": "unknown", "error": str(e)}

    if health["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health)

    return health
```

### Log aggregation

Recommended log format for centralized logging:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)
```

[↑ Back to Table of Contents](#table-of-contents)

## Troubleshooting guide

### Common issues and solutions

#### Issue: Ollama not responding

```text
Symptom: curl http://localhost:11434/api/tags returns connection refused

Diagnosis:
1. Check if service is running: systemctl status ollama
2. Check logs: journalctl -u ollama -n 50
3. Check if port is in use: ss -tlnp | grep 11434

Solutions:
• Service not running → sudo systemctl start ollama
• Port conflict → Stop conflicting service or change Ollama port
• Crash loop → Check logs for OOM or GPU errors, restart with more memory
```

#### Issue: Out of GPU memory (OOM)

```text
Symptom: "CUDA out of memory" errors or model fails to load

Diagnosis:
1. Check current GPU usage: nvidia-smi
2. Check which models are loaded: ollama ps
3. Check model size vs available VRAM

Solutions:
• Too many models loaded → Restart Ollama to clear memory
• Model too large → Use smaller quantization (Q4 instead of Q8)
• Multiple users → Implement request queuing
• Persistent issue → Consider GPU upgrade or model downgrade
```

#### Issue: Slow response times

```text
Symptom: API responses taking > 30 seconds

Diagnosis:
1. Check if model is loaded: ollama ps
2. Check GPU utilization: nvidia-smi
3. Check system load: top, htop
4. Check context length in requests

Solutions:
• Model not loaded (cold start) → Pre-load models at service start
• High GPU utilization → Queue requests, add capacity
• Long context → Reduce input size, implement chunking
• CPU fallback → Ensure CUDA is working: nvidia-smi
```

#### Issue: Model producing poor quality output

```text
Symptom: Responses are incorrect, incomplete, or nonsensical

Diagnosis:
1. Check if correct model is being used
2. Review prompt template
3. Check temperature and other parameters
4. Verify model wasn't corrupted

Solutions:
• Wrong model → Verify model name in API calls
• Poor prompt → Review and improve prompt engineering
• Parameter issues → Adjust temperature (lower = more deterministic)
• Corrupted model → Re-pull model: ollama pull <model>
```

#### Issue: Service crashes under load

```text
Symptom: Service becomes unavailable during high usage

Diagnosis:
1. Check for OOM in logs: dmesg | grep -i oom
2. Check file descriptor limits: ulimit -n
3. Check connection pool exhaustion

Solutions:
• OOM → Implement request rate limiting
• File descriptors → Increase limit: ulimit -n 65535
• Connection pool → Configure async client properly
• Add load balancing → Deploy multiple instances
```

### Diagnostic commands

```bash
# Full system diagnostic
echo "=== System Info ===" && uname -a
echo "=== GPU Status ===" && nvidia-smi
echo "=== Ollama Status ===" && systemctl status ollama
echo "=== Loaded Models ===" && ollama ps
echo "=== Disk Usage ===" && df -h
echo "=== Memory ===" && free -h
echo "=== Recent Errors ===" && journalctl -u ollama --since "1 hour ago" -p err
```

### Error code reference

| Error | Meaning | Resolution |
|:------|:--------|:-----------|
| `CUDA_OUT_OF_MEMORY` | GPU VRAM exhausted | Restart Ollama, use smaller model |
| `connection refused` | Service not running | Start Ollama service |
| `model not found` | Model not pulled | Run `ollama pull <model>` |
| `context length exceeded` | Input too long | Reduce input or use model with larger context |
| `timeout` | Generation took too long | Increase timeout or reduce input complexity |

[↑ Back to Table of Contents](#table-of-contents)

## Disaster recovery

### Backup strategy

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BACKUP COMPONENTS                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  COMPONENT              BACKUP METHOD           FREQUENCY    RETENTION      │
│  ═════════              ═════════════           ═════════    ═════════      │
│                                                                              │
│  Configuration files    Git repository          On change    Permanent      │
│  • docker-compose.yml                                                        │
│  • .env files                                                                │
│  • Nginx/proxy config                                                        │
│                                                                              │
│  Application code       Git repository          On change    Permanent      │
│  • FastAPI service                                                           │
│  • Agent definitions                                                         │
│  • MCP servers                                                               │
│                                                                              │
│  Prompt templates       Git repository          On change    Permanent      │
│  • System prompts                                                            │
│  • Few-shot examples                                                         │
│                                                                              │
│  Model files            Re-download             N/A          N/A            │
│  (Not backed up -       from Ollama                                         │
│   can be re-pulled)     registry                                            │
│                                                                              │
│  Vector DB (if used)    File system backup      Daily        30 days        │
│  • ChromaDB data                                                             │
│  • Embeddings                                                                │
│                                                                              │
│  Audit logs             Log aggregation         Continuous   Per policy     │
│  • Request/response                             (90 days+)                   │
│  • Security events                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Recovery procedures

#### Complete system recovery

```bash
# 1. Provision new server with GPU
# 2. Install prerequisites
sudo apt update && sudo apt install -y nvidia-driver-535 docker.io

# 3. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 4. Pull required models
ollama pull llama3.1:8b
ollama pull llama3.1:70b  # if using larger model

# 5. Clone application code
git clone <repository-url> /opt/local-ai-hub
cd /opt/local-ai-hub

# 6. Restore configuration
# Copy .env and config files from backup/git

# 7. Start services
docker-compose up -d
# OR
uv sync && uvicorn local_ai_hub.api.app:app --host 0.0.0.0 --port 8080

# 8. Verify health
curl http://localhost:8080/health
```

#### Recovery time objectives

| Scenario | RTO | RPO | Procedure |
|:---------|:----|:----|:----------|
| Service crash | 5 minutes | 0 | Restart service |
| Server failure | 2 hours | 0 (stateless) | Provision new server, redeploy |
| Model corruption | 30 minutes | N/A | Re-pull model from Ollama |
| Data center failure | 4 hours | Depends on backup | Restore from DR site |

### High availability (optional)

For critical deployments, consider:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HIGH AVAILABILITY ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────┐                                 │
│                         │  Load Balancer  │                                 │
│                         │  (HAProxy/Nginx)│                                 │
│                         └────────┬────────┘                                 │
│                                  │                                          │
│                    ┌─────────────┼─────────────┐                           │
│                    │             │             │                            │
│              ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐                     │
│              │  Node 1   │ │  Node 2   │ │  Node 3   │                     │
│              │  ───────  │ │  ───────  │ │  ───────  │                     │
│              │ • Ollama  │ │ • Ollama  │ │ • Ollama  │                     │
│              │ • FastAPI │ │ • FastAPI │ │ • FastAPI │                     │
│              │ • GPU     │ │ • GPU     │ │ • GPU     │                     │
│              └───────────┘ └───────────┘ └───────────┘                     │
│                                                                              │
│  Benefits:                                                                   │
│  • No single point of failure                                               │
│  • Rolling updates without downtime                                         │
│  • Horizontal scaling for more capacity                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## Capacity planning

### Sizing guidelines

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CAPACITY PLANNING MATRIX                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  USERS        MODEL SIZE    GPU REQUIREMENT       NOTES                     │
│  ═════        ══════════    ═══════════════       ═════                     │
│                                                                              │
│  1-5          8B            RTX 3060 12GB         Development tier          │
│  (Dev/POC)                  Single GPU            Sequential requests OK    │
│                                                                              │
│  5-15         8B            RTX 4090 24GB         Team tier                 │
│  (Team)                     Single GPU            Some queuing expected     │
│                                                                              │
│  15-30        8B or 14B     2x RTX 4090           Department tier           │
│  (Department)               or A100 40GB          Load balancing needed     │
│                                                                              │
│  30-100       14B-70B       A100 80GB             Production tier           │
│  (Production)               or multi-GPU          HA recommended            │
│                                                                              │
│  100+         70B           Multi-node            Enterprise tier           │
│  (Enterprise)               H100 cluster          Full HA required          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Estimating capacity needs

```python
# Capacity estimation formula
def estimate_capacity(
    concurrent_users: int,
    avg_input_tokens: int = 500,
    avg_output_tokens: int = 200,
    tokens_per_second: int = 30,  # Varies by GPU/model
    acceptable_wait_seconds: int = 10
) -> dict:
    """Estimate required capacity for local-ai-hub deployment."""

    # Average request time
    avg_request_time = (avg_input_tokens + avg_output_tokens) / tokens_per_second

    # Requests per minute per user (estimated)
    requests_per_user_per_minute = 2  # Adjust based on use case

    # Total requests per minute
    total_rpm = concurrent_users * requests_per_user_per_minute

    # Required parallel capacity
    required_capacity = (total_rpm * avg_request_time) / 60

    # Add buffer for queuing
    recommended_capacity = required_capacity * 1.5

    return {
        "concurrent_users": concurrent_users,
        "estimated_rpm": total_rpm,
        "avg_request_time_seconds": round(avg_request_time, 1),
        "min_parallel_capacity": round(required_capacity, 1),
        "recommended_capacity": round(recommended_capacity, 1),
        "recommendation": (
            "Single GPU" if recommended_capacity < 2
            else f"{int(recommended_capacity)} GPUs or request queuing"
        )
    }
```

### Scaling triggers

| Metric | Threshold | Action |
|:-------|:----------|:-------|
| GPU utilization | > 80% sustained | Add GPU or implement queuing |
| P95 latency | > 30 seconds | Add capacity or optimize prompts |
| Queue depth | > 10 requests | Add capacity |
| Error rate | > 5% | Investigate cause, possibly scale |

### Growth planning

| Phase | Timeline | Actions |
|:------|:---------|:--------|
| **Pilot** | Months 1-3 | Single GPU, 5-10 users, gather metrics |
| **Team rollout** | Months 4-6 | Upgrade GPU, 20-30 users, refine use cases |
| **Department** | Months 7-12 | Multi-GPU or HA, 50-100 users |
| **Enterprise** | Year 2+ | Multi-node cluster, 100+ users |

[↑ Back to Table of Contents](#table-of-contents)

## User training

### Onboarding checklist

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    USER ONBOARDING CHECKLIST                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  BEFORE FIRST USE                                                            │
│  □ Read acceptable use policy                                               │
│  □ Complete security awareness training (if required)                       │
│  □ Obtain necessary access credentials                                      │
│  □ Install required tools (Cline, IDE extension, etc.)                     │
│                                                                              │
│  INITIAL TRAINING                                                            │
│  □ Understand what local-ai-hub can and cannot do                          │
│  □ Learn prompt engineering basics                                          │
│  □ Practice with example use cases                                          │
│  □ Understand output review requirements                                    │
│                                                                              │
│  ONGOING                                                                     │
│  □ Report issues or unexpected behavior                                     │
│  □ Share successful prompts with team                                       │
│  □ Attend periodic refresher sessions                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Prompt engineering guidelines

#### Do's

| Practice | Example |
|:---------|:--------|
| **Be specific** | "Analyze this PostgreSQL error log and identify the root cause" |
| **Provide context** | "This is from a production database running PostgreSQL 15" |
| **Specify format** | "Return your analysis as a numbered list" |
| **Include examples** | "Similar to how you analyzed the previous log..." |
| **Set constraints** | "Focus only on connection-related errors" |

#### Don'ts

| Practice | Why |
|:---------|:----|
| **Don't include PII** | Customer data, credentials, SSNs should never be in prompts |
| **Don't trust blindly** | Always review AI output before using in production |
| **Don't skip context** | AI doesn't know your environment without you telling it |
| **Don't expect perfection** | AI makes mistakes; verify critical information |

### Acceptable use policy (template)

```text
LOCAL-AI-HUB ACCEPTABLE USE POLICY

PERMITTED USES:
✓ Analyzing internal logs and error messages
✓ Drafting technical documentation (with human review)
✓ Code review suggestions and refactoring assistance
✓ Explaining queries and configurations
✓ Generating test data and test cases

PROHIBITED USES:
✗ Processing customer PII without authorization
✗ Making automated decisions affecting customers
✗ Generating content that bypasses security controls
✗ Using outputs without human review for production
✗ Sharing proprietary information in prompts unnecessarily

REVIEW REQUIREMENTS:
• All AI-generated code must be reviewed before merging
• All AI-generated documentation must be reviewed before publishing
• All AI-generated analyses must be verified before acting on

REPORTING:
• Report unexpected or concerning outputs to: [security team]
• Report service issues to: [platform team]
```

[↑ Back to Table of Contents](#table-of-contents)

## Incident response

### Incident classification

| Severity | Description | Response Time | Examples |
|:---------|:------------|:--------------|:---------|
| **SEV-1** | Complete service outage | 15 minutes | All services down, no workaround |
| **SEV-2** | Major degradation | 1 hour | Very slow responses, high error rate |
| **SEV-3** | Minor degradation | 4 hours | Intermittent issues, workaround exists |
| **SEV-4** | Low impact | Next business day | Cosmetic issues, minor bugs |

### Incident response procedures

#### SEV-1: Complete outage

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SEV-1 INCIDENT RESPONSE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  0-15 MINUTES: TRIAGE                                                        │
│  1. Acknowledge incident in team channel                                    │
│  2. Run diagnostic commands (see troubleshooting section)                   │
│  3. Identify affected components                                            │
│  4. Notify stakeholders of outage                                           │
│                                                                              │
│  15-60 MINUTES: RESTORE                                                      │
│  1. Attempt service restart                                                 │
│  2. If restart fails, check logs for root cause                            │
│  3. Escalate to platform team if needed                                     │
│  4. Implement temporary workaround if available                             │
│                                                                              │
│  60+ MINUTES: ESCALATE                                                       │
│  1. Engage senior engineers                                                 │
│  2. Consider failover to DR if available                                    │
│  3. Provide regular updates to stakeholders                                 │
│                                                                              │
│  POST-INCIDENT                                                               │
│  1. Document timeline and resolution                                        │
│  2. Conduct blameless post-mortem                                           │
│  3. Identify preventive measures                                            │
│  4. Update runbooks if needed                                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### AI output incident (incorrect/harmful output)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AI OUTPUT INCIDENT RESPONSE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  IMMEDIATE ACTIONS                                                           │
│  1. Document the incident (screenshot, save logs)                           │
│  2. Do NOT use the problematic output                                       │
│  3. Report to model owner and security team                                 │
│                                                                              │
│  INVESTIGATION                                                               │
│  1. Review the prompt that caused the issue                                 │
│  2. Check if issue is reproducible                                          │
│  3. Determine if it's a prompt issue or model issue                        │
│  4. Check if similar prompts produce same result                           │
│                                                                              │
│  REMEDIATION                                                                 │
│  • Prompt issue → Update prompt templates, add guardrails                  │
│  • Model issue → Consider model change, add output filters                 │
│  • User error → Provide additional training                                │
│                                                                              │
│  DOCUMENTATION                                                               │
│  1. Log incident in tracking system                                         │
│  2. Update known issues documentation                                       │
│  3. Share learnings with user community                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Communication templates

**Outage notification:**
```
Subject: [local-ai-hub] Service Disruption - SEV-{X}

Status: {Investigating | Identified | Monitoring | Resolved}
Impact: {Description of user impact}
Start time: {ISO timestamp}
Current status: {What we know}
Next update: {Time of next update}

Updates will be posted to: {channel/location}
```

**Resolution notification:**
```
Subject: [local-ai-hub] Service Restored - SEV-{X}

The service disruption that began at {time} has been resolved.

Root cause: {Brief description}
Resolution: {What was done}
Duration: {Total downtime}

A post-mortem will be shared within {timeframe}.
```

[↑ Back to Table of Contents](#table-of-contents)

## Maintenance procedures

### Scheduled maintenance windows

| Task | Frequency | Duration | Impact |
|:-----|:----------|:---------|:-------|
| Security patches | Monthly | 30 min | Brief restart |
| Model updates | Quarterly | 1-2 hours | Service unavailable |
| Major upgrades | Annually | 4-8 hours | Extended downtime |

### Model update procedure

```bash
# 1. Announce maintenance window
# 2. Stop accepting new requests (drain queue)

# 3. Pull new model version
ollama pull llama3.1:8b

# 4. Test new model
curl -X POST http://localhost:11434/api/generate \
  -d '{"model": "llama3.1:8b", "prompt": "Test prompt", "stream": false}'

# 5. Validate output quality
# Run standard test cases, compare with baseline

# 6. If successful, update production configuration
# 7. Resume service and monitor

# 8. If issues found, rollback:
ollama rm llama3.1:8b
ollama pull llama3.1:8b@<previous-version>
```

### Rollback procedures

| Component | Rollback Method | Time |
|:----------|:----------------|:-----|
| Application code | `git checkout <previous-tag>` + redeploy | 10 min |
| Model | `ollama pull <model>@<previous-digest>` | 15-30 min |
| Configuration | Restore from git/backup | 5 min |
| Full system | Restore from DR/backup | 2-4 hours |

[↑ Back to Table of Contents](#table-of-contents)
