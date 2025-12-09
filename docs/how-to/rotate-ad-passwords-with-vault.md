# How-to: Rotate Active Directory Passwords with HashiCorp Vault

This guide details how to configure HashiCorp Vault to manage and rotate Active Directory (AD) passwords. This functionality is critical for securing service accounts used by database platforms such as Microsoft SQL Server, PostgreSQL, MongoDB, and Snowflake across both Windows and Linux environments.

## Introduction

Rotating passwords for privileged Active Directory accounts is a fundamental security practice. Manual rotation is error-prone and can cause outages. HashiCorp Vault's **Active Directory Secrets Engine** automates this process by:

1. Managing the AD account's password directly.
2. Automatically rotating the password based on a Time-To-Live (TTL).
3. Generating dynamic, strictly scoped credentials for applications.

## Prerequisites

- **HashiCorp Vault** installed and unsealed.
- **Active Directory** domain controller accessible from Vault.
- **Service Account for Vault**: An AD account with permissions to reset passwords on the target User/Service accounts.
  - Required permissions: `Reset Password`, `Read/Write Properties` on target objects.

## Step 1: Enable and Configure the AD Secrets Engine

First, enable the engine and configure it to talk to your Domain Controller.

```bash
# 1. Enable the AD secrets engine
vault secrets enable ad

# 2. Configure the connection config
# binddn: The account Vault uses to perform operations
# url: Your Domain Controller URL (LDAPS recommended)
vault write ad/config \
    binddn="CN=Vault Service,CN=Users,DC=example,DC=com" \
    bindpass='<bind_password>' \
    url=ldaps://dc01.example.com
```

> **Note**: Store the `bindpass` securely or input it interactively.

## Step 2: Configure a Role

A "Role" in Vault maps a name to a specific AD Service Account that Vault will manage.

```bash
# Configure a role for a database service account
# service_account_name: The actual SAMAccountName in AD
vault write ad/roles/db-metrics-collector \
    service_account_name="svc_metrics_collector" \
    ttl=24h
```

Depending on whether you want **Shared** (static account, rotated periodically) or **Dynamic** (Vault creates/deletes users) accounts, the configuration differs. The example above is for a **Shared** account (the account exists in AD, Vault rotates its password).

### For Shared Accounts (Password Rotation)

Vault will rotate the password of `svc_metrics_collector` periodically or on demand. Applications "checkout" the credentials to get the *current* password.

## Step 3: Rotate the Password

You can force a rotation immediately or let Vault handle it based on TTL.

```bash
# Manually rotate the password for the role
vault write -f ad/rotate/roles/db-metrics-collector
```

## Considerations for Database Platforms

When Vault rotates the AD password, any service or application using the old password will fail authentication once the grace period (if configured) expires or immediately. You must ensure your consumers are "Vault-aware" or use a mechanism to retrieve the new password.

### Microsoft SQL Server (Windows & Linux)

**Scenario**: MSSQL using AD Service Accounts for the SQL Service itself.

- **Risk**: If Vault rotates the password of the account running the MSSQL Service, the service will **not** automatically know the new password and will fail to restart or stop functioning if it needs to re-authenticate.
- **Solution**: Do not rotate the *Service Logon* account via pure Vault AD Engine without an orchestrator (like Vault Agent with a template + a restart script).
- **Client Access**: For applications connecting *to* MSSQL using AD Auth (Integrated Security), they should ask Vault for `ad/creds/db-metrics-collector`.

### PostgreSQL & MongoDB (Linux/Windows)

These databases frequently use AD for user authentication via **Kerberos** or **LDAP**.

1. **Kerberos Keytabs (Linux)**:
    - If you rotate the password of an AD principal associated with a Keytab, **the Keytab becomes invalid**.
    - **Action**: You must regenerate the Keytab after rotation. Vault allows you to read the password, but automating Keytab updates usually requires a sidecar or a custom script involving `ktutil`.

2. **LDAP Auth**:
    - If the database is configured to bind to AD using a "Bind User" to search for logging-in users:
        - **Service Account**: The Bind User credentials in `pg_hba.conf` or `mongod.conf` must be updated if that specific account is rotated.
        - **Solution**: Use Vault Agent Templates to render the config file with the new password and signal the DB process to reload config (e.g., `SIGHUP`).

### Snowflake

Snowflake integration with AD usually relies on **External OAuth** or **SCIM** (via Azure AD / Okta) rather than direct LDAP binds with a static password.

- If using a service account for a connector/driver that uses strictly Username/Password AD authentication, the application utilizing the driver must fetch the new password from Vault before establishing a connection.

## Best Practices

1. **Use Vault Agent**: Deploy Vault Agent alongside your databases or applications. It handles the authentication to Vault, fetching of secrets, and rendering them to config files.
    - *Example*: Render `db_creds.json` and restart the application when the password rotates.
2. **Short TTLs**: For human users or highly automated scripts, use short TTLs (e.g., 1 hour) to minimize the attack surface.
3. **Grace Periods**: When possible, allow a grace period where the old password still works (AD supports this via History, but Vault limits it to strictly "current"). *Note: Active Directory does not support dual-valid passwords for the same user account simultaneously.*

## Troubleshooting

- **Access Denied**: Verify the `binddn` account has "Reset Password" rights on the target OU or User.
- **Account Locked**: If applications keep trying the old password, AD explicitly locks the account. Ensure all clients update to the new password immediately.
