# GitHub Workflow Design: db-cicd

## Overview

GitHub Actions workflows provide the orchestration layer for db-cicd, handling validation, approval gates, and deployment.

## Workflow Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    PR Opened / Push to main                  │
└─────────────────────────────┬────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Validation Workflow                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐   │
│  │ Checkout │→ │ Validate │→ │ Policy Check             │   │
│  │          │  │ Changelog│  │                          │   │
│  └──────────┘  └──────────┘  └──────────────────────────┘   │
└─────────────────────────────┬────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Deploy Workflow (main only)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Deploy   │→ │ Approval │→ │ Deploy   │→ │ Deploy     │  │
│  │ Dev      │  │ Gate     │  │ Stage    │  │ Prod       │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Reusable Workflows

### 1. Validate Changelog

```yaml
# .github/workflows/db-validate.yml
name: Validate Changelog

on:
  workflow_call:
    inputs:
      changelog-path:
        required: true
        type: string
      rules-path:
        required: false
        type: string
        default: '.github/policy-rules.yaml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Liquibase Validate
        run: liquibase --changelog-file=${{ inputs.changelog-path }} validate

      - name: Policy Check
        run: |
          db-cicd policy check \
            --changelog ${{ inputs.changelog-path }} \
            --rules ${{ inputs.rules-path }}
```

### 2. Deploy with Approval

```yaml
# .github/workflows/db-deploy.yml
name: Deploy Database Changes

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      properties-file:
        required: true
        type: string

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}  # Triggers approval
    steps:
      - uses: actions/checkout@v4

      - name: Fetch Secrets
        uses: hashicorp/vault-action@v2
        with:
          url: ${{ secrets.VAULT_ADDR }}
          token: ${{ secrets.VAULT_TOKEN }}
          secrets: |
            secret/data/liquibase/${{ inputs.environment }} url | DB_URL ;
            secret/data/liquibase/${{ inputs.environment }} username | DB_USER ;
            secret/data/liquibase/${{ inputs.environment }} password | DB_PASS

      - name: Deploy
        run: |
          liquibase \
            --defaults-file=${{ inputs.properties-file }} \
            --url="${DB_URL}" \
            --username="${DB_USER}" \
            --password="${DB_PASS}" \
            update

      - name: Record Audit
        run: |
          db-cicd audit record \
            --environment ${{ inputs.environment }} \
            --actor ${{ github.actor }} \
            --run-id ${{ github.run_id }}
```

## Environment Protection Rules

| Environment | Required Reviewers | Wait Timer | Branch Restriction |
|-------------|-------------------|------------|-------------------|
| dev | 0 | None | None |
| stage | 1 | None | main |
| prod | 2 | 5 minutes | main |

## CODEOWNERS

```
# .github/CODEOWNERS
# Database changes require DBA review
/changelog/ @org/dba-team
/platforms/*/databases/ @org/dba-team

# Production properties require security review
**/prod.properties @org/security-team
```
