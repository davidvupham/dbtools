# syntax=docker/dockerfile:1

# Miniconda3 base image
FROM continuumio/miniconda3:latest

# Ensure bash is used for conda commands
SHELL ["/bin/bash", "-lc"]

# Update conda and create the 'gds' environment with the latest available Python
RUN conda update -n base -c defaults -y conda \
    && conda create -n gds -y python=3.11 \
    && conda clean -afy

# Make 'gds' the default environment (works for non-interactive shells too)
ENV CONDA_DEFAULT_ENV=gds
ENV PATH=/opt/conda/envs/gds/bin:$PATH

# Initialize conda for bash and auto-activate 'gds' for interactive shells
RUN conda init bash && echo 'conda activate gds' >> /root/.bashrc

# Install Snowflake connector and common dependencies in the 'gds' environment
RUN conda install -n gds -y -c conda-forge \
        snowflake-connector-python \
        pandas \
    pyarrow \
    hvac \
    ansible \
    boto3 \
    pymongo \
    psycopg2 \
    checkov \
    ansible-lint \
    pygithub \
    ldap3 \
    requests-kerberos \
    python-gssapi \
    && conda clean -afy

# Install Microsoft ODBC Driver 18 for SQL Server, sqlcmd (mssql-tools18), and unixODBC dev tools
RUN set -euxo pipefail \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg ca-certificates apt-transport-https software-properties-common \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 mssql-tools18 unixodbc unixodbc-dev \
    && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> /etc/profile.d/mssql-tools.sh \
    && ln -s /opt/mssql-tools18/bin/sqlcmd /usr/local/bin/sqlcmd \
    && ln -s /opt/mssql-tools18/bin/bcp /usr/local/bin/bcp \
    && rm -rf /var/lib/apt/lists/*

# Install Kerberos client and development libraries (non-interactive)
RUN set -euxo pipefail \
    && DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
         krb5-user krb5-config libkrb5-3 libkrb5-dev libsasl2-modules-gssapi-mit \
    && rm -rf /var/lib/apt/lists/*

# Customize bash prompt for interactive shells (append multi-line PS1 safely)
RUN printf '%s\n' 'export PS1="\[$(tput setaf 208)\]\d  \[$(tput setaf 226)\]\u\[$(tput setaf 220)\]@\[$(tput setaf 214)\]\h \[$(tput setaf 33)\]\w ' "\[$(tput sgr0)\]\\$ " >> /root/.bashrc

# Install Terraform using HashiCorp APT repository
RUN set -euxo pipefail \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /etc/apt/keyrings/hashicorp-archive-keyring.gpg \
    && chmod a+r /etc/apt/keyrings/hashicorp-archive-keyring.gpg \
    && . /etc/os-release \
    && echo "deb [signed-by=/etc/apt/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com ${VERSION_CODENAME} main" > /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends terraform unzip wget \
    && rm -rf /var/lib/apt/lists/*

# Install additional IaC tools: tflint, tfsec, terragrunt
RUN set -euxo pipefail \
    && ARCH=$(dpkg --print-architecture) \
    && case "$ARCH" in \
         amd64) TARBALL_ARCH=amd64; ;; \
         arm64) TARBALL_ARCH=arm64; ;; \
         *) echo "Unsupported architecture: $ARCH" && exit 1 ;; \
       esac \
    # tflint
    && wget -q "https://github.com/terraform-linters/tflint/releases/latest/download/tflint_linux_${TARBALL_ARCH}.zip" -O /tmp/tflint.zip \
    && unzip -o /tmp/tflint.zip -d /usr/local/bin \
    && chmod +x /usr/local/bin/tflint \
    && rm -f /tmp/tflint.zip \
    # tfsec
    && wget -q "https://github.com/aquasecurity/tfsec/releases/latest/download/tfsec-linux-${TARBALL_ARCH}" -O /usr/local/bin/tfsec \
    && chmod +x /usr/local/bin/tfsec \
    # terragrunt
    && wget -q "https://github.com/gruntwork-io/terragrunt/releases/latest/download/terragrunt_linux_${TARBALL_ARCH}" -O /usr/local/bin/terragrunt \
    && chmod +x /usr/local/bin/terragrunt

# Install terraform-docs (official install script)
RUN curl -sSfL https://raw.githubusercontent.com/terraform-docs/terraform-docs/main/install.sh | sh -s -- -b /usr/local/bin

# Install Infracost CLI
RUN curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh \
    && mv ./bin/infracost /usr/local/bin/ \
    && rmdir ./bin || true

# Install Azure CLI
RUN set -euxo pipefail \
    && curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install PowerShell 7 (pwsh) and dbatools module
RUN set -euxo pipefail \
    && wget -q https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb \
    && dpkg -i /tmp/packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends powershell \
    && rm -rf /var/lib/apt/lists/* /tmp/packages-microsoft-prod.deb \
    && pwsh -NoLogo -NoProfile -Command "Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; Install-Module -Name dbatools -Force -Scope AllUsers -AllowClobber"

# Install pre-commit in the base env (available globally)
RUN pip install --no-cache-dir pre-commit

# Install AWS CLI v2
RUN set -euxo pipefail \
    && ARCH=$(uname -m) \
    && case "$ARCH" in \
         x86_64) AWS_ARCH=x86_64 ;; \
         aarch64) AWS_ARCH=aarch64 ;; \
         *) echo "Unsupported architecture: $ARCH" && exit 1 ;; \
       esac \
    && curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${AWS_ARCH}.zip" -o /tmp/awscliv2.zip \
    && unzip -q /tmp/awscliv2.zip -d /tmp \
    && /tmp/aws/install -i /usr/local/aws-cli -b /usr/local/bin \
    && rm -rf /tmp/aws /tmp/awscliv2.zip

# Install AWS typing stubs and additional clients via pip
# - pyartifactory (JFrog), jira (Atlassian Jira), pysnow (ServiceNow)
RUN pip install --no-cache-dir "boto3-stubs[essential]" pyartifactory jira pysnow confluent-kafka
