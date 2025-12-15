# pre-commit (docs-as-code)

This folder provides an example `.pre-commit-config.yaml` for documentation checks.

## Why pre-commit

- Same checks run locally and in CI
- Fast feedback before PR

## Prerequisites

- Python (for `pre-commit`)
- Node.js (for `markdownlint-cli2` and `cspell`)
- Vale (binary)
- Lychee (binary)

## Install tools

### pre-commit

Linux/WSL:

```bash
python3 -m pip install --user pre-commit
```

Windows PowerShell:

```powershell
py -m pip install --user pre-commit
```

### Node-based tools

In the target repo root:

```bash
npm init -y
npm install --save-dev markdownlint-cli2 cspell
```

(If you already have a `package.json`, just install the dev dependencies.)

### Vale

Install instructions vary by OS; once installed, validate:

```bash
vale --version
```

### Lychee

Install instructions vary by OS; once installed, validate:

```bash
lychee --version
```

## Enable hooks

Copy `pre-commit/pre-commit-config.yaml` into the target repo root as `.pre-commit-config.yaml`, then:

```bash
pre-commit install
pre-commit run --all-files
```

## Suggested workflow

- Keep local hooks fast (markdownlint + cspell)
- Run Vale + Lychee in CI as the authoritative gate
