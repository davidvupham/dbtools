# AWX Controller Image

A thin wrapper around the upstream `quay.io/ansible/awx` release that adds a curl-based health check and
keeps the version pinned for reproducibility.

## Build

```bash
cd docker/awx
docker build -t dbtools/awx:24.6.1 .
```

Override the upstream tag when you need to test a different controller release:

```bash
docker build --build-arg AWX_VERSION=24.7.0 -t dbtools/awx:24.7.0 .
```

This image is intended to run inside the Compose stack defined in `docker/docker-compose.ansible-awx.yml`,
which wires up the companion PostgreSQL and Redis dependencies that AWX expects.
