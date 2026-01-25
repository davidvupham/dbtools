# Chapter 26: Why local LLMs

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-6_Local_Deployment-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Evaluate when local LLMs are appropriate vs cloud APIs
2. Understand the trade-offs of local deployment
3. Calculate costs and infrastructure requirements
4. Make informed decisions for your organization

## Table of contents

- [Introduction](#introduction)
- [Benefits of local deployment](#benefits-of-local-deployment)
- [Trade-offs and limitations](#trade-offs-and-limitations)
- [Decision framework](#decision-framework)
- [Cost analysis](#cost-analysis)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Running LLMs locally gives you control over your data, costs, and infrastructure. But it's not always the right choice. This chapter helps you understand when local deployment makes sense and how to evaluate the trade-offs.

[↑ Back to Table of Contents](#table-of-contents)

## Benefits of local deployment

### Data privacy and compliance

```text
DATA FLOW COMPARISON
════════════════════

Cloud API:
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Your    │────►│ Internet│────►│ Cloud   │
│ Data    │     │         │     │ Provider│
└─────────┘     └─────────┘     └─────────┘
                                     │
                                     ▼
                              Logs, training?

Local:
┌─────────┐     ┌─────────┐
│ Your    │────►│ Your    │  Data never leaves
│ Data    │     │ Server  │  your infrastructure
└─────────┘     └─────────┘
```

**When data privacy matters:**
- Healthcare (HIPAA requirements)
- Financial services (regulatory compliance)
- Government/defense (classified data)
- Customer PII processing
- Proprietary code analysis

### Cost predictability

```text
COST STRUCTURE
══════════════

Cloud API costs:
- Pay per token
- Unpredictable monthly bills
- Costs scale linearly with usage
- Peak usage = peak costs

Local deployment costs:
- Fixed hardware investment
- Predictable operating costs
- No per-token charges
- High-volume usage = lower per-query cost
```

### Latency and availability

| Aspect | Cloud API | Local |
|:-------|:----------|:------|
| Network latency | 50-200ms | <1ms |
| Rate limits | Yes | No |
| Availability | Provider-dependent | Self-managed |
| Geographic restrictions | May exist | None |

### Customization

Local deployment enables:
- Fine-tuning on your data
- Custom model architectures
- Integration with internal systems
- No API restrictions or content policies

[↑ Back to Table of Contents](#table-of-contents)

## Trade-offs and limitations

### Model capability gap

```text
MODEL CAPABILITIES (approximate)
════════════════════════════════

                    Cloud          Local (7B)    Local (70B)
                    ─────          ──────────    ───────────
Reasoning           ●●●●●          ●●○○○         ●●●●○
Coding              ●●●●●          ●●●○○         ●●●●○
Long context        ●●●●●          ●●●○○         ●●●○○
Multilingual        ●●●●●          ●●○○○         ●●●○○
Speed               ●●●●○          ●●●●●         ●●○○○

Legend: ● = strength, ○ = limitation
```

### Infrastructure requirements

| Model Size | VRAM Required | Example Hardware |
|:-----------|:--------------|:-----------------|
| 7B (Q4) | 6 GB | RTX 3060, RTX 4060 |
| 7B (FP16) | 14 GB | RTX 4090, A4000 |
| 13B (Q4) | 10 GB | RTX 3080, RTX 4070 |
| 70B (Q4) | 40 GB | A100, 2x RTX 4090 |
| 70B (FP16) | 140 GB | Multiple A100s |

### Operational overhead

**Cloud API:**
- No infrastructure management
- Automatic scaling
- Provider handles updates/security

**Local deployment:**
- Hardware procurement and maintenance
- Model updates and security patches
- Monitoring and alerting
- Capacity planning
- Team expertise required

[↑ Back to Table of Contents](#table-of-contents)

## Decision framework

### When to use local LLMs

```text
LOCAL DEPLOYMENT DECISION TREE
══════════════════════════════

Is data extremely sensitive?
├── YES → Local (or on-prem cloud)
│
└── NO → Do you have high, consistent volume?
         ├── YES → Calculate break-even
         │         └── Volume > break-even? → Local
         │
         └── NO → Is latency critical (<10ms)?
                  ├── YES → Local
                  │
                  └── NO → Do you need custom fine-tuning?
                           ├── YES → Local (or cloud fine-tuning)
                           │
                           └── NO → Cloud API (simpler)
```

### Hybrid approach

Many organizations use both:

```text
HYBRID ARCHITECTURE
═══════════════════

┌─────────────────────────────────────────────────────────────────┐
│                         Your Application                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │       Router/Gateway       │
              └─────────────┬─────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Local LLM    │   │  Local LLM    │   │   Cloud API   │
│  (Sensitive)  │   │  (High-vol)   │   │  (Complex)    │
└───────────────┘   └───────────────┘   └───────────────┘
   Internal data      Embeddings         Reasoning tasks
   Customer PII       Simple tasks       Code generation
```

### Use case mapping

| Use Case | Recommended | Reason |
|:---------|:------------|:-------|
| Customer support chat | Hybrid | Privacy + complexity |
| Code completion | Local | Low latency, proprietary code |
| Document summarization | Local | High volume, sensitive docs |
| Complex analysis | Cloud | Needs best model quality |
| Embeddings | Local | High volume, no privacy concern |
| Creative writing | Cloud | Needs nuanced language |

[↑ Back to Table of Contents](#table-of-contents)

## Cost analysis

### Cloud API costs

```python
def calculate_cloud_cost(
    queries_per_month: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    input_price_per_million: float = 3.00,  # GPT-4 Turbo
    output_price_per_million: float = 15.00
) -> float:
    """Calculate monthly cloud API cost."""
    total_input = queries_per_month * avg_input_tokens
    total_output = queries_per_month * avg_output_tokens

    input_cost = (total_input / 1_000_000) * input_price_per_million
    output_cost = (total_output / 1_000_000) * output_price_per_million

    return input_cost + output_cost


# Example: 100K queries/month, 1000 input + 500 output tokens each
monthly_cloud = calculate_cloud_cost(100_000, 1000, 500)
print(f"Cloud cost: ${monthly_cloud:,.2f}/month")  # ~$1,050/month
```

### Local deployment costs

```python
def calculate_local_cost(
    hardware_cost: float,
    monthly_power_watts: float,
    power_cost_kwh: float = 0.15,
    depreciation_months: int = 36
) -> dict:
    """Calculate local deployment monthly cost."""
    # Hardware amortization
    hardware_monthly = hardware_cost / depreciation_months

    # Power cost (assuming 24/7 operation)
    hours_per_month = 24 * 30
    power_monthly = (monthly_power_watts / 1000) * hours_per_month * power_cost_kwh

    # Estimated maintenance/labor (rough estimate)
    maintenance_monthly = hardware_cost * 0.01  # 1% per month

    return {
        "hardware_amortized": hardware_monthly,
        "power": power_monthly,
        "maintenance": maintenance_monthly,
        "total": hardware_monthly + power_monthly + maintenance_monthly
    }


# Example: RTX 4090 server (~$5,000), 500W average
local_costs = calculate_local_cost(5000, 500)
print(f"Local cost: ${local_costs['total']:,.2f}/month")  # ~$240/month
```

### Break-even analysis

```python
def calculate_breakeven(
    hardware_cost: float,
    local_monthly_cost: float,
    query_volume: int,
    cloud_cost_per_query: float
) -> int:
    """Calculate months to break even."""
    cloud_monthly = query_volume * cloud_cost_per_query
    monthly_savings = cloud_monthly - local_monthly_cost

    if monthly_savings <= 0:
        return float('inf')  # Never breaks even

    months_to_breakeven = hardware_cost / monthly_savings
    return int(months_to_breakeven)


# Example
breakeven = calculate_breakeven(
    hardware_cost=5000,
    local_monthly_cost=240,
    query_volume=100000,
    cloud_cost_per_query=0.01  # $10 per 1000 queries
)
print(f"Break-even: {breakeven} months")  # ~6 months
```

### Cost comparison table

| Scenario | Cloud/Month | Local/Month | Break-even |
|:---------|:------------|:------------|:-----------|
| 10K queries | $105 | $240 | Never |
| 50K queries | $525 | $240 | 17 months |
| 100K queries | $1,050 | $240 | 6 months |
| 500K queries | $5,250 | $500* | 1 month |

*Higher volume may require better hardware

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Local LLMs provide data privacy, cost predictability, and low latency
- Trade-offs include reduced model capability and operational overhead
- Use a decision framework based on sensitivity, volume, latency, and customization needs
- Hybrid approaches often work best, using local for sensitive/high-volume and cloud for complex tasks
- Calculate break-even point to make informed investment decisions

## Next steps

Continue to **[Chapter 27: Ollama Setup](./27_ollama_setup.md)** to learn how to set up your local LLM infrastructure.

[↑ Back to Table of Contents](#table-of-contents)
