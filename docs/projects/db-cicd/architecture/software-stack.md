# Software Stack: db-cicd

## Languages & Runtimes

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Policy engine, drift detector, reports, audit |
| Bash | 5.x | Wrapper scripts, orchestration |
| Liquibase | 5.0+ | Core database change management |

## Python Packages

| Package | Purpose |
|---------|---------|
| `pyyaml` | Parse YAML changelogs |
| `lxml` | Parse XML changelogs |
| `jinja2` | HTML report templates |
| `pyodbc` / `psycopg2` | Database connectivity |
| `hvac` | HashiCorp Vault client |
| `boto3` | AWS SDK (Secrets Manager) |
| `requests` | HTTP client for notifications |

## CI/CD

| Tool | Purpose |
|------|---------|
| GitHub Actions | Workflow orchestration |
| GitHub Environments | Approval gates |
| CODEOWNERS | Required reviewers |

## Observability

| Tool | Purpose |
|------|---------|
| Elasticsearch / OpenSearch | Log storage and search |
| Splunk (optional) | Enterprise log aggregation |
| Grafana (optional) | Dashboards |

## Secrets Management

| Tool | Status |
|------|--------|
| HashiCorp Vault | Primary (recommended) |
| AWS Secrets Manager | Alternative |
| Environment Variables | Fallback for dev |
