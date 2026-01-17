# Examples

This directory contains cross-cutting examples and sample configurations that span multiple packages or demonstrate integration patterns.

## Directory structure

| Directory | Description |
|-----------|-------------|
| `monitoring/` | Prometheus and observability configuration examples |
| `notebooks/` | Jupyter notebooks for experimentation and demos |

## Finding examples

Examples are organized following this convention:

### Package-specific examples

Each Python package may contain its own `examples/` directory:

```
python/gds_postgres/examples/    # PostgreSQL usage examples
python/gds_mongodb/examples/     # MongoDB usage examples
python/gds_mssql/examples/       # SQL Server usage examples
python/gds_snowflake/examples/   # Snowflake usage examples
python/gds_liquibase/examples/   # Liquibase configuration examples
python/gds_vault/docs/examples/  # Vault usage examples
```

### Tutorial examples

Tutorials may include hands-on examples:

```
docs/tutorials/infrastructure/docker/examples/
docs/tutorials/infrastructure/ansible/examples/
docs/tutorials/languages/python/modules/fastapi/examples/
docs/tutorials/databases/rabbitmq/examples/
```

### Cross-cutting examples (this directory)

Examples that demonstrate integration between multiple components or don't belong to a specific package are placed here.

## Contributing examples

When adding new examples:

1. **Package-specific**: Add to `python/gds_*/examples/`
2. **Tutorial-related**: Add to the relevant tutorial's `examples/` directory
3. **Cross-cutting**: Add here with a descriptive subdirectory name

Each example should include:
- Clear comments explaining the purpose
- README if complex
- Any required configuration files
