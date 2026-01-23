# local-ai-hub: Implementation guide

**[← Back to local-ai-hub Index](./README.md)**

> **Document Version:** 2.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-How_To-blue)

> [!IMPORTANT]
> **Related Docs:** [Architecture](./architecture.md) | [Hardware Requirements](./hardware-requirements.md) | [MCP Integration](./mcp-integration.md)

## Table of contents

- [Prerequisites](#prerequisites)
- [Infrastructure setup](#infrastructure-setup)
- [Ollama installation](#ollama-installation)
- [Model deployment](#model-deployment)
- [dbtool-ai service setup](#dbtool-ai-service-setup)
- [CrewAI agent implementation](#crewai-agent-implementation)
- [FastAPI service](#fastapi-service)
- [Docker deployment](#docker-deployment)
- [Testing and validation](#testing-and-validation)
- [Production deployment](#production-deployment)

## Prerequisites

### System requirements

| Component | Minimum | Recommended |
|:----------|:--------|:------------|
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| Python | 3.11 | 3.12 |
| CUDA | 11.8 | 12.x |
| GPU Driver | 525.x | 545.x+ |
| RAM | 32 GB | 64 GB |
| Disk | 100 GB | 500 GB SSD |

### Software dependencies

```bash
# System packages
sudo apt update && sudo apt install -y \
    build-essential \
    curl \
    git \
    python3.12 \
    python3.12-venv \
    nvidia-driver-545 \
    nvidia-cuda-toolkit

# Verify GPU
nvidia-smi
```

### Python environment

```bash
# Install UV (recommended package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project directory
mkdir -p ~/projects/dbtool-ai
cd ~/projects/dbtool-ai

# Initialize Python project
uv init
uv python pin 3.12
```

[↑ Back to Table of Contents](#table-of-contents)

## Infrastructure setup

### GPU verification

```bash
# Check NVIDIA driver
nvidia-smi

# Expected output shows GPU(s), driver version, CUDA version
# Example:
# +-----------------------------------------------------------------------------------------+
# | NVIDIA-SMI 545.23.08    Driver Version: 545.23.08    CUDA Version: 12.3               |
# |-----------------------------------------+------------------------+----------------------|
# | GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
# | Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
# |=========================================+========================+======================|
# |   0  NVIDIA GeForce RTX 4090        Off | 00000000:01:00.0  On   |                  Off |
# | 30%   35C    P8              17W / 450W |     512MiB / 24564MiB  |      0%      Default |
# +-----------------------------------------+------------------------+----------------------+
```

### CUDA toolkit verification

```bash
# Verify CUDA
nvcc --version

# If CUDA not found, install:
sudo apt install nvidia-cuda-toolkit
```

### Directory structure

```bash
# Create project structure
mkdir -p ~/projects/dbtool-ai/{src,tests,configs,models,logs}

# Project layout
# dbtool-ai/
# ├── src/
# │   └── dbtool_ai/
# │       ├── __init__.py
# │       ├── agents/
# │       ├── api/
# │       ├── mcp/
# │       └── utils/
# ├── tests/
# ├── configs/
# ├── models/
# ├── logs/
# ├── pyproject.toml
# └── docker-compose.yml
```

[↑ Back to Table of Contents](#table-of-contents)

## Ollama installation

### Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Start Ollama service (if not auto-started)
sudo systemctl start ollama
sudo systemctl enable ollama

# Check service status
sudo systemctl status ollama
```

### Configure Ollama

```bash
# Create Ollama configuration
sudo mkdir -p /etc/ollama

# Set environment variables for systemd
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_MODELS=/var/lib/ollama/models"
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_LOADED_MODELS=2"
EOF

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Verify Ollama API

```bash
# Test API endpoint
curl http://localhost:11434/api/version

# Expected: {"version":"0.x.x"}
```

[↑ Back to Table of Contents](#table-of-contents)

## Model deployment

### Download recommended models

```bash
# Primary model (8B for development)
ollama pull llama3.1:8b

# Tool calling model
ollama pull qwen2.5:7b

# Code-focused model
ollama pull qwen2.5-coder:7b

# Production model (if hardware supports)
ollama pull llama3.1:70b

# Verify models
ollama list
```

### Test model inference

```bash
# Interactive test
ollama run llama3.1:8b "Explain what a SQL deadlock is in 2 sentences."

# API test
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "What causes high CPU usage in PostgreSQL?",
  "stream": false
}'
```

### Create custom model variants

```bash
# Create Modelfile for dbtool-specific configuration
cat > Modelfile.dbtool << 'EOF'
FROM llama3.1:8b

# Set system prompt for database operations
SYSTEM """You are an expert database administrator assistant specializing in SQL Server, PostgreSQL, and MongoDB. You help analyze logs, explain queries, and troubleshoot database issues. Be concise and actionable in your responses. Always consider security best practices."""

# Adjust parameters for our use case
PARAMETER temperature 0.3
PARAMETER num_ctx 8192
PARAMETER stop "<|eot_id|>"
EOF

# Create custom model
ollama create dbtool-assistant -f Modelfile.dbtool

# Test custom model
ollama run dbtool-assistant "Analyze this error: FATAL: too many connections for role 'app_user'"
```

[↑ Back to Table of Contents](#table-of-contents)

## dbtool-ai service setup

### Project configuration

```toml
# pyproject.toml
[project]
name = "dbtool-ai"
version = "0.1.0"
description = "AI-powered database operations assistant"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "crewai>=0.80.0",
    "litellm>=1.50.0",
    "ollama>=0.4.0",
    "mcp>=1.0.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "httpx>=0.28.0",
    "structlog>=24.4.0",
    "opentelemetry-api>=1.28.0",
    "opentelemetry-sdk>=1.28.0",
    "prometheus-client>=0.21.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
```

### Install dependencies

```bash
# Using UV
uv sync

# Or using pip
pip install -e ".[dev]"
```

### Configuration module

```python
# src/dbtool_ai/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Ollama configuration
    ollama_host: str = "http://localhost:11434"
    default_model: str = "llama3.1:8b"
    tool_model: str = "qwen2.5:7b"
    code_model: str = "qwen2.5-coder:7b"

    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_workers: int = 4

    # Model parameters
    temperature: float = 0.3
    max_tokens: int = 2048
    context_length: int = 8192

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    class Config:
        env_prefix = "DBTOOL_AI_"
        env_file = ".env"


settings = Settings()
```

[↑ Back to Table of Contents](#table-of-contents)

## CrewAI agent implementation

### Base agent configuration

```python
# src/dbtool_ai/agents/base.py
from crewai import Agent, LLM
from dbtool_ai.config import settings


def create_llm(model: str | None = None) -> LLM:
    """Create LLM instance configured for Ollama."""
    return LLM(
        model=f"ollama/{model or settings.default_model}",
        base_url=settings.ollama_host,
        temperature=settings.temperature,
    )


class BaseAgent:
    """Base class for dbtool-ai agents."""

    def __init__(self, model: str | None = None):
        self.llm = create_llm(model)
```

### Log analyzer agent

```python
# src/dbtool_ai/agents/log_analyzer.py
from crewai import Agent, Task, Crew
from dbtool_ai.agents.base import create_llm
from dbtool_ai.utils.sanitizer import DataSanitizer


class LogAnalyzerAgent:
    """Analyzes database error logs and identifies issues."""

    def __init__(self):
        self.sanitizer = DataSanitizer()
        self.llm = create_llm()

        self.agent = Agent(
            role="Database Log Analyst",
            goal="Analyze database error logs to identify root causes and provide actionable recommendations",
            backstory=(
                "You are an expert database administrator with 20 years of experience "
                "analyzing SQL Server, PostgreSQL, and MongoDB logs. You excel at "
                "identifying patterns, root causes, and providing clear remediation steps."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    async def analyze(self, log_content: str) -> dict:
        """Analyze log content and return findings."""
        # Sanitize input
        sanitized = self.sanitizer.sanitize(log_content)

        task = Task(
            description=f"""Analyze the following database log and provide:
1. Summary of errors/warnings found
2. Root cause analysis
3. Severity assessment (Critical/High/Medium/Low)
4. Recommended actions

Log content:
```
{sanitized}
```""",
            expected_output="JSON with keys: summary, root_cause, severity, recommendations",
            agent=self.agent,
        )

        crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
        result = crew.kickoff()

        return {
            "analysis": str(result),
            "sanitized_input": sanitized,
        }
```

### Query explainer agent

```python
# src/dbtool_ai/agents/query_explainer.py
from crewai import Agent, Task, Crew
from dbtool_ai.agents.base import create_llm
from dbtool_ai.config import settings


class QueryExplainerAgent:
    """Explains SQL queries and execution plans in plain English."""

    def __init__(self):
        self.llm = create_llm(settings.code_model)

        self.agent = Agent(
            role="SQL Query Performance Specialist",
            goal="Explain SQL queries and execution plans in clear, understandable terms",
            backstory=(
                "You are a database performance expert who specializes in query optimization. "
                "You can read complex execution plans and explain them in plain English, "
                "identifying performance bottlenecks and suggesting improvements."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    async def explain_query(self, query: str, execution_plan: str | None = None) -> dict:
        """Explain a SQL query and optionally its execution plan."""
        task_description = f"""Explain the following SQL query in plain English:

```sql
{query}
```
"""
        if execution_plan:
            task_description += f"""

Also analyze this execution plan:
```xml
{execution_plan}
```

Identify any performance concerns and suggest optimizations.
"""

        task = Task(
            description=task_description,
            expected_output="Plain English explanation with optimization suggestions if applicable",
            agent=self.agent,
        )

        crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
        result = crew.kickoff()

        return {"explanation": str(result)}
```

### Config advisor agent

```python
# src/dbtool_ai/agents/config_advisor.py
from crewai import Agent, Task, Crew
from dbtool_ai.agents.base import create_llm


class ConfigAdvisorAgent:
    """Analyzes database configurations and recommends improvements."""

    def __init__(self):
        self.llm = create_llm()

        self.agent = Agent(
            role="Database Configuration Specialist",
            goal="Analyze database configurations and recommend optimizations based on workload",
            backstory=(
                "You are a database infrastructure expert who has tuned thousands of "
                "production databases. You understand the trade-offs between different "
                "configuration options and can recommend settings based on workload patterns."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    async def analyze_config(self, config_content: str, workload_type: str = "mixed") -> dict:
        """Analyze configuration and provide recommendations."""
        task = Task(
            description=f"""Analyze this database configuration for a {workload_type} workload:

```
{config_content}
```

Provide:
1. Current configuration assessment
2. Recommended changes with justification
3. Potential risks of current settings
4. Priority order for changes (High/Medium/Low)
""",
            expected_output="Configuration analysis with prioritized recommendations",
            agent=self.agent,
        )

        crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
        result = crew.kickoff()

        return {"recommendations": str(result)}
```

### Multi-agent diagnostic crew

```python
# src/dbtool_ai/agents/diagnostic_crew.py
from crewai import Agent, Task, Crew
from dbtool_ai.agents.base import create_llm


class DiagnosticCrew:
    """Multi-agent crew for comprehensive database diagnostics."""

    def __init__(self):
        self.llm = create_llm()

        self.log_analyst = Agent(
            role="Log Analyst",
            goal="Identify errors and anomalies in database logs",
            backstory="Expert at parsing and understanding database log files",
            llm=self.llm,
            verbose=True,
        )

        self.performance_analyst = Agent(
            role="Performance Analyst",
            goal="Identify performance bottlenecks and resource constraints",
            backstory="Specialist in database performance tuning and optimization",
            llm=self.llm,
            verbose=True,
        )

        self.solution_architect = Agent(
            role="Solution Architect",
            goal="Synthesize findings and create actionable remediation plan",
            backstory="Senior architect who creates comprehensive solutions",
            llm=self.llm,
            verbose=True,
        )

    async def diagnose(self, context: dict) -> dict:
        """Run full diagnostic workflow."""
        # Task 1: Log analysis
        log_task = Task(
            description=f"Analyze these logs for errors: {context.get('logs', 'No logs provided')}",
            expected_output="List of identified issues with severity",
            agent=self.log_analyst,
        )

        # Task 2: Performance analysis
        perf_task = Task(
            description=f"Analyze performance metrics: {context.get('metrics', 'No metrics provided')}",
            expected_output="Performance assessment with bottlenecks identified",
            agent=self.performance_analyst,
        )

        # Task 3: Solution synthesis
        solution_task = Task(
            description="Based on the log and performance analysis, create a remediation plan",
            expected_output="Prioritized action plan with estimated impact",
            agent=self.solution_architect,
            context=[log_task, perf_task],
        )

        crew = Crew(
            agents=[self.log_analyst, self.performance_analyst, self.solution_architect],
            tasks=[log_task, perf_task, solution_task],
            verbose=True,
        )

        result = crew.kickoff()
        return {"diagnostic_report": str(result)}
```

[↑ Back to Table of Contents](#table-of-contents)

## FastAPI service

### API application

```python
# src/dbtool_ai/api/app.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

from dbtool_ai.config import settings
from dbtool_ai.agents.log_analyzer import LogAnalyzerAgent
from dbtool_ai.agents.query_explainer import QueryExplainerAgent
from dbtool_ai.agents.config_advisor import ConfigAdvisorAgent
from dbtool_ai.agents.diagnostic_crew import DiagnosticCrew

logger = structlog.get_logger()

# Initialize agents
log_agent: LogAnalyzerAgent | None = None
query_agent: QueryExplainerAgent | None = None
config_agent: ConfigAdvisorAgent | None = None
diagnostic_crew: DiagnosticCrew | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agents on startup."""
    global log_agent, query_agent, config_agent, diagnostic_crew

    logger.info("Initializing AI agents...")
    log_agent = LogAnalyzerAgent()
    query_agent = QueryExplainerAgent()
    config_agent = ConfigAdvisorAgent()
    diagnostic_crew = DiagnosticCrew()
    logger.info("AI agents initialized")

    yield

    logger.info("Shutting down...")


app = FastAPI(
    title="dbtool-ai",
    description="AI-powered database operations assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class LogAnalysisRequest(BaseModel):
    content: str
    max_lines: int = 500


class LogAnalysisResponse(BaseModel):
    analysis: str
    sanitized_input: str


class QueryExplainRequest(BaseModel):
    query: str
    execution_plan: str | None = None


class QueryExplainResponse(BaseModel):
    explanation: str


class ConfigAnalysisRequest(BaseModel):
    config_content: str
    workload_type: str = "mixed"


class ConfigAnalysisResponse(BaseModel):
    recommendations: str


class DiagnosticRequest(BaseModel):
    logs: str | None = None
    metrics: dict | None = None
    config: str | None = None


class DiagnosticResponse(BaseModel):
    diagnostic_report: str


# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": settings.default_model}


@app.post("/api/v1/analyze-log", response_model=LogAnalysisResponse)
async def analyze_log(request: LogAnalysisRequest):
    """Analyze database error logs."""
    if not log_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        result = await log_agent.analyze(request.content)
        return LogAnalysisResponse(**result)
    except Exception as e:
        logger.error("Log analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/explain-query", response_model=QueryExplainResponse)
async def explain_query(request: QueryExplainRequest):
    """Explain SQL query and execution plan."""
    if not query_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        result = await query_agent.explain_query(request.query, request.execution_plan)
        return QueryExplainResponse(**result)
    except Exception as e:
        logger.error("Query explanation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/suggest-config", response_model=ConfigAnalysisResponse)
async def suggest_config(request: ConfigAnalysisRequest):
    """Analyze database configuration."""
    if not config_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        result = await config_agent.analyze_config(request.config_content, request.workload_type)
        return ConfigAnalysisResponse(**result)
    except Exception as e:
        logger.error("Config analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/diagnose", response_model=DiagnosticResponse)
async def diagnose(request: DiagnosticRequest):
    """Run full diagnostic workflow."""
    if not diagnostic_crew:
        raise HTTPException(status_code=503, detail="Diagnostic crew not initialized")

    try:
        context = {
            "logs": request.logs,
            "metrics": request.metrics,
            "config": request.config,
        }
        result = await diagnostic_crew.diagnose(context)
        return DiagnosticResponse(**result)
    except Exception as e:
        logger.error("Diagnostic failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
```

### Run the service

```bash
# Development
uvicorn dbtool_ai.api.app:app --reload --host 0.0.0.0 --port 8080

# Production
uvicorn dbtool_ai.api.app:app --host 0.0.0.0 --port 8080 --workers 4
```

[↑ Back to Table of Contents](#table-of-contents)

## Docker deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-dev

# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Expose port
EXPOSE 8080

# Run application
CMD ["uv", "run", "uvicorn", "dbtool_ai.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.9"

services:
  dbtool-ai:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DBTOOL_AI_OLLAMA_HOST=http://ollama:11434
      - DBTOOL_AI_DEFAULT_MODEL=llama3.1:8b
      - DBTOOL_AI_LOG_LEVEL=INFO
    depends_on:
      ollama:
        condition: service_healthy
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

volumes:
  ollama_data:
```

### Deploy with Docker

```bash
# Build and start
docker compose up -d

# Check logs
docker compose logs -f

# Download models (first time)
docker compose exec ollama ollama pull llama3.1:8b
docker compose exec ollama ollama pull qwen2.5:7b

# Test API
curl http://localhost:8080/health
```

[↑ Back to Table of Contents](#table-of-contents)

## Testing and validation

### Unit tests

```python
# tests/test_agents.py
import pytest
from dbtool_ai.agents.log_analyzer import LogAnalyzerAgent
from dbtool_ai.utils.sanitizer import DataSanitizer


class TestDataSanitizer:
    def test_sanitize_ip_address(self):
        sanitizer = DataSanitizer()
        text = "Connection from 192.168.1.100 failed"
        result = sanitizer.sanitize(text)
        assert "192.168.1.100" not in result
        assert "[REDACTED_IP_ADDRESS]" in result

    def test_sanitize_password(self):
        sanitizer = DataSanitizer()
        text = "Connection string: password=secret123"
        result = sanitizer.sanitize(text)
        assert "secret123" not in result


@pytest.mark.asyncio
class TestLogAnalyzerAgent:
    async def test_analyze_simple_log(self):
        agent = LogAnalyzerAgent()
        log = "ERROR: database connection failed - timeout after 30s"
        result = await agent.analyze(log)
        assert "analysis" in result
        assert len(result["analysis"]) > 0
```

### Integration tests

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from dbtool_ai.api.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_log(client):
    response = client.post(
        "/api/v1/analyze-log",
        json={"content": "ERROR: connection timeout"}
    )
    assert response.status_code == 200
    assert "analysis" in response.json()
```

### Run tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/dbtool_ai --cov-report=html
```

[↑ Back to Table of Contents](#table-of-contents)

## Production deployment

### Systemd service

```ini
# /etc/systemd/system/dbtool-ai.service
[Unit]
Description=dbtool-ai AI Service
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=dbtool
Group=dbtool
WorkingDirectory=/opt/dbtool-ai
ExecStart=/opt/dbtool-ai/.venv/bin/uvicorn dbtool_ai.api.app:app --host 0.0.0.0 --port 8080 --workers 4
Restart=always
RestartSec=10

Environment=DBTOOL_AI_OLLAMA_HOST=http://localhost:11434
Environment=DBTOOL_AI_LOG_LEVEL=INFO

[Install]
WantedBy=multi-user.target
```

### Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable dbtool-ai
sudo systemctl start dbtool-ai
sudo systemctl status dbtool-ai
```

### Monitoring

```bash
# Check service logs
journalctl -u dbtool-ai -f

# Check GPU utilization
watch -n 1 nvidia-smi

# Check API metrics (if Prometheus enabled)
curl http://localhost:8080/metrics
```

[↑ Back to Table of Contents](#table-of-contents)
