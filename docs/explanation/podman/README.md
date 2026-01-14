# Podman Documentation - Where to Start

> **Last Updated:** January 13, 2026

This directory contains key documentation for Podman, the daemonless container engine.

## 🚀 Quick Start

1. **[Podman Architecture Guide](./podman-architecture.md)**
   - What is Podman?
   - Architecture and Key Concepts (Pods, Rootless)
   - Comparison with Docker
   - Usage Scenarios

2. **[Installation Guide](../../how-to/podman/install-podman-rhel.md)**
   - How to install on RHEL

3. **[Runbooks](../../runbooks/podman/)**
   - Operational guides

4. **[Reference](../../reference/podman/)**
   - Command reference

## 📚 Document Map

| Scenario | Document |
|:---|:---|
| I want to understand how Podman works | [Architecture Guide](./podman-architecture.md) |
| I need to install it | [Installation Guide](../../how-to/podman/install-podman-rhel.md) |
| I have a problem or task | [Runbooks](../../runbooks/podman/) |
| I need command help | [Reference](../../reference/podman/) |

## 📖 Full Document List

### 1. **Architecture Guide** (Read First!)
📄 [podman-architecture.md](./podman-architecture.md)

**What it covers:**
- Core concepts (Daemonless, Rootless, Pods)
- Architecture design
- Comparison with Docker
- When to use Podman

**When to read:**
- ✅ You're new to Podman
- ✅ You're planning your container strategy
- ✅ You need to generate systemd units or K8s YAML

---

## 🔗 Document Relationships

```
ARCHITECTURE GUIDE (Concepts)
    ↓
    ├─→ INSTALLATION GUIDE (Setup)
    │
    └─→ RUNBOOKS (Operations)
             ↓
             └─→ REFERENCE GUIDE (Lookup)
```
