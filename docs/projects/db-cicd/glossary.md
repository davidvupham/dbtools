# Glossary: db-cicd

| Term | Definition |
|------|------------|
| **Changelog** | File defining database schema changes (YAML/XML/JSON/SQL) |
| **Changeset** | Atomic unit of change with id, author, and rollback |
| **Drift** | Differences between expected schema and actual database state |
| **Policy Check** | Rule that validates changesets before deployment |
| **Flowfile** | YAML workflow orchestrating multiple Liquibase commands |
| **Targeted Rollback** | Rolling back specific changesets without affecting others |
| **DATABASECHANGELOG** | Liquibase tracking table for applied changesets |
| **Environment Protection** | GitHub feature requiring approvals for deployments |
| **CODEOWNERS** | GitHub file defining required reviewers per path |
