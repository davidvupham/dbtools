# Coding Standards

> Purpose: Index of language-specific coding standards
>
> Last Updated: 2025-11-07

## Overview

This repository maintains language-specific coding standards to ensure consistency, quality, and maintainability across all code generated or refactored by GPT-5 Codex.

## Language-Specific Standards

- **[Python Coding Standards](python-coding-standards.md)** — Style, typing, error handling, testing, security, and documentation practices for Python code.
- **[PowerShell Coding Standards](powershell-coding-standards.md)** — Style, parameters, error handling, testing, security, and documentation practices for PowerShell code.

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

- 2025-11-07 — Initial publication by GPT-5 Codex.
- 2025-11-07 — Split into language-specific documents for Python and PowerShell.
<!-- End of document -->
