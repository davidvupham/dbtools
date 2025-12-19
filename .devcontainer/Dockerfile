# syntax=docker/dockerfile:1.5

FROM registry.access.redhat.com/ubi9/ubi

# Build-time overrides to align the container user with the host VS Code user.
#
# Why this matters:
# - The repo is bind-mounted from the host.
# - Matching UID/GID avoids permission issues on created/modified files.
#
# These build args are provided by .devcontainer/devcontainer.json.
ARG DEVCONTAINER_USER=vscode
ARG DEVCONTAINER_UID=1000
ARG DEVCONTAINER_GID=1000

# Persist the chosen devcontainer user name for runtime scripts.
ENV DEVCONTAINER_USER=${DEVCONTAINER_USER}

ENV ACCEPT_EULA=Y

# Install base dependencies.
# - Use microdnf when available (smaller UBI images).
# - Fall back to dnf with retries to reduce transient network failures.
# - Add Microsoft packages only long enough to install SQL Server tooling.
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
    sudo \
    python3 python3-pip \
    unixODBC unixODBC-devel \
    postgresql \
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
    if sh -xc "ACCEPT_EULA=Y $INSTALL_CMD msodbcsql18 mssql-tools18 powershell"; then success=1; break; fi; \
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

# Create a non-root user aligned with the host user.
# VS Code runs as this user inside the container.
RUN set -eux; \
    DEV_GID="${DEVCONTAINER_GID:-1000}"; DEV_UID="${DEVCONTAINER_UID:-1000}"; \
    getent group "$DEV_GID" >/dev/null 2>&1 || groupadd -g "$DEV_GID" "$DEVCONTAINER_USER"; \
    id -u "$DEVCONTAINER_USER" >/dev/null 2>&1 || useradd -m -u "$DEV_UID" -g "$DEV_GID" -s /bin/bash "$DEVCONTAINER_USER"; \
    # Allow the dev user to run a small set of administrative commands without a password.
    # This is used by postCreate.sh to align docker socket group permissions at runtime.
    echo "$DEVCONTAINER_USER ALL=(root) NOPASSWD:/usr/sbin/groupadd,/usr/sbin/usermod" > /etc/sudoers.d/90-devcontainer; \
    chmod 0440 /etc/sudoers.d/90-devcontainer; \
    mkdir -p /workspaces/dbtools; \
    chown -R "$DEVCONTAINER_USER":"$DEVCONTAINER_USER" /workspaces

ENV PATH=/opt/mssql-tools18/bin:/opt/mssql-tools/bin:$PATH

# NOTE: Python tooling (ruff, pytest, etc.) is installed via postCreate.sh
# using the OS-provided Python (/usr/bin/python3).

# Install Docker CLI and Compose plugin for the RHEL/UBI base image.
# This enables running `docker` commands inside the dev container when the host
# Docker socket is mounted.
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

# Startup hook (runs as containerUser). When containerUser=root, this aligns
# Docker socket group membership before VS Code starts the remote server.
USER root
RUN <<'EOF'
set -eux

cat > /usr/local/bin/devcontainer-init <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

USER_NAME="${DEVCONTAINER_USER:-vscode}"

if [[ -S /var/run/docker.sock ]]; then
    sock_gid="$(stat -c %g /var/run/docker.sock 2>/dev/null || true)"
    if [[ -n "${sock_gid}" ]]; then
        group_name="$(getent group "${sock_gid}" | cut -d: -f1 || true)"
        if [[ -z "${group_name}" ]]; then
            group_name="docker-host"
            groupadd -g "${sock_gid}" "${group_name}" 2>/dev/null || true
            group_name="$(getent group "${sock_gid}" | cut -d: -f1 || true)"
        fi

        if [[ -n "${group_name}" ]] && id -u "${USER_NAME}" >/dev/null 2>&1; then
            usermod -aG "${group_name}" "${USER_NAME}" 2>/dev/null || true
        fi
    fi
fi

exec "$@"
SCRIPT

chmod 0755 /usr/local/bin/devcontainer-init
EOF

# Lightweight container healthcheck: verifies core tooling is on PATH.
# This helps surface broken builds early without assuming any databases are running.
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD bash -lc 'command -v python3 >/dev/null && command -v sqlcmd >/dev/null && command -v pwsh >/dev/null || exit 1'

# Keep container alive for VS Code to attach.
ENTRYPOINT ["/usr/local/bin/devcontainer-init"]
CMD ["sleep", "infinity"]
