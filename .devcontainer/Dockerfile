# syntax=docker/dockerfile:1.4

FROM mcr.microsoft.com/devcontainers/miniconda:latest

# Build args
ARG PYTHON_VERSION=3.14
ARG CONDA_ENV_NAME=gds
ARG DEVCONTAINER_USER=gds
ARG DEVCONTAINER_GROUP=gds
ARG DEVCONTAINER_UID=1000
ARG DEVCONTAINER_GID=1000

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive
ENV ACCEPT_EULA=Y
ENV DEVCONTAINER_USER=${DEVCONTAINER_USER} \
    DEVCONTAINER_GROUP=${DEVCONTAINER_GROUP} \
    DEVCONTAINER_UID=${DEVCONTAINER_UID} \
    DEVCONTAINER_GID=${DEVCONTAINER_GID} \
    DEVCONTAINER_HOME=/home/${DEVCONTAINER_USER}

# Install system dependencies for pyodbc, PowerShell, Docker CLI, and netcat
# RUN apt-get install -y  && \
#     wget -q https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb && \
#     dpkg -i packages-microsoft-prod.deb && \
#     rm packages-microsoft-prod.deb && \
#     # Create directory for keyrings
#     sudo mkdir -p /etc/apt/keyrings && \
#     # Add Docker’s official GPG key
#     curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
#     # Add Docker repository to APT sources
#     echo \
#     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable"  \
#     | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null && \
#     apt-get update && \
#     sudo apt-get remove -y docker docker-engine docker.io containerd runc moby-engine moby-cli moby-containerd && \
#     apt-get install -y powershell msodbcsql18 mssql-tools18 wget gnupg ca-certificates unixodbc-dev curl iputils-ping docker.io \
#     netcat-openbsd build-essential docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin runc && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get update && \
    apt-get install -y wget gnupg ca-certificates curl lsb-release && \
    # Install Microsoft repository for powershell, msodbcsql18, mssql-tools18
    wget -q https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    # Set up Docker’s official repository
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    # Setup HashiCorp repository for vault
    curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
    sudo tee /etc/apt/sources.list.d/hashicorp.list && \
    # Update package index
    apt-get update && \
    # Remove conflicting packages
    apt-get remove -y docker docker-engine docker.io containerd runc moby-engine moby-cli moby-containerd && \
    apt-get autoremove -y && \
    # Fix held packages
    apt-get install -f -y && \
    # Install required packages
    apt-get install -y \
    powershell \
    msodbcsql18 \
    mssql-tools18 \
    unixodbc-dev \
    iputils-ping \
    netcat-openbsd \
    build-essential \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin \
    vault && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create the conda environment and install base packages
# Configure conda-forge as the sole channel to avoid Anaconda TOS prompts and ensure reproducible resolution.
RUN conda config --system --remove-key channels || true && \
    conda config --system --add channels conda-forge && \
    conda config --system --set channel_priority strict && \
    conda update -n base conda -y && \
    conda create -n ${CONDA_ENV_NAME} python=${PYTHON_VERSION} -y && \
    conda clean -afy

# Install required PowerShell modules
RUN pwsh -NoLogo -NoProfile -Command "\
    Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; \
    Install-Module -Name dbatools,Pester,PSFramework -Scope AllUsers -Force -SkipPublisherCheck"

RUN bash <<'BASH'
set -euo pipefail

if getent passwd vscode >/dev/null 2>&1; then
    if getent group vscode >/dev/null 2>&1; then
        groupmod -n "${DEVCONTAINER_GROUP}" vscode
    fi
    usermod -l "${DEVCONTAINER_USER}" -d "${DEVCONTAINER_HOME}" -m -g "${DEVCONTAINER_GROUP}" -u "${DEVCONTAINER_UID}" vscode
elif ! getent passwd "${DEVCONTAINER_USER}" >/dev/null 2>&1; then
    if ! getent group "${DEVCONTAINER_GROUP}" >/dev/null 2>&1; then
        groupadd -g "${DEVCONTAINER_GID}" "${DEVCONTAINER_GROUP}"
    fi
    useradd -m -u "${DEVCONTAINER_UID}" -g "${DEVCONTAINER_GROUP}" "${DEVCONTAINER_USER}"
fi

if [ -d /etc/sudoers.d ]; then
    for file in /etc/sudoers.d/*; do
        [ -f "$file" ] || continue
        sed -i "s/vscode/${DEVCONTAINER_USER}/g" "$file" || true
    done
fi

mkdir -p "${DEVCONTAINER_HOME}"
chown -R "${DEVCONTAINER_USER}:${DEVCONTAINER_GROUP}" "${DEVCONTAINER_HOME}"
mkdir -p /data /logs
chown -R "${DEVCONTAINER_USER}:${DEVCONTAINER_GROUP}" /data /logs

# Add user to docker group for docker socket access
usermod -aG docker "${DEVCONTAINER_USER}" || true
BASH

# Make sure the conda environment is available in interactive shells
SHELL ["/bin/bash", "-lc"]
# Source conda.sh before activation so 'conda activate' works in terminals
RUN for f in /etc/skel/.bashrc ${DEVCONTAINER_HOME}/.bashrc ${DEVCONTAINER_HOME}/.profile; do \
    echo 'if [ -f /opt/conda/etc/profile.d/conda.sh ]; then . /opt/conda/etc/profile.d/conda.sh; fi' >> "$f"; \
    echo "conda activate ${CONDA_ENV_NAME}" >> "$f"; \
    done

# Set a colorful, multi-line prompt for interactive shells in the dev container
RUN <<'BASH'
set -euo pipefail
for f in /etc/skel/.bashrc ${DEVCONTAINER_HOME}/.bashrc ${DEVCONTAINER_HOME}/.profile; do
    cat >> "$f" <<'EOF'
# dbtools devcontainer prompt
if [[ $- == *i* ]]; then
export PS1="\[$(tput setaf 208)\]\d  \[$(tput setaf 226)\]\u\[$(tput setaf 220)\]@\[$(tput setaf 214)\]\h \[$(tput setaf 33)\]\w
\[$(tput sgr0)\]$ "
fi
EOF
done
BASH

RUN <<'BASH'
set -euo pipefail

profile_dir="${DEVCONTAINER_HOME}/.config/powershell"
profile_file="${profile_dir}/profile.ps1"

mkdir -p "$profile_dir"

cat <<'PROFILE' > "$profile_file"
$customModulePath = '/workspaces/dbtools/PowerShell/Modules'
$separator = [System.IO.Path]::PathSeparator

if (Test-Path -LiteralPath $customModulePath) {
    $currentPaths = @()
    if (-not [string]::IsNullOrWhiteSpace($env:PSModulePath)) {
        $currentPaths = $env:PSModulePath -split [regex]::Escape($separator)
    }

    if ($currentPaths -notcontains $customModulePath) {
        if ([string]::IsNullOrWhiteSpace($env:PSModulePath)) {
            $env:PSModulePath = $customModulePath
        }
        else {
            $env:PSModulePath = "$customModulePath$separator$env:PSModulePath"
        }
    }
}
PROFILE

chown -R ${DEVCONTAINER_USER}:${DEVCONTAINER_GROUP} "$profile_dir"
BASH

# Install some common build tooling in the env
RUN conda run -n ${CONDA_ENV_NAME} python -m pip install --upgrade pip && \
    conda run -n ${CONDA_ENV_NAME} pip install ruff pytest pytest-cov wheel \
    build pyodbc aiohttp pre-commit

# Set path
ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:/opt/mssql-tools18/bin:/opt/mssql-tools/bin:$PATH

USER ${DEVCONTAINER_USER}
WORKDIR /workspaces/dbtools

# Pre-create VS Code server directories with correct ownership to avoid permission issues
USER root
RUN mkdir -p ${DEVCONTAINER_HOME}/.vscode-server/extensions ${DEVCONTAINER_HOME}/.vscode-server/extensionsCache \
    && chown -R ${DEVCONTAINER_USER}:${DEVCONTAINER_GROUP} ${DEVCONTAINER_HOME}/.vscode-server
USER ${DEVCONTAINER_USER}

# Keep container running - VS Code will attach to this
CMD ["sleep", "infinity"]
