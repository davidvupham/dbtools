# local-ai-hub: Hardware requirements guide

**[← Back to local-ai-hub Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Reference-blue)

> [!IMPORTANT]
> **Related Docs:** [Architecture](./architecture.md) | [LLM Model Selection](./llm-model-selection.md) | [Implementation Guide](./implementation-guide.md)

## Table of contents

- [Overview](#overview)
- [VRAM requirements by model size](#vram-requirements-by-model-size)
- [Hardware tiers](#hardware-tiers)
- [GPU recommendations](#gpu-recommendations)
- [System requirements](#system-requirements)
- [Quantization and optimization](#quantization-and-optimization)
- [Performance benchmarks](#performance-benchmarks)
- [Procurement recommendations](#procurement-recommendations)
- [Hardware configurations for 70B models](#hardware-configurations-for-70b-models)
- [Cost analysis](#cost-analysis)

## Overview

Local LLM inference requires significant computational resources, primarily GPU memory (VRAM). This guide helps you select appropriate hardware based on your model requirements, user concurrency, and performance expectations.

### Key factors affecting hardware needs

| Factor | Impact |
|:-------|:-------|
| **Model parameters** | Larger models require more VRAM |
| **Quantization level** | Lower bits = less VRAM, slightly lower quality |
| **Context length** | Longer contexts need more memory for KV cache |
| **Batch size** | More concurrent users = more memory |
| **Response speed** | Higher throughput needs more compute power |

[↑ Back to Table of Contents](#table-of-contents)

## VRAM requirements by model size

### General VRAM guidelines

| Model Size | Parameters | FP16 VRAM | Q8 VRAM | Q4 VRAM | Recommended For |
|:-----------|:-----------|:----------|:--------|:--------|:----------------|
| **Tiny** | 1-3B | 2-6 GB | 1-3 GB | 0.5-2 GB | Edge devices, testing |
| **Small** | 7-8B | 14-16 GB | 8-9 GB | 4-5 GB | Development, single user |
| **Medium** | 13-14B | 26-28 GB | 14-16 GB | 7-8 GB | Small teams |
| **Large** | 30-34B | 60-68 GB | 34-38 GB | 17-20 GB | Production workloads |
| **XL** | 70B | 140 GB | 70-80 GB | 35-40 GB | Enterprise, multi-user |
| **XXL** | 70B+ MoE | 200+ GB | 100+ GB | 50+ GB | High-end enterprise |

### Specific model VRAM requirements

| Model | Size | Q4_K_M VRAM | Q8_0 VRAM | Tokens/sec (RTX 4090) |
|:------|:-----|:------------|:----------|:----------------------|
| Llama 3.1 8B | 8B | 4.9 GB | 8.5 GB | 80-100 |
| Llama 3.1 70B | 70B | 40.0 GB | 74.0 GB | 15-25 |
| Mistral 7B | 7B | 4.4 GB | 7.7 GB | 90-110 |
| Mistral Large (123B) | 123B | 70.0 GB | 130.0 GB | 8-15 |
| Qwen 2.5 7B | 7B | 4.5 GB | 7.8 GB | 85-105 |
| Qwen 2.5 72B | 72B | 42.0 GB | 76.0 GB | 14-22 |
| DeepSeek-Coder 6.7B | 6.7B | 4.2 GB | 7.2 GB | 95-115 |
| Phi-3 Mini (3.8B) | 3.8B | 2.3 GB | 4.0 GB | 120-150 |

> [!NOTE]
> VRAM requirements increase with context length. Add ~0.5 GB per 4K context tokens for 7B models, ~2 GB per 4K for 70B models.

[↑ Back to Table of Contents](#table-of-contents)

## Hardware tiers

### Tier 1: Development / proof of concept

**Use case**: Individual developer testing, proof of concept, evaluation

| Component | Specification | Notes |
|:----------|:--------------|:------|
| **GPU** | NVIDIA RTX 3060 12GB or RTX 4060 Ti 16GB | Consumer-grade |
| **CPU** | Intel i7/i9 or AMD Ryzen 7/9 (8+ cores) | For CPU fallback |
| **RAM** | 32 GB DDR4/DDR5 | Model offloading |
| **Storage** | 500 GB NVMe SSD | Model storage |
| **OS** | Ubuntu 22.04 LTS / Windows 11 | CUDA support |

**Supported models**: 7B-8B (full precision), 13B-14B (quantized)

**Estimated cost**: $1,500 - $2,500 (workstation)

---

### Tier 2: Small team / departmental

**Use case**: 5-10 concurrent users, production pilot

| Component | Specification | Notes |
|:----------|:--------------|:------|
| **GPU** | NVIDIA RTX 4090 24GB or RTX A4000 16GB | Prosumer/workstation |
| **CPU** | Intel Xeon or AMD EPYC (16+ cores) | Parallel processing |
| **RAM** | 64 GB DDR5 ECC | Reliability |
| **Storage** | 1 TB NVMe SSD | Multiple models |
| **OS** | Ubuntu 22.04 LTS Server | Production OS |

**Supported models**: 7B-8B (full), 30B-34B (quantized), 70B (heavily quantized)

**Estimated cost**: $5,000 - $15,000 (workstation/entry server)

---

### Tier 3: Production / enterprise

**Use case**: 20+ concurrent users, production deployment

| Component | Specification | Notes |
|:----------|:--------------|:------|
| **GPU** | NVIDIA A100 40GB/80GB or H100 80GB | Data center grade |
| **CPU** | Dual Intel Xeon or AMD EPYC (32+ cores) | High throughput |
| **RAM** | 128-256 GB DDR5 ECC | Large context, caching |
| **Storage** | 2+ TB NVMe RAID | Model versioning |
| **Network** | 25 GbE | Multi-node inference |
| **OS** | Ubuntu 22.04 LTS / RHEL 9 | Enterprise support |

**Supported models**: All sizes up to 70B (full precision), 200B+ (quantized/MoE)

**Estimated cost**: $20,000 - $100,000+ (server)

---

### Tier 4: Multi-GPU cluster

**Use case**: 100+ concurrent users, multiple large models

| Component | Specification | Notes |
|:----------|:--------------|:------|
| **GPU** | 4-8x NVIDIA H100 80GB (NVLink) | Tensor parallelism |
| **CPU** | Dual AMD EPYC 9004 (64+ cores) | Orchestration |
| **RAM** | 512 GB - 1 TB DDR5 ECC | Large batch processing |
| **Storage** | 10+ TB NVMe (distributed) | Model farm |
| **Network** | 100 GbE / InfiniBand | GPU-to-GPU comms |
| **OS** | Ubuntu 22.04 / RHEL 9 | Kubernetes ready |

**Supported models**: All models including 405B Llama, mixture-of-experts

**Estimated cost**: $200,000 - $1,000,000+ (HPC cluster)

[↑ Back to Table of Contents](#table-of-contents)

## GPU recommendations

### Consumer GPUs (Tier 1-2)

| GPU | VRAM | CUDA Cores | TDP | Price (Est.) | Best For |
|:----|:-----|:-----------|:----|:-------------|:---------|
| RTX 3060 | 12 GB | 3584 | 170W | $300 | Budget development |
| RTX 4060 Ti | 16 GB | 4352 | 165W | $450 | Development |
| RTX 4070 Ti Super | 16 GB | 8448 | 285W | $800 | Small team |
| RTX 4080 Super | 16 GB | 10240 | 320W | $1,000 | Small team |
| RTX 4090 | 24 GB | 16384 | 450W | $1,600 | Best consumer |
| RTX 5090 | 32 GB | 21760 | 575W | $2,000 | Latest consumer |

### Professional GPUs (Tier 2-3)

| GPU | VRAM | Tensor Cores | TDP | Price (Est.) | Best For |
|:----|:-----|:-------------|:----|:-------------|:---------|
| RTX A4000 | 16 GB | 192 | 140W | $1,000 | Workstation |
| RTX A5000 | 24 GB | 256 | 230W | $2,500 | Professional |
| RTX A6000 | 48 GB | 336 | 300W | $4,500 | Production |
| L40S | 48 GB | 568 | 350W | $8,000 | Data center |

### Data center GPUs (Tier 3-4)

| GPU | VRAM | Tensor Cores | TDP | Price (Est.) | Best For |
|:----|:-----|:-------------|:----|:-------------|:---------|
| A100 PCIe | 40/80 GB | 432 | 250/300W | $10,000-20,000 | Enterprise |
| H100 PCIe | 80 GB | 528 | 350W | $25,000-35,000 | High-end enterprise |
| H100 SXM | 80 GB | 528 | 700W | $35,000-45,000 | HPC clusters |
| H200 | 141 GB | 528 | 700W | $40,000+ | Latest data center |

> [!WARNING]
> GPU prices fluctuate significantly. Verify current pricing before procurement. Consider used/refurbished A100s for cost savings.

[↑ Back to Table of Contents](#table-of-contents)

## System requirements

### Minimum system requirements

| Component | Minimum | Recommended |
|:----------|:--------|:------------|
| **Operating System** | Ubuntu 20.04, Windows 10 | Ubuntu 22.04 LTS |
| **NVIDIA Driver** | 525.x | 545.x or newer |
| **CUDA Toolkit** | 11.8 | 12.x |
| **Python** | 3.9 | 3.11 or 3.12 |
| **Docker** | 24.0 | 25.x with NVIDIA runtime |

### Storage requirements

| Item | Size | Notes |
|:-----|:-----|:------|
| Base Ollama install | 500 MB | Runtime only |
| 7B model (Q4) | 4-5 GB | Per model |
| 7B model (FP16) | 14-16 GB | Per model |
| 70B model (Q4) | 35-40 GB | Per model |
| Model cache/temp | 10-20 GB | Working space |
| **Recommended total** | 200-500 GB | Multiple models |

### Network requirements

| Scenario | Bandwidth | Latency |
|:---------|:----------|:--------|
| Single server | N/A (localhost) | < 1 ms |
| API clients | 1 Gbps | < 10 ms |
| Multi-GPU inference | 25-100 Gbps | < 1 ms |
| Model downloads | 100+ Mbps | Varies |

[↑ Back to Table of Contents](#table-of-contents)

## Quantization and optimization

### Quantization levels explained

Quantization reduces model precision to decrease VRAM usage with minimal quality loss.

| Quantization | Bits | VRAM Savings | Quality Impact | Use Case |
|:-------------|:-----|:-------------|:---------------|:---------|
| FP16 | 16-bit | Baseline | None | Unlimited VRAM |
| Q8_0 | 8-bit | ~50% | Negligible | Production |
| Q6_K | 6-bit | ~62% | Very minor | Balanced |
| Q5_K_M | 5-bit | ~69% | Minor | Memory constrained |
| Q4_K_M | 4-bit | ~75% | Noticeable | Consumer GPUs |
| Q3_K_M | 3-bit | ~81% | Significant | Extreme constraint |
| Q2_K | 2-bit | ~87% | Severe | Testing only |

> [!NOTE]
> **Recommended**: Q4_K_M provides the best balance of quality and VRAM savings for most use cases. Use Q8_0 when VRAM permits for better quality.

### Optimization techniques

| Technique | Description | VRAM Impact | Speed Impact |
|:----------|:------------|:------------|:-------------|
| **Quantization** | Reduce weight precision | 50-80% reduction | Slight increase |
| **Flash Attention** | Efficient attention computation | 20-40% reduction | 2-3x faster |
| **KV Cache Quantization** | Quantize attention cache | 30-50% reduction | Minimal |
| **Tensor Parallelism** | Split model across GPUs | Linear scaling | Near-linear |
| **PagedAttention** | Dynamic memory allocation | Variable | Improved batching |

### Context length impact on VRAM

| Context Length | 7B Model | 70B Model |
|:---------------|:---------|:----------|
| 2K tokens | +0.1 GB | +0.5 GB |
| 4K tokens | +0.2 GB | +1.0 GB |
| 8K tokens | +0.5 GB | +2.0 GB |
| 32K tokens | +2.0 GB | +8.0 GB |
| 128K tokens | +8.0 GB | +32.0 GB |

[↑ Back to Table of Contents](#table-of-contents)

## Performance benchmarks

### Tokens per second by hardware

| Hardware | Llama 3.1 8B (Q4) | Llama 3.1 70B (Q4) | Notes |
|:---------|:------------------|:-------------------|:------|
| RTX 3060 12GB | 25-35 t/s | N/A | 8B only |
| RTX 4060 Ti 16GB | 40-50 t/s | N/A | 8B only |
| RTX 4090 24GB | 80-100 t/s | N/A | 8B; can't fit 70B Q4 |
| RTX A6000 48GB | 60-80 t/s | 12-18 t/s | 70B barely fits |
| A100 80GB | 90-120 t/s | 25-35 t/s | Production grade |
| H100 80GB | 150-200 t/s | 45-60 t/s | Highest throughput |
| 2x A100 80GB | 170-220 t/s | 50-70 t/s | Tensor parallel |

### Latency expectations

| Model Size | First Token | Generation (per token) |
|:-----------|:------------|:-----------------------|
| 7-8B | 100-300 ms | 10-40 ms |
| 30-34B | 300-800 ms | 25-80 ms |
| 70B | 500-1500 ms | 40-150 ms |

### Concurrent user capacity

| Hardware | 7B Model | 70B Model | Notes |
|:---------|:---------|:----------|:------|
| RTX 4090 | 3-5 users | N/A | Limited batching |
| A100 40GB | 10-15 users | 2-4 users | vLLM recommended |
| A100 80GB | 20-30 users | 5-10 users | vLLM recommended |
| 2x H100 | 50-100 users | 20-40 users | Production scale |

[↑ Back to Table of Contents](#table-of-contents)

## Procurement recommendations

### Option 1: Repurpose existing hardware

**Best for**: Proof of concept, budget-constrained projects

1. Inventory existing GPU workstations
2. Prioritize machines with 16GB+ VRAM
3. Upgrade RAM to 32GB+ if needed
4. Install Ubuntu or use WSL2

**Pros**: Zero CapEx, fast start
**Cons**: Limited model options, shared resources

### Option 2: Workstation purchase

**Best for**: Small teams, departmental use

**Recommended configurations**:

| Config | Components | Est. Cost |
|:-------|:-----------|:----------|
| Entry | RTX 4070 Ti Super, 64GB RAM, 1TB NVMe | $3,000 |
| Standard | RTX 4090, 64GB RAM, 2TB NVMe | $5,000 |
| Professional | RTX A6000, 128GB RAM, 4TB NVMe | $12,000 |

**Vendors**: Dell Precision, HP Z-series, Lenovo ThinkStation, custom build

### Option 3: Server purchase

**Best for**: Production deployment, multi-user

**Recommended servers**:

| Vendor | Model | GPU Options | Est. Cost |
|:-------|:------|:------------|:----------|
| Dell | PowerEdge R750xa | 2-4x A100/H100 | $40,000-150,000 |
| HPE | ProLiant DL380a | 2-4x A100/H100 | $45,000-160,000 |
| Supermicro | GPU Server | 4-8x GPUs | $30,000-200,000 |

### Option 4: Cloud burst (hybrid)

**Best for**: Variable workload, testing larger models

Use cloud GPU instances for:
- Initial model evaluation
- Peak load handling
- Testing models too large for local hardware

> [!WARNING]
> Cloud instances may conflict with data privacy requirements. Ensure compliance before using cloud resources.

[↑ Back to Table of Contents](#table-of-contents)

## Hardware configurations for 70B models

This section provides specific, purchasable hardware configurations for running Llama 3.1 70B and similar 70B parameter models.

### VRAM requirements for 70B models

| Quantization | VRAM Needed | Quality | Use Case |
|:-------------|:------------|:--------|:---------|
| FP16 (full) | ~140 GB | Best | Research only (impractical) |
| Q8 | ~70-80 GB | Very good | Production with A100 80GB |
| **Q4 (recommended)** | **~40 GB** | Good | Production with 48GB+ VRAM |
| Q2 | ~21 GB | Lower | Fits single RTX 4090, quality tradeoff |

### Option A: Dual RTX 4090 workstation (Best value)

**Configuration for ~$8,000-12,000 total:**

| Component | Specification | Est. Price | Where to Buy |
|:----------|:--------------|:-----------|:-------------|
| **GPU (x2)** | NVIDIA RTX 4090 24GB | $1,800-2,000 each | [Newegg](https://www.newegg.com/msi-rtx-4090-gaming-x-trio-24g-geforce-rtx-4090-24gb-graphics-card-triple-fans/p/N82E16814137761), [Amazon](https://www.amazon.com/MSI-GeForce-Graphics-384-bit-DisplayPort/dp/B09YCLG5PB), Micro Center |
| **Motherboard** | ASUS WRX80, ASRock TRX50 (dual x16 PCIe) | $400-800 | Newegg, Amazon |
| **CPU** | AMD Threadripper PRO 5955WX or Intel Xeon W | $1,000-2,500 | Newegg, Amazon |
| **RAM** | 128GB DDR5 ECC (for VRAM spillover) | $400-600 | Crucial, Kingston |
| **PSU** | 1600W 80+ Platinum (two 4090s = ~900W) | $300-400 | Corsair, EVGA |
| **Storage** | 2TB NVMe PCIe 4.0 | $150-200 | Samsung, WD |
| **Case** | Full tower with dual GPU support | $200-300 | Fractal, Corsair |
| **Cooling** | High airflow, consider AIO for CPU | $150-250 | Noctua, Corsair |

**Combined VRAM:** 48 GB (split across 2 GPUs)
**Performance:** ~20 tokens/second with Llama 3.1 70B Q4
**Power draw:** ~900W under load

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  DUAL RTX 4090 BUILD NOTES                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CRITICAL REQUIREMENTS:                                                     │
│  • Motherboard MUST have two physical x16 PCIe slots with proper spacing   │
│  • Both slots should run at x8 or x16 (check CPU lane count)              │
│  • 1600W+ PSU required (two 16-pin connectors or adapters)                │
│  • Excellent case airflow (4090s run hot)                                  │
│                                                                             │
│  RECOMMENDED MOTHERBOARDS:                                                  │
│  • AMD: ASUS Pro WS WRX80E-SAGE SE WIFI                                    │
│  • AMD: ASRock TRX50 WS                                                    │
│  • Intel: ASUS Pro WS W790E-SAGE SE                                        │
│                                                                             │
│  MULTI-GPU SOFTWARE:                                                        │
│  • Ollama handles multi-GPU automatically                                  │
│  • Models split across GPUs via tensor parallelism                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Option B: Single RTX 6000 Ada 48GB (Simplest setup)

**Configuration for ~$10,000-14,000 total:**

| Component | Specification | Est. Price | Where to Buy |
|:----------|:--------------|:-----------|:-------------|
| **GPU** | NVIDIA RTX 6000 Ada 48GB | $6,800-7,300 | [NVIDIA Marketplace](https://marketplace.nvidia.com/en-us/enterprise/laptops-workstations/nvidia-rtx-6000-ada-generation/), [Newegg](https://www.newegg.com/nvidia-900-5g133-2250-000-rtx-6000-ada-48gb-graphics-card/p/N82E16814132103) |
| **Workstation** | Dell Precision 7875, HP Z8 G5, or custom | $3,000-6,000 | Dell, HP, custom |

**VRAM:** 48 GB (single card)
**Performance:** ~18-22 tokens/second with Llama 3.1 70B Q4
**Power draw:** ~300W under load

**Advantages:**
- Single card = simpler setup, no multi-GPU complexity
- Professional GPU with ECC memory
- Better driver support for workstation use
- Lower power consumption than dual 4090

### Option C: NVIDIA A100 80GB server (Enterprise)

**Configuration for ~$20,000-40,000 total:**

| Component | Specification | Est. Price | Where to Buy |
|:----------|:--------------|:-----------|:-------------|
| **GPU** | NVIDIA A100 80GB PCIe | $9,000-15,000 | [Server Supply](https://www.serversupply.com/GPU/HBM2E/80GB/NVIDIA/A100_413940.htm), Dell, HPE |
| **Server** | Dell PowerEdge R750xa, Supermicro 4U | $8,000-20,000 | [Dell](https://www.dell.com/en-us/shop/storage-servers-and-networking-for-business/sf/poweredge-ai-servers), [Supermicro](https://www.supermicro.com/en/products/gpu) |

**VRAM:** 80 GB
**Performance:** ~25-35 tokens/second with Llama 3.1 70B Q8
**Power draw:** ~400W under load

**Advantages:**
- Larger VRAM allows Q8 quantization (better quality)
- Can run multiple 7B models simultaneously
- Datacenter reliability and support
- Better for multi-user production deployment

**Server vendors:**
- [Dell PowerEdge GPU Servers](https://www.dell.com/en-us/shop/storage-servers-and-networking-for-business/sf/poweredge-ai-servers)
- [Supermicro GPU Systems](https://www.supermicro.com/en/products/gpu)
- [HPE ProLiant](https://www.hpe.com/us/en/compute/hpc/hpc-servers.html)

### Option D: Pre-built AI workstation (Turnkey)

**For organizations preferring turnkey solutions:**

| Vendor | Product | GPU Options | Est. Price | Link |
|:-------|:--------|:------------|:-----------|:-----|
| **BIZON** | ZX9000 | 2-7x RTX 4090, water-cooled | $15,000-50,000 | [bizon-tech.com](https://bizon-tech.com/bizon-zx9000.html) |
| **Lambda Labs** | Vector | 2-4x RTX 4090 or A100 | $20,000-80,000 | lambdalabs.com |
| **Puget Systems** | AI workstation | RTX 4090, A6000, or H100 | $10,000-100,000 | pugetsystems.com |

**Advantages:**
- Pre-configured, tested, and warrantied
- Professional support included
- Optimized cooling and power delivery
- Water-cooled options for dense GPU configurations

### Hardware comparison summary

| Option | VRAM | 70B Q4 | 70B Q8 | Est. Cost | Best For |
|:-------|:-----|:-------|:-------|:----------|:---------|
| **Dual RTX 4090** | 48 GB | Yes | No | $8,000-12,000 | Budget production |
| **RTX 6000 Ada** | 48 GB | Yes | No | $10,000-14,000 | Simple setup |
| **A100 80GB** | 80 GB | Yes | Yes | $20,000-40,000 | Enterprise, multi-user |
| **Pre-built** | Varies | Yes | Depends | $15,000-100,000 | Turnkey, supported |

### Recommendation by deployment scale

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    70B MODEL HARDWARE RECOMMENDATIONS                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DEVELOPMENT / PILOT (1-5 users)                                            │
│  ────────────────────────────────                                            │
│  • Hardware: Single RTX 6000 Ada 48GB OR Dual RTX 4090                     │
│  • Budget: $10,000-15,000                                                   │
│  • Model: Llama 3.1 70B Q4                                                 │
│  • Performance: 15-20 tokens/sec                                           │
│                                                                             │
│  TEAM PRODUCTION (5-20 users)                                               │
│  ────────────────────────────                                                │
│  • Hardware: A100 80GB in server OR Dual RTX 4090 + request queuing        │
│  • Budget: $20,000-40,000                                                   │
│  • Model: Llama 3.1 70B Q4 or Q8                                           │
│  • Consider: Load balancing, request queuing                               │
│                                                                             │
│  ENTERPRISE (20+ concurrent users)                                          │
│  ──────────────────────────────────                                          │
│  • Hardware: Multiple A100 80GB or H100 servers                            │
│  • Budget: $50,000-200,000+                                                 │
│  • Vendor: Dell PowerEdge, HPE, Supermicro with support contract          │
│  • Consider: HA deployment, load balancing, dedicated ops team            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cloud rental alternative

For variable workloads or before committing to hardware purchase:

| Provider | GPU | Hourly Rate | Monthly (24/7) | Link |
|:---------|:----|:------------|:---------------|:-----|
| [Hyperstack](https://www.hyperstack.cloud/a100) | A100 80GB | $1.35/hr | ~$1,000 | hyperstack.cloud |
| [RunPod](https://runpod.io) | A100 80GB | $1.99/hr | ~$1,450 | runpod.io |
| [Vast.ai](https://vast.ai) | RTX 4090 | $0.40-0.60/hr | ~$350 | vast.ai |
| [Lambda Cloud](https://lambdalabs.com/cloud) | A100 80GB | $1.29/hr | ~$940 | lambdalabs.com |

**Break-even analysis:** Hardware purchase becomes cost-effective after approximately 3,500-5,000 hours of use (~5-7 months running 24/7).

> [!NOTE]
> Cloud rentals may conflict with financial services data privacy requirements. Verify compliance before using cloud GPU instances with any sensitive data.

[↑ Back to Table of Contents](#table-of-contents)

## Cost analysis

### Total cost of ownership (5-year)

| Tier | Hardware | Power (5yr) | Maintenance | Total |
|:-----|:---------|:------------|:------------|:------|
| Tier 1 (Dev) | $2,500 | $1,500 | $500 | $4,500 |
| Tier 2 (Team) | $10,000 | $5,000 | $2,000 | $17,000 |
| Tier 3 (Prod) | $50,000 | $20,000 | $10,000 | $80,000 |
| Tier 4 (Enterprise) | $300,000 | $100,000 | $50,000 | $450,000 |

### Comparison vs cloud LLM APIs

| Usage Level | Cloud API (5yr) | Local (Tier 2) | Savings |
|:------------|:----------------|:---------------|:--------|
| Low (100K tokens/day) | $18,000 | $17,000 | 6% |
| Medium (1M tokens/day) | $180,000 | $17,000 | 91% |
| High (10M tokens/day) | $1,800,000 | $80,000 | 96% |

> [!NOTE]
> Local deployment becomes cost-effective at medium to high usage levels. Factor in development and operations costs for accurate comparison.

### Power consumption estimates

| Hardware | Idle | Load | Annual Cost (@ $0.12/kWh) |
|:---------|:-----|:-----|:--------------------------|
| RTX 4090 workstation | 150W | 600W | $400-600 |
| Dual A100 server | 400W | 1200W | $800-1,200 |
| 4x H100 server | 800W | 3500W | $2,000-3,500 |

[↑ Back to Table of Contents](#table-of-contents)
