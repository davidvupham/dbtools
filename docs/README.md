# Project Documentation

This directory contains all project documentation organized by category.

## 📚 Documentation Structure

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

- [TESTING.md](development/TESTING.md) - Complete testing guide
- [TESTING_QUICK_REF.md](development/TESTING_QUICK_REF.md) - Quick testing reference
- [UNIT_TESTING_SUMMARY.md](development/UNIT_TESTING_SUMMARY.md) - Unit testing summary
- [REFACTORING.md](development/REFACTORING.md) - Refactoring history

---

### [coding-standards/](coding-standards/) - Coding Standards

- [README.md](coding-standards/README.md) - Coding standards overview
- [Python](coding-standards/python-coding-standards.md) - Python coding standards
- [PowerShell](coding-standards/powershell-coding-standards.md) - PowerShell coding standards
- [Language Agnostic](coding-standards/language-agnostic-coding-standards.md) - General coding standards
- [Systems Design](coding-standards/systems-design-best-practices.md) - Systems design best practices

---

### [runbooks/](runbooks/) - Operational Runbooks

- [README.md](runbooks/README.md) - Runbooks overview
- [GMSA](runbooks/gmsa/) - Group Managed Service Account runbooks

---

### [vscode/](vscode/) - VS Code Setup

- [README.md](vscode/README.md) - VS Code documentation index
- [VSCODE_FEATURES.md](vscode/VSCODE_FEATURES.md) - VS Code features guide
- [DEVCONTAINER.md](vscode/DEVCONTAINER.md) - Dev container setup
- [DEVCONTAINER_BEGINNERS_GUIDE.md](vscode/DEVCONTAINER_BEGINNERS_GUIDE.md) - Dev container beginner guide
- [CICD_INTEGRATION.md](vscode/CICD_INTEGRATION.md) - CI/CD integration guide

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

### Viewing Diagrams

GitHub renders Mermaid diagrams in Markdown natively. Open the architecture files in the GitHub UI to see class and sequence diagrams. In local editors without Mermaid preview, consider exporting SVGs via Mermaid CLI or simply rely on GitHub for viewing.
