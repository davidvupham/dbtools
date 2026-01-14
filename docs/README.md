# Project Documentation

This directory contains all project documentation organized by category.

## Table of Contents

- [Documentation Organization](#documentation-organization)
  - [**Browse by Topic**](#browse-by-topic)
  - [tutorials/ - Learning-Oriented Guides](#tutorials---learning-oriented-guides)
  - [projects/ - Project Documentation](#projects---project-documentation)
  - [how-to/ - How-to Guides](#how-to---how-to-guides)
  - [explanation/ - Understanding-Oriented Documentation](#explanation---understanding-oriented-documentation)
  - [runbooks/ - Operational Runbooks](#runbooks---operational-runbooks)
  - [best-practices/ - Standards & Best Practices](#best-practices---standards--best-practices)
  - [reference/ - Technical Reference](#reference---technical-reference)
  - [development/ - Development Documentation](#development---development-documentation)

- [Component Documentation](#component-documentation)
- [Quick Links](#quick-links)

## Browse by Topic

Find documentation across all categories (Tutorials, How-to, Reference) for specific technologies:

| Topic | Main Entry Point | How-to / Reference |
| :--- | :--- | :--- |
| **Python** | [Tutorials](tutorials/python/README.md) | [How-to](how-to/python/README.md) • [Ref](reference/python/README.md) |
| **UV (Pkg Mgr)** | [Tutorials](tutorials/python/uv/README.md) | [How-to](how-to/python/README.md) • [Ref](reference/python/uv/uv-reference.md) |
| **PowerShell** | [Tutorials](tutorials/powershell/README.md) | [How-to](how-to/powershell/README.md) • [Ref](reference/README.md) |
| **Docker** | [Tutorials](tutorials/docker/README.md) | [Standards](best-practices/docker/README.md) |
| **Podman** | [Overview](explanation/podman/README.md) | [Install](how-to/podman/install-podman-rhel.md) • [Systemd](how-to/podman/systemd-integration.md) • [Troubleshoot](how-to/podman/troubleshooting.md) • [Ref](reference/podman/cheatsheet.md) |
| **Kubernetes** | [Tutorials](tutorials/kubernetes/README.md) | |
| **AWS** | [Tutorials](tutorials/aws/README.md) | |
| **Terraform** | [Tutorials](tutorials/terraform/README.md) | |
| **Ansible** | [Tutorials](tutorials/ansible/README.md) | |
| **Liquibase** | [📍 **Start Here**](explanation/liquibase/README.md) | [Concepts](explanation/liquibase/liquibase-concepts.md) • [How-to](how-to/liquibase/liquibase-operations-guide.md) • [Ref](reference/liquibase/liquibase-reference.md) |
| **GDS Vault** | [Tutorials](tutorials/gds-vault/README.md) | [How-to](how-to/vault/README.md) |
| **Kafka** | [Tutorials](tutorials/kafka/README.md) | |
| **Observability** | [Course](courses/observability/README.md) | |
| **System Design** | [Tutorials](system-design/README.md) | |
| **Linux** | [Tutorials](linux/README.md) | [Ref](reference/linux/README.md) |

## Documentation Organization

This documentation follows the **[Diátaxis Framework](https://diataxis.fr/)**, a systematic approach to technical
documentation that organizes content by **user intent**.

The framework divides documentation into four distinct quadrants:

1. **[Tutorials](tutorials/README.md)** (Learning-oriented): *"Teach me."* Lessons that lead the user through a
    series of steps to complete a project.
2. **[How-to Guides](how-to/README.md)** (Problem-oriented): *"Help me do it."* Steps to solve a specific problem or
    real-world task.
3. **[Reference](reference/README.md)** (Information-oriented): *"Describe it."* Technical descriptions of the
    machinery and how to operate it.
4. **[Explanation](explanation/README.md)** (Understanding-oriented): *"Explain it."* Discussion that clarifies and
    illuminates a particular topic.

For more information, visit the [official Diátaxis documentation](https://diataxis.fr/).

Other categories in this repository include:

- **[Courses](courses/python/README.md)**: Extended curriculums that combine multiple tutorials and projects.
- **[Projects](projects/README.md)**: Real-world implementation documentation.
- **[Runbooks](runbooks/README.md)**: Operational procedures.

### [courses/](courses/python/README.md) - Curriculums

Deep-dive, project-based engineering courses.

- [**Python Engineering Course**](courses/python/README.md) - From zero to production engineer.

### [tutorials/](tutorials/README.md) - Learning-Oriented Guides

Step-by-step tutorials for learning various technologies:

- [**Ansible**](tutorials/ansible/README.md)
- [**Docker**](tutorials/docker/README.md)
- [**Podman Getting Started**](tutorials/podman/getting-started.md)
- [**Liquibase**](tutorials/liquibase/README.md)
- [**Python**](tutorials/python/README.md)
  - [**UV Package Manager**](tutorials/python/uv/README.md) - **Start Here for UV**
- [**Kafka**](tutorials/kafka/README.md)

### [projects/](projects/README.md) - Project Documentation

Documentation for large-scale projects:

- [**Active Directory Password Rotation**](projects/ad-password-rotation/README.md)
- [**Database Patching & Upgrade**](projects/db-patching-upgrade/README.md)

### [how-to/](how-to/README.md) - How-to Guides

Task-oriented guides for solving specific problems:

- [**PowerShell Guides**](how-to/powershell/README.md)
- [**Python & UV Guides**](how-to/python/README.md)
- [**Configure Service Dependencies**](how-to/configure-service-dependencies.md)
- [**Rotate AD Passwords with Vault**](how-to/rotate-ad-passwords-with-vault.md)

### [explanation/](explanation/README.md) - Understanding-Oriented Documentation

Background, context, and architecture:

- [**Architecture**](explanation/architecture/README.md)
- [**Design Records**](explanation/design-records/README.md)
- [**Podman Overview**](explanation/podman/README.md)
- [**Secrets Management Comparison**](explanation/secrets-management-comparison.md)

### [runbooks/](runbooks/README.md) - Operational Runbooks

Practical procedures for operations:

- [**GMSA**](runbooks/gmsa/README.md)
- [**Podman Maintenance**](runbooks/podman/maintenance.md)

### [best-practices/](best-practices/README.md) - Standards & Best Practices

Organizational standards and recommended practices:

- [**Technical Project Management**](best-practices/technical-project-management.md) - Project documentation framework
- [**Docker Standards**](best-practices/docker/README.md) - Corporate registry and security policies.

### [templates/](templates/README.md) - Project Templates

Standard templates for project documentation:

- [**Project Charter**](templates/project-charter.md)
- [**Decision Log**](templates/decision-log.md)
- [**Status Reports**](templates/status-report.md)

### [reference/](reference/README.md) - Technical Reference

Technical specifications and reference material:

- [**Linux**](reference/linux/) - Linux tool references.

### [development/](development/README.md) - Development Documentation

Guides for contributors:

- [**Coding Standards**](development/coding-standards/README.md)
- [**Testing**](development/testing/README.md)
- [**VS Code Setup**](development/vscode/README.md)
- [**Developer Onboarding (Linux: WSL2/RHEL)**](development/developer-onboarding.md)

### [archive/](archive/README.md) - Archived Files

Deprecated documentation and reports.

---

## Component Documentation

For component-specific documentation, see:

- **Package**: [../gds_snowflake/README.md](../gds_snowflake/README.md)
- **Application**: [../snowflake_monitoring/README.md](../snowflake_monitoring/README.md)

## Quick Links

- [Workspace Overview](../README.md)
