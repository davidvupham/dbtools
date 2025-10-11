# syntax=docker/dockerfile:1.4

ARG VARIANT="latest"
FROM mcr.microsoft.com/devcontainers/miniconda:${VARIANT}

# Build args
ARG PYTHON_VERSION=3.9
ARG CONDA_ENV_NAME=gds

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Create the conda environment and install base packages
RUN conda update -n base -c defaults conda -y && \
    conda create -n ${CONDA_ENV_NAME} python=${PYTHON_VERSION} -y && \
    conda clean -afy

# Make sure the environment is activated for all shells
SHELL ["/bin/bash", "-lc"]
RUN echo "conda activate ${CONDA_ENV_NAME}" >> /etc/skel/.bashrc && \
    echo "conda activate ${CONDA_ENV_NAME}" >> /home/vscode/.bashrc && \
    echo "conda activate ${CONDA_ENV_NAME}" >> /home/vscode/.profile

# Install some common build tooling in the env
RUN conda run -n ${CONDA_ENV_NAME} python -m pip install --upgrade pip && \
    conda run -n ${CONDA_ENV_NAME} pip install ruff pytest pytest-cov wheel build

# Set path
ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:$PATH

USER vscode
WORKDIR /workspaces/dbtools
