# UV architecture deep dive

**🔗 [← Back to UV Documentation Index](./README.md)**

> **Document Version:** 2.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Architecture-blue)

> [!IMPORTANT]
> **Related Docs:** [Adoption Rationale](./README.md) | [Getting Started](../../../tutorials/languages/python/uv/uv-getting-started.md) | [How-to Guides](../../../how-to/python/uv/) | [Reference](../../../reference/python/uv/uv-reference.md)

This document provides a technical deep dive into `uv`'s architecture, explaining how it achieves its performance and reliability.

## Table of contents

- [The speed story](#the-speed-story)
- [Core components](#core-components)
  - [Universal lock file](#universal-lock-file)
  - [The PubGrub resolver](#the-pubgrub-resolver)
  - [Global cache](#global-cache)
  - [Managed Python versions](#managed-python-versions)
- [Resolution strategy](#resolution-strategy)
- [Platform support](#platform-support)

---

## The speed story

[↑ Back to table of contents](#table-of-contents)

`uv` is not just "slightly" faster. It is written in **Rust**, enabling a magnitude of performance difference that changes how you work.

- **No garbage collection**: Unlike Python tools, `uv` has no GC pauses.
- **True parallelism**: It utilizes all CPU cores to download and unzip packages simultaneously.
- **Copy-on-write / hardlinking**: It creates virtual environments in milliseconds by linking to a global cache, rather than copying files.

| Operation | pip | UV | Speedup |
|:---|:---|:---|:---|
| Clean install (large project) | ~60s | ~2s | ~30x |
| Dependency resolution | ~30s | ~0.1s | ~300x |
| Create .venv | ~3s | ~0.01s | ~300x |
| Cached reinstall | ~15s | ~0.5s | ~30x |

[↑ Back to table of contents](#table-of-contents)

---

## Core components

[↑ Back to table of contents](#table-of-contents)

### Universal lock file

`uv.lock` is **cross-platform by design**. Unlike pip's `pip freeze` output (which captures only the current platform's state), UV resolves for all platforms simultaneously.

- **Cross-platform**: You can lock on a Mac and deploy to a Linux Docker container with zero fear of resolution changes.
- **TOML format**: The lock file is human-readable TOML, making diffs in version control meaningful.
- **Platform markers**: The lock file includes environment markers so each platform installs only the packages it needs.

```toml
# Example uv.lock entry
[[package]]
name = "requests"
version = "2.32.3"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "certifi" },
    { name = "charset-normalizer" },
    { name = "idna" },
    { name = "urllib3" },
]
```

### The PubGrub resolver

Dependency resolution is NP-hard. UV uses **PubGrub**, a state-of-the-art algorithm originally developed for the Dart language, that:

1. **Is mathematically optimized for speed**: Uses version-solving as a satisfiability problem, avoiding unnecessary backtracking.
2. **Provides human-readable error messages**: When conflicts occur, it explains exactly *why* package A conflicts with package B, showing the full chain of requirements.
3. **Resolves deterministically**: Given the same inputs, always produces the same output regardless of platform or order of operations.

### Global cache

UV maintains a global package cache (typically at `~/.cache/uv/`) that eliminates redundant downloads:

- **Content-addressed**: Packages are stored by their content hash, ensuring integrity.
- **Hardlinked into projects**: Virtual environments link to cached packages rather than copying them, saving disk space.
- **Shared across projects**: If two projects use the same version of `requests`, it is stored once on disk.
- **Prunable**: `uv cache prune` removes entries not referenced by any project.

### Managed Python versions

UV downloads "Portable Python Builds" (from the `python-build-standalone` project). These are:

- **Pre-compiled**: No waiting for compilation from source (unlike `pyenv`).
- **Statically linked**: Run on any Linux distribution without worrying about `glibc` versions.
- **Isolated**: Installed in `~/.local/share/uv/python/`, keeping your system directories clean.
- **Version-parallel**: Multiple Python versions coexist without conflict.

[↑ Back to table of contents](#table-of-contents)

---

## Resolution strategy

[↑ Back to table of contents](#table-of-contents)

UV's resolver supports several strategies for dependency resolution:

| Strategy | Behavior | Use case |
|:---|:---|:---|
| Default (highest) | Selects the highest compatible version of each package | Standard development |
| `--resolution lowest` | Selects the lowest compatible version | Testing minimum version compatibility |
| `--resolution lowest-direct` | Lowest for direct deps, highest for transitive | Verifying your version constraints are correct |

UV also supports **overrides** and **constraints** for advanced scenarios:

- **Overrides** (`[tool.uv.override-dependencies]`): Force a specific version of a package, ignoring what other packages request.
- **Constraints** (`--constraints` or `constraints.txt`): Add additional version limits without adding the package as a dependency.
- **Exclude newer** (`--exclude-newer`): Ignore packages published after a specific date, enabling reproducible resolution at a point in time.

[↑ Back to table of contents](#table-of-contents)

---

## Platform support

[↑ Back to table of contents](#table-of-contents)

UV is a single binary that runs on:

- **Linux**: x86_64, aarch64 (including musl-based Alpine)
- **macOS**: x86_64 (Intel), aarch64 (Apple Silicon)
- **Windows**: x86_64

The lock file resolves for all supported platforms simultaneously, meaning a `uv.lock` created on any platform works identically on all others.

[↑ Back to table of contents](#table-of-contents)

---

## Related documentation

- [UV Adoption Rationale](./README.md)
- [UV Getting Started](../../../tutorials/languages/python/uv/uv-getting-started.md)
- [UV Command Reference](../../../reference/python/uv/uv-reference.md)
- [Official UV Documentation](https://docs.astral.sh/uv/)
