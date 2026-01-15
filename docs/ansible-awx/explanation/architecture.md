# Ansible AWX Architecture & Concepts

**🔗 [← Back to Ansible AWX Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 15, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Architecture-blue)

> [!IMPORTANT]
> **Related Docs:** [Best Practices](../reference/best-practices.md)

## Introduction

This document explains the core architecture and concepts of Ansible AWX. Understanding these components is critical for designing scalable and secure automation workflows.

## Core Components

### 1. Control Plane vs. Execution Plane

Modern AWX (since version 18+) adopts a container-native architecture that separates the control plane from the execution plane.

- **Control Plane**: Manages the Web UI, API, Scheduler, and Inventory updates. It runs as a set of deployments on Kubernetes (managed by the AWX Operator).
- **Execution Plane**: Runs the actual automation jobs. Uses **Execution Environments (EE)**, which are container images containing Ansible, Python, and required Libraries (collections).

### 2. Execution Environments (EE)

Execution Environments replacing the legacy "virtual environment" approach. An EE is a container image that includes:
- A specific version of Ansible Core.
- A specific version of Python.
- Ansible Collections (e.g., `community.general`, `kubernetes.core`).
- System dependencies (e.g., `git`, `openssh`).

This ensures that automation is portable and consistent from development to production.

### 3. Instance Groups

Instance Groups allow you to dedicate cluster resources to specific tasks.
- **Control Plane Group**: Handles system tasks like inventory updates.
- **Container Groups**: Execution nodes usually running as Pods in Kubernetes. You can route specific Job Templates to specific groups (e.g., a "DMZ" group).

### 4. Projects and SCM

AWX treats **Projects** as logical collections of Ansible Playbooks.
- **Source Control (SCM)**: Projects should always map to a Git repository.
- **Update on Launch**: Ensures the latest automation code is used.

## Operations Concepts

### The AWX Operator

AWX is deployed on Kubernetes using the **AWX Operator**. This follows the Kubernetes Operator pattern to manage the lifecycle of the AWX application, covering:
- Database migrations.
- Upgrades.
- Backup and Restore.

### Hop Nodes

For secure environments, AWX supports execution nodes that act as "Hop Nodes" to reach restricted network segments without exposing the entire control plane.

[↑ Back to Table of Contents](#introduction)
