# Runbooks Overview

## Table of Contents

- [Overview](#overview)
- [Usage Guidelines](#usage-guidelines)
  - [Audience](#audience)
  - [Change Control](#change-control)
  - [Structure](#structure)
  - [Conventions](#conventions)
- [Contribution Workflow](#contribution-workflow)
- [Support](#support)

## Overview

This directory contains runbooks for operational procedures that support the database tooling ecosystem. Each runbook is version-controlled, reviewed, and intended to be executable by on-call engineers, infrastructure administrators, and database reliability engineers.

## Usage Guidelines

### Audience

Operations teams responsible for database tooling services and their supporting infrastructure.

### Change Control

Follow the standard change management process before executing a runbook in production environments.

### Structure

Runbooks are organized by technology area, then by specific workload or scenario (for example, `gmsa/dpa`). Each runbook directory should include prerequisites, execution steps, validation guidance, and rollback instructions.

### Conventions

Use uppercase imperative verbs for step headings, include command snippets using PowerShell or Bash format as appropriate, and reference authoritative documentation when available.

## Contribution Workflow

1. Create a subdirectory that reflects the technology stack and scenario (e.g., `gmsa/dpa`).
2. Include a primary Markdown file named for the procedure (e.g., `migrate-*.md`).
3. Provide environment-specific notes, validation steps, and rollback guidance.
4. Update this README if the structure or conventions evolve.

## Support

For questions or proposals for new runbooks, open an issue in this repository with context and desired outcomes.
