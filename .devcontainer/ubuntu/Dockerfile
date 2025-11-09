# syntax=docker/dockerfile:1.4

FROM mcr.microsoft.com/devcontainers/miniconda:latest

# Build args
ARG PYTHON_VERSION=3.13
ARG CONDA_ENV_NAME=gds
ARG DEVCONTAINER_USER=gds
ARG DEVCONTAINER_GROUP=gds
ARG DEVCONTAINER_UID=1000
ARG DEVCONTAINER_GID=1000

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive
ENV DEVCONTAINER_USER=${DEVCONTAINER_USER} \
    DEVCONTAINER_GROUP=${DEVCONTAINER_GROUP} \
    DEVCONTAINER_UID=${DEVCONTAINER_UID} \
    DEVCONTAINER_GID=${DEVCONTAINER_GID} \
    DEVCONTAINER_HOME=/home/${DEVCONTAINER_USER}

# Install system dependencies for pyodbc and PowerShell
RUN apt-get update && \
    apt-get install -y wget gnupg ca-certificates unixodbc-dev && \
    wget -q https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y powershell && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create the conda environment and install base packages
# Configure conda-forge as the sole channel to avoid Anaconda TOS prompts and ensure reproducible resolution.
RUN conda config --system --remove-key channels || true && \
    conda config --system --add channels conda-forge && \
    conda config --system --set channel_priority strict && \
    conda update -n base conda -y && \
    conda create -n ${CONDA_ENV_NAME} python=${PYTHON_VERSION} -y && \
    conda clean -afy

# Install required PowerShell modules
RUN pwsh -NoLogo -NoProfile -Command "Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force; Install-Module -Name dbatools,Pester,PSFramework -Scope AllUsers -Force"

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
mkdir -p /gds/data /gds/log
chown -R "${DEVCONTAINER_USER}:${DEVCONTAINER_GROUP}" /gds
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

# Install some common build tooling in the env
RUN conda run -n ${CONDA_ENV_NAME} python -m pip install --upgrade pip && \
    conda run -n ${CONDA_ENV_NAME} pip install ruff pytest pytest-cov wheel build pyodbc aiohttp

# Set path
ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:$PATH

USER ${DEVCONTAINER_USER}
WORKDIR /workspaces/dbtools

# Pre-create VS Code server directories with correct ownership to avoid permission issues
USER root
RUN mkdir -p ${DEVCONTAINER_HOME}/.vscode-server/extensions ${DEVCONTAINER_HOME}/.vscode-server/extensionsCache \
    && chown -R ${DEVCONTAINER_USER}:${DEVCONTAINER_GROUP} ${DEVCONTAINER_HOME}/.vscode-server
USER ${DEVCONTAINER_USER}
