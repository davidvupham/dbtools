# Configuring Container Registry Proxies

This guide explains how to configure Docker and Podman to use corporate registry proxies or mirrors instead of accessing public registries directly.

## Overview

If registry mirrors or proxies are used instead of accessing public registries like `docker.io` or `mcr.microsoft.com` directly, configure your container runtime as described below.

## Docker Configuration

### System-wide (requires root)

Edit `/etc/docker/daemon.json`:

```json
{
  "registry-mirrors": [
    "https://your-corporate-registry.example.com"
  ],
  "insecure-registries": [
    "internal-registry.example.com:5000"
  ]
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

### Per-image prefix (no config change)

Prefix image names with your registry:

```bash
docker pull myregistry.example.com/library/nginx:latest
```

## Podman Configuration

### Using the project template

This project includes a template at `docker/containers/registries.conf.example`. Copy and customize it:

```bash
# Create the config directory if it doesn't exist
mkdir -p ~/.config/containers

# Copy the template
cp docker/containers/registries.conf.example ~/.config/containers/registries.conf

# Edit to match your registry proxy
vi ~/.config/containers/registries.conf
```

### Manual configuration

Alternatively, create `~/.config/containers/registries.conf` manually:

```toml
# Mirror docker.io through proxy
[[registry]]
location = "docker.io"
[[registry.mirror]]
location = "your-registry-proxy.example.com/docker.io"

# Mirror mcr.microsoft.com
[[registry]]
location = "mcr.microsoft.com"
[[registry.mirror]]
location = "your-registry-proxy.example.com/mcr.microsoft.com"

# Allow insecure internal registries
[[registry]]
location = "internal-registry.example.com:5000"
insecure = true
```

### System-wide (requires root)

Edit `/etc/containers/registries.conf` with the same syntax.

### Verify configuration

```bash
podman info | grep -A 20 registries
```

## Proxy Server Configuration

If your environment uses an HTTP/HTTPS proxy:

### Docker

Edit `/etc/systemd/system/docker.service.d/http-proxy.conf`:

```ini
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:8080"
Environment="HTTPS_PROXY=http://proxy.example.com:8080"
Environment="NO_PROXY=localhost,127.0.0.1,internal-registry.example.com"
```

Reload and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### Podman

Set environment variables in your shell profile (`~/.bashrc`):

```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
export NO_PROXY="localhost,127.0.0.1,internal-registry.example.com"
```

## Recommended Approach

Configure registry mirroring at the **container runtime level** (registries.conf for Podman, daemon.json for Docker) rather than modifying image names in scripts. This provides:

- **Transparency**: Scripts use standard image names (e.g., `mcr.microsoft.com/mssql/server:2025-latest`)
- **Portability**: Same scripts work in environments with or without proxies
- **Centralized config**: One configuration affects all containers

## Troubleshooting

### Test connectivity

```bash
# Docker
docker pull hello-world

# Podman
podman pull docker.io/library/hello-world
```

### Check current registries

```bash
# Docker
docker info | grep -i registry

# Podman
podman info --format '{{.Registries}}'
```

### Debug pull failures

```bash
# Verbose output
podman pull --log-level=debug docker.io/library/nginx:latest
```

## References

- [Docker daemon configuration](https://docs.docker.com/config/daemon/)
- [Podman registries.conf](https://github.com/containers/image/blob/main/docs/containers-registries.conf.5.md)
- [Configuring container storage](https://docs.podman.io/en/latest/markdown/podman-system-reset.1.html)
