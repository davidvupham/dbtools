# Decision log: dbtool-cli

**[← Back to Project Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** DBRE Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Decisions-blue)

This document tracks architectural decisions for the `dbtool-cli` project using Architecture Decision Records (ADRs).

## Table of contents

- [ADR-000: Use decision log](#adr-000-use-decision-log)
- [ADR-001: Unified CLI wrapper strategy](#adr-001-unified-cli-wrapper-strategy)
- [ADR-002: Python Typer + Rich framework](#adr-002-python-typer--rich-framework)
- [ADR-003: Cross-platform authentication](#adr-003-cross-platform-authentication-vault)
- [ADR-004: Configuration precedence & paths](#adr-004-configuration-precedence--paths)

## ADR-000: Use decision log

* **Status**: Accepted
* **Context**: We need to track architectural decisions for the `dbtool-cli` project.
* **Decision**: Use `decision-log.md` in the `management/` folder.
* **Consequences**: All major design choices must be recorded here.

[↑ Back to Table of Contents](#table-of-contents)

## ADR-001: Unified CLI wrapper strategy

* **Status**: Accepted
* **Context**: The DBRE team uses many tools (Databases, Ansible, Terraform, Liquibase, Vault) with different syntaxes and auth patterns.
* **Decision**: Build a single "Meta-Tool" (`dbtool`) that wraps these underlying tools.
* **Consequences**:
  * **Pros**: Single interface, unified auth injection, standardized logging.
  * **Cons**: Must maintain wrappers; explicit dependency on external tools being present in paths.

[↑ Back to Table of Contents](#table-of-contents)

## ADR-002: Python Typer + Rich framework

* **Status**: Accepted
* **Context**: We need a modern, type-safe, and visually appealing CLI for engineers.
* **Decision**: Use **Typer** for argument parsing and **Rich** for terminal output.
* **Consequences**:
  * Clear, auto-generated help.
  * Beautiful tables/JSON output.
  * Python 3.12+ required.

[↑ Back to Table of Contents](#table-of-contents)

## ADR-003: Cross-platform authentication (Vault)

* **Status**: Accepted
* **Context**: Engineers use Windows; Servers use Linux. Auth must work on both.
* **Decision**:
  * **Linux**: Use Kerberos tickets (auto-negotiated via `requests-kerberos`).
  * **Windows**: Use Active Directory (LDAP) with Vault (`dbtool login` prompt).
* **Consequences**: Code must detect OS and switch auth strategies at runtime.

[↑ Back to Table of Contents](#table-of-contents)

## ADR-004: Configuration precedence & paths

* **Status**: Accepted
* **Context**: Tools like Ansible and Terraform live in different paths on different machines.
* **Decision**: Use a valid precedence order: CLI Flag > Env Var > Config File (`~/.config/dbtool/config.toml`).
* **Consequences**: Users must configure their `paths` in the TOML file for the wrappers to work.

[↑ Back to Table of Contents](#table-of-contents)
