# syntax=docker/dockerfile:1.5

FROM registry.access.redhat.com/ubi9/ubi

# Build-time overrides to align container user with host VS Code user
ARG DEVCONTAINER_USER=vscode
ARG DEVCONTAINER_UID=1000
ARG DEVCONTAINER_GID=1000
ARG USE_PYENV=0
ARG PYENV_PYTHON_VERSION=3.14.0

ENV ACCEPT_EULA=Y

# Minimal layers: install base deps with microdnf, add Microsoft repo, install SQL tools & PowerShell
RUN set -eux; \
    if command -v microdnf >/dev/null 2>&1; then \
    PM=microdnf; \
    UPDATE_CMD="$PM -y --refresh update"; \
    INSTALL_CMD="$PM -y --refresh install"; \
    CLEAN_CMD="$PM -y clean all"; \
    MAKECACHE_CMD="true"; \
    else \
    PM=dnf; \
    UPDATE_CMD="$PM -y --setopt=timeout=300 --setopt=retries=10 update"; \
    INSTALL_CMD="$PM -y --setopt=timeout=300 --setopt=retries=10 --best --allowerasing install"; \
    CLEAN_CMD="$PM -y clean all"; \
    MAKECACHE_CMD="$PM -y makecache --refresh"; \
    fi; \
    # Update with retries to mitigate flaky mirrors
    for i in 1 2 3 4 5; do \
    sh -xc "$UPDATE_CMD" && break || (echo "[base] update failed (try $i)"; sh -xc "$CLEAN_CMD"; sh -xc "$MAKECACHE_CMD" || true; sleep 3); \
    done; \
    # Base packages with retries
    for i in 1 2 3 4 5; do \
    sh -xc "$INSTALL_CMD curl-minimal gnupg2 ca-certificates git gcc gcc-c++ make python3 python3-pip python3-devel shadow-utils unixODBC unixODBC-devel" && break || (echo "[base] install failed (try $i)"; sh -xc "$CLEAN_CMD"; sh -xc "$MAKECACHE_CMD" || true; sleep 3); \
    done; \
    # Optional pyenv build deps with retries
    if [ "$USE_PYENV" = "1" ]; then \
    for i in 1 2 3 4 5; do \
    sh -xc "$INSTALL_CMD zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk tk-devel libffi-devel xz xz-devel" && break || (echo "[pyenv] deps install failed (try $i)"; sh -xc "$CLEAN_CMD"; sh -xc "$MAKECACHE_CMD" || true; sleep 3); \
    done; \
    fi; \
    # Microsoft repo and tools (with retries)
    curl -fsSL https://packages.microsoft.com/config/rhel/9/packages-microsoft-prod.rpm -o /tmp/packages-microsoft-prod.rpm; \
    rpm -Uvh /tmp/packages-microsoft-prod.rpm; \
    for i in 1 2 3 4 5; do \
    sh -xc "ACCEPT_EULA=Y $INSTALL_CMD msodbcsql18 mssql-tools18 powershell" && break || (echo "[ms] tools install failed (try $i)"; sh -xc "$CLEAN_CMD"; sh -xc "$MAKECACHE_CMD" || true; sleep 3); \
    done; \
    ln -sf /opt/mssql-tools18/bin/sqlcmd /usr/local/bin/sqlcmd || true; \
    sh -xc "$CLEAN_CMD"; \
    rm -rf /var/cache/dnf /var/cache/yum /tmp/*

ENV PATH=/opt/mssql-tools18/bin:/opt/mssql-tools/bin:$PATH

# Install Docker CLI and Compose plugin (always latest stable) for RHEL/UBI base
RUN set -eux; \
    ARCH_RAW="$(uname -m)"; \
    case "$ARCH_RAW" in \
    x86_64|amd64) ARCH="x86_64" ;; \
    aarch64|arm64) ARCH="aarch64" ;; \
    *) ARCH="$ARCH_RAW" ;; \
    esac; \
    # Discover latest Docker CLI static build from download.docker.com and install
    LATEST_DOCKER_VER="$(curl -fsSL "https://download.docker.com/linux/static/stable/${ARCH}/" \
    | grep -oE 'docker-[0-9]+(\.[0-9]+)*\.tgz' \
    | sed -E 's/docker-|\.tgz//g' \
    | sort -V | tail -n1)"; \
    curl -fsSL "https://download.docker.com/linux/static/stable/${ARCH}/docker-${LATEST_DOCKER_VER}.tgz" -o /tmp/docker.tgz; \
    tar -xzf /tmp/docker.tgz -C /tmp; \
    install -m 0755 /tmp/docker/docker /usr/local/bin/docker; \
    rm -rf /tmp/docker /tmp/docker.tgz; \
    # Install latest Docker Compose plugin via GitHub releases "latest" endpoint
    mkdir -p /usr/local/lib/docker/cli-plugins; \
    curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-${ARCH}" -o /usr/local/lib/docker/cli-plugins/docker-compose; \
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose; \
    docker --version; \
    docker compose version || true

# Create non-root user aligned with host
RUN set -eux; \
    DEV_GID="${DEVCONTAINER_GID:-1000}"; DEV_UID="${DEVCONTAINER_UID:-1000}"; \
    getent group "$DEV_GID" >/dev/null 2>&1 || groupadd -g "$DEV_GID" "$DEVCONTAINER_USER"; \
    id -u "$DEVCONTAINER_USER" >/dev/null 2>&1 || useradd -m -u "$DEV_UID" -g "$DEV_GID" -s /bin/bash "$DEVCONTAINER_USER"; \
    mkdir -p /workspaces/dbtools; \
    chown -R "$DEVCONTAINER_USER":"$DEVCONTAINER_USER" /workspaces

USER ${DEVCONTAINER_USER}
WORKDIR /workspaces/dbtools

# Optional: install pyenv and Python ${PYENV_PYTHON_VERSION} for Red Hat base
ENV PYENV_ROOT=/home/${DEVCONTAINER_USER}/.pyenv
ENV PATH=${PYENV_ROOT}/bin:${PYENV_ROOT}/shims:$PATH
RUN set -eux; \
    if [ "$USE_PYENV" = "1" ]; then \
    echo "[pyenv] Installing pyenv for ${DEVCONTAINER_USER}..."; \
    curl -fsSL https://pyenv.run | bash; \
    /bin/bash -lc "pyenv --version"; \
    echo "[pyenv] Installing Python ${PYENV_PYTHON_VERSION}..."; \
    /bin/bash -lc "pyenv install -s ${PYENV_PYTHON_VERSION}"; \
    /bin/bash -lc "pyenv global ${PYENV_PYTHON_VERSION}"; \
    /bin/bash -lc "python --version"; \
    else \
    echo "[pyenv] Skipped (USE_PYENV=0)"; \
    fi

# Lightweight container healthcheck: verifies core tooling is on PATH
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD bash -lc 'command -v python3 >/dev/null && command -v pwsh >/dev/null && command -v sqlcmd >/dev/null || exit 1'

# Keep container alive for VS Code to attach
CMD ["sleep", "infinity"]
