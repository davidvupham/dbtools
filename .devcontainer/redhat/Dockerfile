# syntax=docker/dockerfile:1.4

FROM registry.access.redhat.com/ubi9/ubi:latest

ARG PYTHON_VERSION=3.13
ARG CONDA_ENV_NAME=gds
ARG DEVCONTAINER_USER=gds
ARG DEVCONTAINER_GROUP=gds
ARG DEVCONTAINER_UID=1000
ARG DEVCONTAINER_GID=1000
ENV CONDA_DIR=/opt/conda
ENV PATH=${CONDA_DIR}/bin:${PATH}
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV ACCEPT_EULA=Y \
    DEVCONTAINER_USER=${DEVCONTAINER_USER} \
    DEVCONTAINER_GROUP=${DEVCONTAINER_GROUP} \
    DEVCONTAINER_UID=${DEVCONTAINER_UID} \
    DEVCONTAINER_GID=${DEVCONTAINER_GID} \
    DEVCONTAINER_HOME=/home/${DEVCONTAINER_USER}

RUN dnf -y update && \
    dnf -y install \
    curl \
    tar \
    glibc-langpack-en \
    glibc-locale-source \
    gzip \
    unzip \
    gnupg2 \
    shadow-utils \
    findutils \
    git \
    wget \
    which \
    make \
    gcc \
    gcc-c++ \
    openssl \
    unixODBC-devel \
    ca-certificates \
    procps-ng \
    python3-pip \
    sudo \
    ncurses && \
    ln -s /usr/bin/python3 /usr/bin/python || true && \
    dnf clean all && \
    rm -rf /var/cache/dnf

RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/microsoft.gpg && \
    install -o root -g root -m 644 /tmp/microsoft.gpg /etc/pki/rpm-gpg/microsoft.gpg && \
    rm -f /tmp/microsoft.gpg && \
    curl -sSL -o /etc/yum.repos.d/microsoft.repo https://packages.microsoft.com/config/rhel/9/prod.repo && \
    dnf -y install powershell msodbcsql18 mssql-tools18 && \
    dnf clean all && \
    rm -rf /var/cache/dnf || true

RUN curl -fsSLo /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash /tmp/miniconda.sh -b -p ${CONDA_DIR} && \
    rm /tmp/miniconda.sh && \
    # Configure conda to use conda-forge as the default channel to avoid Anaconda TOS prompts
    ${CONDA_DIR}/bin/conda config --system --remove-key channels || true && \
    ${CONDA_DIR}/bin/conda config --system --add channels conda-forge && \
    ${CONDA_DIR}/bin/conda config --system --set channel_priority strict && \
    ${CONDA_DIR}/bin/conda update -n base conda -y && \
    ${CONDA_DIR}/bin/conda clean -afy

RUN ${CONDA_DIR}/bin/conda create -n ${CONDA_ENV_NAME} -c conda-forge python=${PYTHON_VERSION} -y && \
    ${CONDA_DIR}/bin/conda clean -afy

RUN pwsh -NoLogo -NoProfile -Command "\
    Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; \
    Install-Module -Name dbatools,Pester,PSFramework -Scope AllUsers -Force -SkipPublisherCheck"

RUN ${CONDA_DIR}/bin/conda run -n ${CONDA_ENV_NAME} python -m pip install --upgrade pip && \
    ${CONDA_DIR}/bin/conda run -n ${CONDA_ENV_NAME} pip install ruff pytest pytest-cov wheel build pyodbc aiohttp

RUN <<'BASH'
set -euo pipefail

if getent group "${DEVCONTAINER_GROUP}" >/dev/null 2>&1; then
    groupmod -g "${DEVCONTAINER_GID}" "${DEVCONTAINER_GROUP}"
else
    groupadd --gid "${DEVCONTAINER_GID}" "${DEVCONTAINER_GROUP}"
fi

if getent passwd "${DEVCONTAINER_USER}" >/dev/null 2>&1; then
    usermod -d "${DEVCONTAINER_HOME}" -m "${DEVCONTAINER_USER}"
    usermod -g "${DEVCONTAINER_GROUP}" "${DEVCONTAINER_USER}"
    usermod -u "${DEVCONTAINER_UID}" "${DEVCONTAINER_USER}"
else
    useradd --uid "${DEVCONTAINER_UID}" --gid "${DEVCONTAINER_GID}" -m -s /bin/bash "${DEVCONTAINER_USER}"
fi

mkdir -p "${DEVCONTAINER_HOME}"
chown -R "${DEVCONTAINER_USER}:${DEVCONTAINER_GROUP}" "${DEVCONTAINER_HOME}"

mkdir -p /etc/sudoers.d
echo "${DEVCONTAINER_USER} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${DEVCONTAINER_USER}"
chmod 0440 "/etc/sudoers.d/${DEVCONTAINER_USER}"

mkdir -p /data /logs
chown -R "${DEVCONTAINER_USER}:${DEVCONTAINER_GROUP}" /data /logs
BASH

SHELL ["/bin/bash", "-lc"]
RUN for f in /etc/skel/.bashrc ${DEVCONTAINER_HOME}/.bashrc ${DEVCONTAINER_HOME}/.profile; do \
    echo 'if [ -f /opt/conda/etc/profile.d/conda.sh ]; then . /opt/conda/etc/profile.d/conda.sh; fi' >> "$f"; \
    echo "conda activate ${CONDA_ENV_NAME}" >> "$f"; \
    done

RUN <<'BASH'
set -euo pipefail
for f in /etc/skel/.bashrc ${DEVCONTAINER_HOME}/.bashrc ${DEVCONTAINER_HOME}/.profile; do
    cat >> "$f" <<'PROMPT'
# dbtools devcontainer prompt
if [[ $- == *i* ]]; then
export PS1="\[$(tput setaf 208)\]\d  \[$(tput setaf 226)\]\u\[$(tput setaf 220)\]@\[$(tput setaf 214)\]\h \[$(tput setaf 33)\]\w
\[$(tput sgr0)\]$ "
fi
PROMPT

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

RUN mkdir -p /opt/conda/envs/${CONDA_ENV_NAME}
ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:/opt/mssql-tools18/bin:/opt/mssql-tools/bin:${PATH}

USER ${DEVCONTAINER_USER}
WORKDIR /workspaces/dbtools

USER root
RUN mkdir -p ${DEVCONTAINER_HOME}/.vscode-server/extensions ${DEVCONTAINER_HOME}/.vscode-server/extensionsCache && \
    chown -R ${DEVCONTAINER_USER}:${DEVCONTAINER_GROUP} ${DEVCONTAINER_HOME}/.vscode-server

USER ${DEVCONTAINER_USER}
