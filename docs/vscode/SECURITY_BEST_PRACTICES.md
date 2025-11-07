# Security Best Practices for Dev Containers

This guide covers security considerations and best practices when using dev containers with the dbtools project.

## Table of Contents

- [Secrets Management](#secrets-management)
- [Container Security](#container-security)
- [Database Credentials](#database-credentials)
- [SSH Keys and Git Authentication](#ssh-keys-and-git-authentication)
- [Network Security](#network-security)
- [Vault Integration](#vault-integration)
- [Common Security Pitfalls](#common-security-pitfalls)

## Secrets Management

### Never Commit Secrets

❌ **Bad Practice:**

```python
# config.py
DB_PASSWORD = "MySecretPassword123"
VAULT_TOKEN = "s.abc123xyz789"
API_KEY = "sk-proj-1234567890"
```

✅ **Good Practice:**

```python
# config.py
import os

DB_PASSWORD = os.getenv("DB_PASSWORD")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
API_KEY = os.getenv("API_KEY")

if not all([DB_PASSWORD, VAULT_TOKEN, API_KEY]):
    raise ValueError("Required environment variables are not set")
```

### Use Environment Variables

#### Local Development with .env Files

Create `.env` (add to `.gitignore`):

```bash
# Database Credentials
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=SecurePassword123!

# Snowflake
SNOWFLAKE_ACCOUNT=myaccount
SNOWFLAKE_USER=myuser
SNOWFLAKE_PASSWORD=SecurePassword456!
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=MYDB
SNOWFLAKE_SCHEMA=PUBLIC

# Vault
VAULT_ADDR=https://vault.example.com
VAULT_TOKEN=s.abc123xyz789
VAULT_NAMESPACE=my-namespace

# MongoDB
MONGODB_CONNECTION_STRING=mongodb://user:pass@localhost:27017/mydb

# API Keys
API_KEY=your-api-key-here
```

#### Load Environment Variables in Python

```python
# Using python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()

# Access secrets
db_password = os.getenv("POSTGRES_PASSWORD")
```

#### Load in Dev Container

Add to `devcontainer.json`:

```json
{
  "containerEnv": {
    "ENVIRONMENT": "development"
  },
  "runArgs": [
    "--env-file", "${localWorkspaceFolder}/.env"
  ]
}
```

### Use Secret Scanning

#### GitHub Secret Scanning

Enable in repository settings:
- Settings → Security → Code security and analysis
- Enable "Secret scanning"
- Enable "Push protection"

#### Pre-commit Hook for Secrets

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

Initialize:

```bash
detect-secrets scan > .secrets.baseline
```

### Use Azure Key Vault / AWS Secrets Manager

#### Azure Key Vault Example

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net/", credential=credential)

db_password = client.get_secret("db-password").value
```

#### AWS Secrets Manager Example

```python
import boto3
import json

client = boto3.client('secretsmanager', region_name='us-east-1')
response = client.get_secret_value(SecretId='myapp/database/password')
secret = json.loads(response['SecretString'])

db_password = secret['password']
```

## Container Security

### Run as Non-Root User

✅ **Already configured in our devcontainer:**

```dockerfile
USER vscode
```

❌ **Avoid:**

```dockerfile
USER root
# Running as root increases security risks
```

### Limit Container Capabilities

Add to `devcontainer.json`:

```json
{
  "capAdd": [],  // Don't add unnecessary capabilities
  "securityOpt": [
    "no-new-privileges:true"
  ]
}
```

### Read-Only Mounts

Mount sensitive directories as read-only:

```json
{
  "mounts": [
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached,readonly",
    "source=${localEnv:HOME}/.aws,target=/home/vscode/.aws,type=bind,consistency=cached,readonly"
  ]
}
```

### Use Official Base Images

✅ **Good:**

```dockerfile
FROM mcr.microsoft.com/devcontainers/miniconda:latest
```

❌ **Bad:**

```dockerfile
FROM random-user/custom-image:latest
```

### Scan Images for Vulnerabilities

```bash
# Using Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image devcontainer:latest

# Using Snyk
snyk container test devcontainer:latest
```

### Keep Base Images Updated

```bash
# Rebuild with latest base image regularly
docker pull mcr.microsoft.com/devcontainers/miniconda:latest
docker build --no-cache -f .devcontainer/Dockerfile -t devcontainer:latest .
```

## Database Credentials

### Use Connection Strings from Environment

```python
import os
from urllib.parse import quote_plus

# PostgreSQL
pg_connection_string = f"postgresql://{os.getenv('POSTGRES_USER')}:{quote_plus(os.getenv('POSTGRES_PASSWORD'))}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

# MongoDB
mongo_connection_string = os.getenv('MONGODB_CONNECTION_STRING')

# SQL Server
mssql_connection_string = f"mssql+pyodbc://{os.getenv('MSSQL_USER')}:{quote_plus(os.getenv('MSSQL_PASSWORD'))}@{os.getenv('MSSQL_HOST')}:{os.getenv('MSSQL_PORT')}/{os.getenv('MSSQL_DB')}?driver=ODBC+Driver+18+for+SQL+Server"
```

### Rotate Credentials Regularly

```python
# Example: Check credential age
from datetime import datetime, timedelta

CREDENTIAL_MAX_AGE_DAYS = 90

def check_credential_age(credential_created_date):
    age = datetime.now() - credential_created_date
    if age > timedelta(days=CREDENTIAL_MAX_AGE_DAYS):
        raise ValueError(f"Credential is {age.days} days old. Please rotate.")
```

### Use Least Privilege Access

```sql
-- PostgreSQL: Grant only necessary permissions
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
-- Don't grant DELETE or DROP unless necessary

-- SQL Server: Create limited role
CREATE USER app_user WITH PASSWORD = 'Secure_Password123!';
ALTER ROLE db_datareader ADD MEMBER app_user;
ALTER ROLE db_datawriter ADD MEMBER app_user;
-- Don't add to db_owner or sysadmin
```

### Use Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Connection pooling helps prevent credential exposure
engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False           # Don't log SQL queries (may contain sensitive data)
)
```

## SSH Keys and Git Authentication

### Protect SSH Keys

```bash
# Correct permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 644 ~/.ssh/known_hosts
chmod 600 ~/.ssh/config
```

### Use SSH Agent Forwarding (Carefully)

In `devcontainer.json`:

```json
{
  "mounts": [
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached,readonly"
  ],
  "postStartCommand": "eval $(ssh-agent -s) && ssh-add ~/.ssh/id_rsa || true"
}
```

⚠️ **Warning:** Only use SSH agent forwarding on trusted containers.

### Use HTTPS with Credential Helper

```bash
# Configure Git credential helper
git config --global credential.helper store

# Or use GitHub CLI
gh auth login
```

### Use Deploy Keys for CI/CD

Don't use personal SSH keys in CI/CD. Use deploy keys:

```yaml
# GitHub Actions
- uses: webfactory/ssh-agent@v0.8.0
  with:
    ssh-private-key: ${{ secrets.DEPLOY_KEY }}
```

## Network Security

### Limit Network Exposure

```json
{
  "forwardPorts": [5432, 1433, 27017],
  "portsAttributes": {
    "5432": {
      "label": "PostgreSQL",
      "onAutoForward": "notify",
      "protocol": "tcp",
      "requireLocalPort": true
    }
  }
}
```

### Use TLS/SSL for Database Connections

```python
# PostgreSQL with SSL
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="myuser",
    password=os.getenv("DB_PASSWORD"),
    sslmode="require",  # Require SSL
    sslrootcert="/path/to/ca-cert.pem"
)

# SQL Server with TLS
import pyodbc

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server={os.getenv('MSSQL_HOST')};"
    f"Database={os.getenv('MSSQL_DB')};"
    f"Uid={os.getenv('MSSQL_USER')};"
    f"Pwd={os.getenv('MSSQL_PASSWORD')};"
    "Encrypt=yes;"  # Enforce encryption
    "TrustServerCertificate=no;"  # Don't trust self-signed certs
)
```

### Firewall Rules

```bash
# Example: Only allow specific IPs to connect to database
# (Configure on your database server, not in container)

# PostgreSQL pg_hba.conf
hostssl all all 192.168.1.0/24 md5

# SQL Server firewall rule
sp_set_database_firewall_rule 'MyRule', '192.168.1.1', '192.168.1.255'
```

### Use VPN for Remote Databases

```bash
# Example: Connect to VPN before accessing databases
sudo openvpn --config /path/to/vpn-config.ovpn
```

## Vault Integration

### Use HashiCorp Vault for Secrets

#### Setup Vault Client

```python
from gds_vault import VaultClient
import os

# Use Vault token from environment
vault = VaultClient(
    url=os.getenv("VAULT_ADDR"),
    token=os.getenv("VAULT_TOKEN"),
    namespace=os.getenv("VAULT_NAMESPACE")
)

# Retrieve secrets
db_creds = vault.get_secret("database/postgres/prod")
db_password = db_creds["password"]
```

#### Use AppRole Authentication

```python
from gds_vault import VaultClient

# More secure than tokens
vault = VaultClient(
    url=os.getenv("VAULT_ADDR"),
    role_id=os.getenv("VAULT_ROLE_ID"),
    secret_id=os.getenv("VAULT_SECRET_ID")
)

secrets = vault.get_secret("database/postgres/prod")
```

#### Vault Token Renewal

```python
import time
from datetime import datetime

def renew_vault_token(vault_client):
    """Automatically renew Vault token before expiration"""
    while True:
        try:
            lookup = vault_client.lookup_token()
            ttl = lookup['data']['ttl']

            # Renew when 50% of TTL has passed
            time.sleep(ttl / 2)
            vault_client.renew_token()
            print(f"Vault token renewed at {datetime.now()}")
        except Exception as e:
            print(f"Failed to renew token: {e}")
            break
```

### Vault Policies

Create least-privilege policies:

```hcl
# vault-policy.hcl
path "database/postgres/dev/*" {
  capabilities = ["read", "list"]
}

path "database/postgres/prod/*" {
  capabilities = ["read"]  # Read-only in production
}

path "secret/api-keys/*" {
  capabilities = ["read"]
}
```

Apply policy:

```bash
vault policy write app-policy vault-policy.hcl
```

## Common Security Pitfalls

### 1. Logging Sensitive Data

❌ **Bad:**

```python
import logging

password = os.getenv("DB_PASSWORD")
logging.info(f"Connecting with password: {password}")  # DON'T!
```

✅ **Good:**

```python
import logging

password = os.getenv("DB_PASSWORD")
logging.info("Connecting to database")  # No sensitive data
logging.debug("Connection string configured")  # Still no password
```

### 2. Hardcoded Credentials in Code

❌ **Bad:**

```python
connection_string = "postgresql://admin:password123@localhost:5432/mydb"
```

✅ **Good:**

```python
connection_string = os.getenv("DATABASE_URL")
```

### 3. Committing .env Files

Add to `.gitignore`:

```
# Environment files
.env
.env.local
.env.*.local

# Credentials
config.sh
*.key
*.pem
*.crt
secrets/
credentials.json
```

### 4. Overly Permissive File Permissions

```bash
# Check and fix permissions
find ~/.ssh -type f -exec chmod 600 {} \;
find ~/.ssh -type d -exec chmod 700 {} \;
chmod 644 ~/.ssh/*.pub
```

### 5. Using Default Passwords

❌ **Default passwords for databases:**
- postgres/postgres
- root/root
- sa/sa

✅ **Use strong, unique passwords:**

```bash
# Generate strong passwords
openssl rand -base64 32

# Or use a password manager
```

### 6. Exposing Ports Publicly

❌ **Bad:**

```json
{
  "forwardPorts": [5432],
  "portsAttributes": {
    "5432": {
      "visibility": "public"  // DON'T expose databases publicly!
    }
  }
}
```

✅ **Good:**

```json
{
  "forwardPorts": [5432],
  "portsAttributes": {
    "5432": {
      "visibility": "private"  // Keep it private
    }
  }
}
```

### 7. Not Validating Input

```python
# SQL Injection prevention
import psycopg2

# ❌ Bad: String interpolation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ Good: Parameterized queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### 8. Ignoring Certificate Validation

❌ **Bad:**

```python
import requests

response = requests.get("https://api.example.com", verify=False)  # DON'T!
```

✅ **Good:**

```python
import requests

response = requests.get("https://api.example.com", verify=True)  # Default
# Or specify CA bundle
response = requests.get("https://api.example.com", verify="/path/to/ca-bundle.crt")
```

## Security Checklist

Before committing code:

- [ ] No hardcoded passwords or API keys
- [ ] All secrets in environment variables or Vault
- [ ] `.env` files in `.gitignore`
- [ ] SSH keys have correct permissions (600)
- [ ] Database connections use TLS/SSL
- [ ] Parameterized queries used (no SQL injection)
- [ ] Sensitive data not logged
- [ ] Pre-commit hooks configured
- [ ] Secret scanning enabled
- [ ] Container runs as non-root user
- [ ] Least privilege database access
- [ ] Ports not publicly exposed
- [ ] Dependencies up to date (no known vulnerabilities)

Before deploying:

- [ ] Rotate credentials if exposed
- [ ] Use different credentials for dev/staging/prod
- [ ] Enable audit logging
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Document incident response procedures

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Vault Best Practices](https://www.vaultproject.io/docs/internals/security)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

## Incident Response

If credentials are compromised:

1. **Immediately rotate all affected credentials**
2. **Revoke compromised tokens/keys**
3. **Audit access logs** for unauthorized access
4. **Notify security team** if applicable
5. **Document the incident**
6. **Review and improve security practices**

```bash
# Example: Rotate Vault token
vault token revoke <compromised-token>
vault token create -policy=app-policy

# Example: Rotate database password
ALTER USER myuser WITH PASSWORD 'NewSecurePassword123!';
```

## Conclusion

Security is a continuous process, not a one-time task. Regularly review and update your security practices, keep dependencies updated, and stay informed about new vulnerabilities and best practices.

Remember: **Defense in depth** - multiple layers of security are better than relying on a single control.
