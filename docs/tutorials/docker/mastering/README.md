# Mastering Docker (Multi‑Chapter Tutorial)

A structured, from‑first‑principles tutorial that takes you from fundamentals to production‑ready Docker. This series is organized into Parts and Chapters to mirror a traditional book format. All content is original and tailored to practical, runnable examples in this repo.

Use this as the primary landing page. Each chapter links to runnable examples and deeper references.

---

## Table of Contents

- Part I — Foundations
  - Chapter 1: The Why and How of Docker (motivation and core ideas)
  - Chapter 2: Setting Up Your Docker Environment (Linux/macOS/Windows, Docker Desktop)
  - Chapter 3: CLI Essentials and First Run (images, containers, lifecycle)
- Part II — Building and Optimizing Images
  - Chapter 4: Dockerfile Basics (layers, context, .dockerignore)
  - Chapter 5: Advanced Dockerfile Techniques (multi‑stage, build args, cache)
  - Chapter 6: Managing Images (inspect, history, prune, save/load, tags)
- Part III — Containers, Networking, and Data
  - Chapter 7: Container Management (logs, exec, inspect, health)
  - Chapter 8: Docker Networking (bridge, host, user‑defined, name resolution)
  - Chapter 9: Persistence with Volumes and Mounts (named volumes, bind mounts)
  - Chapter 10: Advanced Data & Storage (drivers, tmpfs, backups)
- Part IV — Compose and Orchestration
  - Chapter 11: Introduction to Docker Compose (services, networks, volumes)
  - Chapter 12: Advanced Compose (profiles, overrides, scaling)
  - Chapter 13: Orchestration 101 (Swarm concepts, services)
  - Chapter 14: Kubernetes Concepts for Docker Users (pods, deployments, services)
- Part V — Real‑World Practice and Hardening
  - Chapter 15: Docker‑Driven Dev Workflow (live reload, local stacks)
  - Chapter 16: CI/CD for Containers (buildx, multi‑arch, push, scan)
  - Chapter 17: Security Hardening (least privilege, capabilities, scanning)
  - Chapter 18: Troubleshooting & Debugging (logs, events, stats, common issues)
  - Chapter 19: Ecosystem Tools (registries, scanners, rootless, contexts)
  - Chapter 20: Beyond the Basics (performance, content trust, SBOM, next steps)

---

## What’s in each chapter

- [Chapter 1: The Why and How of Docker](./chapter01_why_and_how.md) — motivations, containers vs. VMs, core terms (image, container, registry), and your first `hello-world` run.
- [Chapter 2: Setting Up Your Docker Environment](./chapter02_setup.md) — install on Linux/macOS/Windows, verify the engine, and quick sanity checks.
- [Chapter 3: CLI Essentials and First Run](./chapter03_cli_essentials.md) — `run`, `ps`, `logs`, `exec`, stop/remove; mapping ports and working with env vars.
- [Chapter 4: Dockerfile Basics](./chapter04_dockerfile_basics.md) — layers and context, `.dockerignore`, a minimal Python HTTP server image.
- [Chapter 5: Advanced Dockerfile Techniques](./chapter05_dockerfile_advanced.md) — multi‑stage builds, build args/env, cache behavior, and minimal base images.
- [Chapter 6: Managing Images](./chapter06_image_management.md) — `inspect`, `history`, pruning safely, save/load, tagging/pushing, and finding images in use by containers.
- [Chapter 7: Container Management](./chapter07_container_management.md) — logs, `exec`, stats, healthchecks, restart policies, and lifecycle tips.
- [Chapter 8: Docker Networking](./chapter08_networking.md) — bridge/host/user‑defined networks, DNS, connectivity, and troubleshooting. See also: networking deep dive and runnable examples:
  - Deep dive: `docs/tutorials/docker/networking_deep_dive.md`
  - Examples (Compose + echo servers): `docs/tutorials/docker/examples/networking/`
- [Chapter 9: Persistence with Volumes and Mounts](./chapter09_volumes_and_mounts.md) — named volumes, bind mounts, backups, and common data pitfalls.
- [Chapter 10: Advanced Data & Storage](./chapter10_advanced_storage.md) — storage drivers, tmpfs, performance considerations, and when to choose what.
- [Chapter 11: Introduction to Docker Compose](./chapter11_compose_intro.md) — define multi‑container apps, `up`/`down`, logs, and networks. Try a small stack in the networking examples:
  - Examples: `docs/tutorials/docker/examples/networking/`
- [Chapter 12: Advanced Compose](./chapter12_compose_advanced.md) — profiles, overrides, scaling, env files, and production‑friendly patterns.
- [Chapter 13: Orchestration 101 (Swarm)](./chapter13_orchestration_swarm.md) — services, rolling updates, and when Swarm still fits.
- [Chapter 14: Kubernetes Concepts for Docker Users](./chapter14_kubernetes_for_docker_users.md) — pods/deployments/services mapped from Docker concepts with a quick deployment example.
- [Chapter 15: Docker‑Driven Dev Workflow](./chapter15_dev_workflow.md) — live reload, bind mounts, local stacks via Compose, and productive inner loops.
- [Chapter 16: CI/CD for Containers](./chapter16_cicd.md) — Buildx multi‑arch builds, registry pushes, caching, and scanning. See the Buildx example:
  - Examples (Buildx multi‑arch demo): `docs/tutorials/docker/examples/buildx/`
- [Chapter 17: Security Hardening](./chapter17_security.md) — run as non‑root, drop capabilities, read‑only filesystems, secrets management, and image scanning.
- [Chapter 18: Troubleshooting & Debugging](./chapter18_troubleshooting.md) — logs, events, stats, common networking issues, and safe cleanup.
- [Chapter 19: Ecosystem Tools](./chapter19_ecosystem_tools.md) — registries (Hub/GHCR/ECR/ACR/Harbor), contexts and remote builders, rootless mode, scanners (Trivy/Grype/Snyk), and SBOMs (Syft).
- [Chapter 20: Beyond the Basics](./chapter20_beyond_the_basics.md) — BuildKit cache export/import and mounts, advanced multi‑stage patterns, reproducible builds, provenance/attestations, and signing (cosign/OCI artifacts). See also Buildx example:
  - Examples (Buildx multi‑arch demo): `docs/tutorials/docker/examples/buildx/`

---

## How to use this tutorial

- Start at Chapter 1 and progress linearly, or jump to a chapter you need.
- Most chapters include copy‑paste commands and cross‑links to examples:
  - Networking examples: `docs/tutorials/docker/examples/networking/`
  - Buildx multi‑arch example: `docs/tutorials/docker/examples/buildx/`
- If you’re new to Docker, also see the Quick Start and Cheat Sheet in `docs/tutorials/docker/README.md`.

---

## Chapters

- Chapter 1: The Why and How of Docker → `chapter01_why_and_how.md`
- Chapter 2: Setting Up Your Docker Environment → `chapter02_setup.md`
- Chapter 3: CLI Essentials and First Run → `chapter03_cli_essentials.md`
- Chapter 4: Dockerfile Basics → `chapter04_dockerfile_basics.md`
- Chapter 5: Advanced Dockerfile Techniques → `chapter05_dockerfile_advanced.md`
- Chapter 6: Managing Images → `chapter06_image_management.md`
- Chapter 7: Container Management → `chapter07_container_management.md`
- Chapter 8: Docker Networking → `chapter08_networking.md`
- Chapter 9: Persistence with Volumes and Mounts → `chapter09_volumes_and_mounts.md`
- Chapter 10: Advanced Data & Storage → `chapter10_advanced_storage.md`
- Chapter 11: Introduction to Docker Compose → `chapter11_compose_intro.md`
- Chapter 12: Advanced Compose → `chapter12_compose_advanced.md`
- Chapter 13: Orchestration 101 (Swarm) → `chapter13_orchestration_swarm.md`
- Chapter 14: Kubernetes Concepts for Docker Users → `chapter14_kubernetes_for_docker_users.md`
- Chapter 15: Docker‑Driven Dev Workflow → `chapter15_dev_workflow.md`
- Chapter 16: CI/CD for Containers → `chapter16_cicd.md`
- Chapter 17: Security Hardening → `chapter17_security.md`
- Chapter 18: Troubleshooting & Debugging → `chapter18_troubleshooting.md`
- Chapter 19: Ecosystem Tools → `chapter19_ecosystem_tools.md`
- Chapter 20: Beyond the Basics → `chapter20_beyond_the_basics.md`
