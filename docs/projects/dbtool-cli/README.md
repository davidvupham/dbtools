# Project: dbtool-cli

**Status**: 🟡 In Progress (Initiation)

A unified CLI tool for Database Reliability Engineering (DBRE) to troubleshooting database alerts and performing operational tasks across a heterogeneous environment (Snowflake, SQL Server, MongoDB, PostgreSQL).

## Key Features (MVP)

1. **Cross-Platform Support**: Runs seamlessly on Windows (Workstations) and Linux (Servers/WSL).
2. **Unified Authentication**:
    - **Windows**: AD Integration via LDAP/Vault.
    - **Linux**: Kerberos ticket-based authentication with Vault.
3. **Troubleshooting Module**: Automated diagnostic checks based on alert context.
4. **Ecosystem Integrations**: Vault, Liquibase, Airflow, Ansible.

## Documentation Index

- [Project Plan](management/project-plan.md) - Timeline and logic.
- [Functional Specification](specs/functional-spec.md) - Requirements and User Stories.
- [Command Reference](specs/command-reference.md) - **Full Inventory of CLI Commands**.
- [Technical Architecture](architecture/technical-architecture.md) - Authentication flows and design.

### Related Projects

- [dbtool-ai](../dbtool-ai/README.md) - AI/LLM Companion Service.
