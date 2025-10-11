# SQL tools in the Dev Container

The dev container includes Microsoft SQL client and ODBC tooling:

- msodbcsql18 (Microsoft ODBC Driver 18 for SQL Server)
- mssql-tools18 (sqlcmd and bcp)
- unixODBC and unixODBC-dev

## Verify tools

```bash
sqlcmd -?
which sqlcmd
bcp -?
odbcinst -j
```

## Verify Snowflake connector

```bash
python -c "import snowflake.connector as s; print('snowflake:', s.__version__)"
python -c "import pandas as pd, pyarrow as pa; print('pandas:', pd.__version__, 'pyarrow:', pa.__version__)"
```

## Verify HashiCorp Vault client (hvac)

```bash
python -c "import hvac; print('hvac:', hvac.__version__)"
```

## Verify Terraform and Ansible

```bash
terraform -version
ansible --version
```

## Verify additional IaC tools

```bash
tflint --version
tfsec --version
terragrunt --version
terraform-docs --version
infracost --version
```

VS Code extensions installed for IaC:
- hashicorp.terraform
- redhat.ansible
 - amazonwebservices.aws-toolkit-vscode

## Verify AWS, MongoDB, and Postgres Python packages

```bash
python -c "import boto3; print('boto3:', boto3.__version__)"
python -c "import pymongo; print('pymongo:', pymongo.__version__)"
python -c "import psycopg2; print('psycopg2:', psycopg2.__version__)"
python -c "import confluent_kafka, github; from pyartifactory import Artifactory; print('confluent-kafka:', confluent_kafka.__version__); print('pygithub:', github.__version__)"
```

## Verify AWS CLI

```bash
aws --version
```

## Verify Azure CLI and pre-commit

```bash
az version
pre-commit --version
```

## Verify Kerberos

```bash
krb5-config --version || true
dpkg -l | grep -E 'krb5|libsasl2' | head -n 10
python -c "import requests_kerberos, gssapi; print('requests-kerberos OK; gssapi OK')"
```

Kerberos configuration:
- Provide a krb5.conf (e.g., mount to /etc/krb5.conf via devcontainer mounts if needed)
- Acquire a ticket with: `kinit user@REALM` and check with `klist`

## Example usage

```bash
# Connect with Azure AD interactive/managed identities is not available inside the container by default.
# Use SQL auth for quick tests (example only):
sqlcmd -S yourserver.database.windows.net -d master -U youruser -P 'yourpassword' -C -Q "SELECT @@VERSION;"
```

Notes:
- PATH includes /opt/mssql-tools18/bin via profile and symlinks in /usr/local/bin.
- For DSN configs, edit /etc/odbcinst.ini and /etc/odbc.ini or provide user-level files under ~/.odbc* as needed.
