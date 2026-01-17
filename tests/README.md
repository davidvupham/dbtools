# Integration tests

This directory contains cross-package integration tests only.

## Guidelines

- **Package-specific tests** belong in `python/gds_*/tests/`
- **Integration tests** that span multiple packages belong here
- Each test file should clearly document which packages it integrates

## Current tests

| File | Purpose |
|------|---------|
| `test_cert_migration.py` | Certificate migration integration tests |
