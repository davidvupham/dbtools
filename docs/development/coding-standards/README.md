# Coding Standards

> Version: 1.0.0
>
> Purpose: Index of language-specific coding standards for code generation and refactoring
>
> Last Updated: 2025-11-07

## Overview

This repository maintains comprehensive, beginner-friendly coding standards to ensure consistency, quality, and maintainability across all code. These standards serve both human programmers learning best practices and AI-generated code.

## Documentation

### Standards Documents

- **[Python Coding Standards](python-coding-standards.md)** — Comprehensive guide covering style, naming conventions, typing, error handling, concurrency, testing, security, and documentation. Includes detailed explanations and examples for beginners.

- **[PowerShell Coding Standards](powershell-coding-standards.md)** — Complete guide covering style, naming conventions, parameters, error handling, testing, security, and documentation. Includes detailed explanations and examples for beginners.

- **[Language-Agnostic Coding Standards](language-agnostic-coding-standards.md)** — Baseline principles and expectations that apply to all languages: clarity, structure, error handling, logging, testing, security, performance, and CI/CD.

- **[Systems Design Best Practices](systems-design-best-practices.md)** — Technology-agnostic guidance for designing reliable, scalable, secure, and observable systems; includes resilience, data modeling, API contracts, caching, async, deployment, and operational readiness checklists.

### Enforcement Guide

- **[Enforcement Guide](enforcement-guide.md)** — Practical guide for enforcing coding standards through automation, tooling, pre-commit hooks, CI/CD pipelines, and IDE integration. Includes complete configuration examples for all tools.

## Key Features

Both standards documents include:

- **Detailed Explanations**: Every concept is explained with "what it is" and "why it matters"
- **Naming Conventions**: Clear definitions of snake_case, PascalCase, and UPPER_SNAKE_CASE with examples
- **Practical Examples**: Code samples showing both good and bad practices
- **Beginner-Friendly**: Written to be accessible to programmers at all skill levels
- **Best Practices**: Based on industry standards (PEP 8, PowerShell best practices)
- **Security Guidance**: Input validation, secret management, and vulnerability prevention
- **Testing Strategies**: Unit testing, mocking, and test organization

## General Expectations

All code, regardless of language, should:

- Document assumptions, external dependencies, and side effects in README entries or module-level notes; link to runbooks when available.
- Keep behavior deterministic and idempotent; prefer pure functions when practical and surface intentional statefulness in documentation.
- Provide clear commit messages and change summaries when handing off work.
- Run formatters, linters, type checkers, and automated tests before completion; report any skipped step with justification.
- Eliminate hard-coded secrets; rely on environment variables, secret stores, or configuration injection and scrub logs of sensitive data.
- Pin tooling versions in dependency manifests to maintain reproducibility.

## Quick Start

### For Developers

1. Read the relevant coding standards: [Python](python-coding-standards.md) or [PowerShell](powershell-coding-standards.md)
2. Set up your IDE using configurations from the [Enforcement Guide](enforcement-guide.md#ide-integration)
3. Install pre-commit hooks: `pre-commit install`
4. Run quality checks before committing: `make all` (Python) or `./build.ps1` (PowerShell)

### For Teams

1. Review all three documents with your team
2. Customize tool configurations in the [Enforcement Guide](enforcement-guide.md) for your needs
3. Set up CI/CD pipelines using provided examples
4. Add quality gates to your pull request process

## Maintenance

- Revisit these documents whenever language versions, linters, or project requirements change.
- Record updates with dates and a short rationale in the version history sections of each language-specific document.

## Version History

### 1.0.0 (2025-11-07)

- Initial publication
- Split into language-specific documents for Python and PowerShell
- Enhanced both documents with detailed explanations, examples, and beginner-friendly definitions
- Added comprehensive Enforcement Guide with tooling, CI/CD, and automation practices

<!-- End of document -->
