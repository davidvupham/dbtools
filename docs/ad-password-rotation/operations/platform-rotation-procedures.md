# Platform-Specific Rotation Procedures

This document details the exact steps for rotating Active Directory passwords for each supported database platform.

## 1. Microsoft SQL Server (Windows/Linux)

**Scenario**: The AD account is the *Service Account* running the MSSQL Instance.

### Procedure (Windows)

*Automation Tool: Vault Agent + PowerShell*

1. **Trigger**: Vault Agent detects the leased password is near expiry (e.g., reached 85% of TTL) or the Template is updated.
2. **Retrieve**: Vault Agent fetches the specific credentials from `ad/creds/mssql-svc`.
3. **Action**: Vault Agent executes `command` defined in the template: `powershell -File C:\Ops\Rotate-Mssql.ps1`.
4. **Script Logic (`Rotate-Mssql.ps1`)**:
    - **Step 4a**: Validate the new password works (LDAP bind check).
    - **Step 4b**: Update Service Config:

      ```powershell
      # SecureString conversion
      $secPass = ConvertTo-SecureString $NewPassword -AsPlainText -Force
      # Set Service credentials
      Set-Service -Name "MSSQLSERVER" -Credential (New-Object pscredential($Upn, $secPass))
      ```

    - **Step 4c**: **Restart Service**.

      ```powershell
      Restart-Service "MSSQLSERVER" -Force
      ```

    - **Step 4d (Clustered)**: If AlwaysOn, failover availability groups *before* restarting if using an external orchestrator.

### Procedure (Linux)

*Automation Tool: Vault Agent + mssql-conf*

1. **Action**: Vault Agent renders a temporary environment file or explicitly runs the setup tool.
2. **Command**:

    ```bash
    # Setting the environment variable for setup
    export MSSQL_SA_PASSWORD=$NEW_PASSWORD
    # OR using mssql-conf for AD setup (requires re-running ad-auth setup steps mostly for initial join, but for service execution it relies on systemd service)
    # Typically on Linux, MSSQL runs as 'mssql' user, but uses keytab for AD auth.
    ```

    *Correction*: On Linux, MSSQL usually uses a **Keytab** for AD Authentication (Integrated Security). It does not "Run As" the AD User in the OS sense. See **PostgreSQL** section for Keytab rotation.

## 2. PostgreSQL (Windows/Linux)

**Scenario**: PostgreSQL runs as a local service but uses AD for **Client Authentication** (Kerberos/GSSAPI or LDAP).

### Mechanism A: Kerberos Keytab (Standard for Linux)

*The DB Service Account has a Keytab file `/etc/postgres/postgres.keytab`.*

1. **Trigger**: Vault rotates the password for the AD User `postgres_svc`.
2. **Problem**: The existing Keytab is now invalid.
3. **Action**: Vault Agent (running as root/postgres) executes `Rotate-Keytab.sh`.
4. **Script Logic**:

    ```bash
    # 1. Authentic to Vault is already done by Agent.
    # 2. Keytab Generation (Requires 'ktutil' or 'adcli' or 'msktutil')

    # Example using ktutil
    printf "%b" "addent -password -p postgres_svc@EXAMPLE.COM -k 1 -e aes256-cts-hmac-sha1-96\n$NEW_PASSWORD\nwrite_kt /etc/postgres/postgres.keytab.new\nquit" | ktutil

    # 3. Atomic Swap
    mv /etc/postgres/postgres.keytab.new /etc/postgres/postgres.keytab
    chown postgres:postgres /etc/postgres/postgres.keytab
    chmod 600 /etc/postgres/postgres.keytab
    ```

5. **Restart?**: Usually **not required** for Keytab updates if the application re-reads the file (most do). If cached, a `SIGHUP` or Restart is needed.

### Mechanism B: LDAP Simple Bind

*Postgres is configured to "Bind" to AD to verify other users credentials.*

1. **Update**: Vault Agent renders `ldap_passfile` or updates `pg_ident.conf`/`pg_hba.conf` if passwords are embedded (discouraged).
2. **Action**: `systemctl reload postgresql`.

## 3. MongoDB

**Scenario**: MongoDB Enterprise uses Kerberos or LDAP.

### Kerberos (Linux)

- **Procedure**: Identical to PostgreSQL (Keytab Rotation).
- **Target File**: `/etc/mongodb/mongodb.keytab`.
- **Command**: Rotate Keytab, then nothing (Mongo reads keytab on connection attempt) or Restart if strict caching is enabled.

### LDAP Auth

- **Procedure**:
    1. Vault Agent renders the `mongod.conf` with new `security.ldap.bind.servicePassword`.
    2. **Restart**: MongoDB generally requires a **Process Restart** to load new config changes to `mongod.conf`.
    3. **Orchestration**: If usage Replica Sets, rotate **Secondaries** first, then stepdown Primary and rotate Primary. **Temporal** is highly recommended here to automate the rolling restart.

## 4. Snowflake

**Scenario**: External Application needs to connect to Snowflake. Service Account is in AD. Snowflake is configured with "External OAuth" or "LDAP/AD Federation".

- **Federated (Okta/AzureAD)**: Vault rotates AD password. Okta/AzureAD syncs. Sso works.
- **Direct AD Info**: Snowflake doesn't "Join" AD.
- **Client Side**:
  - The *Application* connecting to Snowflake needs the new password.
  - **Vault Agent (On App Server)**: Renders `snowflake_connection.json` or Environment Variable.
  - **App Reload**: Application restarts or re-initializes connection pool with new credentials.
