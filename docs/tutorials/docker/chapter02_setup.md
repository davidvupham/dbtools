# Chapter 2: Setting Up Your Docker Environment

## Introduction

Before you can start using Docker, you need to install and configure it on your system. This chapter provides detailed, step-by-step instructions for **Linux**, **macOS**, and **Windows**, plus verification steps, troubleshooting tips, and optional configuration for advanced users.

**What you'll learn**:
- How to install Docker on your operating system
- How to verify your installation works correctly
- How to configure Docker for your workflow
- Common installation issues and solutions
- Setting up credentials for registries

## Quick Decision Guide

**Choose your installation method**:

| Operating System | Installation Method | Best For |
|-----------------|---------------------|----------|
| **Linux** | Docker Engine | Servers, production, lightweight |
| **macOS** | Docker Desktop | Development on Mac |
| **Windows 10/11 Pro** | Docker Desktop (WSL2) | Development on Windows |
| **Windows 10 Home** | Docker Desktop (WSL2) | Development on Windows |
| **All platforms** | Docker in VM | Learning, isolation |

---

## Installing Docker on Linux

### Ubuntu / Debian

**Step 1: Remove old versions (if any)**

```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

**Step 2: Update package index and install prerequisites**

```bash
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

**Step 3: Add Docker's official GPG key**

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

**Step 4: Set up the repository**

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

**Step 5: Install Docker Engine**

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin
```

**Step 6: Verify installation**

```bash
sudo docker run hello-world
```

You should see:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

**Step 7: Add your user to the docker group (recommended)**

This allows you to run Docker commands without `sudo`:

```bash
# Add your user to the docker group
sudo usermod -aG docker $USER

# Apply the new group membership
newgrp docker

# Verify you can run docker without sudo
docker run hello-world
```

**⚠️ Important**: After adding yourself to the docker group, you may need to:
1. Log out and log back in, OR
2. Run `newgrp docker` in your terminal, OR
3. Restart your system

**Step 8: Enable Docker to start on boot**

```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```

### CentOS / RHEL / Fedora

**Step 1: Remove old versions**

```bash
sudo yum remove docker \
    docker-client \
    docker-client-latest \
    docker-common \
    docker-latest \
    docker-latest-logrotate \
    docker-logrotate \
    docker-engine
```

**Step 2: Install yum-utils and add Docker repository**

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
```

**Step 3: Install Docker Engine**

```bash
sudo yum install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin
```

**Step 4: Start Docker**

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

**Step 5: Add user to docker group**

```bash
sudo usermod -aG docker $USER
newgrp docker
```

**Step 6: Verify**

```bash
docker run hello-world
```

### Arch Linux

```bash
# Install Docker
sudo pacman -S docker docker-compose

# Start and enable Docker service
sudo systemctl start docker.service
sudo systemctl enable docker.service

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker run hello-world
```

---

## Installing Docker on macOS

**Docker Desktop for Mac** is the recommended way to run Docker on macOS. It includes:
- Docker Engine
- Docker CLI
- Docker Compose
- Kubernetes (optional)
- GUI for managing containers

### Requirements

- macOS 11 or newer
- At least 4GB of RAM
- Intel chip or Apple Silicon (M1/M2/M3)

### Installation Steps

**Step 1: Download Docker Desktop**

Visit: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

- For **Intel Macs**: Download "Docker Desktop for Mac (Intel chip)"
- For **Apple Silicon (M1/M2/M3)**: Download "Docker Desktop for Mac (Apple chip)"

**Step 2: Install**

1. Open the `.dmg` file you downloaded
2. Drag the Docker icon to your Applications folder
3. Open Docker from Applications
4. Grant necessary permissions when prompted (privileged helper, networking)

**Step 3: Wait for Docker to start**

- Docker icon appears in the menu bar (whale icon)
- Wait for it to show "Docker Desktop is running"
- First start may take a few minutes

**Step 4: Verify installation**

Open Terminal and run:

```bash
docker version
docker run hello-world
```

### Configuration (macOS)

**Access settings**: Click the Docker whale icon in menu bar → Settings

**Recommended settings**:

1. **Resources → Advanced**:
   - CPUs: 4-6 cores (adjust based on your system)
   - Memory: 8GB minimum, 16GB recommended for heavy workloads
   - Swap: 1-2GB
   - Disk image size: 64GB (can be increased later)

2. **General**:
   - ✓ Start Docker Desktop when you log in (optional, but convenient)
   - ✓ Use Docker Compose V2

3. **Docker Engine**:
   - Default configuration is usually fine

**Performance tip**: Docker Desktop on Mac uses a VM under the hood. File operations (especially bind mounts) can be slower than native Linux. For performance-critical work, consider:
- Using named volumes instead of bind mounts
- Using Docker Sync for file synchronization
- Developing inside a container (Dev Containers)

---

## Installing Docker on Windows

**Docker Desktop for Windows** runs Docker in a lightweight VM using WSL2 (Windows Subsystem for Linux).

### Requirements

- Windows 10 64-bit: Home, Pro, Enterprise, or Education version 21H2 or higher
- Windows 11 64-bit: Home, Pro, Enterprise, or Education version 21H2 or higher
- WSL2 feature enabled
- BIOS-level hardware virtualization enabled
- At least 4GB RAM

### Installation Steps

**Step 1: Enable WSL2**

Open PowerShell as Administrator and run:

```powershell
# Enable WSL
wsl --install

# This will:
# 1. Enable WSL
# 2. Install Ubuntu as default Linux distribution
# 3. Require a restart
```

After restart, open Ubuntu from the Start menu and complete the initial setup (create username/password).

**Step 2: Download Docker Desktop**

Visit: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

Download "Docker Desktop for Windows"

**Step 3: Install Docker Desktop**

1. Run the installer
2. **Important**: Ensure "Use WSL 2 instead of Hyper-V" is checked
3. Follow the installation wizard
4. Restart your computer when prompted

**Step 4: Start Docker Desktop**

1. Launch Docker Desktop from Start menu
2. Accept the service agreement
3. Wait for Docker to start (may take a few minutes on first launch)
4. Docker icon appears in system tray

**Step 5: Verify installation**

Open PowerShell or Command Prompt:

```powershell
docker version
docker run hello-world
```

Or open your WSL Ubuntu terminal:

```bash
docker version
docker run hello-world
```

### Configuration (Windows)

**Access settings**: Right-click Docker icon in system tray → Settings

**Recommended settings**:

1. **General**:
   - ✓ Use the WSL 2 based engine
   - ✓ Start Docker Desktop when you log in

2. **Resources → WSL Integration**:
   - ✓ Enable integration with my default WSL distro
   - ✓ Enable integration with additional distros (Ubuntu, Debian, etc.)

3. **Resources → Advanced**:
   - CPUs: 4-6 cores
   - Memory: 8GB
   - Swap: 1-2GB
   - Disk image size: 64GB

**Using Docker from WSL2 (Recommended for development)**:

```bash
# Open your WSL2 Ubuntu terminal
# Docker commands work natively here!
docker run -it ubuntu:latest bash
```

**Using Docker from PowerShell/CMD**:

```powershell
# Works from Windows terminals too
docker run -it ubuntu:latest bash
```

### Troubleshooting Windows

**Issue**: "WSL 2 installation is incomplete"

**Solution**:
```powershell
# Update WSL
wsl --update

# Check WSL version
wsl --list --verbose
```

**Issue**: "Hardware assisted virtualization and data execution protection must be enabled in the BIOS"

**Solution**:
1. Restart computer
2. Enter BIOS/UEFI (usually F2, F10, F12, or Del key during boot)
3. Find virtualization settings (Intel VT-x, AMD-V, SVM)
4. Enable virtualization
5. Save and exit

**Issue**: Docker Desktop won't start

**Solution**:
```powershell
# Restart WSL
wsl --shutdown

# Restart Docker Desktop
# Then try again
```

---

## Verifying Your Installation

After installing on any platform, verify everything works:

### 1. Check Docker Version

```bash
docker version
```

**Expected output** (versions may differ):
```
Client:
 Version:           24.0.7
 API version:       1.43
 Go version:        go1.20.10
 Git commit:        afdd53b
 Built:             Thu Oct 26 09:08:44 2023
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          24.0.7
  API version:      1.43 (minimum version 1.12)
  Go version:       go1.20.10
  Git commit:       311b9ff
  Built:            Thu Oct 26 09:08:44 2023
  OS/Arch:          linux/amd64
  Experimental:     false
```

**What this tells you**:
- **Client version**: The `docker` CLI tool version
- **Server version**: The Docker Engine (daemon) version
- **API version**: How client and server communicate
- **OS/Arch**: Your system architecture

**⚠️ If you only see Client info**: The Docker daemon isn't running. Try:
```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Restart Docker Desktop from GUI
```

### 2. Check System Info

```bash
docker info
```

**Key information** to look for:
```
Server:
 Containers: 0
  Running: 0
  Paused: 0
  Stopped: 0
 Images: 0
 Server Version: 24.0.7
 Storage Driver: overlay2
 Cgroup Driver: systemd
 Logging Driver: json-file
 Cgroup Version: 2
 Plugins:
  Volume: local
  Network: bridge host ipvlan macvlan null overlay
  Log: awslogs fluentd gcplogs gelf journald json-file local logentries splunk syslog
```

**Important fields**:
- **Storage Driver**: Should be `overlay2` (most common)
- **Cgroup Driver**: Should be `systemd` on modern Linux
- **Containers/Images**: Shows current count
- **Plugins**: Available drivers for volumes, networks, logging

### 3. Run Test Container

```bash
# Run hello-world
docker run hello-world

# Run a more interactive test
docker run -it --rm alpine:latest sh
# Try: ls, pwd, whoami, cat /etc/os-release
# Type 'exit' to leave

# Run a web server test
docker run -d --name nginx-test -p 8080:80 nginx:alpine
# Visit http://localhost:8080 in your browser
# Should see nginx welcome page

# Clean up
docker stop nginx-test
docker rm nginx-test
```

### 4. Test Docker Compose

```bash
# Check Docker Compose is installed
docker compose version

# Expected output:
# Docker Compose version v2.23.0
```

**Create a simple test** (optional):

```bash
# Create a test directory
mkdir -p ~/docker-test && cd ~/docker-test

# Create a simple compose file
cat > docker-compose.yml << 'EOF'
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
  redis:
    image: redis:alpine
EOF

# Start services
docker compose up -d

# Check they're running
docker compose ps

# Test
curl http://localhost:8080

# Clean up
docker compose down
cd ~ && rm -rf ~/docker-test
```

---

## Post-Installation Configuration

### 1. Configure Docker to Start on Boot

**Linux**:
```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```

**macOS/Windows**: Docker Desktop has a setting:
- Settings → General → "Start Docker Desktop when you log in"

### 2. Configure Docker Daemon (Advanced)

Docker daemon configuration is in `/etc/docker/daemon.json` (Linux) or Docker Desktop settings (Mac/Windows).

**Example configuration** (`/etc/docker/daemon.json`):

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-address-pools": [
    {
      "base": "172.17.0.0/16",
      "size": 24
    }
  ],
  "storage-driver": "overlay2",
  "features": {
    "buildkit": true
  }
}
```

**What these settings do**:
- **log-driver**: How container logs are stored
- **log-opts**: Log rotation (prevent logs from filling disk)
- **default-address-pools**: IP ranges for Docker networks
- **storage-driver**: File system driver (overlay2 is recommended)
- **buildkit**: Enable BuildKit for faster, better builds

**Apply changes** (Linux):
```bash
sudo systemctl restart docker
```

**Apply changes** (Docker Desktop):
- Settings → Docker Engine → Edit JSON → Apply & Restart

### 3. Enable BuildKit (Recommended)

BuildKit is Docker's improved build system. Enable it:

**Option 1: Environment variable (per-command)**:
```bash
DOCKER_BUILDKIT=1 docker build -t myapp .
```

**Option 2: Set permanently**:

**Linux/macOS** (add to `~/.bashrc` or `~/.zshrc`):
```bash
export DOCKER_BUILDKIT=1
```

**Windows PowerShell** (add to profile):
```powershell
$env:DOCKER_BUILDKIT=1
```

**Option 3: Daemon configuration**:
Add to `daemon.json`:
```json
{
  "features": {
    "buildkit": true
  }
}
```

### 4. Install Docker Buildx (Extended Build Features)

Buildx enables multi-platform builds and is now included by default with Docker Desktop and modern Docker installations.

**Verify it's installed**:
```bash
docker buildx version
```

**Create a buildx builder** (optional, for multi-arch builds):
```bash
# Create a new builder instance
docker buildx create --name mybuilder --use --bootstrap

# Verify
docker buildx inspect mybuilder
```

---

## Configuring Registry Access

To push/pull images from registries, you need to authenticate.

### Docker Hub

**Sign up**: [https://hub.docker.com](https://hub.docker.com)

**Login from CLI**:
```bash
docker login

# Enter your Docker Hub username and password
# Credentials are stored in ~/.docker/config.json
```

**Verify**:
```bash
# Pull from Docker Hub (no prefix needed)
docker pull alpine:latest

# Tag and push your own image
docker tag myapp:latest YOUR_USERNAME/myapp:latest
docker push YOUR_USERNAME/myapp:latest
```

### GitHub Container Registry (GHCR)

**Step 1: Create a Personal Access Token (PAT)**
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `write:packages`, `read:packages`, `delete:packages`
4. Copy the token

**Step 2: Login**:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

**Step 3: Use GHCR**:
```bash
# Tag for GHCR (format: ghcr.io/USERNAME/IMAGE:TAG)
docker tag myapp:latest ghcr.io/YOUR_USERNAME/myapp:latest

# Push
docker push ghcr.io/YOUR_USERNAME/myapp:latest

# Pull
docker pull ghcr.io/YOUR_USERNAME/myapp:latest
```

### JFrog Artifactory (Preview)

We'll cover JFrog in detail in Chapter 21, but here's a quick setup:

**Login to JFrog Artifactory**:
```bash
docker login mycompany.jfrog.io

# Or with credentials
echo $JFROG_PASSWORD | docker login mycompany.jfrog.io -u $JFROG_USERNAME --password-stdin
```

**Use JFrog as registry**:
```bash
# Format: JFROG_DOMAIN/REPO_NAME/IMAGE:TAG
docker pull mycompany.jfrog.io/docker-local/alpine:latest
docker push mycompany.jfrog.io/docker-local/myapp:v1.0
```

### AWS ECR, GCR, ACR

**AWS ECR**:
```bash
# Authenticate (requires AWS CLI)
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    123456789012.dkr.ecr.us-east-1.amazonaws.com

# Use ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
```

**Google GCR**:
```bash
# Authenticate (requires gcloud CLI)
gcloud auth configure-docker

# Use GCR
docker push gcr.io/PROJECT_ID/myapp:latest
```

**Azure ACR**:
```bash
# Authenticate (requires Azure CLI)
az acr login --name myregistry

# Use ACR
docker push myregistry.azurecr.io/myapp:latest
```

---

## Credential Helpers (Secure Credential Storage)

By default, Docker stores credentials in `~/.docker/config.json` in base64 (not secure!).

**Credential helpers** securely store credentials in your OS keychain.

### Linux: pass

```bash
# Install pass
sudo apt-get install pass gnupg2

# Initialize pass
gpg --generate-key
pass init YOUR_GPG_KEY_ID

# Configure Docker to use pass
echo '{"credsStore": "pass"}' > ~/.docker/config.json
```

### macOS: osxkeychain

**Built-in with Docker Desktop**. Verify:

```bash
cat ~/.docker/config.json
```

Should contain:
```json
{
  "credsStore": "osxkeychain"
}
```

### Windows: wincred

**Built-in with Docker Desktop**. Verify:

```powershell
cat ~/.docker/config.json
```

Should contain:
```json
{
  "credsStore": "wincred"
}
```

---

## Common Issues and Solutions

### Issue: "Permission denied" when running Docker commands (Linux)

**Symptom**:
```
Got permission denied while trying to connect to the Docker daemon socket
```

**Solutions**:
```bash
# Solution 1: Add user to docker group (recommended)
sudo usermod -aG docker $USER
newgrp docker

# Solution 2: Use sudo (not recommended for regular use)
sudo docker run hello-world

# Solution 3: Change socket permissions (not recommended)
sudo chmod 666 /var/run/docker.sock
```

### Issue: Docker daemon won't start (Linux)

**Check status**:
```bash
sudo systemctl status docker
```

**Common fixes**:
```bash
# Restart Docker service
sudo systemctl restart docker

# Check logs
sudo journalctl -u docker -n 50 --no-pager

# Check Docker daemon directly
sudo dockerd --debug
```

**Possible causes**:
- Conflicting virtualization software
- Corrupted Docker configuration
- Disk space issues
- Port conflicts

### Issue: "Cannot connect to the Docker daemon" (All platforms)

**macOS/Windows**:
- Ensure Docker Desktop is running (check system tray)
- Restart Docker Desktop
- Check Docker Desktop → Troubleshoot → Reset to factory defaults

**Linux**:
```bash
# Check if daemon is running
sudo systemctl status docker

# Start daemon
sudo systemctl start docker
```

### Issue: Slow performance (macOS/Windows)

**Causes**:
- Bind mounts are slower on macOS/Windows due to file system translation

**Solutions**:
1. **Use named volumes** instead of bind mounts:
   ```bash
   # Slow (bind mount)
   docker run -v $(pwd):/app myapp

   # Faster (named volume)
   docker run -v mydata:/app myapp
   ```

2. **Increase resources**: Docker Desktop → Settings → Resources
   - More CPUs
   - More memory
   - Faster disk

3. **Use Dev Containers**: Develop inside a container

4. **Use Docker Sync** (macOS): [https://docker-sync.io/](https://docker-sync.io/)

### Issue: "No space left on device"

**Check disk usage**:
```bash
docker system df
```

**Clean up**:
```bash
# Remove unused containers, networks, images
docker system prune

# Remove everything (including volumes)
docker system prune -a --volumes

# Be specific
docker container prune   # Remove stopped containers
docker image prune -a    # Remove unused images
docker volume prune      # Remove unused volumes
```

### Issue: Port already in use

**Symptom**:
```
Error starting userland proxy: listen tcp 0.0.0.0:8080: bind: address already in use
```

**Solutions**:
```bash
# Find what's using the port
sudo lsof -i :8080  # Linux/macOS
netstat -ano | findstr :8080  # Windows

# Use a different port
docker run -p 8081:80 nginx:alpine

# Stop the conflicting service
# Then retry
```

---

## Testing Your Setup

Run this comprehensive test to ensure everything works:

```bash
#!/bin/bash
# Docker Installation Test Script

echo "=== Docker Installation Test ==="

echo -e "\n1. Checking Docker version..."
docker version || exit 1

echo -e "\n2. Checking Docker info..."
docker info | head -n 10 || exit 1

echo -e "\n3. Running hello-world..."
docker run --rm hello-world || exit 1

echo -e "\n4. Running interactive Alpine..."
docker run --rm alpine:latest echo "Alpine works!" || exit 1

echo -e "\n5. Testing port mapping..."
docker run -d --name test-nginx -p 18080:80 nginx:alpine || exit 1
sleep 2
curl -s http://localhost:18080 > /dev/null && echo "Port mapping works!" || echo "Port mapping failed!"
docker stop test-nginx && docker rm test-nginx

echo -e "\n6. Testing Docker Compose..."
docker compose version || exit 1

echo -e "\n7. Testing BuildKit..."
export DOCKER_BUILDKIT=1
echo "FROM alpine:latest" | docker build -t test-buildkit - || exit 1
docker rmi test-buildkit

echo -e "\n8. Checking disk space..."
docker system df

echo -e "\n=== All tests passed! ==="
```

Save this as `test-docker.sh`, make it executable (`chmod +x test-docker.sh`), and run it.

---

## Summary

You've learned how to:

✅ Install Docker on **Linux**, **macOS**, and **Windows**
✅ Verify your installation works correctly
✅ Configure Docker daemon and BuildKit
✅ Set up registry authentication (Docker Hub, GHCR, JFrog, etc.)
✅ Use credential helpers for secure storage
✅ Troubleshoot common installation issues
✅ Test your Docker setup comprehensively

**Recommended next steps**:
1. Ensure Docker is installed and working
2. Create a Docker Hub account (free)
3. Practice the verification commands
4. Explore Docker Desktop (if using Mac/Windows)

---

**Next Chapter**: [Chapter 3: CLI Essentials and First Run](./chapter03_cli_essentials.md)
