# How-to: Rotate Active Directory Passwords with HashiCorp Vault

This guide details how to configure HashiCorp Vault to manage and rotate Active Directory (AD) passwords. This functionality is critical for securing service accounts used by database platforms such as Microsoft SQL Server, PostgreSQL, MongoDB, and Snowflake across both Windows and Linux environments.

## Introduction

Rotating passwords for privileged Active Directory accounts is a fundamental security practice. Manual rotation is error-prone and can cause outages. HashiCorp Vault's **Active Directory Secrets Engine** automates this process by:

1. Managing the AD account's password directly.
2. Automatically rotating the password based on a Time-To-Live (TTL) using **lazy rotation** (rotation occurs on the next credential request *after* TTL expires).
3. Generating dynamic, strictly scoped credentials for applications.

## Prerequisites

- **HashiCorp Vault** installed and unsealed.
- **Active Directory** domain controller accessible from Vault.
- **TLS Certificate**: A valid certificate for LDAPS communication (required by Microsoft for password changes).
- **Service Account for Vault**: An AD account with permissions to manage passwords on the target User/Service accounts.
  - Required permissions on target OU/objects:
    - `Reset Password`
    - `Change Password`
    - `Read userAccountControl`
    - `Write userAccountControl`
    - `Read/Write Properties` on target objects

## Step 1: Enable and Configure the AD Secrets Engine

First, enable the engine and configure it to communicate with your Domain Controller over TLS.

```bash
# 1. Enable the AD secrets engine
vault secrets enable ad

# 2. Configure the connection
# binddn: The account Vault uses to perform operations
# url: Your Domain Controller URL (LDAPS required for password operations)
# userdn: Base DN where managed service accounts reside
vault write ad/config \
    binddn="CN=Vault Service,CN=Users,DC=example,DC=com" \
    bindpass='<bind_password>' \
    url=ldaps://dc01.example.com \
    userdn="OU=ServiceAccounts,DC=example,DC=com" \
    certificate=@/path/to/ca-cert.pem \
    insecure_tls=false
```

> [!WARNING]
> **TLS is mandatory**. Microsoft requires LDAP password changes over TLS. Always use `ldaps://` and provide a valid CA certificate. Never set `insecure_tls=true` in production.

> [!TIP]
> Store the `bindpass` securely or input it interactively using `vault write ad/config -` to read from stdin.

### Password Policy Alignment

Ensure your AD password policy aligns with Vault's generated passwords. HashiCorp recommends:

- **Length**: 14-64 characters
- **Complexity**: At least one lowercase, one uppercase, one number, and one special character
- **History**: New password cannot be one of the last 24 used

## Step 2: Configure a Role

A "Role" in Vault maps a name to a specific AD Service Account that Vault will manage.

```bash
# Configure a role for a database service account
# service_account_name: The actual sAMAccountName in AD
vault write ad/roles/db-metrics-collector \
    service_account_name="svc_metrics_collector" \
    ttl=24h
```

Depending on whether you want **Shared** (static account, rotated periodically) or **Dynamic** (Vault creates/deletes users) accounts, the configuration differs. The example above is for a **Shared** account (the account exists in AD, Vault rotates its password).

### For Shared Accounts (Password Rotation)

Vault will rotate the password of `svc_metrics_collector` when credentials are requested *after* the TTL has expired (**lazy rotation**). Applications retrieve the current password via the credentials endpoint.

## Step 3: Retrieve and Rotate Credentials

### Retrieve Current Credentials

```bash
# Get the current password for the managed account
vault read ad/creds/db-metrics-collector
```

### Force Immediate Rotation

```bash
# Manually rotate the password for the role
vault write -f ad/rotate-role/db-metrics-collector
```

> [!NOTE]
> **Lazy Rotation**: Passwords are not rotated automatically at TTL expiration. Instead, rotation occurs on the next credential request *after* the TTL has passed. Use `rotate-role` for immediate rotation.

## Step 4: Configure Vault Policies (ACLs)

Implement granular access control to restrict who can read credentials.

```hcl
# policy: db-metrics-reader.hcl
# Allow reading credentials for the db-metrics-collector role
path "ad/creds/db-metrics-collector" {
  capabilities = ["read"]
}

# Deny rotation capabilities to non-admin users
path "ad/rotate-role/*" {
  capabilities = ["deny"]
}
```

Apply the policy:

```bash
vault policy write db-metrics-reader db-metrics-reader.hcl
```

## Considerations for Database Platforms

When Vault rotates the AD password, any service or application using the old password will fail authentication immediately. You must ensure your consumers are "Vault-aware" or use a mechanism to retrieve the new password.

### Microsoft SQL Server (Windows & Linux)

**Scenario**: MSSQL using AD Service Accounts for the SQL Service itself.

- **Risk**: If Vault rotates the password of the account running the MSSQL Service, the service will **not** automatically know the new password and will fail to restart or stop functioning if it needs to re-authenticate.
- **Solution**: Do not rotate the *Service Logon* account via Vault AD Engine without an orchestrator (like Vault Agent with a template + a restart script).
- **Client Access**: For applications connecting *to* MSSQL using AD Auth (Integrated Security), they should retrieve credentials from `ad/creds/db-metrics-collector`.

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

1. **Use Vault Agent**: Deploy Vault Agent alongside your databases or applications. It handles authentication to Vault, fetching of secrets, and rendering them to config files.
    - *Example*: Render `db_creds.json` and restart the application when the password rotates.

2. **Short TTLs**: For human users or highly automated scripts, use short TTLs (e.g., 1 hour) to minimize the attack surface.

3. **Enable Audit Logging**: Configure Vault audit devices to log all credential access and rotation events for compliance and security monitoring.
    ```bash
    vault audit enable file file_path=/var/log/vault/audit.log
    ```

4. **Use LDAPS Only**: Never use unencrypted LDAP (`ldap://`) for password operations. Microsoft explicitly requires TLS.

5. **Dedicated Service Account**: Use a dedicated AD account for Vault with minimal permissions scoped only to the OUs containing managed accounts.

6. **Monitor Account Lockouts**: Set up alerting for AD account lockouts, which may indicate applications using stale credentials.

## Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| **Access Denied** | Insufficient permissions | Verify `binddn` account has `Reset Password`, `Change Password`, and `Read/Write userAccountControl` rights on the target OU |
| **Account Locked** | Applications using old password | Ensure all clients update to new password immediately; consider shorter TTLs with coordinated rotation |
| **Certificate Error** | Invalid or missing TLS cert | Provide valid CA certificate via `certificate` parameter; verify cert chain |
| **Password Policy Violation** | AD policy stricter than Vault default | Align AD policy with Vault password generation settings |

## See Also

- [HashiCorp Vault AD Secrets Engine Documentation](https://developer.hashicorp.com/vault/docs/secrets/ad)
- [Vault Agent Auto-Auth and Templates](https://developer.hashicorp.com/vault/docs/agent)
