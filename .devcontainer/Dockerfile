# syntax=docker/dockerfile:1.5

FROM registry.access.redhat.com/ubi9/ubi

# Build-time overrides to align container user with host VS Code user
ARG DEVCONTAINER_USER=vscode
ARG DEVCONTAINER_UID=1000
ARG DEVCONTAINER_GID=1000

ENV ACCEPT_EULA=Y

# Minimal layers: install base deps with microdnf, add Microsoft repo, install SQL tools & PowerShell
RUN --mount=type=cache,target=/var/cache/dnf set -eux; \
    if command -v microdnf >/dev/null 2>&1; then \
    PM=microdnf; \
    INSTALL_CMD="$PM -y --refresh install"; \
    CLEAN_CMD="$PM -y clean all"; \
    MAKECACHE_CMD="true"; \
    else \
    PM=dnf; \
    # Keep dnf options conservative; rely on explicit retries below.
    # Limit parallel downloads to reduce partial-download failures from flaky networks.
    INSTALL_CMD="$PM -y --setopt=timeout=600 --setopt=retries=10 --setopt=max_parallel_downloads=1 --best --allowerasing install"; \
    CLEAN_CMD="$PM -y clean all"; \
    MAKECACHE_CMD="$PM -y --setopt=timeout=600 --setopt=retries=10 --setopt=max_parallel_downloads=1 makecache --refresh"; \
    fi; \
    # Refresh metadata (required for dnf; harmless for microdnf branch)
    success=0; \
    for i in 1 2 3 4 5; do \
    if sh -xc "$MAKECACHE_CMD"; then success=1; break; fi; \
    echo "[base] makecache failed (try $i)"; \
    sh -xc "$CLEAN_CMD" || true; \
    find /var/cache/dnf /var/cache/yum -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true; \
    sleep 3; \
    done; \
    [ "$success" -eq 1 ]; \
    # Install base packages with retries. IMPORTANT: fail the build if we cannot install.
    success=0; \
    for i in 1 2 3 4 5; do \
    if sh -xc "$INSTALL_CMD \
    ca-certificates curl-minimal gnupg2 shadow-utils \
    python3 python3-pip \
    unixODBC unixODBC-devel \
    git bash-completion openssh-clients jq"; then \
    success=1; break; \
    fi; \
    echo "[base] install failed (try $i)"; \
    sh -xc "$CLEAN_CMD" || true; \
    find /var/cache/dnf /var/cache/yum -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true; \
    sh -xc "$MAKECACHE_CMD" || true; \
    sleep 3; \
    done; \
    [ "$success" -eq 1 ]; \
    # Microsoft repo and tools (with retries)
    curl -fsSL https://packages.microsoft.com/config/rhel/9/packages-microsoft-prod.rpm -o /tmp/packages-microsoft-prod.rpm; \
    rpm -Uvh /tmp/packages-microsoft-prod.rpm; \
    rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-Microsoft || true; \
    success=0; \
    for i in 1 2 3 4 5; do \
    if sh -xc "ACCEPT_EULA=Y $INSTALL_CMD msodbcsql18 mssql-tools18"; then success=1; break; fi; \
    echo "[ms] tools install failed (try $i)"; \
    sh -xc "$CLEAN_CMD" || true; \
    find /var/cache/dnf /var/cache/yum -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true; \
    sh -xc "$MAKECACHE_CMD" || true; \
    sleep 3; \
    done; \
    [ "$success" -eq 1 ]; \
    # Provide a `python` entrypoint for scripts that don't call python3 explicitly.
    ln -sf /usr/bin/python3 /usr/local/bin/python || true; \
    ln -sf /opt/mssql-tools18/bin/sqlcmd /usr/local/bin/sqlcmd || true; \
    # Avoid unrelated build failures later (e.g., devcontainer features running dnf check-update)
    # by removing the Microsoft repo definition after we've installed the needed packages.
    # (The repo has intermittently served metadata with a bad GPG signature, which breaks unrelated installs.)
    if [ -f /etc/yum.repos.d/microsoft-prod.repo ]; then \
    rm -f /etc/yum.repos.d/microsoft-prod.repo; \
    fi; \
    if [ -f /etc/yum.repos.d/packages-microsoft-com-prod.repo ]; then \
    rm -f /etc/yum.repos.d/packages-microsoft-com-prod.repo; \
    fi; \
    sh -xc "$CLEAN_CMD"; \
    find /var/cache/dnf /var/cache/yum -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true; \
    rm -rf /tmp/*

# Create non-root user aligned with host
RUN set -eux; \
    DEV_GID="${DEVCONTAINER_GID:-1000}"; DEV_UID="${DEVCONTAINER_UID:-1000}"; \
    getent group "$DEV_GID" >/dev/null 2>&1 || groupadd -g "$DEV_GID" "$DEVCONTAINER_USER"; \
    id -u "$DEVCONTAINER_USER" >/dev/null 2>&1 || useradd -m -u "$DEV_UID" -g "$DEV_GID" -s /bin/bash "$DEVCONTAINER_USER"; \
    mkdir -p /workspaces/dbtools; \
    chown -R "$DEVCONTAINER_USER":"$DEVCONTAINER_USER" /workspaces

ENV PATH=/opt/mssql-tools18/bin:/opt/mssql-tools/bin:$PATH

# NOTE: Python tooling (ruff, pytest, etc.) is installed via postCreate.sh
# using the OS-provided Python (/usr/bin/python3).

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

USER ${DEVCONTAINER_USER}
WORKDIR /workspaces/dbtools

# Lightweight container healthcheck: verifies core tooling is on PATH
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD bash -lc 'command -v python3 >/dev/null && command -v sqlcmd >/dev/null || exit 1'

# Keep container alive for VS Code to attach
CMD ["sleep", "infinity"]
