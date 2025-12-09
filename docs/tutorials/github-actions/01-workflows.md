# GitHub Actions CI/CD

## Introduction
GitHub Actions automates your build, test, and deployment pipeline.

## Core Concepts

### Workflows
Defined in `.github/workflows/` as YAML files.
```yaml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run a script
        run: echo "Hello World"
```

### Triggers (`on`)
- `push`: Trigger on push to branch.
- `pull_request`: Trigger on PR.
- `schedule`: Cron jobs.

### Jobs and Steps
- **Jobs** run in parallel by default.
- **Steps** run sequentially inside a job.

### Secrets
Encrypted environment variables (e.g., `AWS_ACCESS_KEY`) stored in Repo Settings > Secrets.
- Usage: `${{ secrets.MY_SECRET }}`
