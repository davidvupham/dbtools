# AI Engineering Course

**[← Back to Courses Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Course-blue)

**Goal:** Transform from an AI beginner to a practitioner who can build, deploy, and integrate AI systems for enterprise applications.

**Philosophy:** Learn by Doing. You will build **5 practical projects** throughout this course, culminating in a local AI assistant with MCP integration.

> **Navigation:**
>
> * [Local AI Hub Project](../../projects/local-ai-hub/README.md) (Reference Implementation)
> * [AI Concepts Glossary](../../projects/local-ai-hub/ai-concepts-glossary.md) (Deep Dive Reference)

---

## Course overview

This course covers the essential concepts and practical skills for working with AI systems in enterprise environments. You will learn how Large Language Models (LLMs) work, how to write effective prompts, how to extend AI capabilities with tools via Model Context Protocol (MCP), and how to build agentic AI systems.

### Who this course is for

- Infrastructure engineers adding AI capabilities to existing systems
- Database administrators using AI for log analysis and query optimization
- Developers building AI-powered applications
- Operations teams deploying local AI infrastructure
- Anyone wanting to understand modern AI beyond the hype

### What you will learn

By the end of this course, you will be able to:

1. Explain how LLMs work (transformers, attention, tokenization)
2. Write effective prompts using proven techniques
3. Build and connect MCP servers to extend AI capabilities
4. Design multi-agent systems for complex workflows
5. Implement RAG for domain-specific knowledge retrieval
6. Deploy and operate local LLM infrastructure with Ollama

---

## Module 1: AI fundamentals

*Focus: Understanding how LLMs work under the hood.*

| Chapter | Topic | Description |
|:--------|:------|:------------|
| [01](./module_1_fundamentals/01_what_are_llms.md) | What are LLMs? | Neural networks, training vs inference, capabilities and limitations |
| [02](./module_1_fundamentals/02_transformer_architecture.md) | Transformer architecture | Attention mechanism, encoder-decoder, self-attention |
| [03](./module_1_fundamentals/03_tokenization.md) | Tokenization | How text becomes numbers, BPE, context windows |
| [04](./module_1_fundamentals/04_model_parameters.md) | Model parameters | What 7B vs 70B means, quantization, VRAM requirements |
| [05](./module_1_fundamentals/05_inference.md) | Inference | Temperature, top-p, sampling strategies, latency |

📝 **[Exercises](./module_1_fundamentals/exercises/)** | 📋 **[Quiz](./module_1_fundamentals/quiz_module_1.md)**

🛠️ **Project 1: [Model Explorer](./module_1_fundamentals/project_1_model_explorer.md)** - Compare responses from different model sizes using Ollama

---

## Module 2: Prompt engineering

*Focus: Writing effective prompts for reliable AI outputs.*

| Chapter | Topic | Description |
|:--------|:------|:------------|
| [06](./module_2_prompt_engineering/06_prompt_anatomy.md) | Prompt anatomy | System prompts, user messages, structure |
| [07](./module_2_prompt_engineering/07_basic_techniques.md) | Basic techniques | Zero-shot, few-shot, role prompting |
| [08](./module_2_prompt_engineering/08_advanced_techniques.md) | Advanced techniques | Chain-of-thought, tree-of-thought, self-consistency |
| [09](./module_2_prompt_engineering/09_prompt_patterns.md) | Prompt patterns | Templates, structured output, JSON mode |
| [10](./module_2_prompt_engineering/10_avoiding_pitfalls.md) | Avoiding pitfalls | Hallucinations, bias, prompt injection |

📝 **[Exercises](./module_2_prompt_engineering/exercises/)** | 📋 **[Quiz](./module_2_prompt_engineering/quiz_module_2.md)**

🛠️ **Project 2: [Prompt Library](./module_2_prompt_engineering/project_2_prompt_library.md)** - Build a reusable prompt template system for database tasks

---

## Module 3: Model Context Protocol (MCP)

*Focus: Extending AI capabilities with tools and external data.*

| Chapter | Topic | Description |
|:--------|:------|:------------|
| [11](./module_3_mcp/11_mcp_overview.md) | MCP overview | What MCP is, why it matters, architecture |
| [12](./module_3_mcp/12_mcp_primitives.md) | MCP primitives | Tools, resources, prompts - when to use each |
| [13](./module_3_mcp/13_building_mcp_servers.md) | Building MCP servers | Python SDK, implementing tools, testing |
| [14](./module_3_mcp/14_mcp_clients.md) | MCP clients | Cline, OpenCode, custom clients with Ollama |
| [15](./module_3_mcp/15_mcp_patterns.md) | MCP patterns | Security, error handling, performance |

📝 **[Exercises](./module_3_mcp/exercises/)** | 📋 **[Quiz](./module_3_mcp/quiz_module_3.md)**

🛠️ **Project 3: [Database MCP Server](./module_3_mcp/project_3_mcp_server.md)** - Build an MCP server for database log analysis

---

## Module 4: Agentic AI

*Focus: Building autonomous AI systems that plan and execute tasks.*

| Chapter | Topic | Description |
|:--------|:------|:------------|
| [16](./module_4_agentic_ai/16_agent_fundamentals.md) | Agent fundamentals | What agents are, components (prompt, memory, tools) |
| [17](./module_4_agentic_ai/17_agent_patterns.md) | Agent patterns | ReAct, plan-and-execute, reflection |
| [18](./module_4_agentic_ai/18_multi_agent_systems.md) | Multi-agent systems | Orchestration, delegation, communication |
| [19](./module_4_agentic_ai/19_agent_frameworks.md) | Agent frameworks | CrewAI, LangGraph, AutoGen comparison |
| [20](./module_4_agentic_ai/20_agent_governance.md) | Agent governance | Safety, observability, human-in-the-loop |

📝 **[Exercises](./module_4_agentic_ai/exercises/)** | 📋 **[Quiz](./module_4_agentic_ai/quiz_module_4.md)**

🛠️ **Project 4: [Database Operations Agent](./module_4_agentic_ai/project_4_db_agent.md)** - Build an agent that analyzes logs and suggests remediations

---

## Module 5: Retrieval-Augmented Generation (RAG)

*Focus: Grounding AI responses in your own data.*

| Chapter | Topic | Description |
|:--------|:------|:------------|
| [21](./module_5_rag/21_rag_fundamentals.md) | RAG fundamentals | Why RAG, architecture overview, when to use |
| [22](./module_5_rag/22_document_processing.md) | Document processing | Chunking strategies, metadata extraction |
| [23](./module_5_rag/23_embeddings.md) | Embeddings | Vector representations, embedding models, similarity |
| [24](./module_5_rag/24_vector_stores.md) | Vector stores | ChromaDB, pgvector, FAISS comparison |
| [25](./module_5_rag/25_retrieval_strategies.md) | Retrieval strategies | Hybrid search, re-ranking, evaluation |

📝 **[Exercises](./module_5_rag/exercises/)** | 📋 **[Quiz](./module_5_rag/quiz_module_5.md)**

🛠️ **Project 5: [Documentation RAG](./module_5_rag/project_5_docs_rag.md)** - Build a RAG system for querying internal documentation

---

## Module 6: Local LLM deployment

*Focus: Running AI infrastructure on-premise with Ollama.*

| Chapter | Topic | Description |
|:--------|:------|:------------|
| [26](./module_6_local_deployment/26_why_local.md) | Why local? | Privacy, cost, compliance, latency |
| [27](./module_6_local_deployment/27_ollama_setup.md) | Ollama setup | Installation, configuration, model management |
| [28](./module_6_local_deployment/28_model_selection.md) | Model selection | Choosing models for different tasks |
| [29](./module_6_local_deployment/29_performance_tuning.md) | Performance tuning | GPU optimization, batching, caching |
| [30](./module_6_local_deployment/30_production_operations.md) | Production operations | Monitoring, scaling, high availability |

📝 **[Exercises](./module_6_local_deployment/exercises/)** | 📋 **[Quiz](./module_6_local_deployment/quiz_module_6.md)**

🛠️ **Capstone Project: [Local AI Hub](./module_6_local_deployment/capstone_local_ai_hub.md)** - Deploy a complete local AI assistant with MCP integration

---

## Learning path

| Week | Modules | Focus |
|:-----|:--------|:------|
| 1-2 | Module 1-2 | Foundations: How LLMs work + Prompt engineering |
| 3-4 | Module 3 | MCP: Extending AI with tools |
| 5-6 | Module 4 | Agentic AI: Autonomous systems |
| 7-8 | Module 5 | RAG: Domain-specific knowledge |
| 9-10 | Module 6 | Deployment: Production operations |

---

## Prerequisites

Before starting this course, ensure you have:

- [ ] Basic Python programming (functions, classes, async/await)
- [ ] Familiarity with command line and Git
- [ ] Access to a machine with 8GB+ RAM (16GB+ recommended)
- [ ] Optional: NVIDIA GPU with 8GB+ VRAM for local models

---

## Quick reference materials

| Resource | Description |
|:---------|:------------|
| [AI Concepts Glossary](../../projects/local-ai-hub/ai-concepts-glossary.md) | Comprehensive terminology reference |
| [MCP Integration Guide](../../projects/local-ai-hub/mcp-integration.md) | Detailed MCP implementation guide |
| [Hardware Requirements](../../projects/local-ai-hub/hardware-requirements.md) | GPU and VRAM sizing guide |
| [LLM Model Selection](../../projects/local-ai-hub/llm-model-selection.md) | Model comparison and recommendations |

---

## Sources and references

### Official documentation

- [Anthropic MCP Documentation](https://modelcontextprotocol.io/)
- [Anthropic MCP Course](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

### Industry resources

- [IBM Guide to AI Agents](https://www.ibm.com/think/ai-agents)
- [IBM Guide to Prompt Engineering](https://www.ibm.com/think/prompt-engineering)
- [Deloitte Agentic AI Strategy](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2026/agentic-ai-strategy.html)
- [DataCamp Transformers Tutorial](https://www.datacamp.com/tutorial/how-transformers-work)

### Research and deep dives

- [Attention Is All You Need (Original Transformer Paper)](https://arxiv.org/abs/1706.03762)
- [RAG Best Practices Study](https://arxiv.org/abs/2501.07391)
- [Machine Learning Mastery: Agentic AI Roadmap](https://machinelearningmastery.com/the-roadmap-for-mastering-agentic-ai-in-2026/)
