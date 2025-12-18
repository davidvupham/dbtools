# Platform-Specific Guide for Dev Containers

This guide covers platform-specific setup, optimizations, and troubleshooting for using dev containers with VS Code on different operating systems.

## Table of Contents

- [WSL2 (Windows Subsystem for Linux)](#wsl2-windows-subsystem-for-linux)
- [macOS](#macos)
- [Linux](#linux)
- [Performance Optimization](#performance-optimization)
- [Common Issues](#common-issues)

## WSL2 (Windows Subsystem for Linux)

### Prerequisites

1. **Windows 10/11** (Build 19041 or higher)
2. **WSL2** installed and configured
3. **Docker Desktop for Windows** with WSL2 backend
4. **VS Code** with Remote - WSL extension

### Setup Instructions

#### 1. Enable WSL2

```powershell
# Run in PowerShell as Administrator
wsl --install

# Or manually enable features
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Set WSL2 as default
wsl --set-default-version 2
```

#### 2. Install a Linux Distribution

```powershell
# List available distributions
wsl --list --online

# Install Ubuntu (recommended)
wsl --install -d Ubuntu-22.04
```

#### 3. Configure Docker Desktop

1. Open **Docker Desktop Settings**
2. Go to **General** → Enable "Use the WSL 2 based engine"
3. Go to **Resources → WSL Integration** → Enable integration with your Ubuntu distribution
4. Click **Apply & Restart**

#### 4. Clone Repository in WSL2

**Important**: Clone the repository inside WSL2 filesystem for best performance.

```bash
# Open WSL2 terminal
wsl

# Clone in WSL2 home directory (NOT /mnt/c/)
cd ~
git clone https://github.com/yourusername/dbtools.git
cd dbtools

# Open in VS Code
code .
```

### WSL2 Best Practices

#### ✅ DO

- **Clone repos in WSL2 filesystem** (`~/projects`, not `/mnt/c/`)
- **Store Docker volumes in WSL2** filesystem
- **Use WSL2 terminal** for git operations
- **Access files via `\\wsl$\Ubuntu\home\username\` from Windows**

#### ❌ DON'T

- **Don't clone in `/mnt/c/` (Windows filesystem)** - extremely slow
- **Don't edit WSL files with Windows applications** directly
- **Don't store large datasets on Windows filesystem**

### Performance Optimization for WSL2

#### 1. Configure WSL2 Memory and CPU

Create or edit `%USERPROFILE%\.wslconfig`:

```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true

# Disable GUI features if not needed
guiApplications=false
```

Apply changes:

```powershell
wsl --shutdown
```

#### 2. Docker Desktop Settings

- **Memory**: Allocate 6-8GB (in Docker Desktop → Resources)
- **CPU**: Allocate at least 4 cores
- **Disk image size**: Increase if needed (default 256GB)

#### 3. File System Performance

```bash
# Check filesystem type (should be ext4, not 9p/drvfs)
df -T ~/dbtools
# Should show ext4, not 9p or drvfs

# Avoid these slow paths:
# /mnt/c/ - Windows C: drive (9p filesystem, very slow)
# /mnt/d/ - Windows D: drive (9p filesystem, very slow)

# Use these fast paths:
# /home/username/ - WSL2 native filesystem (ext4, fast)
# ~ - Your WSL2 home directory
```

### WSL2-Specific Issues

#### Issue: Port Already in Use

Windows and WSL2 share the same ports. Check conflicts:

```powershell
# Windows: Check what's using a port
netstat -ano | findstr :5432

# WSL2: Check what's using a port
sudo lsof -i :5432
```

#### Issue: Docker Desktop Not Starting

```powershell
# Restart WSL
wsl --shutdown
# Wait 8 seconds
# Restart Docker Desktop

# If issues persist, reset WSL
wsl --unregister Ubuntu-22.04
# Then reinstall Ubuntu
```

#### Issue: DNS Resolution Problems

Add to `/etc/wsl.conf` in WSL2:

```ini
[network]
generateResolvConf = false
```

Then create `/etc/resolv.conf`:

```
nameserver 8.8.8.8
nameserver 8.8.4.4
```

#### Issue: Clock Drift

WSL2 clock can drift when Windows sleeps:

```bash
# Sync clock manually
sudo hwclock -s

# Add to ~/.bashrc for auto-sync
if [ $(date +%s) -ne $(date -r /proc/1/stat +%s) ]; then
    sudo hwclock -s
fi
```

### Accessing Databases from Windows

When databases run in WSL2 containers:

```
# Access from Windows applications
Host: localhost
Port: 5432 (or forwarded port)

# WSL2 automatically forwards ports to Windows
```

### File Permissions

```bash
# Set correct permissions for SSH keys
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# Set correct ownership
sudo chown -R $USER:$USER ~/dbtools
```

## macOS

### Prerequisites

1. **macOS 11.0 (Big Sur) or later**
2. **Docker Desktop for Mac**
3. **VS Code**
4. **Homebrew** (optional but recommended)

### Setup Instructions

#### 1. Install Docker Desktop

```bash
# Using Homebrew (recommended)
brew install --cask docker

# Or download from https://www.docker.com/products/docker-desktop
```

Start Docker Desktop from Applications.

#### 2. Install VS Code

```bash
# Using Homebrew
brew install --cask visual-studio-code

# Install extensions
code --install-extension ms-vscode-remote.remote-containers
code --install-extension ms-python.python
```

#### 3. Clone and Open Repository

```bash
cd ~/Projects
git clone https://github.com/yourusername/dbtools.git
cd dbtools
code .
```

### macOS Best Practices

#### Apple Silicon (M1/M2/M3) Considerations

The dev container uses `linux/amd64` architecture by default. For Apple Silicon:

**Option 1: Use ARM64 native images (faster)**

Add to `devcontainer.json`:

```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": "..",
    "args": {
      "PYTHON_VERSION": "3.13",
      "CONDA_ENV_NAME": "gds"
    },
    "platform": "linux/arm64"
  }
}
```

**Option 2: Use Rosetta 2 for x86_64 compatibility**

Keep default settings, Docker will use Rosetta 2 translation.

#### Performance Optimization for macOS

1. **Docker Desktop Settings**
   - Open Docker Desktop → Settings
   - **Resources → Advanced**:
     - CPUs: 4-6 cores
     - Memory: 8-12 GB
     - Swap: 2 GB
     - Disk image size: Increase if needed

2. **File Sharing**
   - Docker Desktop → Settings → Resources → File sharing
   - Only share necessary directories
   - Avoid sharing entire home directory

3. **Use Volumes for Data**

```json
{
  "mounts": [
    "source=dbtools-data,target=/data,type=volume"
  ]
}
```

Volumes are faster than bind mounts on macOS.

1. **Enable VirtioFS** (Docker Desktop 4.6+)

   - Settings → General → "Enable VirtioFS accelerated directory sharing"
   - Significantly improves file system performance

### macOS-Specific Issues

#### Issue: File System Slow Performance

```bash
# Use named volumes instead of bind mounts for frequently accessed files
# In devcontainer.json:
"mounts": [
  "source=node_modules,target=/workspaces/dbtools/node_modules,type=volume"
]
```

#### Issue: Port Conflicts

```bash
# Check what's using a port
sudo lsof -i :5432

# Kill process if needed
sudo kill -9 <PID>
```

#### Issue: Docker Desktop Memory Pressure

```bash
# Monitor Docker memory usage
docker stats

# Prune unused resources
docker system prune -a --volumes
```

#### Issue: Slow Git Operations

```bash
# Disable fsmonitor on macOS for better performance in containers
git config --global core.fsmonitor false
git config --global core.untrackedcache true
```

### File Permissions on macOS

macOS handles permissions differently:

```bash
# SSH keys
chmod 600 ~/.ssh/id_rsa

# Git config
chmod 644 ~/.gitconfig
```

## Linux

### Prerequisites

1. **Docker** (not Docker Desktop)
2. **VS Code**
3. **Git**

### Setup Instructions

#### 1. Install Docker

**Ubuntu/Debian:**

```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

**Fedora/RHEL/CentOS:**

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
```

#### 2. Configure Docker for Non-Root User

```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker

# Test
docker run hello-world
```

#### 3. Install VS Code

**Ubuntu/Debian:**

```bash
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update
sudo apt install code
```

**Fedora:**

```bash
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
sudo dnf install code
```

### Linux Best Practices

#### Storage Drivers

Check Docker storage driver:

```bash
docker info | grep "Storage Driver"
```

Recommended: `overlay2` (default on most modern systems)

#### SELinux Considerations (Fedora/RHEL/CentOS)

If using SELinux:

```bash
# Check SELinux status
getenforce

# If Enforcing, ensure container_t has proper permissions
sudo semanage fcontext -a -t container_file_t "/path/to/dbtools(/.*)?"
sudo restorecon -R /path/to/dbtools
```

Or add `:z` to mounts in devcontainer.json:

```json
{
  "mounts": [
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached,readonly,z"
  ]
}
```

#### AppArmor Considerations (Ubuntu)

Docker uses AppArmor by default on Ubuntu. Usually no configuration needed, but if issues:

```bash
# Check AppArmor status
sudo aa-status

# View Docker profiles
sudo aa-status | grep docker
```

### Performance Optimization for Linux

Linux has the best dev container performance (native Docker).

#### Optimize Docker Daemon

Edit `/etc/docker/daemon.json`:

```json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

#### Use tmpfs for Temporary Data

In devcontainer.json:

```json
{
  "mounts": [
    "type=tmpfs,target=/tmp,tmpfs-size=2G"
  ]
}
```

### Linux-Specific Issues

#### Issue: Permission Denied

```bash
# Ensure user is in docker group
groups | grep docker

# If not, add and re-login
sudo usermod -aG docker $USER
```

#### Issue: Docker Socket Permissions

```bash
# Check socket permissions
ls -la /var/run/docker.sock

# Fix if needed
sudo chmod 666 /var/run/docker.sock
```

#### Issue: Out of Disk Space

```bash
# Check Docker disk usage
docker system df

# Clean up
docker system prune -a --volumes

# Check filesystem
df -h
```

#### Issue: Network Problems

```bash
# Restart Docker network
sudo systemctl restart docker

# Or reset Docker network
docker network prune
```

## Performance Optimization

### General Performance Tips

#### 1. Exclude Unnecessary Files

Add to `.dockerignore`:

```
__pycache__
*.pyc
.git
.vscode
node_modules
.pytest_cache
htmlcov
*.log
```

#### 2. Use BuildKit

Enable Docker BuildKit for faster builds:

```bash
# In devcontainer.json
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": "..",
    "options": ["--progress=plain"]
  },
  "containerEnv": {
    "DOCKER_BUILDKIT": "1"
  }
}
```

#### 3. Layer Caching

Optimize Dockerfile layer order (least to most frequently changed):

```dockerfile
# System packages (rarely change)
RUN apt-get update && apt-get install -y ...

# Python environment (occasionally changes)
RUN conda create -n gds python=3.13 -y

# Python packages (occasionally change)
RUN pip install -e ".[devcontainer]"

# Copy code (frequently changes)
COPY . /workspaces/dbtools
```

#### 4. Use Multi-Stage Builds

```dockerfile
# Build stage
FROM mcr.microsoft.com/devcontainers/miniconda:latest as builder
RUN conda create -n gds python=3.13 -y
RUN conda install -n gds -c conda-forge pyodbc -y

# Final stage
FROM mcr.microsoft.com/devcontainers/miniconda:latest
COPY --from=builder /opt/conda/envs/gds /opt/conda/envs/gds
```

### Benchmarking Performance

#### Test File I/O Speed

```bash
# Write test
dd if=/dev/zero of=/tmp/testfile bs=1M count=1024 oflag=direct

# Read test
dd if=/tmp/testfile of=/dev/null bs=1M iflag=direct

# Clean up
rm /tmp/testfile
```

#### Test Container Start Time

```bash
time docker run --rm mcr.microsoft.com/devcontainers/miniconda:latest echo "Hello"
```

## Common Issues

### Issue: Extension Host Performance

```json
// In settings.json
{
  "extensions.autoUpdate": false,
  "extensions.autoCheckUpdates": false,
  "search.followSymlinks": false,
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/node_modules/**": true,
    "**/.hg/store/**": true,
    "**/__pycache__/**": true,
    "**/.pytest_cache/**": true
  }
}
```

### Issue: Out of Memory

Increase Docker memory limits per platform instructions above.

Monitor container memory:

```bash
docker stats
```

### Issue: Slow Network

Test network speed:

```bash
# Inside container
curl -o /dev/null -s -w "Download: %{speed_download} bytes/sec\n" https://speed.cloudflare.com/__down?bytes=100000000
```

### Issue: Time Synchronization

```bash
# Check time in container
date

# Sync with host (if needed)
docker run --rm --privileged alpine hwclock -s
```

## Platform Comparison

| Feature | WSL2 | macOS | Linux |
|---------|------|-------|-------|
| Performance | Good | Good | Excellent |
| File I/O | Fast (in WSL2 FS) | Medium | Fast |
| Integration | Excellent | Good | Native |
| Setup Complexity | Medium | Easy | Medium |
| Resource Usage | Shared with Windows | Isolated VM | Native |
| Best For | Windows users | Mac users | Servers, CI/CD |

## Conclusion

- **WSL2**: Best for Windows developers, but requires careful filesystem management
- **macOS**: Great for Mac users, use Apple Silicon native images when possible
- **Linux**: Best overall performance and integration

Choose your platform based on your primary OS and optimize according to the guidelines above.
