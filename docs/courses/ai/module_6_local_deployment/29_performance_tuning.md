# Chapter 29: Performance tuning

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-6_Local_Deployment-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Optimize Ollama configuration for performance
2. Implement batching and concurrency strategies
3. Configure GPU memory and offloading
4. Monitor and profile inference performance

## Table of contents

- [Introduction](#introduction)
- [Inference fundamentals](#inference-fundamentals)
- [Ollama optimization](#ollama-optimization)
- [Batching strategies](#batching-strategies)
- [GPU optimization](#gpu-optimization)
- [Monitoring and profiling](#monitoring-and-profiling)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Local LLM performance depends on hardware configuration, model settings, and how you structure requests. This chapter covers techniques to maximize throughput and minimize latency.

[↑ Back to Table of Contents](#table-of-contents)

## Inference fundamentals

### Understanding latency components

```text
INFERENCE PIPELINE
══════════════════

Total latency = Model load + Prefill + Generation

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Model Load (first request only)                                │
│  └── Load weights from disk to GPU memory                       │
│      Time: seconds to minutes (depends on model size)           │
│                                                                 │
│  Prefill (every request)                                        │
│  └── Process entire prompt at once                              │
│      Time: ~milliseconds per 1000 tokens                        │
│                                                                 │
│  Generation (every request)                                     │
│  └── Generate tokens one at a time                              │
│      Time: ~20-100ms per token (depends on model/hardware)      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key metrics

| Metric | Definition | Target |
|:-------|:-----------|:-------|
| TTFT | Time to first token | < 500ms |
| Tokens/second | Generation speed | 20-80 tok/s |
| Throughput | Requests/minute | Depends on use case |
| VRAM usage | GPU memory used | < 90% of available |

### Factors affecting performance

```text
PERFORMANCE FACTORS
═══════════════════

Hardware:
├── GPU compute (CUDA cores, tensor cores)
├── VRAM bandwidth
├── CPU for offloading
└── Storage speed for model loading

Model:
├── Parameter count
├── Quantization level
├── Context length used
└── Architecture (attention mechanism)

Request:
├── Prompt length
├── Response length
├── Batch size
└── Concurrency
```

[↑ Back to Table of Contents](#table-of-contents)

## Ollama optimization

### Keep-alive settings

```bash
# Keep model loaded for 30 minutes (reduces load time)
export OLLAMA_KEEP_ALIVE=30m

# Keep model loaded indefinitely
export OLLAMA_KEEP_ALIVE=-1

# Unload after 5 minutes (default)
export OLLAMA_KEEP_ALIVE=5m
```

### Concurrent requests

```bash
# Maximum number of parallel requests
export OLLAMA_NUM_PARALLEL=4

# Maximum loaded models
export OLLAMA_MAX_LOADED_MODELS=2
```

### Context length optimization

```python
# Only request the context you need
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.1:8b",
        "prompt": prompt,
        "options": {
            "num_ctx": 2048,  # Smaller context = faster
            # Default is often 4096 or higher
        }
    }
)
```

### Generation parameters

```python
def optimized_generate(
    prompt: str,
    model: str = "llama3.1:8b",
    max_tokens: int = 256
) -> str:
    """Generate with optimized parameters."""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "options": {
                "num_predict": max_tokens,  # Limit output length
                "num_ctx": 2048,            # Limit context
                "temperature": 0.7,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                # Performance options
                "num_thread": 8,            # CPU threads for offloaded layers
                "num_gpu": 35,              # GPU layers (model-dependent)
            },
            "stream": False
        }
    )
    return response.json()["response"]
```

[↑ Back to Table of Contents](#table-of-contents)

## Batching strategies

### Request batching

```python
import asyncio
from collections import deque
from dataclasses import dataclass
import time


@dataclass
class BatchRequest:
    prompt: str
    future: asyncio.Future
    timestamp: float


class BatchingClient:
    """Client that batches requests for efficiency."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        batch_size: int = 4,
        max_wait_ms: int = 100
    ):
        self.base_url = base_url
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.queue: deque[BatchRequest] = deque()
        self._lock = asyncio.Lock()
        self._processor_task = None

    async def generate(self, prompt: str, model: str = "llama3.1:8b") -> str:
        """Submit request and wait for result."""
        future = asyncio.get_event_loop().create_future()
        request = BatchRequest(
            prompt=prompt,
            future=future,
            timestamp=time.time()
        )

        async with self._lock:
            self.queue.append(request)

            # Start processor if not running
            if self._processor_task is None or self._processor_task.done():
                self._processor_task = asyncio.create_task(
                    self._process_batch(model)
                )

        return await future

    async def _process_batch(self, model: str):
        """Process queued requests in batches."""
        await asyncio.sleep(self.max_wait_ms / 1000)  # Wait for more requests

        async with self._lock:
            batch = []
            while self.queue and len(batch) < self.batch_size:
                batch.append(self.queue.popleft())

        if not batch:
            return

        # Process batch concurrently
        tasks = [
            self._single_generate(req.prompt, model)
            for req in batch
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Deliver results
        for req, result in zip(batch, results):
            if isinstance(result, Exception):
                req.future.set_exception(result)
            else:
                req.future.set_result(result)

    async def _single_generate(self, prompt: str, model: str) -> str:
        """Execute single generation."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            ) as response:
                data = await response.json()
                return data["response"]


# Usage
async def main():
    client = BatchingClient(batch_size=4, max_wait_ms=50)

    # Submit multiple requests - they'll be batched
    prompts = [
        "Explain PostgreSQL indexes",
        "What is database normalization?",
        "How do transactions work?",
        "Describe query optimization"
    ]

    tasks = [client.generate(p) for p in prompts]
    results = await asyncio.gather(*tasks)

    for prompt, result in zip(prompts, results):
        print(f"Q: {prompt[:30]}...\nA: {result[:100]}...\n")
```

### Response streaming

```python
async def stream_generate(
    prompt: str,
    model: str = "llama3.1:8b",
    on_token: callable = None
) -> str:
    """Stream tokens as they're generated."""
    full_response = []

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": True}
        ) as response:
            async for line in response.content:
                if line:
                    data = json.loads(line)
                    token = data.get("response", "")
                    full_response.append(token)

                    if on_token:
                        on_token(token)

                    if data.get("done"):
                        break

    return "".join(full_response)


# Usage with callback
def print_token(token: str):
    print(token, end="", flush=True)

result = await stream_generate(
    "Explain database sharding",
    on_token=print_token
)
```

[↑ Back to Table of Contents](#table-of-contents)

## GPU optimization

### Layer offloading

```bash
# Offload all layers to GPU (default if VRAM allows)
export OLLAMA_NUM_GPU=99

# Partial offload (35 layers to GPU, rest to CPU)
export OLLAMA_NUM_GPU=35

# CPU only
export OLLAMA_NUM_GPU=0
```

### Finding optimal layer count

```python
import subprocess


def find_optimal_layers(model: str, vram_limit_gb: float) -> int:
    """Find optimal GPU layer count through testing."""
    # Start with all layers on CPU
    for num_gpu in range(0, 100, 5):
        try:
            # Test with this layer count
            result = subprocess.run(
                ["ollama", "run", model, "--num-gpu", str(num_gpu),
                 "Say hello"],
                capture_output=True,
                timeout=30,
                env={**os.environ, "OLLAMA_NUM_GPU": str(num_gpu)}
            )

            # Check VRAM usage
            vram_used = get_vram_usage()

            if vram_used > vram_limit_gb * 0.9:
                return max(0, num_gpu - 5)  # Back off

            print(f"Layers: {num_gpu}, VRAM: {vram_used:.1f} GB")

        except subprocess.TimeoutExpired:
            return max(0, num_gpu - 5)

    return 99  # All layers fit


def get_vram_usage() -> float:
    """Get current VRAM usage in GB."""
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,nounits,noheader"],
        capture_output=True,
        text=True
    )
    return float(result.stdout.strip()) / 1024
```

### Multi-GPU setup

```yaml
# docker-compose.multi-gpu.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    environment:
      - CUDA_VISIBLE_DEVICES=0,1  # Use both GPUs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0', '1']
              capabilities: [gpu]
```

[↑ Back to Table of Contents](#table-of-contents)

## Monitoring and profiling

### Basic metrics collection

```python
import time
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class InferenceMetrics:
    total_requests: int = 0
    total_tokens: int = 0
    total_time_ms: float = 0
    latencies: list = field(default_factory=list)
    tokens_per_request: list = field(default_factory=list)

    @property
    def avg_latency_ms(self) -> float:
        return self.total_time_ms / self.total_requests if self.total_requests else 0

    @property
    def tokens_per_second(self) -> float:
        return (self.total_tokens / self.total_time_ms) * 1000 if self.total_time_ms else 0

    @property
    def p95_latency_ms(self) -> float:
        if not self.latencies:
            return 0
        sorted_latencies = sorted(self.latencies)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[idx]


class MetricsCollector:
    """Collect inference metrics."""

    def __init__(self):
        self.metrics_by_model: dict[str, InferenceMetrics] = defaultdict(InferenceMetrics)

    def record(self, model: str, latency_ms: float, tokens: int):
        """Record a completed inference."""
        metrics = self.metrics_by_model[model]
        metrics.total_requests += 1
        metrics.total_tokens += tokens
        metrics.total_time_ms += latency_ms
        metrics.latencies.append(latency_ms)
        metrics.tokens_per_request.append(tokens)

    def report(self) -> dict:
        """Generate metrics report."""
        return {
            model: {
                "total_requests": m.total_requests,
                "avg_latency_ms": m.avg_latency_ms,
                "p95_latency_ms": m.p95_latency_ms,
                "tokens_per_second": m.tokens_per_second,
            }
            for model, m in self.metrics_by_model.items()
        }


# Usage
collector = MetricsCollector()


async def generate_with_metrics(prompt: str, model: str) -> str:
    """Generate with metrics collection."""
    start = time.time()
    response = await client.generate(prompt, model)
    elapsed_ms = (time.time() - start) * 1000

    # Estimate tokens (rough)
    tokens = len(response.split())

    collector.record(model, elapsed_ms, tokens)

    return response
```

### Prometheus metrics

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
inference_requests = Counter(
    'ollama_inference_requests_total',
    'Total inference requests',
    ['model', 'status']
)

inference_latency = Histogram(
    'ollama_inference_latency_seconds',
    'Inference latency in seconds',
    ['model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

tokens_generated = Counter(
    'ollama_tokens_generated_total',
    'Total tokens generated',
    ['model']
)

gpu_memory_used = Gauge(
    'ollama_gpu_memory_bytes',
    'GPU memory used',
    ['gpu_id']
)


class PrometheusOllamaClient:
    """Ollama client with Prometheus metrics."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        start_http_server(8000)  # Metrics endpoint

    async def generate(self, prompt: str, model: str) -> str:
        """Generate with metrics."""
        start = time.time()

        try:
            response = await self._do_generate(prompt, model)
            inference_requests.labels(model=model, status="success").inc()
            tokens = len(response.split())
            tokens_generated.labels(model=model).inc(tokens)
            return response

        except Exception as e:
            inference_requests.labels(model=model, status="error").inc()
            raise

        finally:
            elapsed = time.time() - start
            inference_latency.labels(model=model).observe(elapsed)
            self._update_gpu_metrics()

    def _update_gpu_metrics(self):
        """Update GPU memory metrics."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,memory.used",
                 "--format=csv,nounits,noheader"],
                capture_output=True, text=True
            )
            for line in result.stdout.strip().split('\n'):
                gpu_id, memory = line.split(',')
                gpu_memory_used.labels(gpu_id=gpu_id.strip()).set(
                    float(memory.strip()) * 1024 * 1024  # Convert to bytes
                )
        except Exception:
            pass
```

### Health check endpoint

```python
from fastapi import FastAPI, HTTPException
import aiohttp

app = FastAPI()


@app.get("/health")
async def health_check():
    """Check Ollama health."""
    try:
        async with aiohttp.ClientSession() as session:
            # Check if Ollama is responding
            async with session.get(
                "http://localhost:11434/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status != 200:
                    raise HTTPException(500, "Ollama not healthy")

                data = await response.json()
                models = data.get("models", [])

                return {
                    "status": "healthy",
                    "models_loaded": len(models),
                    "models": [m["name"] for m in models]
                }

    except aiohttp.ClientError as e:
        raise HTTPException(503, f"Ollama unavailable: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Return current metrics."""
    return collector.report()
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Understand inference latency components (load, prefill, generation)
- Optimize Ollama with keep-alive, parallel requests, and context settings
- Implement request batching for higher throughput
- Configure GPU layer offloading for optimal memory usage
- Monitor performance with metrics and health checks

## Next steps

Continue to **[Chapter 30: Production Operations](./30_production_operations.md)** to learn about reliability, scaling, and operational best practices.

[↑ Back to Table of Contents](#table-of-contents)
