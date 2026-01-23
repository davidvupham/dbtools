# local-ai-hub: LLM model selection guide

**[← Back to local-ai-hub Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Reference-blue)

> [!IMPORTANT]
> **Related Docs:** [Hardware Requirements](./hardware-requirements.md) | [Architecture](./architecture.md) | [Implementation Guide](./implementation-guide.md)

## Table of contents

- [Selection criteria](#selection-criteria)
- [Recommended models](#recommended-models)
- [Model comparison matrix](#model-comparison-matrix)
- [Model families overview](#model-families-overview)
- [Use case recommendations](#use-case-recommendations)
- [Licensing considerations](#licensing-considerations)
- [Evaluation methodology](#evaluation-methodology)
- [Model versioning and updates](#model-versioning-and-updates)

## Selection criteria

When selecting an LLM for on-premise deployment, consider these factors:

### Primary criteria

| Criterion | Weight | Description |
|:----------|:-------|:------------|
| **License** | Critical | Must allow commercial use without restrictions |
| **Performance** | High | Quality of outputs for database tasks |
| **Resource efficiency** | High | VRAM and compute requirements |
| **Tool calling** | High | Native function/tool calling support for MCP |
| **Context length** | Medium | Maximum input size for log analysis |
| **Community support** | Medium | Documentation, fine-tunes, troubleshooting |

### Secondary criteria

| Criterion | Description |
|:----------|:------------|
| **Quantization support** | Availability of optimized quantized versions |
| **Multilingual** | Support for non-English documentation/logs |
| **Code understanding** | SQL, Python, configuration file parsing |
| **Update frequency** | Active development and improvements |

[↑ Back to Table of Contents](#table-of-contents)

## Recommended models

### Primary recommendation: Llama 3.1/3.3

**Why Llama**: Industry standard, excellent performance, permissive license, extensive ecosystem

| Variant | Parameters | VRAM (Q4) | Best For |
|:--------|:-----------|:----------|:---------|
| Llama 3.1 8B | 8B | 4.9 GB | Development, single-user, fast responses |
| Llama 3.1 70B | 70B | 40 GB | Production, complex analysis |
| Llama 3.3 70B | 70B | 40 GB | Latest, improved reasoning |

**Ollama installation**:
```bash
ollama pull llama3.1:8b
ollama pull llama3.1:70b
ollama pull llama3.3:70b
```

---

### Alternative: Qwen 2.5

**Why Qwen**: Excellent tool calling, strong on code, good multilingual support

| Variant | Parameters | VRAM (Q4) | Best For |
|:--------|:-----------|:----------|:---------|
| Qwen 2.5 7B | 7B | 4.5 GB | MCP integration, tool calling |
| Qwen 2.5 14B | 14B | 8.5 GB | Balanced performance |
| Qwen 2.5 72B | 72B | 42 GB | Production, complex tasks |
| Qwen 2.5 Coder | 7B/32B | 4.5/19 GB | Code-heavy tasks |

**Ollama installation**:
```bash
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
ollama pull qwen2.5:72b
ollama pull qwen2.5-coder:7b
```

> [!NOTE]
> Qwen 2.5 has some of the best native tool calling capabilities, making it ideal for MCP integration.

---

### Alternative: Mistral

**Why Mistral**: Efficient architecture, good performance-to-size ratio

| Variant | Parameters | VRAM (Q4) | Best For |
|:--------|:-----------|:----------|:---------|
| Mistral 7B | 7B | 4.4 GB | Fast inference, low resources |
| Mixtral 8x7B | 46.7B (12.9B active) | 26 GB | MoE efficiency |
| Mistral Large | 123B | 70 GB | Highest quality |

**Ollama installation**:
```bash
ollama pull mistral:7b
ollama pull mixtral:8x7b
ollama pull mistral-large:latest
```

---

### Specialized: DeepSeek Coder

**Why DeepSeek Coder**: Purpose-built for code understanding and generation

| Variant | Parameters | VRAM (Q4) | Best For |
|:--------|:-----------|:----------|:---------|
| DeepSeek Coder V2 Lite | 16B | 9.5 GB | SQL, query analysis |
| DeepSeek Coder V2 | 236B | 135 GB | Complex code tasks |

**Ollama installation**:
```bash
ollama pull deepseek-coder-v2:16b
ollama pull deepseek-coder-v2:236b
```

> [!WARNING]
> DeepSeek reasoning models (R1) do not support tool calling and are not compatible with MCP.

---

### CPU-only: Small Language Models (SLMs)

For environments without GPUs:

| Model | Parameters | RAM Required | Speed (CPU) |
|:------|:-----------|:-------------|:------------|
| Phi-3 Mini | 3.8B | 4-6 GB | 10-20 t/s |
| Gemma 2 2B | 2B | 3-4 GB | 15-25 t/s |
| Qwen 2.5 0.5B | 0.5B | 1-2 GB | 30-50 t/s |
| TinyLlama 1.1B | 1.1B | 2-3 GB | 20-30 t/s |

**Ollama installation**:
```bash
ollama pull phi3:mini
ollama pull gemma2:2b
ollama pull qwen2.5:0.5b
```

[↑ Back to Table of Contents](#table-of-contents)

## Model comparison matrix

### Overall comparison

| Model | Quality | Speed | VRAM | Tool Calling | License | Recommendation |
|:------|:--------|:------|:-----|:-------------|:--------|:---------------|
| Llama 3.1 8B | Good | Fast | Low | Good | Llama 3 | **Development** |
| Llama 3.1 70B | Excellent | Medium | High | Good | Llama 3 | **Production** |
| Qwen 2.5 7B | Good | Fast | Low | Excellent | Apache 2.0 | **MCP Focus** |
| Qwen 2.5 72B | Excellent | Medium | High | Excellent | Apache 2.0 | **Enterprise** |
| Mistral 7B | Good | Fastest | Lowest | Good | Apache 2.0 | **Speed Priority** |
| Mixtral 8x7B | Very Good | Good | Medium | Good | Apache 2.0 | **Balanced** |
| DeepSeek Coder | Excellent (code) | Medium | Medium | Limited | MIT | **Code Tasks** |
| Phi-3 Mini | Moderate | Slow (CPU) | Very Low | Basic | MIT | **CPU Only** |

### Benchmark scores (approximate)

| Model | MMLU | HumanEval | SQL Tasks* | Log Analysis* |
|:------|:-----|:----------|:-----------|:--------------|
| Llama 3.1 8B | 68% | 62% | Good | Good |
| Llama 3.1 70B | 82% | 81% | Excellent | Excellent |
| Qwen 2.5 7B | 70% | 65% | Good | Good |
| Qwen 2.5 72B | 84% | 83% | Excellent | Excellent |
| Mistral 7B | 62% | 58% | Good | Good |
| DeepSeek Coder 16B | 72% | 79% | Excellent | Moderate |

*Internal evaluation criteria

[↑ Back to Table of Contents](#table-of-contents)

## Model families overview

### Meta Llama family

```text
Llama 3.x Series (2024-2025)
├── Llama 3.1 8B    - Entry level, fast
├── Llama 3.1 70B   - Production workhorse
├── Llama 3.1 405B  - Maximum capability (requires cluster)
├── Llama 3.2 1B/3B - Mobile/edge optimized
├── Llama 3.2 11B/90B Vision - Multimodal
└── Llama 3.3 70B   - Improved reasoning

Llama 4 Series (2025)
├── Llama 4 Scout   - Efficient, 17B active (MoE)
└── Llama 4 Maverick - Advanced, larger MoE
```

**Key features**:
- Most widely adopted open-source LLM
- Extensive fine-tune ecosystem
- Strong general-purpose capabilities
- 128K context window (3.1+)

**License**: Llama 3 Community License (commercial use allowed, some restrictions on >700M MAU)

---

### Alibaba Qwen family

```text
Qwen 2.5 Series (2024-2025)
├── Qwen 2.5 0.5B/1.5B/3B - Edge/mobile
├── Qwen 2.5 7B/14B       - Mainstream
├── Qwen 2.5 32B          - Mid-range
├── Qwen 2.5 72B          - High-end
├── Qwen 2.5 Coder        - Code specialized
├── Qwen 2.5 Math         - Math specialized
└── Qwen 2.5 Turbo        - Speed optimized

Qwen 3 Series (2025)
└── Qwen 3 235B MoE       - Mixture of Experts
```

**Key features**:
- Excellent native tool/function calling
- Strong multilingual (29+ languages)
- Specialized variants (coder, math)
- Apache 2.0 license (truly open)

**License**: Apache 2.0 (fully permissive)

---

### Mistral AI family

```text
Mistral Series (2023-2025)
├── Mistral 7B        - Original efficient model
├── Mixtral 8x7B      - MoE architecture
├── Mixtral 8x22B     - Larger MoE
├── Mistral Small     - Optimized 22B
├── Mistral Medium    - Deprecated
├── Mistral Large     - 123B flagship
└── Codestral        - Code specialized
```

**Key features**:
- Pioneer of efficient small models
- Sliding window attention
- Strong European data handling
- Good price/performance ratio

**License**: Apache 2.0 (open models), Commercial (Mistral Large)

---

### DeepSeek family

```text
DeepSeek Series (2024-2025)
├── DeepSeek-V2       - General purpose
├── DeepSeek-V3       - Improved general
├── DeepSeek-Coder-V2 - Code specialized
├── DeepSeek-R1       - Reasoning focused
└── DeepSeek-R1-Distill - Smaller reasoning
```

**Key features**:
- Exceptional coding capabilities
- Competitive with GPT-4 on benchmarks
- Cost-effective training approach
- Strong reasoning (R1 series)

**License**: MIT (highly permissive)

> [!WARNING]
> DeepSeek-R1 reasoning models use chain-of-thought that is incompatible with tool calling. Do not use for MCP integration.

[↑ Back to Table of Contents](#table-of-contents)

## Use case recommendations

### By task type

| Use Case | Recommended Model | Alternative | Notes |
|:---------|:------------------|:------------|:------|
| **Log analysis** | Llama 3.1 8B | Qwen 2.5 7B | Fast, handles structured text |
| **Query explanation** | Qwen 2.5-Coder 7B | DeepSeek Coder | SQL understanding |
| **Config tuning** | Llama 3.1 70B | Qwen 2.5 72B | Needs reasoning |
| **Error diagnosis** | Llama 3.1 70B | Qwen 2.5 72B | Complex analysis |
| **MCP tool calling** | Qwen 2.5 7B | Llama 3.1 8B | Best tool support |
| **Multi-agent crews** | Llama 3.1 8B | Mistral 7B | Balance speed/quality |

### By hardware tier

| Hardware | Primary Model | Secondary Model |
|:---------|:--------------|:----------------|
| **Consumer GPU (12-16GB)** | Llama 3.1 8B | Qwen 2.5 7B |
| **Prosumer GPU (24GB)** | Llama 3.1 8B + Qwen 2.5 14B | Mixtral 8x7B (Q4) |
| **Workstation (48GB)** | Llama 3.1 70B (Q4) | Qwen 2.5 72B (Q4) |
| **Server (80GB)** | Llama 3.1 70B | Qwen 2.5 72B |
| **Multi-GPU (160GB+)** | Llama 3.1 70B (FP16) | Multiple models |
| **CPU-only** | Phi-3 Mini | Qwen 2.5 0.5B |

### Recommended model combinations

For production deployment, we recommend running multiple models:

**Tier 2 setup (24GB VRAM)**:
```bash
# Fast model for simple tasks
ollama pull llama3.1:8b

# Code-focused for SQL
ollama pull qwen2.5-coder:7b
```

**Tier 3 setup (80GB VRAM)**:
```bash
# Primary production model
ollama pull llama3.1:70b

# Fast model for simple queries
ollama pull qwen2.5:7b

# Code specialist
ollama pull deepseek-coder-v2:16b
```

[↑ Back to Table of Contents](#table-of-contents)

## Licensing considerations

### License comparison

| Model Family | License | Commercial Use | Modifications | Attribution |
|:-------------|:--------|:---------------|:--------------|:------------|
| Llama 3.x | Llama 3 Community | Yes* | Yes | Required |
| Qwen 2.5 | Apache 2.0 | Yes | Yes | Required |
| Mistral (open) | Apache 2.0 | Yes | Yes | Required |
| DeepSeek | MIT | Yes | Yes | Required |
| Phi-3 | MIT | Yes | Yes | Required |
| Gemma 2 | Gemma Terms | Yes* | Yes | Required |

*Subject to specific terms (e.g., >700M MAU restrictions for Llama)

### Enterprise licensing notes

1. **Llama 3 Community License**:
   - Free for commercial use
   - Must accept license agreement
   - Additional terms for >700M monthly active users
   - Cannot use outputs to train competing models

2. **Apache 2.0** (Qwen, Mistral open models):
   - Fully permissive
   - Can use, modify, distribute freely
   - Must include license and attribution
   - No patent claims against users

3. **MIT** (DeepSeek, Phi):
   - Most permissive
   - Minimal restrictions
   - Only requires license inclusion

> [!IMPORTANT]
> Always verify current license terms before deployment. Consult legal for enterprise use cases.

[↑ Back to Table of Contents](#table-of-contents)

## Evaluation methodology

### Evaluation criteria for dbtool-ai

| Category | Weight | Metrics |
|:---------|:-------|:--------|
| **Log analysis** | 25% | Error identification accuracy, summary quality |
| **SQL understanding** | 25% | Query explanation accuracy, plan interpretation |
| **Tool calling** | 20% | Function call accuracy, parameter extraction |
| **Response quality** | 15% | Coherence, actionability, formatting |
| **Speed** | 15% | Tokens/second, time to first token |

### Sample evaluation prompts

**Log analysis**:
```text
Analyze this SQL Server error log and identify the root cause:
[sample error log content]

Expected output: Clear identification of error, likely cause, remediation steps
```

**Query explanation**:
```text
Explain this execution plan in plain English. What optimizations would you suggest?
[sample execution plan XML]

Expected output: Plain English explanation, specific optimization recommendations
```

**Tool calling**:
```text
User wants to analyze the database logs from /var/log/mssql/errorlog for the last hour.

Expected output: Correct function call with appropriate parameters
```

### Evaluation process

1. **Prepare test dataset**: 50+ samples per category
2. **Run inference**: Same prompts across all candidate models
3. **Human evaluation**: Rate outputs 1-5 on accuracy and usefulness
4. **Automated metrics**: Measure speed, resource usage
5. **Score and rank**: Weighted scoring based on criteria
6. **Sensitivity analysis**: Test with quantized versions

[↑ Back to Table of Contents](#table-of-contents)

## Model versioning and updates

### Version management strategy

```text
/var/lib/ollama/models/
├── llama3.1-8b-v1.0/          # Baseline version
├── llama3.1-8b-v1.1/          # Updated version
├── llama3.1-8b-current -> v1.1 # Symlink to current
└── qwen2.5-7b-v1.0/
```

### Update policy

| Update Type | Frequency | Testing Required | Rollback Plan |
|:------------|:----------|:-----------------|:--------------|
| **Security patches** | Immediate | Smoke tests | Keep previous version |
| **Minor updates** | Monthly | Full regression | Keep N-1 version |
| **Major updates** | Quarterly | Full evaluation | Keep N-2 versions |
| **New model adoption** | As needed | Full evaluation | Parallel deployment |

### Model refresh checklist

- [ ] Review release notes for changes
- [ ] Download to staging environment
- [ ] Run evaluation suite
- [ ] Compare with current version
- [ ] Update documentation
- [ ] Deploy with rollback plan
- [ ] Monitor for regressions
- [ ] Clean up old versions (keep N-2)

[↑ Back to Table of Contents](#table-of-contents)
