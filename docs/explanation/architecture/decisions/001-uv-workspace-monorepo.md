# ADR-001: Use UV workspace for Python monorepo

## Status

Accepted

## Context

The dbtools repository contains multiple Python packages that share common dependencies and are often developed together. We needed a solution that:

- Allows multiple packages to share a single lockfile for reproducibility
- Supports local package dependencies without publishing to PyPI
- Provides fast dependency resolution and installation
- Works well with modern Python tooling

Options considered:

1. **Separate repositories**: Each package in its own repo with separate CI/CD
2. **pip + requirements.txt**: Traditional approach with manual dependency management
3. **Poetry workspaces**: Poetry's monorepo support
4. **UV workspaces**: Astral's UV tool with workspace support

## Decision

We chose UV workspaces for managing the Python monorepo.

Configuration in root `pyproject.toml`:

```toml
[tool.uv.workspace]
members = ["python/*"]
```

Each package in `python/gds_*/` has its own `pyproject.toml` and can depend on other workspace packages.

## Consequences

### Benefits

- **Single lockfile** (`uv.lock`) ensures all developers and CI use identical dependency versions
- **Fast resolution**: UV is significantly faster than pip or Poetry for dependency resolution
- **Local dependencies**: Packages can depend on each other using workspace references
- **Simplified CI**: One lockfile to cache and restore across all packages
- **Modern tooling**: UV integrates well with pyproject.toml standards

### Trade-offs

- **Newer tool**: UV is less mature than pip or Poetry; may have edge cases
- **Learning curve**: Developers need to learn UV commands
- **Ecosystem support**: Some tools may not fully support UV yet

### Migration notes

- Existing packages were migrated by adding workspace configuration
- Dependencies were consolidated into the root lockfile
- CI workflows were updated to use `uv sync` instead of `pip install`
