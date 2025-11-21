# syntax=docker/dockerfile:1.7
ARG AWX_VERSION=24.6.1
FROM quay.io/ansible/awx:${AWX_VERSION}

USER root

LABEL org.opencontainers.image.title="dbtools-awx" \
      org.opencontainers.image.description="Opinionated AWX image with health check and pinned upstream release" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/davidvupham/dbtools"

RUN --mount=type=cache,target=/var/cache/dnf \
    microdnf update -y \
    && microdnf install -y \
        curl \
        tzdata \
    && microdnf clean all

COPY healthcheck.sh /usr/local/bin/awx-healthcheck
RUN chmod +x /usr/local/bin/awx-healthcheck

ENV AWX_HTTP_PORT=8052 \
    AWX_HEALTHCHECK_HOST=http://127.0.0.1:${AWX_HTTP_PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=5 CMD /usr/local/bin/awx-healthcheck

USER 1000
