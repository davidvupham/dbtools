# Drift Detector Design: db-cicd

## Overview

The Drift Detector compares the current database state against the expected state from changelogs, identifying unauthorized changes.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Drift Detector                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │ Snapshot │→ │ Diff     │→ │ Alert + Report       │ │
│  │ Capture  │  │ Analyzer │  │ Generator            │ │
│  └──────────┘  └──────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

## Detection Workflow

1. Capture current database snapshot using `liquibase snapshot`
2. Run `liquibase diff` against changelog or previous snapshot
3. Parse diff output (JSON format)
4. Categorize changes: Missing, Unexpected, Changed
5. Generate report
6. Send alert if drift detected

## CLI Interface

```bash
# Run drift detection
db-cicd drift check \
  --properties /path/to/liquibase.properties \
  --reference snapshot  # or 'changelog'
  --output drift-report.html \
  --alert-webhook $SLACK_WEBHOOK

# Compare two databases
db-cicd drift compare \
  --source liquibase.dev.properties \
  --target liquibase.prod.properties \
  --output comparison-report.html
```

## Report Format

```json
{
  "timestamp": "2025-12-20T10:00:00Z",
  "database": "customer_db",
  "environment": "prod",
  "drift_detected": true,
  "summary": {
    "missing_objects": 0,
    "unexpected_objects": 2,
    "changed_objects": 1
  },
  "details": [
    {
      "type": "UNEXPECTED",
      "object": "TABLE public.temp_debug",
      "description": "Table exists in database but not in changelog"
    }
  ]
}
```

## Scheduling (GitHub Actions)

```yaml
# .github/workflows/drift-check.yml
name: Daily Drift Check

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC

jobs:
  drift-check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        database: [customer, orders, inventory]
    steps:
      - uses: actions/checkout@v4

      - name: Fetch Secrets
        uses: hashicorp/vault-action@v2
        with:
          secrets: secret/data/db/${{ matrix.database }}/prod

      - name: Run Drift Check
        run: |
          db-cicd drift check \
            --properties env/liquibase.${{ matrix.database }}.prod.properties \
            --output drift-${{ matrix.database }}.html

      - name: Alert on Drift
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {"text": "Drift detected in ${{ matrix.database }}"}
```

## Alert Channels

- Slack webhook
- PagerDuty (via `gds_notification`)
- Email
- GitHub Issue (auto-create)
