# Tooling (examples you can copy)

This folder contains **example configurations** and **scripts** to implement docs-as-code in another repository.

These examples are designed for internal-only docs and do not require a docs website.

## What you copy into the target repo

Minimum recommended set (copy to repo root unless noted):

- `.pre-commit-config.yaml` (from `pre-commit/pre-commit-config.yaml`)
- `.github/workflows/docs-checks.yml` (from `github-actions/docs-checks.yml`)
- `.markdownlint-cli2.yaml` (from `markdownlint/markdownlint-cli2.yaml`)
- `cspell.json` (from `cspell/cspell.json`)
- `.vale.ini` and `styles/` (from `vale/vale.ini` and `vale/styles/`)
- `lychee.toml` (from `lychee/lychee.toml`)
- Optional helper scripts: `scripts/run-doc-checks.*`

### Rename note (important)

Some of these are stored here without a leading dot to make them easier to browse and copy. When you copy them into the **target repo root**, rename them as shown above:

- `pre-commit/pre-commit-config.yaml` → `.pre-commit-config.yaml`
- `markdownlint/markdownlint-cli2.yaml` → `.markdownlint-cli2.yaml`
- `vale/vale.ini` → `.vale.ini`

## Tool choices (why these)

- **markdownlint-cli2**: consistent Markdown formatting rules
- **cspell**: spellcheck that works well in repositories (custom dictionaries)
- **Vale**: terminology and style linting (great for consistency)
- **Lychee**: link checking
- **pre-commit**: one command to run the checks locally, same checks in CI

## Running checks locally

Linux/WSL:

```bash
bash tooling/scripts/run-doc-checks.sh
```

Windows PowerShell:

```powershell
pwsh -File tooling/scripts/run-doc-checks.ps1
```

## CI

Use GitHub Actions example at `github-actions/docs-checks.yml`.
