# Appendix C — Packaging, Boundaries, and Public API Design (Python)

Design goal: clear module boundaries, stable public API, minimal coupling.

## Suggested Layout (example)
```
my_lib/
  __init__.py          # re-export public symbols, set __all__
  __version__.py
  core/                # core domain types (low deps)
    __init__.py
    item.py            # Item, Book, EBook...
    pricing.py         # strategies
  services/            # orchestrators; depend on core via interfaces
    __init__.py
    library.py         # Library, Inventory
    notify.py          # NotificationService interface + impls
  adapters/            # I/O, DB, integrations (optional)
    __init__.py
    repo_sqlite.py
  _internal/           # helpers not part of public API
    utils.py
```

## Public API via `__init__.py`
```python
# my_lib/__init__.py
from .core.item import Item, Book, EBook
from .services.library import Library

__all__ = ["Item", "Book", "EBook", "Library"]
```
- Re-export stable, documented types only.
- Keep unstable helpers under `_internal` and avoid re-exporting.

## Dos & Don’ts
- Do
  - Depend on abstractions (ABCs/Protocols) across package layers (DIP).
  - Keep `core` small and free of I/O; push integrations to `adapters`.
  - Provide factories for object creation when constructors get complex.
  - Document deprecations and keep a CHANGELOG; version your API.
- Don’t
  - Don’t create cyclic imports; split modules or invert dependency.
  - Don’t export everything; curate your public surface.
  - Don’t leak exceptions from adapters; translate to domain errors.

## Avoiding Cycles
- Move shared types to `core`.
- Use interfaces (Protocols/ABCs) for cross-layer references.
- Defer imports inside functions if needed (last resort).

## Versioning & Deprecation
- Semantic versioning; only break API on major versions.
- Mark deprecated members in docs; emit warnings when feasible.

## Pros/Cons of Re-exporting
- Pros: Simple import paths for users; stable facade.
- Cons: Requires curation and maintenance; hides internal structure.
