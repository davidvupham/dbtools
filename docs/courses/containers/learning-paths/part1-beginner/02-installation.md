# Installing Docker and Podman

> **Module:** Part 1 - Beginner | **Level:** Foundation | **Time:** 30 minutes

## Learning Objectives

By the end of this section, you will be able to:

- Install Docker on your operating system
- Install Podman on your operating system
- Configure post-installation settings
- Verify both tools are working correctly
- Understand the differences in installation requirements

---

## Installation Overview

### Platform Support

| Platform | Docker | Podman |
|----------|--------|--------|
| **Linux (native)** | Full support | Full support (best) |
| **macOS** | Via Docker Desktop or Colima | Via Podman machine |
| **Windows** | Via Docker Desktop (WSL2) | Via Podman machine (WSL2) |

### What Gets Installed

**Docker Installation:**
```
┌─────────────────────────────────────────┐
│  Docker Desktop (macOS/Windows)         │
│  ├── Docker Engine (dockerd)            │
│  ├── Docker CLI                         │
│  ├── Docker Compose                     │
│  ├── Docker Build (BuildKit)            │
│  └── containerd + runc                  │
└─────────────────────────────────────────┘
```

**Podman Installation:**
```
┌─────────────────────────────────────────┐
│  Podman                                 │
│  ├── Podman CLI                         │
│  ├── Buildah (image building)           │
│  ├── Skopeo (image operations)          │
│  └── crun/runc (container runtime)      │
└─────────────────────────────────────────┘
```

---

## Linux Installation

### Ubuntu / Debian

**Install Docker:**

```bash
# Remove old versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install prerequisites
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
sudo systemctl enable --now docker
```

**Install Podman:**

```bash
# Ubuntu 22.04+ / Debian 11+
sudo apt update
sudo apt install -y podman

# Verify installation
podman --version
```

### Fedora / RHEL / CentOS Stream

**Install Docker:**

```bash
# Remove old versions
sudo dnf remove docker docker-client docker-client-latest docker-common \
    docker-latest docker-latest-logrotate docker-logrotate docker-engine

# Add Docker repository
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

# Install Docker
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
sudo systemctl enable --now docker
```

**Install Podman:**

```bash
# Usually pre-installed on Fedora/RHEL
# If not:
sudo dnf install -y podman

# Verify
podman --version
```

### Arch Linux

```bash
# Docker
sudo pacman -S docker docker-compose
sudo systemctl enable --now docker

# Podman
sudo pacman -S podman
```

---

## macOS Installation

### Docker Desktop

**Option 1: Download from Website**
1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Download Docker Desktop for Mac
3. Open the `.dmg` file and drag to Applications
4. Launch Docker Desktop
5. Complete the setup wizard

**Option 2: Homebrew**
```bash
brew install --cask docker
```

**Post-Installation:**
```bash
# Launch Docker Desktop from Applications
# Or from terminal:
open -a Docker

# Wait for Docker to start (whale icon in menu bar)
# Then verify:
docker version
docker run hello-world
```

### Podman on macOS

Podman on macOS runs in a lightweight Linux VM.

```bash
# Install Podman
brew install podman

# Initialize the Podman machine (Linux VM)
podman machine init

# Start the machine
podman machine start

# Verify
podman version
podman run hello-world
```

**Managing the Podman Machine:**
```bash
# Check status
podman machine list

# Stop the machine
podman machine stop

# Start the machine
podman machine start

# SSH into the machine (for debugging)
podman machine ssh
```

### Alternative: Colima (Lightweight Docker Runtime)

```bash
# Install Colima (lightweight Docker alternative)
brew install colima docker

# Start Colima
colima start

# Use Docker CLI normally
docker run hello-world

# Stop when done
colima stop
```

---

## Windows Installation

### Prerequisites

1. **Windows 10/11 Pro, Enterprise, or Education** (or Home with WSL2)
2. **WSL 2 enabled** (Windows Subsystem for Linux 2)

**Enable WSL 2:**
```powershell
# Run PowerShell as Administrator
wsl --install

# Restart your computer
# After restart, set WSL 2 as default:
wsl --set-default-version 2
```

### Docker Desktop for Windows

1. Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Run the installer
3. Select "Use WSL 2 instead of Hyper-V" during installation
4. Complete setup and restart if prompted
5. Launch Docker Desktop

**Verify in PowerShell or WSL:**
```powershell
docker version
docker run hello-world
```

### Podman on Windows

**Option 1: Podman Desktop**
1. Download from [podman-desktop.io](https://podman-desktop.io/)
2. Run the installer
3. Launch Podman Desktop
4. Initialize and start the Podman machine

**Option 2: Command Line**
```powershell
# Install via winget
winget install RedHat.Podman

# Or download from GitHub releases:
# https://github.com/containers/podman/releases

# Initialize Podman machine
podman machine init

# Start Podman machine
podman machine start

# Verify
podman version
podman run hello-world
```

---

## Post-Installation Configuration

### Linux: Run Docker Without sudo

By default, Docker requires root. To run as a regular user:

```bash
# Add your user to the docker group
sudo usermod -aG docker $USER

# Apply the changes (or log out and back in)
newgrp docker

# Verify
docker run hello-world  # Should work without sudo
```

> **Security Note:** Adding users to the `docker` group grants root-equivalent privileges. In production, consider rootless Docker or use Podman instead.

### Linux: Enable Rootless Docker

For better security, run Docker without root:

```bash
# Install rootless prerequisites
sudo apt install -y uidmap dbus-user-session

# Run the rootless setup script
dockerd-rootless-setuptool.sh install

# Add to your shell profile
echo 'export PATH=/usr/bin:$PATH' >> ~/.bashrc
echo 'export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock' >> ~/.bashrc
source ~/.bashrc

# Start rootless Docker
systemctl --user enable --now docker

# Verify
docker run hello-world
```

### Podman: Enable Lingering (Linux)

For containers to persist after logout:

```bash
# Enable lingering for your user
loginctl enable-linger $USER

# Verify
loginctl show-user $USER | grep Linger
# Linger=yes
```

### Configure Subordinate UIDs (Rootless)

Podman rootless requires subordinate UIDs:

```bash
# Check current configuration
cat /etc/subuid | grep $USER
cat /etc/subgid | grep $USER

# If missing, add them (requires root)
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER

# Reset Podman storage (if already used)
podman system reset
```

---

## Verifying Installation

### Docker Verification

```bash
# Check version
docker version

# System information
docker info

# Run test container
docker run hello-world

# Run interactive container
docker run -it alpine sh
# Type 'exit' to leave

# Check running containers
docker ps

# Check all containers
docker ps -a
```

### Podman Verification

```bash
# Check version
podman version

# System information
podman info

# Run test container
podman run hello-world

# Run interactive container
podman run -it alpine sh
# Type 'exit' to leave

# Check running containers
podman ps

# Check all containers
podman ps -a
```

### Verification Checklist

| Check | Docker Command | Podman Command | Expected Result |
|-------|---------------|----------------|-----------------|
| Version | `docker version` | `podman version` | Shows client and server version |
| Hello World | `docker run hello-world` | `podman run hello-world` | "Hello from Docker!" message |
| Interactive | `docker run -it alpine sh` | `podman run -it alpine sh` | Shell prompt inside container |
| List containers | `docker ps -a` | `podman ps -a` | Shows test containers |

---

## Troubleshooting

### Docker Issues

**"Cannot connect to Docker daemon"**
```bash
# Check if Docker is running
sudo systemctl status docker

# Start Docker if stopped
sudo systemctl start docker

# If using rootless Docker, check user service
systemctl --user status docker
```

**"Permission denied" on Linux**
```bash
# Ensure you're in the docker group
groups | grep docker

# If not, add yourself
sudo usermod -aG docker $USER
newgrp docker
```

**Docker Desktop not starting (macOS/Windows)**
- Ensure virtualization is enabled in BIOS
- Check for conflicting software (VirtualBox, VMware)
- Try resetting Docker Desktop to factory defaults

### Podman Issues

**"Error: XDG_RUNTIME_DIR is not set"**
```bash
# Set the variable
export XDG_RUNTIME_DIR=/run/user/$(id -u)

# Or enable lingering
loginctl enable-linger $USER
```

**"Cannot connect to Podman" (macOS/Windows)**
```bash
# Check machine status
podman machine list

# Start if stopped
podman machine start

# If issues persist, recreate the machine
podman machine rm podman-machine-default
podman machine init
podman machine start
```

**Slow performance on macOS/Windows**
- Both Docker Desktop and Podman use VMs on these platforms
- Performance is best on native Linux
- Consider using WSL 2 on Windows for better performance

---

## Resource Allocation

### Docker Desktop Settings

Access via Docker Desktop > Settings > Resources:

| Resource | Recommended | Notes |
|----------|-------------|-------|
| **CPUs** | 2-4 | More for builds |
| **Memory** | 4-8 GB | More for larger apps |
| **Disk** | 60 GB+ | For storing images |

### Podman Machine Settings

```bash
# View current settings
podman machine inspect

# Create machine with custom resources
podman machine init --cpus 4 --memory 4096 --disk-size 60

# Modify existing machine (stop first)
podman machine stop
podman machine set --cpus 4 --memory 4096
podman machine start
```

---

## Key Takeaways

1. **Linux is the best platform** for containers (native support)
2. **macOS and Windows use VMs** to run containers
3. **Post-installation steps** (user permissions) are important
4. **Rootless mode** (default in Podman) is more secure
5. **Both tools should be installed** to follow this course effectively
6. **Verify installation** before proceeding

---

## What's Next

Now that Docker and Podman are installed, let's run our first container!

Continue to: [03-first-container.md](03-first-container.md)

---

## Quick Quiz

1. What is required to run Docker/Podman on Windows?
   - [ ] Windows XP or later
   - [x] WSL 2 (Windows Subsystem for Linux 2)
   - [ ] Hyper-V only
   - [ ] A separate Linux computer

2. Why should you add your user to the `docker` group on Linux?
   - [ ] It makes Docker faster
   - [ ] It's required for Docker to work
   - [x] It allows running Docker commands without sudo
   - [ ] It enables rootless mode

3. What does `podman machine` do on macOS/Windows?
   - [ ] Converts the Mac into a Linux machine
   - [x] Manages a lightweight Linux VM for running containers
   - [ ] Installs Podman on Linux
   - [ ] Creates container images

4. Which command verifies Docker is working correctly?
   - [ ] `docker check`
   - [ ] `docker test`
   - [x] `docker run hello-world`
   - [ ] `docker verify`

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Introduction](01-introduction.md) | [Part 1 Overview](../../course_overview.md#part-1-beginner) | [First Container](03-first-container.md) |
