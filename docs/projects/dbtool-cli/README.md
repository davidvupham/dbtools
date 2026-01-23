# Project: dbtool-cli

**[← Back to Projects Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** DBRE Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Phase](https://img.shields.io/badge/Phase-Initiation-blue)

A unified CLI tool for Database Reliability Engineering (DBRE) that troubleshoots database alerts and performs operational tasks across a heterogeneous environment (Snowflake, SQL Server, MongoDB, PostgreSQL).

## Table of contents

- [Key features](#key-features)
- [Documentation index](#documentation-index)
- [Related projects](#related-projects)

## Key features

1. **Cross-platform support**: Runs seamlessly on Windows (Workstations) and Linux (Servers/WSL).
2. **Unified authentication**:
    - **Windows**: AD Integration via LDAP/Vault.
    - **Linux**: Kerberos ticket-based authentication with Vault.
3. **Troubleshooting module**: Automated diagnostic checks based on alert context.
4. **Ecosystem integrations**: Vault, Liquibase, Airflow, Ansible.

[↑ Back to Table of Contents](#table-of-contents)

## Documentation index

- [Project Plan](management/project-plan.md) - Timeline and milestones
- [Functional Specification](specs/functional-spec.md) - Requirements and user stories
- [Command Reference](specs/command-reference.md) - Full inventory of CLI commands
- [Technical Architecture](architecture/technical-architecture.md) - Authentication flows and design
- [Decision Log](management/decision-log.md) - Architectural decisions
- [Troubleshooting Guide](specs/troubleshooting.md) - Common issues and solutions

[↑ Back to Table of Contents](#table-of-contents)

## Related projects

- [dbtool-ai](../dbtool-ai/README.md) - AI/LLM Companion Service

[↑ Back to Table of Contents](#table-of-contents)
