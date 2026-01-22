# Decision Log: dbtool-cli

## ADR-000: Use Decision Log

* **Status**: Accepted
* **Context**: We need to track architectural decisions for the `dbtool-cli` project.
* **Decision**: Use `decision-log.md` in the `management/` folder.
* **Consequences**: All major design choices must be recorded here.

## ADR-001: Unified CLI Wrapper Strategy

* **Status**: Accepted
* **Context**: The DBRE team uses many tools (Databases, Ansible, Terraform, Liquibase, Vault) with different syntaxes and auth patterns.
* **Decision**: Build a single "Meta-Tool" (`dbtool`) that wraps these underlying tools.
* **Consequences**:
  * **Pros**: Single interface, unified auth injection, standardized logging.
  * **Cons**: Must maintain wrappers; explicit dependency on external tools being present in paths.

## ADR-002: Python Typer + Rich Framework

* **Status**: Accepted
* **Context**: We need a modern, type-safe, and visually appealing CLI for engineers.
* **Decision**: Use **Typer** for argument parsing and **Rich** for terminal output.
* **Consequences**:
  * Clear, auto-generated help.
  * Beautiful tables/JSON output.
  * Python 3.12+ required.

## ADR-003: Cross-Platform Authentication (Vault)

* **Status**: Accepted
* **Context**: Engineers use Windows; Servers use Linux. Auth must work on both.
* **Decision**:
  * **Linux**: Use Kerberos tickets (auto-negotiated via `requests-kerberos`).
  * **Windows**: Use Active Directory (LDAP) with Vault (`dbtool login` prompt).
* **Consequences**: Code must detect OS and switch auth strategies at runtime.

## ADR-004: Configuration Precedence & Paths

* **Status**: Accepted
* **Context**: Tools like Ansible and Terraform live in different paths on different machines.
* **Decision**: Use a valid precedence order: CLI Flag > Env Var > Config File (`~/.config/dbtool/config.toml`).
* **Consequences**: Users must configure their `paths` in the TOML file for the wrappers to work.
