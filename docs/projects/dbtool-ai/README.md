# Project: dbtool-ai

**Status**: 🟡 Initiation

This project defines the "AI Agent" companion to the `dbtool-cli` ecosystem. It is a separate service/library designed to leverage Local LLMs (via Ollama) for advanced database troubleshooting, log analysis, and query explanation, without bloating the core Ops CLI.

## 1. Core Architecture

The integration follows a "Sidecar" or "Plugin" pattern.

```mermaid
graph TD
    CLI[dbtool CLI] -->|API Call| AI_Service[dbtool-ai Service]
    AI_Service -->|Inference| Ollama[Ollama Server (Localhost)]
    Ollama -->|Load| Model[Local LLM (Llama3/Mistral)]
```

## 2. Technology Stack

- **Runtime**: Python 3.12+
- **Engine**: **Ollama** (Local Inference).
- **Framework**: **CrewAI** (Agent Orchestration) or **LangGraph**.
- **Interface**: REST API (FastAPI) or CLI Plugin.

## 3. Hardware Requirements

Local AI requires hardware acceleration for acceptable performance.

| Component | Minimum (Concept) | Recommended (Production/Dev) | Notes |
| :--- | :--- | :--- | :--- |
| **GPU (NVIDIA)** | 4GB VRAM (GTX 1650) | **16GB+ VRAM** (RTX 4080 / A1000) | Crucial for "Quantized" models (4-bit). |
| **RAM (System)** | 16GB | **32GB+** | AI Models load into RAM if VRAM is insufficient. |
| **CPU** | 8 Core (i7/Ryzen 7) | 12+ Core | Fallback inference (slow but functional). |
| **Storage** | 20GB SSD | 100GB NVMe | Model weights are large (Llama3-8B is ~5GB). |

*Note: For machines without GPUs (standard laptops), we recommend using specialized "Small Language Models" (SLMs) like **Phi-3** or **Gemma-2B** which are optimized for CPU usage.*

## 4. Key Use Cases

1. **Log Analysis (Privacy Safe)**:
    - *Scenario*: SQL Server Error Logs contain PII.
    - *Flow*: `dbtool` sends log chunk -> `dbtool-ai` sanitizes & analyzes -> Returns summary.
2. **Query Explanation**:
    - *Scenario*: Complex execution plans.
    - *Flow*: `dbtool-ai` explains "Nested Loops vs Hash Match" in plain English.
3. **Config Tuning**:
    - *Scenario*: `postgres.conf` analysis.

## 5. Separation of Concerns

This project is separated from `dbtool-cli` to:

1. **Isolate Dependencies**: Avoid installing heavy ML libraries (Torch, LangChain) on every Ops machine.
2. **Lifecycle**: Allow the AI service to evolve rapidly (Research) while the Core CLI remains stable (Ops).
