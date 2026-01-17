#!/usr/bin/env bash
set -euo pipefail
IMAGE_NAME=${IMAGE_NAME:-dbtools-dev}
IMAGE_TAG=${IMAGE_TAG:-latest}
WORKDIR=${WORKDIR:-/workspaces/dbtools}

cmd='python -V && terraform -version && tflint --version && tfsec --version && terragrunt --version && terraform-docs --version && infracost --version && aws --version && az version | head -n 5 && sqlcmd -? | head -n 1 && pwsh -NoLogo -NoProfile -Command "\$PSVersionTable.PSVersion.ToString(); Import-Module dbatools; Get-Module dbatools | Select-Object -ExpandProperty Version" && python -c "import pandas, pyarrow, boto3, psycopg2, pymongo, hvac, snowflake.connector, requests_kerberos, gssapi, ldap3; import jira; import pysnow; print(\"python libs OK\")"'

docker run --rm \
  -v "$(pwd)":"${WORKDIR}" \
  -w "${WORKDIR}" \
  "${IMAGE_NAME}:${IMAGE_TAG}" bash -lc "$cmd"
