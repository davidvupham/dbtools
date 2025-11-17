# GDS Liquibase - Database Change Management CI/CD

A comprehensive database change management package for the GDS ecosystem, providing Liquibase-based schema versioning and automated deployment through GitHub Actions.

## Installation

### Install from source

```bash
# Clone the repository
git clone https://github.com/davidvupham/dbtools.git
cd dbtools/gds_liquibase

# Install the package
pip install .

# Or install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Install from PyPI (when published)

```bash
pip install gds-liquibase
```

### Requirements

- Python 3.8+
- Liquibase 5.0+ (must be installed separately and available in PATH)
- JDBC drivers for your target databases

### Dependencies

This package integrates with other GDS packages:

- `gds-database` - Base database utilities
- `gds-postgres` - PostgreSQL support
- `gds-mssql` - Microsoft SQL Server support
- `gds-mongodb` - MongoDB support

## Quick Start

### Basic Usage

```python
from gds_liquibase import LiquibaseConfig, LiquibaseMigrationRunner

# Configure from environment variables
config = LiquibaseConfig.from_env()

# Or configure directly
config = LiquibaseConfig(
    changelog_file="changelogs/db.changelog-master.xml",
    url="jdbc:postgresql://localhost:5432/mydb",
    username="dbuser",
    password="dbpass",
)

# Create runner and execute migrations
runner = LiquibaseMigrationRunner(config)
runner.update()
```

### Configuration from Properties File

```python
from pathlib import Path
from gds_liquibase import LiquibaseConfig, LiquibaseMigrationRunner

# Load from liquibase.properties
config = LiquibaseConfig.from_properties_file(Path("liquibase.properties"))
runner = LiquibaseMigrationRunner(config)

# Check status
runner.status(verbose=True)

# Tag current state
runner.tag("release-1.0.0")
```

### Rollback Operations

```python
# Rollback to a specific tag
runner.rollback("release-1.0.0")

# Rollback specific number of changesets
runner.rollback_count(3)

# Generate rollback SQL without executing
runner.rollback_sql("release-1.0.0", output_file="rollback.sql")
```

### Managing Changelogs

```python
from pathlib import Path
from gds_liquibase import ChangelogManager

manager = ChangelogManager(Path("changelogs"))

# Create a new changelog
changelog = manager.create_changelog(
    author="developer@example.com",
    description="Database schema updates",
)

# List changesets in a changelog
changesets = manager.list_changesets(changelog)
for cs in changesets:
    print(f"{cs['id']}: {cs['comment']}")
```

## Quick Links

- **[📋 Project Plan](PROJECT_PLAN.md)** - Comprehensive implementation plan
- **[💻 Code Examples](examples/)** - Working code samples and templates
  - [GitHub Actions Workflows](examples/workflows/)
  - [Changelog Templates](examples/changelogs/)
  - [Configuration Files](examples/config/)
  - [Python Wrappers](examples/python/)
  - [Helm Charts](examples/helm/)

## Project Status

**Status**: Planning Phase
**Version**: 0.1.0 (Pre-release)
**Target Release**: Q1 2026

## 📋 Overview

This package provides:

- **Python wrapper** for Liquibase commands
- **GitHub Actions workflows** for automated database migrations
- **Multi-database support**: PostgreSQL, MSSQL, Snowflake, MongoDB
- **Environment management**: Dev, Staging, Production
- **Rollback capabilities** for safe deployments
- **Audit trail** for all database changes

## 📚 Documentation

- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Comprehensive implementation plan with:
  - Architecture and design
  - GitHub Actions workflow examples
  - Best practices and patterns
  - Implementation phases and timeline
  - Integration with existing gds_* packages

## 🏗️ Planned Structure

```
gds_liquibase/
├── gds_liquibase/              # Python package
│   ├── __init__.py
│   ├── migration_runner.py    # Liquibase command wrapper
│   ├── changelog_manager.py   # Changelog utilities
│   ├── validator.py            # Validation tools
│   └── config.py               # Configuration management
├── tests/                      # Test suite
├── examples/                   # Usage examples
├── docs/                       # User documentation
├── changelogs/                 # Database changelogs
└── PROJECT_PLAN.md            # Detailed project plan
```

## 🎯 Key Features (Planned)

### GitHub Actions Integration

- **Automated validation** on pull requests
- **Environment-specific deployments** (dev, staging, production)
- **Manual rollback workflows** with audit trail
- **Changelog preview generation** for reviews

### Python API

```python
from gds_liquibase import LiquibaseMigrationRunner, LiquibaseConfig

# Configure
config = LiquibaseConfig(
    changelog_file='changelogs/db.changelog-master.xml',
    url='jdbc:postgresql://localhost:5432/mydb',
    username='dbuser',
    password='password'
)

# Run migrations
runner = LiquibaseMigrationRunner(config)
runner.update()
runner.status(verbose=True)
```

### Multi-Database Support

| Database | Status | Driver |
|----------|--------|--------|
| PostgreSQL | Planned | org.postgresql:postgresql |
| MSSQL | Planned | com.microsoft.sqlserver:mssql-jdbc |
| Snowflake | Planned | net.snowflake:snowflake-jdbc |
| MongoDB | Planned | org.mongodb:mongodb-driver-sync + liquibase-mongodb extension |
| H2 (Testing) | Planned | com.h2database:h2 |

## 🔧 Technology Stack

- **Liquibase**: 5.0.0+ (Community or Secure Edition)
- **GitHub Actions**: `liquibase/setup-liquibase@v2`
- **Python**: 3.8+
- **Testing**: pytest

## 📖 Research & Best Practices

The project plan incorporates research from:

1. **Official Liquibase GitHub Action** (`liquibase/setup-liquibase`)
   - Automatic caching for faster workflows
   - Cross-platform support
   - Security best practices

2. **Liquibase Official Documentation**
   - Changelog organization patterns
   - Rollback strategies
   - Multi-environment deployments

3. **Industry Best Practices**
   - Semantic versioning for changes
   - Automated validation before deployment
   - Comprehensive audit trails
   - Zero-downtime deployment strategies

## 🚦 Getting Started (Future)

Once implemented, you'll be able to:

```bash
# Install the package
pip install gds-liquibase

# Initialize a new project
gds-liquibase init --database postgres

# Generate changelog from existing database
gds-liquibase generate-changelog --url jdbc:postgresql://localhost/mydb

# Validate changes
gds-liquibase validate

# Deploy changes
gds-liquibase update --environment dev
```

## 🤝 Integration with GDS Packages

Will integrate seamlessly with:

- **gds_postgres** - PostgreSQL connection management
- **gds_mssql** - SQL Server operations
- **gds_snowflake** - Snowflake data warehouse
- **gds_mongodb** - MongoDB NoSQL database operations (using liquibase-mongodb extension)
- **gds_vault** - Secure credential management

### MongoDB Support Details

MongoDB integration uses the [Liquibase MongoDB Extension](https://github.com/liquibase/liquibase-mongodb) which provides:

- **Collection Management**: Create, modify, and drop collections
- **Index Operations**: Create and manage indexes with various options
- **Schema Validation**: JSON Schema-based document validation
- **Document Operations**: Insert, update, and delete documents
- **Rollback Support**: Full rollback capabilities for MongoDB changes

**Note**: MongoDB requires additional setup:

- MongoDB JDBC driver JAR
- BSON library JAR
- liquibase-mongodb extension JAR

See [PROJECT_PLAN.md](PROJECT_PLAN.md) Appendix D for complete MongoDB configuration examples.

## 📅 Implementation Timeline

- **Week 1-2**: Foundation & package scaffolding
- **Week 3-4**: GitHub Actions workflows
- **Week 5-6**: Python implementation
- **Week 7-8**: Testing & documentation
- **Week 9**: Review & refinement
- **Week 10**: Production readiness

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed timeline.

## 🎓 Learning Resources

- [Liquibase Documentation](https://docs.liquibase.com/)
- [Liquibase University](https://learn.liquibase.com/)
- [setup-liquibase Action](https://github.com/liquibase/setup-liquibase)
- [Liquibase Best Practices](https://docs.liquibase.com/concepts/bestpractices.html)

## 📝 Contributing

Once the project is in active development, contributions will be welcome! See the project plan for areas where help is needed.

## 📄 License

MIT License (to be confirmed)

## 📧 Contact

For questions about this project, please contact the Database DevOps team.

---

**Next Steps**: Review the [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed implementation details and begin Phase 1 development.
