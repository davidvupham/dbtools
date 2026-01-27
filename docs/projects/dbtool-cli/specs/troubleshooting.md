# Troubleshooting guide: dbtool-cli

**[← Back to Project Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** GDS Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Troubleshooting-blue)

This guide helps you diagnose and resolve common issues when using `dbtool`.

## Table of contents

- [Authentication issues](#authentication-issues)
- [Connection issues](#connection-issues)
- [Command issues](#command-issues)
- [Configuration issues](#configuration-issues)
- [Getting help](#getting-help)

## Authentication issues

### Kerberos ticket expired (Linux)

**Symptom**: `VAULT_AUTH_FAILED: Kerberos ticket invalid or expired`

**Resolution**:
1. Check your current ticket status:
   ```bash
   klist
   ```
2. If expired or missing, obtain a new ticket:
   ```bash
   kinit
   ```
3. Retry your `dbtool` command.

[↑ Back to Table of Contents](#table-of-contents)

### Vault token expired

**Symptom**: `VAULT_AUTH_FAILED: Token expired`

**Resolution**:
- **Linux**: Obtain a new Kerberos ticket with `kinit`, then retry.
- **Windows**: Run `dbtool login` to re-authenticate.

[↑ Back to Table of Contents](#table-of-contents)

### AD credentials rejected (Windows)

**Symptom**: `VAULT_AUTH_FAILED: Invalid credentials`

**Resolution**:
1. Verify you are using the correct AD domain (check `config.toml`).
2. Ensure your account is not locked or disabled:
   ```bash
   dbtool ck ad <your-username> --status
   ```
3. Reset your password if necessary.

[↑ Back to Table of Contents](#table-of-contents)

## Connection issues

### Database unreachable

**Symptom**: `CONNECTION_TIMEOUT: Unable to connect to <target>`

**Resolution**:
1. Verify network connectivity:
   ```bash
   ping <hostname>
   ```
2. Check if the database port is accessible:
   ```bash
   nc -zv <hostname> <port>
   ```
3. Verify firewall rules allow traffic from your machine.
4. Confirm the target exists in the inventory:
   ```bash
   dbtool inventory list | grep <target>
   ```

[↑ Back to Table of Contents](#table-of-contents)

### Target not found

**Symptom**: `TARGET_NOT_FOUND: <target> not in inventory`

**Resolution**:
1. Check spelling of the target name.
2. List available targets:
   ```bash
   dbtool inventory list
   ```
3. If the target is new, contact the team to add it to the inventory.

[↑ Back to Table of Contents](#table-of-contents)

## Command issues

### Command not recognized

**Symptom**: `Error: No such command '<command>'`

**Resolution**:
1. Check available commands:
   ```bash
   dbtool --help
   ```
2. Verify you are using the correct alias (e.g., `ck` for `check`, `sh` for `shell`).
3. Update to the latest version of `dbtool`.

[↑ Back to Table of Contents](#table-of-contents)

### Permission denied

**Symptom**: `PERMISSION_DENIED: Insufficient Vault policy permissions`

**Resolution**:
1. Your Vault policy may not grant access to this database.
2. Contact the security team to request appropriate permissions.
3. Verify you are authenticating with the correct identity.

[↑ Back to Table of Contents](#table-of-contents)

### Driver not found

**Symptom**: `DRIVER_NOT_FOUND: <driver> not installed`

**Resolution**:

| Database | Required Driver | Install Command |
|----------|-----------------|-----------------|
| PostgreSQL | psycopg | `pip install psycopg[binary]` |
| SQL Server | pymssql | `pip install pymssql` |
| MongoDB | pymongo | `pip install pymongo` |
| Snowflake | snowflake-connector-python | `pip install snowflake-connector-python` |

[↑ Back to Table of Contents](#table-of-contents)

## Configuration issues

### Config file not found

**Symptom**: `Config file not found, using defaults`

**Resolution**:
1. Create the config directory:
   - **Linux**: `mkdir -p ~/.config/dbtool`
   - **Windows**: Create `%APPDATA%\dbtool\`
2. Create `config.toml` with your settings:
   ```toml
   [auth]
   ad_domain = "CONTOSO"
   vault_url = "https://vault.example.com"
   vault_namespace = "db-ops"

   [defaults]
   output_format = "table"
   ```

[↑ Back to Table of Contents](#table-of-contents)

### Invalid config syntax

**Symptom**: `Config parse error: <details>`

**Resolution**:
1. Validate your TOML syntax using an online validator.
2. Ensure all string values are quoted.
3. Check for missing closing brackets or quotes.

[↑ Back to Table of Contents](#table-of-contents)

## Getting help

If you cannot resolve your issue:

1. **Check debug output**: Add `--debug` to your command for detailed logging.
2. **Review logs**: Check `~/.local/share/dbtool/logs/` for detailed error information.
3. **Contact the team**: Reach out to the DBRE team with:
   - The exact command you ran
   - The full error message
   - Your OS and `dbtool` version (`dbtool --version`)

[↑ Back to Table of Contents](#table-of-contents)
