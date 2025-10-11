# syntax=docker/dockerfile:1.4

ARG VARIANT="latest"
FROM mcr.microsoft.com/devcontainers/miniconda:${VARIANT}

# Build args
ARG PYTHON_VERSION=3.13
ARG CONDA_ENV_NAME=gds

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Create the conda environment and install base packages
RUN conda update -n base -c defaults conda -y && \
    conda create -n ${CONDA_ENV_NAME} -c conda-forge python=${PYTHON_VERSION} -y && \
    conda clean -afy

# Make sure the conda environment is available in interactive shells
SHELL ["/bin/bash", "-lc"]
# Source conda.sh before activation so 'conda activate' works in terminals
RUN for f in /etc/skel/.bashrc /home/vscode/.bashrc /home/vscode/.profile; do \
            echo 'if [ -f /opt/conda/etc/profile.d/conda.sh ]; then . /opt/conda/etc/profile.d/conda.sh; fi' >> "$f"; \
            echo "conda activate ${CONDA_ENV_NAME}" >> "$f"; \
        done

# Install some common build tooling in the env
RUN conda run -n ${CONDA_ENV_NAME} python -m pip install --upgrade pip && \
    conda run -n ${CONDA_ENV_NAME} pip install ruff pytest pytest-cov wheel build

# Set path
ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:$PATH

USER vscode
WORKDIR /workspaces/dbtools

# Pre-create VS Code server directories with correct ownership to avoid permission issues
USER root
RUN mkdir -p /home/vscode/.vscode-server/extensions /home/vscode/.vscode-server/extensionsCache \
    && chown -R vscode:vscode /home/vscode/.vscode-server
USER vscode
