# Docker Roadmap Essentials

## Note
This file is part of the 6-Month DevOps Roadmap. For deep dives, verify the existing chapters 1-21 in this directory.

## Container vs Virtual Machine
- **VM**: Hardware virtualization, heavy OS overhead.
- **Container**: OS virtualization, shares kernel, lightweight.

## Docker Architecture
- **Daemon**: Background service.
- **Client**: CLI tool (`docker`).
- **Registry**: Store for images (Docker Hub).

## Basic Commands
- `docker run -d -p 80:80 nginx`: Run Nginx.
- `docker ps`: List running containers.
- `docker images`: List images.
- `docker stop <id>`: Stop container.

## Dockerfile
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```
