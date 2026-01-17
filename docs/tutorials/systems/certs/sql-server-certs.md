# TLS Certificates for SQL Server & Availability Groups

This tutorial covers how to configure TLS encryption for SQL Server instances and Always On Availability Groups (AG).

## SQL Server TLS Setup

Securing connections to SQL Server involves provisioning a certificate and configuring the server to use it.

### Prerequisites

* A certificate installed in the **Local Computer** certificate store on the Windows server.
* The certificate must be meant for **Server Authentication**.
* The **CN (Common Name)** of the certificate must match the FQDN of the server.

### Steps

1. **Install the Certificate**: Import your PFX file (containing the certificate and private key) into the Windows Certificate Store (Local Computer > Personal).
2. **Grant Permissions**:
    * Open the "Manage Private Keys" option for the installed certificate.
    * Grant **Read** permission to the SQL Server service account (e.g., `NT SERVICE\MSSQLSERVER`).
3. **Configure SQL Server**:
    * Open **SQL Server Configuration Manager**.
    * Expand **SQL Server Network Configuration**.
    * Right-click **Protocols for [Instance Name]** and select **Properties**.
    * On the **Certificate** tab, select your certificate from the dropdown.
    * On the **Flags** tab, set **Force Encryption** to `Yes` if you want to mandate encryption for all connections.
4. **Restart SQL Server**: Restart the SQL Server service for changes to take effect.

## Availability Groups TLS Setup

For Always On Availability Groups, certificates are used to secure the database mirroring endpoints. This is crucial for secure data synchronization between replicas.

### 1. Create Master Key and Certificate

On the **Primary Replica**, execute the following T-SQL to create a master key and a certificate.

```sql
USE master;
GO
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'StrongPassword123!';
GO
CREATE CERTIFICATE db_mirroring_cert
WITH SUBJECT = 'DB Mirroring Certificate',
EXPIRY_DATE = '2030-12-31';
GO
```

### 2. Create the Endpoint

Create the mirroring endpoint using the certificate for authentication.

```sql
CREATE ENDPOINT [Hadr_endpoint]
    STATE = STARTED
    AS TCP (LISTENER_PORT = 5022)
    FOR DATABASE_MIRRORING (
        AUTHENTICATION = CERTIFICATE db_mirroring_cert,
        ENCRYPTION = REQUIRED ALGORITHM AES,
        ROLE = ALL
    );
GO
```

### 3. Backup Certificate and Private Key

Backup the certificate to a file so it can be restored on other replicas.

```sql
BACKUP CERTIFICATE db_mirroring_cert
TO FILE = 'C:\Certs\db_mirroring_cert.cer'
WITH PRIVATE KEY (
    FILE = 'C:\Certs\db_mirroring_cert.pvk',
    ENCRYPTION BY PASSWORD = 'StrongPassword123!'
);
GO
```

### 4. Configure Secondary Replicas

Copy the `.cer` and `.pvk` files to all secondary replicas. On **each secondary replica**, run:

```sql
USE master;
GO
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'StrongPassword123!';
GO
CREATE CERTIFICATE db_mirroring_cert
FROM FILE = 'C:\Certs\db_mirroring_cert.cer'
WITH PRIVATE KEY (
    FILE = 'C:\Certs\db_mirroring_cert.pvk',
    DECRYPTION BY PASSWORD = 'StrongPassword123!'
);
GO

-- Create the endpoint (same as step 2)
CREATE ENDPOINT [Hadr_endpoint]
    STATE = STARTED
    AS TCP (LISTENER_PORT = 5022)
    FOR DATABASE_MIRRORING (
        AUTHENTICATION = CERTIFICATE db_mirroring_cert,
        ENCRYPTION = REQUIRED ALGORITHM AES,
        ROLE = ALL
    );
GO
```

### 5. Grant Permissions

Ensure the SQL Server service account has permission to connect to the endpoint.

```sql
GRANT CONNECT ON ENDPOINT::[Hadr_endpoint] TO [DOMAIN\ServiceAccount];
GO
```
