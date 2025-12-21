# Implementation Guide: db-cicd

## Prerequisites

- Python 3.11+
- Liquibase 5.0+
- GitHub Actions (self-hosted or GitHub-hosted runners)
- Access to secrets manager (Vault or AWS)

## Installation

### 1. Install db-cicd Package

```bash
# From sources (development)
cd packages/gds_db_cicd
uv pip install -e .

# From wheel (production)
pip install gds_db_cicd-*.whl
```

### 2. Configure Policy Rules

Create `.github/policy-rules.yaml`:

```yaml
rules:
  - id: no-drop-table
    name: Block DROP TABLE
    severity: ERROR
    pattern:
      type: sql-regex
      match: "DROP\\s+TABLE"
```

### 3. Set Up GitHub Workflows

Copy reusable workflows to your repository:

```bash
cp .github/workflows/db-*.yml <your-repo>/.github/workflows/
```

### 4. Configure Environments

In GitHub repo settings, create environments:

- `dev` - No protection
- `stage` - Require 1 reviewer
- `prod` - Require 2 reviewers, 5-minute wait

## Usage

### Run Policy Checks Locally

```bash
db-cicd policy check \
  --changelog changelog/db.changelog-master.yaml \
  --rules .github/policy-rules.yaml
```

### Run Drift Detection

```bash
db-cicd drift check \
  --properties env/liquibase.prod.properties
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Rule not found" | Check rule ID in policy-rules.yaml |
| "Connection failed" | Verify secrets are injected correctly |
| "Approval timeout" | Check GitHub Environment settings |
