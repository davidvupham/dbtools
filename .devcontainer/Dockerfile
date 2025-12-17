# syntax=docker/dockerfile:1.4

FROM mcr.microsoft.com/devcontainers/miniconda:latest

# Build arguments
ARG PYTHON_VERSION=3.14
ARG CONDA_ENV_NAME=gds
ARG DEVCONTAINER_USER=gds
ARG DEVCONTAINER_GROUP=gds
ARG DEVCONTAINER_UID=1000
ARG DEVCONTAINER_GID=1000

# Environment variables - set once
ENV DEBIAN_FRONTEND=noninteractive \
    ACCEPT_EULA=Y \
    DEVCONTAINER_USER=${DEVCONTAINER_USER} \
    DEVCONTAINER_GROUP=${DEVCONTAINER_GROUP} \
    DEVCONTAINER_UID=${DEVCONTAINER_UID} \
    DEVCONTAINER_GID=${DEVCONTAINER_GID} \
    DEVCONTAINER_HOME=/home/${DEVCONTAINER_USER}

# Layer 1: Install repository keys and sources (changes less frequently)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    curl \
    lsb-release && \
    # Microsoft repository
    wget -q https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    # Docker repository
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list && \
    # HashiCorp repository
    curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    chmod a+r /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > /etc/apt/sources.list.d/hashicorp.list

# Layer 2: Remove conflicting packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get remove -y --purge \
    docker \
    docker-engine \
    docker.io \
    containerd \
    runc \
    moby-engine \
    moby-cli \
    moby-containerd || true && \
    apt-get autoremove -y

# Layer 3: Install runtime dependencies (alphabetically sorted for maintainability)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    ansible \
    build-essential \
    containerd.io \
    docker-buildx-plugin \
    docker-ce \
    docker-ce-cli \
    docker-compose-plugin \
    gh \
    iputils-ping \
    msodbcsql18 \
    mssql-tools18 \
    netcat-openbsd \
    powershell \
    terraform \
    unixodbc-dev \
    vault && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Layer 4: Configure conda environment
RUN conda config --system --remove-key channels || true && \
    conda config --system --add channels conda-forge && \
    conda config --system --set channel_priority strict && \
    conda update -n base conda -y && \
    conda create -n ${CONDA_ENV_NAME} python=${PYTHON_VERSION} -y && \
    conda clean -afy

# Layer 5: Install PowerShell modules
RUN pwsh -NoLogo -NoProfile -Command "\
    Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; \
    Install-Module -Name dbatools,Pester,PSFramework -Scope AllUsers -Force -SkipPublisherCheck"

# Layer 6: Create user and configure permissions
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

# Layer 7: Configure conda activation in shell profiles
SHELL ["/bin/bash", "-lc"]
RUN for f in /etc/skel/.bashrc ${DEVCONTAINER_HOME}/.bashrc ${DEVCONTAINER_HOME}/.profile; do \
    echo 'if [ -f /opt/conda/etc/profile.d/conda.sh ]; then . /opt/conda/etc/profile.d/conda.sh; fi' >> "$f"; \
    echo "conda activate ${CONDA_ENV_NAME}" >> "$f"; \
    done

# Layer 8: Configure custom bash prompt
RUN bash <<'BASH'
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

# Layer 9: Configure PowerShell profile
RUN bash <<'BASH'
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

# Layer 10: Install Python packages in conda environment
RUN conda run -n ${CONDA_ENV_NAME} python -m pip install --upgrade pip && \
    conda run -n ${CONDA_ENV_NAME} pip install --no-cache-dir \
    ipykernel \
    jupyterlab \
    numpy \
    pandas \
    ruff \
    pytest \
    pytest-cov \
    pytest-asyncio \
    wheel \
    build \
    pyodbc \
    aiohttp \
    pre-commit

# Set PATH environment variable
ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:/opt/mssql-tools18/bin:/opt/mssql-tools/bin:$PATH

# Layer 11: Pre-create VS Code server directories (as root, then fix ownership)
RUN mkdir -p ${DEVCONTAINER_HOME}/.vscode-server/extensions ${DEVCONTAINER_HOME}/.vscode-server/extensionsCache && \
    chown -R ${DEVCONTAINER_USER}:${DEVCONTAINER_GROUP} ${DEVCONTAINER_HOME}/.vscode-server

# Switch to non-root user for runtime
USER ${DEVCONTAINER_USER}
WORKDIR /workspaces/dbtools

# Keep container running - VS Code will attach to this
CMD ["sleep", "infinity"]
