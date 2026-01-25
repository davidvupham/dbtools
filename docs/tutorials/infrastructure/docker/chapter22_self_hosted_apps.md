# Chapter 22: Self-hosted applications with Docker

Run your own cloud services, media server, password manager, and more. This chapter covers popular self-hosted applications and best practices for running them in Docker containers.

---

## Why self-host?

Self-hosting gives you:

- **Data ownership** - Your files, passwords, and media stay on your hardware
- **Privacy** - No third-party access to your data
- **Cost savings** - No recurring subscription fees (after initial hardware)
- **Customization** - Configure services exactly how you need them
- **Learning** - Hands-on experience with networking, security, and infrastructure

> [!NOTE]
> Self-hosting requires maintenance. You're responsible for updates, backups, and security. Start small and add services incrementally.

---

## Essential containers for your homelab

Here are battle-tested applications commonly run in Docker, organized by category:

| Category | Application | Purpose |
|:---|:---|:---|
| **Cloud storage** | Nextcloud | Files, notes, calendar, contacts |
| **Media** | Jellyfin | Stream movies, TV, music |
| **Passwords** | Vaultwarden | Bitwarden-compatible password manager |
| **Network** | Pi-hole | Network-wide ad blocking |
| **Management** | Portainer | Docker container UI |
| **Documents** | Paperless-ngx | Scan, OCR, and organize documents |
| **Monitoring** | Uptime Kuma | Service availability monitoring |
| **Reverse proxy** | Nginx Proxy Manager | SSL and routing for services |

---

## Setting up your environment

### Directory structure

Organize your self-hosted services with a consistent structure:

```
~/docker/
├── compose/
│   ├── nextcloud/
│   │   └── docker-compose.yml
│   ├── jellyfin/
│   │   └── docker-compose.yml
│   └── vaultwarden/
│       └── docker-compose.yml
├── data/
│   ├── nextcloud/
│   ├── jellyfin/
│   └── vaultwarden/
└── .env                    # Shared environment variables
```

### Create a Docker network

Use a shared network so containers can communicate:

```bash
docker network create homelab
```

---

## Nextcloud: Self-hosted cloud storage

Nextcloud replaces Google Drive, Calendar, and Contacts with a self-hosted solution.

### Docker Compose configuration

```yaml
# ~/docker/compose/nextcloud/docker-compose.yml
services:
  nextcloud:
    image: nextcloud:stable
    container_name: nextcloud
    restart: unless-stopped
    ports:
      - "8080:80"
    environment:
      - MYSQL_HOST=nextcloud-db
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=${NEXTCLOUD_DB_PASSWORD}
      - NEXTCLOUD_ADMIN_USER=${NEXTCLOUD_ADMIN_USER}
      - NEXTCLOUD_ADMIN_PASSWORD=${NEXTCLOUD_ADMIN_PASSWORD}
      - NEXTCLOUD_TRUSTED_DOMAINS=${NEXTCLOUD_DOMAIN}
    volumes:
      - ${DATA_DIR}/nextcloud/html:/var/www/html
      - ${DATA_DIR}/nextcloud/data:/var/www/html/data
    networks:
      - homelab
    depends_on:
      - nextcloud-db
      - nextcloud-redis

  nextcloud-db:
    image: mariadb:10.11
    container_name: nextcloud-db
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD=${NEXTCLOUD_DB_ROOT_PASSWORD}
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=${NEXTCLOUD_DB_PASSWORD}
    volumes:
      - ${DATA_DIR}/nextcloud/db:/var/lib/mysql
    networks:
      - homelab

  nextcloud-redis:
    image: redis:7-alpine
    container_name: nextcloud-redis
    restart: unless-stopped
    networks:
      - homelab

networks:
  homelab:
    external: true
```

### Environment file

```bash
# ~/docker/.env
DATA_DIR=/home/user/docker/data
NEXTCLOUD_DB_PASSWORD=secure-password-here
NEXTCLOUD_DB_ROOT_PASSWORD=secure-root-password
NEXTCLOUD_ADMIN_USER=admin
NEXTCLOUD_ADMIN_PASSWORD=admin-password-here
NEXTCLOUD_DOMAIN=nextcloud.local
```

### Security best practices for Nextcloud

> [!IMPORTANT]
> Never place the Nextcloud data directory inside the web root. The configuration above correctly separates data from the application.

- Enable two-factor authentication (2FA) after first login
- Use HTTPS (configure via reverse proxy)
- Keep the image updated regularly
- Configure fail2ban or CrowdSec for brute-force protection

---

## Jellyfin: Self-hosted media server

Jellyfin streams your personal media library - movies, TV shows, and music.

### Basic configuration

```yaml
# ~/docker/compose/jellyfin/docker-compose.yml
services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    restart: unless-stopped
    ports:
      - "8096:8096"
    environment:
      - JELLYFIN_PublishedServerUrl=http://jellyfin.local:8096
    volumes:
      - ${DATA_DIR}/jellyfin/config:/config
      - ${DATA_DIR}/jellyfin/cache:/cache
      - /mnt/media/movies:/data/movies:ro
      - /mnt/media/tvshows:/data/tvshows:ro
      - /mnt/media/music:/data/music:ro
    networks:
      - homelab

networks:
  homelab:
    external: true
```

### Hardware transcoding (Intel/AMD)

For hardware-accelerated transcoding, pass the GPU device:

```yaml
services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    restart: unless-stopped
    ports:
      - "8096:8096"
    environment:
      - JELLYFIN_PublishedServerUrl=http://jellyfin.local:8096
    volumes:
      - ${DATA_DIR}/jellyfin/config:/config
      - ${DATA_DIR}/jellyfin/cache:/cache
      - /mnt/media:/data:ro
    devices:
      - /dev/dri/renderD128:/dev/dri/renderD128   # Intel/AMD GPU
      - /dev/dri/card0:/dev/dri/card0
    group_add:
      - "109"   # render group - find with: getent group render | cut -d: -f3
    networks:
      - homelab

networks:
  homelab:
    external: true
```

### Hardware transcoding (NVIDIA)

```yaml
services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    restart: unless-stopped
    runtime: nvidia
    ports:
      - "8096:8096"
    environment:
      - NVIDIA_DRIVER_CAPABILITIES=all
      - NVIDIA_VISIBLE_DEVICES=all
    volumes:
      - ${DATA_DIR}/jellyfin/config:/config
      - ${DATA_DIR}/jellyfin/cache:/cache
      - /mnt/media:/data:ro
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - homelab

networks:
  homelab:
    external: true
```

> [!TIP]
> After starting Jellyfin, enable hardware acceleration in Dashboard > Playback > Transcoding. Select VA-API for Intel/AMD or NVENC for NVIDIA.

---

## Vaultwarden: Lightweight password manager

Vaultwarden is a Bitwarden-compatible server that uses minimal resources (~50MB RAM vs 2-4GB for official Bitwarden).

### Docker Compose configuration

```yaml
# ~/docker/compose/vaultwarden/docker-compose.yml
services:
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    ports:
      - "8081:80"
    environment:
      - DOMAIN=https://vault.yourdomain.com   # Required for WebAuthn
      - SIGNUPS_ALLOWED=false                 # Disable after creating your account
      - ADMIN_TOKEN=${VAULTWARDEN_ADMIN_TOKEN}
      - WEBSOCKET_ENABLED=true
    volumes:
      - ${DATA_DIR}/vaultwarden:/data
    networks:
      - homelab

networks:
  homelab:
    external: true
```

### Important security settings

| Setting | Recommendation |
|:---|:---|
| `SIGNUPS_ALLOWED` | Set to `false` after creating your account |
| `ADMIN_TOKEN` | Use a strong, random token (generate with `openssl rand -base64 48`) |
| `DOMAIN` | Required for WebAuthn/passkey support |
| HTTPS | Always use HTTPS via reverse proxy |

> [!WARNING]
> Vaultwarden is community-maintained and lacks formal security audits. For enterprise use, consider official Bitwarden. For personal use, it's a solid choice used by thousands.

### Comparison: Vaultwarden vs Bitwarden

| Aspect | Vaultwarden | Bitwarden (Self-hosted) |
|:---|:---|:---|
| RAM usage | ~50MB | 2-4GB |
| Docker containers | 1 | 11 |
| Setup difficulty | Easy | Complex |
| Official support | Community | Yes |
| Premium features | Free | License required |

---

## Pi-hole: Network-wide ad blocking

Pi-hole blocks ads and trackers at the DNS level for your entire network.

### Docker Compose configuration

```yaml
# ~/docker/compose/pihole/docker-compose.yml
services:
  pihole:
    image: pihole/pihole:latest
    container_name: pihole
    restart: unless-stopped
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "8082:80/tcp"
    environment:
      - TZ=America/New_York
      - WEBPASSWORD=${PIHOLE_PASSWORD}
      - PIHOLE_DNS_=1.1.1.1;1.0.0.1   # Upstream DNS (Cloudflare)
    volumes:
      - ${DATA_DIR}/pihole/etc-pihole:/etc/pihole
      - ${DATA_DIR}/pihole/etc-dnsmasq.d:/etc/dnsmasq.d
    cap_add:
      - NET_ADMIN
    networks:
      homelab:
        ipv4_address: 172.20.0.2   # Static IP recommended

networks:
  homelab:
    external: true
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

> [!IMPORTANT]
> After deployment, configure your router to use Pi-hole's IP address as the primary DNS server. This ensures all devices on your network benefit from ad blocking.

---

## Portainer: Container management UI

Portainer provides a web interface for managing Docker containers, images, volumes, and networks.

### Docker Compose configuration

```yaml
# ~/docker/compose/portainer/docker-compose.yml
services:
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    ports:
      - "9443:9443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ${DATA_DIR}/portainer:/data
    networks:
      - homelab

networks:
  homelab:
    external: true
```

> [!CAUTION]
> Portainer has full access to Docker. Never expose it to the public internet. Keep it LAN-only or access via VPN.

---

## Paperless-ngx: Document management

Paperless-ngx scans, OCRs, and organizes documents with automatic tagging.

### Docker Compose configuration

```yaml
# ~/docker/compose/paperless/docker-compose.yml
services:
  paperless-broker:
    image: redis:7-alpine
    container_name: paperless-broker
    restart: unless-stopped
    networks:
      - homelab

  paperless-db:
    image: postgres:15
    container_name: paperless-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=paperless
      - POSTGRES_USER=paperless
      - POSTGRES_PASSWORD=${PAPERLESS_DB_PASSWORD}
    volumes:
      - ${DATA_DIR}/paperless/db:/var/lib/postgresql/data
    networks:
      - homelab

  paperless:
    image: ghcr.io/paperless-ngx/paperless-ngx:latest
    container_name: paperless
    restart: unless-stopped
    ports:
      - "8083:8000"
    environment:
      - PAPERLESS_REDIS=redis://paperless-broker:6379
      - PAPERLESS_DBHOST=paperless-db
      - PAPERLESS_DBNAME=paperless
      - PAPERLESS_DBUSER=paperless
      - PAPERLESS_DBPASS=${PAPERLESS_DB_PASSWORD}
      - PAPERLESS_SECRET_KEY=${PAPERLESS_SECRET_KEY}
      - PAPERLESS_OCR_LANGUAGE=eng
      - PAPERLESS_TIME_ZONE=America/New_York
      - USERMAP_UID=1000
      - USERMAP_GID=1000
    volumes:
      - ${DATA_DIR}/paperless/data:/usr/src/paperless/data
      - ${DATA_DIR}/paperless/media:/usr/src/paperless/media
      - ${DATA_DIR}/paperless/export:/usr/src/paperless/export
      - ${DATA_DIR}/paperless/consume:/usr/src/paperless/consume
    depends_on:
      - paperless-db
      - paperless-broker
    networks:
      - homelab

networks:
  homelab:
    external: true
```

### Create admin user

```bash
docker exec -it paperless python manage.py createsuperuser
```

---

## Uptime Kuma: Service monitoring

Monitor the availability of your services and receive alerts when something goes down.

```yaml
# ~/docker/compose/uptime-kuma/docker-compose.yml
services:
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    restart: unless-stopped
    ports:
      - "3001:3001"
    volumes:
      - ${DATA_DIR}/uptime-kuma:/app/data
    networks:
      - homelab

networks:
  homelab:
    external: true
```

---

## Nginx Proxy Manager: Reverse proxy with SSL

Expose services securely with automatic SSL certificates.

```yaml
# ~/docker/compose/nginx-proxy-manager/docker-compose.yml
services:
  npm:
    image: jc21/nginx-proxy-manager:latest
    container_name: nginx-proxy-manager
    restart: unless-stopped
    ports:
      - "80:80"      # HTTP
      - "443:443"    # HTTPS
      - "81:81"      # Admin UI
    volumes:
      - ${DATA_DIR}/npm/data:/data
      - ${DATA_DIR}/npm/letsencrypt:/etc/letsencrypt
    networks:
      - homelab

networks:
  homelab:
    external: true
```

Default login: `admin@example.com` / `changeme`

---

## Security best practices

### Network isolation

```
                    Internet
                        │
                   ┌────┴────┐
                   │ Router  │
                   │ Firewall│
                   └────┬────┘
                        │
              ┌─────────┴─────────┐
              │                   │
        ┌─────┴─────┐       ┌─────┴─────┐
        │  Public   │       │   LAN     │
        │ Services  │       │  Only     │
        │           │       │           │
        │ Nextcloud │       │ Portainer │
        │ Jellyfin  │       │ Pi-hole   │
        │ Vaultwarden       │ Admin UIs │
        └───────────┘       └───────────┘
```

### Access control recommendations

| Service | Access Level | How |
|:---|:---|:---|
| Nextcloud | Public (with auth) | Reverse proxy + SSL |
| Jellyfin | Public or VPN | Reverse proxy or Tailscale |
| Vaultwarden | Public (with auth) | Reverse proxy + SSL (required) |
| Portainer | LAN only | No port forwarding |
| Pi-hole Admin | LAN only | No port forwarding |

### Remote access with Tailscale

For secure remote access without exposing ports:

```yaml
services:
  tailscale:
    image: tailscale/tailscale:latest
    container_name: tailscale
    hostname: homelab
    environment:
      - TS_AUTHKEY=${TAILSCALE_AUTHKEY}
      - TS_STATE_DIR=/var/lib/tailscale
      - TS_USERSPACE=false
    volumes:
      - ${DATA_DIR}/tailscale:/var/lib/tailscale
      - /dev/net/tun:/dev/net/tun
    cap_add:
      - NET_ADMIN
      - NET_RAW
    restart: unless-stopped
    networks:
      - homelab

networks:
  homelab:
    external: true
```

---

## Backup strategy

### What to back up

| Data type | Location | Priority |
|:---|:---|:---|
| Application data | `${DATA_DIR}/*` | Critical |
| Docker Compose files | `~/docker/compose/` | High |
| Environment files | `~/docker/.env` | High (encrypted) |
| Container configs | Volumes | High |

### Automated backup script

```bash
#!/bin/bash
# ~/scripts/backup-docker.sh

BACKUP_DIR="/mnt/backup/docker"
DATA_DIR="/home/user/docker"
DATE=$(date +%Y-%m-%d)

# Stop services that need consistent backups
docker compose -f ~/docker/compose/nextcloud/docker-compose.yml stop

# Create backup
tar -czf "$BACKUP_DIR/docker-data-$DATE.tar.gz" "$DATA_DIR"

# Restart services
docker compose -f ~/docker/compose/nextcloud/docker-compose.yml start

# Keep last 7 days
find "$BACKUP_DIR" -name "docker-data-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/docker-data-$DATE.tar.gz"
```

---

## Complete homelab stack

Here's a combined Docker Compose file for a full homelab setup:

```yaml
# ~/docker/compose/homelab/docker-compose.yml
# Start with: docker compose up -d
# This creates a complete self-hosted environment

services:
  # === Reverse Proxy ===
  nginx-proxy-manager:
    image: jc21/nginx-proxy-manager:latest
    container_name: npm
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "81:81"
    volumes:
      - npm-data:/data
      - npm-letsencrypt:/etc/letsencrypt
    networks:
      - homelab

  # === Password Manager ===
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    expose:
      - "80"
    environment:
      - DOMAIN=https://vault.${DOMAIN}
      - SIGNUPS_ALLOWED=false
      - ADMIN_TOKEN=${VAULTWARDEN_ADMIN_TOKEN}
    volumes:
      - vaultwarden-data:/data
    networks:
      - homelab

  # === Monitoring ===
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    restart: unless-stopped
    expose:
      - "3001"
    volumes:
      - uptime-kuma-data:/app/data
    networks:
      - homelab

  # === Container Management ===
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    expose:
      - "9443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer-data:/data
    networks:
      - homelab

volumes:
  npm-data:
  npm-letsencrypt:
  vaultwarden-data:
  uptime-kuma-data:
  portainer-data:

networks:
  homelab:
    driver: bridge
```

---

## Troubleshooting

### Common issues

| Issue | Solution |
|:---|:---|
| Permission denied on volumes | Check `USERMAP_UID`/`USERMAP_GID` match your host user |
| Port already in use | Change the host port in the compose file |
| Container can't reach another | Ensure both are on the same Docker network |
| Hardware transcoding not working | Verify device permissions and group membership |
| Slow performance | Consider SSD for container data, HDD for media |

### Useful commands

```bash
# View all running containers
docker ps

# Check container logs
docker logs -f <container_name>

# Enter container shell
docker exec -it <container_name> /bin/sh

# View resource usage
docker stats

# Restart a service
docker compose restart <service_name>

# Update all containers
docker compose pull && docker compose up -d
```

---

## Additional applications to explore

| Application | Purpose | URL |
|:---|:---|:---|
| Home Assistant | Smart home automation | homeassistant.io |
| Immich | Google Photos alternative | immich.app |
| Gitea/Forgejo | Self-hosted Git | gitea.io |
| Calibre-Web | eBook library | github.com/janeczku/calibre-web |
| Sonarr/Radarr | Media management automation | sonarr.tv / radarr.video |
| Audiobookshelf | Audiobook/podcast server | audiobookshelf.org |
| Mealie | Recipe management | mealie.io |
| Tandoor | Recipe management | docs.tandoor.dev |

---

## Summary

| Concept | Key takeaway |
|:---|:---|
| Start small | Add services incrementally; debug before expanding |
| Security | Never expose admin UIs; use VPN or reverse proxy |
| Backups | Automate backups of data volumes and compose files |
| Updates | Regularly pull new images and restart containers |
| Networking | Use a shared Docker network for inter-container communication |
| Storage | SSD for databases and configs; HDD for media is fine |

**Next Chapter:** Review your Docker learning path in **[Chapter 23: Docker basics roadmap](./chapter23-roadmap-basics.md)**.
