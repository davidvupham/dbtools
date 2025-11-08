# syntax=docker/dockerfile:1.4

FROM registry.access.redhat.com/ubi9/ubi:latest

ARG PYTHON_VERSION=3.13
ARG CONDA_ENV_NAME=gds
ENV CONDA_DIR=/opt/conda
ENV PATH=${CONDA_DIR}/bin:${PATH}
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

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
    dnf -y install powershell && \
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

RUN pwsh -NoLogo -NoProfile -Command "Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force; Install-Module -Name dbatools,Pester,PSFramework -Scope AllUsers -Force"

RUN ${CONDA_DIR}/bin/conda run -n ${CONDA_ENV_NAME} python -m pip install --upgrade pip && \
    ${CONDA_DIR}/bin/conda run -n ${CONDA_ENV_NAME} pip install ruff pytest pytest-cov wheel build pyodbc aiohttp

RUN groupadd --gid 1000 vscode && \
    useradd --uid 1000 --gid 1000 -m vscode && \
    mkdir -p /etc/sudoers.d && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vscode && \
    chmod 0440 /etc/sudoers.d/vscode

SHELL ["/bin/bash", "-lc"]
RUN for f in /etc/skel/.bashrc /home/vscode/.bashrc /home/vscode/.profile; do \
    echo 'if [ -f /opt/conda/etc/profile.d/conda.sh ]; then . /opt/conda/etc/profile.d/conda.sh; fi' >> "$f"; \
    echo "conda activate ${CONDA_ENV_NAME}" >> "$f"; \
    done

RUN <<'BASH'
set -euo pipefail
for f in /etc/skel/.bashrc /home/vscode/.bashrc /home/vscode/.profile; do
    cat >> "$f" <<'PROMPT'
# dbtools devcontainer prompt
if [[ $- == *i* ]]; then
export PS1="\[$(tput setaf 208)\]\d  \[$(tput setaf 226)\]\u\[$(tput setaf 220)\]@\[$(tput setaf 214)\]\h \[$(tput setaf 33)\]\w
\[$(tput sgr0)\]$ "
fi
PROMPT

done
BASH

RUN mkdir -p /opt/conda/envs/${CONDA_ENV_NAME}
ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:${PATH}

USER vscode
WORKDIR /workspaces/dbtools

USER root
RUN mkdir -p /home/vscode/.vscode-server/extensions /home/vscode/.vscode-server/extensionsCache && \
    chown -R vscode:vscode /home/vscode/.vscode-server

USER vscode
