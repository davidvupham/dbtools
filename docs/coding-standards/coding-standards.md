# Coding Standards

> Purpose: Index of language-specific coding standards
>
> Last Updated: 2025-11-07

## Overview

This repository maintains language-agnostic and language-specific coding standards to ensure consistency, quality, and maintainability across all code.

## Language-Specific Standards

- **[Python Coding Standards](python-coding-standards.md)** — Style, typing, error handling, testing, security, and documentation practices for Python code.
- **[PowerShell Coding Standards](powershell-coding-standards.md)** — Style, parameters, error handling, testing, security, and documentation practices for PowerShell code.

## Language-Agnostic Standards

- **[Language-Agnostic Coding Standards](language-agnostic-coding-standards.md)** — Baseline principles that apply to all languages: readability, structure, error handling, logging, testing, security, performance, and CI/CD expectations.
- **[Systems Design Best Practices](systems-design-best-practices.md)** — Technology-agnostic guidance for resilient, scalable, secure, and observable system architectures.

## General Expectations

All code, regardless of language, should:

- Document assumptions, external dependencies, and side effects in README entries or module-level notes; link to runbooks when available.
- Keep behavior deterministic and idempotent; prefer pure functions when practical and surface intentional statefulness in documentation.
- Provide clear commit messages and change summaries when handing off work.
- Run formatters, linters, type checkers, and automated tests before completion; report any skipped step with justification.
- Eliminate hard-coded secrets; rely on environment variables, secret stores, or configuration injection and scrub logs of sensitive data.
- Pin tooling versions in dependency manifests to maintain reproducibility.

## Maintenance

- Revisit these documents whenever language versions, linters, or project requirements change.
- Record updates with dates and a short rationale in the version history sections of each language-specific document.

## Version History

- 2025-11-07 — Initial publication.
- 2025-11-07 — Split into language-specific documents for Python and PowerShell.
<!-- End of document -->
