# Examples Directory

This directory contains reference implementations and code samples for the gds_liquibase package.

## Directory Structure

```
examples/
├── workflows/          # GitHub Actions workflow examples
│   ├── liquibase-validate.yml
│   ├── liquibase-deploy-dev.yml
│   ├── liquibase-deploy-prod.yml
│   └── liquibase-rollback.yml
├── changelogs/         # Sample changelog files
│   ├── db.changelog-master.xml
│   └── mongodb-changelog.xml
├── config/             # Configuration file examples
│   ├── liquibase.properties
│   └── liquibase-mongodb.properties
├── python/             # Python wrapper examples
│   ├── liquibase_config.py
│   └── migration_runner.py
└── helm/               # Helm chart examples
    ├── Chart.yaml
    └── values.yaml
```

## Usage

### GitHub Actions Workflows

Copy the workflow files to your `.github/workflows/` directory:

```bash
cp examples/workflows/*.yml .github/workflows/
```

### Changelogs

Use as templates for your database changes:

```bash
cp examples/changelogs/db.changelog-master.xml changelogs/
```

### Configuration

Adapt the properties files for your environment:

```bash
cp examples/config/liquibase.properties .
```

### Python Examples

Import and use the Python wrappers:

```python
from gds_liquibase.examples.python.liquibase_config import LiquibaseConfig
from gds_liquibase.examples.python.migration_runner import LiquibaseMigrationRunner

config = LiquibaseConfig.from_env()
runner = LiquibaseMigrationRunner(config)
runner.update()
```

### Helm Charts

Deploy using the Helm chart templates:

```bash
helm install liquibase examples/helm/ -f examples/helm/values.yaml
```

## Documentation

For detailed information, see the [PROJECT_PLAN.md](../PROJECT_PLAN.md) in the parent directory.
