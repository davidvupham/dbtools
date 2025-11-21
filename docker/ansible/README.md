# Ansible Execution Image

A minimal, reproducible container for running Ansible CLI tooling locally. The image follows Dockerfile
best practices (non-root user, pinned versions, cached apt installs) and layers quality tooling such as
`ansible-lint` and `molecule` for quick feedback loops.

## Build

```bash
cd docker/ansible
docker build -t dbtools/ansible:latest .
```

Environment variables such as `ANSIBLE_VERSION` and `ANSIBLE_LINT_VERSION` can be overridden at build time:

```bash
docker build \
  --build-arg ANSIBLE_VERSION=10.4.0 \
  --build-arg ANSIBLE_LINT_VERSION=24.9.0 \
  -t dbtools/ansible:latest .
```

## Run via Compose

See `docker/docker-compose.ansible-awx.yml` for a ready-to-run service that mounts the repository into
`/workspace` and reuses the shared `tool-library-network` bridge.
