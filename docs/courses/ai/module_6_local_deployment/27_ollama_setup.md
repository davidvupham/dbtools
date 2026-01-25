# Chapter 27: Ollama setup

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-6_Local_Deployment-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Install and configure Ollama on Linux, macOS, and Windows
2. Pull and manage models efficiently
3. Use the Ollama API for inference
4. Configure Ollama for production workloads

## Table of contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Basic usage](#basic-usage)
- [API usage](#api-usage)
- [Configuration](#configuration)
- [Docker deployment](#docker-deployment)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Ollama is the easiest way to run LLMs locally. It handles model downloading, quantization, and serving with a simple interface. This chapter covers installation, configuration, and production deployment.

[↑ Back to Table of Contents](#table-of-contents)

## Installation

### Linux

```bash
# One-line install
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Start the service (usually starts automatically)
sudo systemctl start ollama
sudo systemctl enable ollama

# Check status
sudo systemctl status ollama
```

### macOS

```bash
# Download from website or use Homebrew
brew install ollama

# Start Ollama (runs as background app)
ollama serve

# Or use the desktop app from https://ollama.com/download
```

### Windows

```powershell
# Download installer from https://ollama.com/download
# Or use winget
winget install Ollama.Ollama

# Verify installation
ollama --version
```

### Verify GPU support

```bash
# Check if GPU is detected
ollama run llama3.2:1b "Say hello"

# During inference, check GPU usage
nvidia-smi  # NVIDIA
rocm-smi    # AMD
```

[↑ Back to Table of Contents](#table-of-contents)

## Basic usage

### Pulling models

```bash
# Pull a model
ollama pull llama3.1:8b

# Pull specific quantization
ollama pull llama3.1:8b-q4_0

# List available models
ollama list

# Show model details
ollama show llama3.1:8b

# Remove a model
ollama rm llama3.1:8b
```

### Running models

```bash
# Interactive chat
ollama run llama3.1:8b

# Single prompt
ollama run llama3.1:8b "Explain PostgreSQL indexes in 3 sentences"

# With system prompt
ollama run llama3.1:8b --system "You are a database expert" "How do I optimize slow queries?"
```

### Model naming convention

```text
MODEL NAMING
════════════

Format: name:version-quantization

Examples:
├── llama3.1:8b          # Default (Q4_0)
├── llama3.1:8b-q4_0     # 4-bit quantization
├── llama3.1:8b-q8_0     # 8-bit quantization
├── llama3.1:8b-fp16     # Full precision
├── qwen2.5:7b           # Different model family
└── codellama:13b        # Code-specialized
```

[↑ Back to Table of Contents](#table-of-contents)

## API usage

### REST API basics

```bash
# Generate completion
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Why is PostgreSQL popular?",
  "stream": false
}'

# Chat format
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.1:8b",
  "messages": [
    {"role": "system", "content": "You are a database expert."},
    {"role": "user", "content": "Explain connection pooling."}
  ],
  "stream": false
}'

# Get embeddings
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "PostgreSQL performance tuning"
}'
```

### Python client

```python
import requests
from typing import Generator


class OllamaClient:
    """Simple Ollama API client."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def generate(
        self,
        prompt: str,
        model: str = "llama3.1:8b",
        system: str = None,
        stream: bool = False
    ) -> str | Generator[str, None, None]:
        """Generate text completion."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        if system:
            payload["system"] = system

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            stream=stream
        )

        if stream:
            return self._stream_response(response)
        else:
            return response.json()["response"]

    def _stream_response(self, response) -> Generator[str, None, None]:
        """Stream response chunks."""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]

    def chat(
        self,
        messages: list[dict],
        model: str = "llama3.1:8b"
    ) -> str:
        """Chat completion."""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={"model": model, "messages": messages, "stream": False}
        )
        return response.json()["message"]["content"]

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        """Generate embedding."""
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": model, "prompt": text}
        )
        return response.json()["embedding"]


# Usage
client = OllamaClient()

# Simple generation
response = client.generate("Explain ACID properties in databases")
print(response)

# Chat with context
messages = [
    {"role": "system", "content": "You are a PostgreSQL expert."},
    {"role": "user", "content": "How do I create an index?"},
    {"role": "assistant", "content": "Use CREATE INDEX..."},
    {"role": "user", "content": "What about partial indexes?"}
]
response = client.chat(messages)
```

### Async client

```python
import aiohttp
import asyncio


class AsyncOllamaClient:
    """Async Ollama API client."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    async def generate(
        self,
        prompt: str,
        model: str = "llama3.1:8b",
        system: str = None
    ) -> str:
        """Async text generation."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                data = await response.json()
                return data["response"]

    async def generate_batch(
        self,
        prompts: list[str],
        model: str = "llama3.1:8b",
        concurrency: int = 2
    ) -> list[str]:
        """Generate multiple prompts with limited concurrency."""
        semaphore = asyncio.Semaphore(concurrency)

        async def limited_generate(prompt: str) -> str:
            async with semaphore:
                return await self.generate(prompt, model)

        tasks = [limited_generate(p) for p in prompts]
        return await asyncio.gather(*tasks)


# Usage
async def main():
    client = AsyncOllamaClient()

    # Single request
    result = await client.generate("What is PostgreSQL?")
    print(result)

    # Batch requests
    prompts = [
        "Explain indexes",
        "Explain transactions",
        "Explain replication"
    ]
    results = await client.generate_batch(prompts, concurrency=2)
    for prompt, result in zip(prompts, results):
        print(f"Q: {prompt}\nA: {result[:100]}...\n")

asyncio.run(main())
```

[↑ Back to Table of Contents](#table-of-contents)

## Configuration

### Environment variables

```bash
# Model storage location (default: ~/.ollama)
export OLLAMA_MODELS=/data/ollama/models

# Server host and port (default: 127.0.0.1:11434)
export OLLAMA_HOST=0.0.0.0:11434

# Keep models loaded (default: 5m)
export OLLAMA_KEEP_ALIVE=30m

# Maximum loaded models
export OLLAMA_MAX_LOADED_MODELS=2

# GPU layers to offload (for partial GPU)
export OLLAMA_NUM_GPU=35

# Disable GPU (CPU only)
export OLLAMA_NO_GPU=1
```

### Systemd service configuration

```ini
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_MODELS=/data/ollama/models"
Environment="OLLAMA_KEEP_ALIVE=30m"
```

```bash
# Apply changes
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Custom model with Modelfile

```dockerfile
# Modelfile
FROM llama3.1:8b

# Set parameters
PARAMETER temperature 0.7
PARAMETER num_ctx 8192
PARAMETER top_p 0.9

# Set system prompt
SYSTEM """You are a database operations assistant. You help with:
- Database performance analysis
- Query optimization
- Configuration tuning
- Troubleshooting

Always provide specific, actionable recommendations."""

# Add custom template
TEMPLATE """{{ if .System }}<|system|>
{{ .System }}<|end|>
{{ end }}{{ if .Prompt }}<|user|>
{{ .Prompt }}<|end|>
{{ end }}<|assistant|>
{{ .Response }}<|end|>
"""
```

```bash
# Create custom model
ollama create db-assistant -f Modelfile

# Run custom model
ollama run db-assistant "Why are my queries slow?"
```

[↑ Back to Table of Contents](#table-of-contents)

## Docker deployment

### Basic Docker setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=30m
    restart: unless-stopped

volumes:
  ollama_data:
```

### With GPU support

```yaml
# docker-compose.gpu.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama-gpu
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=30m
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped

volumes:
  ollama_data:
```

```bash
# Start with GPU
docker compose -f docker-compose.gpu.yml up -d

# Pull models into container
docker exec -it ollama-gpu ollama pull llama3.1:8b
```

### Production deployment with health checks

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - /data/ollama:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=60m
      - OLLAMA_MAX_LOADED_MODELS=2
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        limits:
          memory: 32G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "3"

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - ollama
    restart: unless-stopped
```

### Pre-loading models on startup

```bash
#!/bin/bash
# init-models.sh

# Wait for Ollama to be ready
until curl -s http://localhost:11434/api/tags > /dev/null; do
    echo "Waiting for Ollama..."
    sleep 2
done

# Pull required models
echo "Pulling models..."
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama pull codellama:7b

# Pre-warm models (optional)
echo "Pre-warming models..."
curl -s http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Hello",
  "stream": false
}' > /dev/null

echo "Models ready!"
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Install Ollama on Linux, macOS, and Windows
- Pull and manage models using the CLI
- Use the REST API for generation, chat, and embeddings
- Configure Ollama for different environments
- Deploy with Docker for production workloads

## Next steps

Continue to **[Chapter 28: Model Selection](./28_model_selection.md)** to learn how to choose the right model for your use case.

[↑ Back to Table of Contents](#table-of-contents)
