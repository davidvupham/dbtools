# Project Documentation

This directory contains all project documentation organized by category.

## Table of Contents

- [Documentation Organization](#documentation-organization)
  - [tutorials/ - Learning-Oriented Guides](#tutorials---learning-oriented-guides)
  - [explanation/ - Understanding-Oriented Documentation](#explanation---understanding-oriented-documentation)
  - [development/ - Development Documentation](#development---development-documentation)
  - [coding-standards/ - Coding Standards](#coding-standards---coding-standards)
  - [runbooks/ - Operational Runbooks](#runbooks---operational-runbooks)
  - [vscode/ - VS Code Setup](#vscode---vs-code-setup)
  - [archive/ - Archived Files](#archive---archived-files)
- [Component Documentation](#component-documentation)
- [Quick Links](#quick-links)

## 📚 Documentation Organization

This documentation follows the **Diátaxis framework**, organizing content by user intent to help you find what you need based on your goal:

- **Tutorials** (Learning-oriented): Step-by-step lessons to help you get started and acquire new skills.
- **Explanation** (Understanding-oriented): High-level context, architecture decisions, and "why" things work the way they do.
- **Runbooks** (Goal-oriented): Practical, procedural guides for performing specific operational tasks.
- **Development** (Contributor-oriented): Standards and guides for working on the codebase itself.

### Diagrams as Code (Mermaid)

This project uses **[Mermaid.js](https://mermaid.js.org/)** for architectural, sequence, and class diagrams. This "diagram-as-code" approach aligns with best practices for engineering documentation:

- **Version Control**: Diagrams are text-based, allowing them to be versioned, diffed, and reviewed in Pull Requests just like code.
- **Maintainability**: No need for external binary files or proprietary tools; anyone can edit the diagrams using a text editor.
- **Integration**: GitHub renders Mermaid diagrams natively in markdown files.

Open the architecture files in the GitHub UI to see the diagrams rendered. In local editors (like VS Code), install the **Markdown Preview Mermaid Support** extension.

### [tutorials/](tutorials/) - Learning-Oriented Guides

Step-by-step tutorials for learning various technologies:

- [Ansible](tutorials/ansible/) - Ansible automation tutorials
- [Docker](tutorials/docker/) - Container and Docker tutorials
- [Liquibase](tutorials/liquibase/) - Database change management tutorials
- [Python](tutorials/python/) - Python programming tutorials
- [OOP](tutorials/oop/) - Object-oriented programming tutorials
- [Kafka](tutorials/kafka/) - Apache Kafka tutorials
- [RabbitMQ](tutorials/rabbitmq/) - RabbitMQ messaging tutorials
- [**Observability**](tutorials/observability/) - **Comprehensive 9-part tutorial** covering:
  - OpenTelemetry, distributed tracing, and the three pillars (traces, metrics, logs)
  - Kafka streaming pipelines and data architecture
  - Python and PowerShell instrumentation
  - Alerting, notification, and best practices
  - Hands-on exercises and quick reference guide
- [Certificates](tutorials/certs/) - TLS/SSL certificate tutorials
- [SSH Agent](tutorials/ssh-agent/) - SSH agent configuration

---

### [explanation/](explanation/) - Understanding-Oriented Documentation

Architecture decisions, design records, and conceptual explanations:

- [Architecture](explanation/architecture/) - System architecture documentation
  - [Observability](explanation/architecture/observability/) - Monitoring and metrics architecture
  - [Liquibase](explanation/architecture/liquibase/) - Liquibase implementation guides
  - [Database CI/CD](explanation/architecture/database-change-cicd/) - Database change pipeline architecture
- [Design Records](explanation/design-records/) - Design decisions and refactoring plans
  - [Database Instance OO Design](explanation/design-records/database-instance-oo-design.md)
  - [Database Instance Refactor Plan](explanation/design-records/database-instance-refactor-plan.md)
  - [Database Platform OO Design](explanation/design-records/database-platform-oo-design.md)

---

### [development/](development/) - Development Documentation

- [TESTING.md](development/testing.md) - Complete testing guide
- [TESTING_QUICK_REF.md](development/testing-quick-ref.md) - Quick testing reference
- [UNIT_TESTING_SUMMARY.md](development/unit-testing-summary.md) - Unit testing summary
- [REFACTORING.md](development/refactoring.md) - Refactoring history

---

### [coding-standards/](development/coding-standards/) - Coding Standards

- [README.md](development/coding-standards/README.md) - Coding standards overview
- [Python](development/coding-standards/python-coding-standards.md) - Python coding standards
- [PowerShell](development/coding-standards/powershell-coding-standards.md) - PowerShell coding standards
- [Language Agnostic](development/coding-standards/language-agnostic-coding-standards.md) - General coding standards
- [Systems Design](development/coding-standards/systems-design-best-practices.md) - Systems design best practices
- [Enforcement Guide](development/coding-standards/enforcement-guide.md) - Guide on enforcing coding standards
- [General Standards](development/coding-standards/coding-standards.md) - Additional general coding standards

---

### [runbooks/](runbooks/) - Operational Runbooks

- [README.md](runbooks/README.md) - Runbooks overview
- [GMSA](runbooks/gmsa/) - Group Managed Service Account runbooks

---

### [vscode/](development/vscode/) - VS Code Setup

- [README.md](development/vscode/README.md) - VS Code documentation index
- [VSCODE_FEATURES.md](development/vscode/VSCODE_FEATURES.md) - VS Code features guide
- [DEVCONTAINER.md](development/vscode/DEVCONTAINER.md) - Dev container setup
- [DEVCONTAINER_BEGINNERS_GUIDE.md](development/vscode/DEVCONTAINER_BEGINNERS_GUIDE.md) - Dev container beginner guide
- [CICD_INTEGRATION.md](development/vscode/CICD_INTEGRATION.md) - CI/CD integration guide
- [DEVCONTAINER_SQLTOOLS.md](development/vscode/DEVCONTAINER_SQLTOOLS.md) - SQLTools extension configuration in Dev Container
- [PLATFORM_SPECIFIC.md](development/vscode/PLATFORM_SPECIFIC.md) - Platform-specific VS Code settings (Windows/Linux/macOS)
- [SECURITY_BEST_PRACTICES.md](development/vscode/SECURITY_BEST_PRACTICES.md) - Security best practices for VS Code development

---

### [archive/](archive/) - Archived Files

- [README_old.md](archive/README_old.md) - Original root README
- [validation-reports/](archive/validation-reports/) - Development validation and implementation reports

---

## Component Documentation

For component-specific documentation, see:

- **Package**: [../gds_snowflake/README.md](../gds_snowflake/README.md)
- **Application**: [../snowflake_monitoring/README.md](../snowflake_monitoring/README.md)

## Quick Links

- [Workspace Overview](../README.md)
