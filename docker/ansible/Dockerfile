# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ARG ANSIBLE_VERSION=10.4.0
ARG ANSIBLE_LINT_VERSION=24.9.0

ENV ANSIBLE_HOME=/opt/ansible \
    PATH=/opt/ansible/bin:/home/ansible/.local/bin:${PATH} \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ANSIBLE_CONFIG=/workspace/ansible.cfg

LABEL org.opencontainers.image.title="dbtools-ansible" \
      org.opencontainers.image.description="Batteries-included Ansible execution image with linting and molecule" \
      org.opencontainers.image.authors="dbtools" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/davidvupham/dbtools"

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        iputils-ping \
        jq \
        openssh-client \
        rsync \
        sshpass \
        tini \
        tzdata \
        vim-tiny \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN python -m venv ${ANSIBLE_HOME} \
    && ${ANSIBLE_HOME}/bin/pip install --upgrade pip \
    && ${ANSIBLE_HOME}/bin/pip install --no-cache-dir \
        ansible==${ANSIBLE_VERSION} \
        ansible-lint==${ANSIBLE_LINT_VERSION} \
        -r /tmp/requirements.txt \
    && ln -s ${ANSIBLE_HOME}/bin/ansible /usr/local/bin/ansible \
    && ln -s ${ANSIBLE_HOME}/bin/ansible-playbook /usr/local/bin/ansible-playbook \
    && ln -s ${ANSIBLE_HOME}/bin/ansible-lint /usr/local/bin/ansible-lint \
    && ln -s ${ANSIBLE_HOME}/bin/molecule /usr/local/bin/molecule \
    && rm -f /tmp/requirements.txt

RUN groupadd --system --gid 5000 ansible \
    && useradd --system --uid 5000 --gid ansible --create-home --shell /bin/bash ansible \
    && mkdir -p /workspace \
    && chown -R ansible:ansible /workspace /opt/ansible

WORKDIR /workspace
VOLUME ["/workspace"]

USER ansible

ENTRYPOINT ["tini","--"]
CMD ["bash"]
