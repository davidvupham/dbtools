# Policy Engine Design: db-cicd

## Overview

The Policy Engine validates changelogs against configurable rules before deployment. It replaces Liquibase Pro's Quality Checks feature.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Policy Engine                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │ Parser   │→ │ Rule     │→ │ Report Generator     │ │
│  │ (YAML/   │  │ Engine   │  │ (HTML/JSON)          │ │
│  │ XML/SQL) │  │          │  │                      │ │
│  └──────────┘  └──────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

## Rule Definition Format

Rules are defined in YAML:

```yaml
# policy-rules.yaml
rules:
  - id: no-drop-table
    name: Block DROP TABLE
    severity: ERROR  # ERROR | WARNING | INFO
    scope: changeset  # changeset | changelog | database
    pattern:
      type: sql-regex
      match: "DROP\\s+TABLE"
    message: "DROP TABLE requires explicit approval"

  - id: require-rollback
    name: Require Rollback Block
    severity: ERROR
    scope: changeset
    condition:
      type: missing-element
      element: rollback
    message: "All changesets must include rollback"
```

## Built-in Rules (Phase 1)

| Rule ID | Name | Severity |
|---------|------|----------|
| `no-drop-table` | Block DROP TABLE | ERROR |
| `no-drop-column` | Block DROP COLUMN | WARNING |
| `require-rollback` | Require rollback block | ERROR |
| `require-labels` | Require labels on changesets | WARNING |
| `check-naming` | Enforce naming conventions | WARNING |
| `no-raw-sql-ddl` | Prefer Liquibase DDL over raw SQL | INFO |

## CLI Interface

```bash
# Check changelog against rules
db-cicd policy check \
  --changelog /path/to/changelog.yaml \
  --rules /path/to/policy-rules.yaml \
  --output report.html

# Exit codes:
# 0 = All checks passed
# 1 = Errors found (deployment blocked)
# 2 = Warnings found (deployment allowed)
```

## Integration with GitHub Actions

```yaml
# .github/workflows/validate.yml
jobs:
  policy-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Policy Checks
        run: |
          db-cicd policy check \
            --changelog changelog/db.changelog-master.yaml \
            --rules .github/policy-rules.yaml \
            --output policy-report.html

      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: policy-report
          path: policy-report.html
```

## Custom Rules

Users can add custom Python rules:

```python
# custom_rules/my_rule.py
from gds_db_cicd.policy import Rule, RuleResult

class MyCustomRule(Rule):
    id = "my-custom-rule"
    name = "My Custom Rule"
    severity = "ERROR"

    def evaluate(self, changeset) -> RuleResult:
        if some_condition(changeset):
            return RuleResult.fail("Reason for failure")
        return RuleResult.pass_()
```
