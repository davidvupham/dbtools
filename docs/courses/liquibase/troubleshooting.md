# Liquibase Tutorial Troubleshooting

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 15, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Liquibase-blue)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick_reference.md) | [Reference Guide](../../reference/liquibase/liquibase-reference.md#troubleshooting)

This guide covers common issues and their solutions for the Liquibase tutorial.

---

## Container Issues

### Container Won't Start

**Symptoms:**

- `podman compose up` fails
- Container exits immediately after starting

**Solutions:**

```bash
# Check container logs
podman logs mssql_dev

# Verify password meets SQL Server requirements (8+ chars, complexity)
echo $MSSQL_LIQUIBASE_TUTORIAL_PWD

# Check if port is already in use
ss -tlnp | grep 14331

# Remove stale container and retry
podman rm -f mssql_dev
podman compose up -d mssql_dev
```

### Container Shows "Unhealthy"

**Symptoms:**

- `podman ps` shows `(unhealthy)` status
- SQL Server not accepting connections

**Solutions:**

```bash
# Wait longer for SQL Server to initialize (first run can take 30-60s)
podman logs -f mssql_dev

# Check if SQL Server process is running inside container
podman exec mssql_dev ps aux | grep sqlservr

# Verify sufficient memory (SQL Server needs 2GB minimum)
free -h
```

### Permission Denied on Volumes

**Symptoms:**

- Container exits with permission errors
- `/var/opt/mssql` access denied

**Solutions:**

```bash
# Ensure :Z,U flags are on volume mounts (SELinux/rootless Podman)
# These should already be in docker-compose.yml

# Fix ownership on data directory
sudo chown -R $UID:$GID /data/$USER/liquibase_tutorial

# Verify directory exists
ls -la /data/$USER/liquibase_tutorial/
```

---

## Connection Issues

### Cannot Connect to SQL Server

**Symptoms:**

- `sqlcmd` connection timeout
- Liquibase connection refused

**Solutions:**

```bash
# Verify container is running and healthy
podman ps | grep mssql

# Test connection from host
podman exec mssql_dev /opt/mssql-tools18/bin/sqlcmd \
  -C -S localhost -U sa -P "$MSSQL_LIQUIBASE_TUTORIAL_PWD" \
  -Q "SELECT 1"

# Check if using correct port
# Dev: 14331, Stg: 14332, Prd: 14333

# Verify environment variable is set
echo $MSSQL_LIQUIBASE_TUTORIAL_PWD
```

### Liquibase Cannot Reach SQL Server

**Symptoms:**

- `lb -e dev -- status` fails with connection error
- "Connection refused" or "Host not found"

**Solutions:**

```bash
# With slirp4netns, use host.containers.internal
# Check liquibase.mssql_dev.properties has correct URL:
# url=jdbc:sqlserver://host.containers.internal:14331;...

# Verify properties file exists
cat $LIQUIBASE_TUTORIAL_DATA_DIR/platform/mssql/database/orderdb/env/liquibase.mssql_dev.properties

# Test from Liquibase container
podman run --rm --network slirp4netns liquibase:latest \
  ping -c 1 host.containers.internal
```

---

## Liquibase Execution Issues

### Changeset Already Executed

**Symptoms:**

- `update` reports "changeset already executed"
- Changes not being applied

**Solutions:**

```bash
# Check what's been applied
lb -e dev -- history

# View pending changes
lb -e dev -- status

# If baseline was incorrectly applied, may need to clear tracking
# WARNING: Only do this in dev, never in production
lb -e dev -- changelog-sync-to-tag baseline
```

### Rollback Fails

**Symptoms:**

- `rollback-count 1` fails
- "No rollback SQL defined"

**Solutions:**

```bash
# Ensure changeset has rollback defined
# Check the SQL file for --rollback comment

# Example of proper rollback definition:
# --changeset author:id
# CREATE TABLE app.example (...);
# GO
# --rollback DROP TABLE IF EXISTS app.example;
```

### Checksum Validation Failed

**Symptoms:**

- "Checksum validation failed"
- MD5 hash mismatch

**Solutions:**

```bash
# NEVER modify a changeset after it's been applied
# If you must fix in dev:

# Option 1: Clear checksum (dev only)
lb -e dev -- clear-checksums

# Option 2: Mark as rerun
# Add runOnChange:true to changeset
```

---

## Environment Issues

### LIQUIBASE_TUTORIAL_DIR Not Set

**Symptoms:**

- Scripts fail with "variable not set"
- Paths not resolving

**Solutions:**

```bash
# Set the tutorial directory
export LIQUIBASE_TUTORIAL_DIR="/path/to/repo/docs/courses/liquibase"

# Source setup script
source "$LIQUIBASE_TUTORIAL_DIR/scripts/setup_tutorial.sh"

# Verify aliases are loaded
type lb
```

### Password Not Set

**Symptoms:**

- "MSSQL_LIQUIBASE_TUTORIAL_PWD is required"
- Connection authentication failures

**Solutions:**

```bash
# Set password (minimum 8 chars, uppercase, lowercase, number)
export MSSQL_LIQUIBASE_TUTORIAL_PWD="YourStr0ngP@ssword"

# Or use the prompt script
$LIQUIBASE_TUTORIAL_DIR/scripts/prompt_mssql_password.sh
```

---

## Cleanup Issues

### Cannot Remove Containers

**Symptoms:**

- `podman rm` fails
- Container in use

**Solutions:**

```bash
# Force stop and remove
podman stop mssql_dev mssql_stg mssql_prd
podman rm -f mssql_dev mssql_stg mssql_prd

# Remove all tutorial containers
podman ps -a | grep -E 'mssql_(dev|stg|prd)|liquibase' | awk '{print $1}' | xargs podman rm -f
```

### Data Directory Not Removed

**Symptoms:**

- `/data/$USER/liquibase_tutorial` still exists after cleanup

**Solutions:**

```bash
# Run cleanup script
$LIQUIBASE_TUTORIAL_DIR/scripts/cleanup_tutorial.sh

# Or manually remove
rm -rf /data/$USER/liquibase_tutorial
```

---

## Validation

Run the validation script to check your environment:

```bash
$LIQUIBASE_TUTORIAL_DIR/scripts/validate_tutorial.sh
```

This checks:

- Environment variables set
- Containers running and healthy
- Database connectivity
- Liquibase configuration

---

## Getting Help

1. Check container logs: `podman logs <container_name>`
2. Run validation: `./scripts/validate_tutorial.sh`
3. Review the [Quick Reference](./quick_reference.md)
4. Check [Architecture](./architecture.md) for network details
