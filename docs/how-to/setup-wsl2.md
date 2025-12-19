# Set Up WSL2 (Windows Subsystem for Linux) for dbtools Development

This guide is for developers who will use **their own personal WSL2 instance** to work on this repo.

For general VS Code + dev container guidance (including platform-specific details), see:

- [docs/development/vscode/README.md](../development/vscode/README.md)
- [docs/development/vscode/platform-specific.md](../development/vscode/platform-specific.md)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1 — Install WSL2](#step-1--install-wsl2)
- [Step 2 — Install a Linux distribution](#step-2--install-a-linux-distribution)
- [Step 3 — Update Linux packages](#step-3--update-linux-packages)
- [Step 3.1 — Create /data (owned by you)](#step-31--create-data-owned-by-you)
- [Step 3.2 — Install Docker (latest)](#step-32--install-docker-latest)
- [Step 4 — Install VS Code + Remote WSL](#step-4--install-vs-code--remote-wsl)
- [Step 5 — Configure Docker Desktop for WSL2](#step-5--configure-docker-desktop-for-wsl2)
- [Step 6 — Create an SSH key (for GitHub)](#step-6--create-an-ssh-key-for-github)
- [Step 7 — Create ~/src and clone GitHub repos](#step-7--create-src-and-clone-github-repos)
- [Step 8 — Open in Dev Container](#step-8--open-in-dev-container)
- [Step 9 — Verify the environment](#step-9--verify-the-environment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Windows 10/11 with WSL2 support
- No local admin rights required on your machine (expected)
- Docker Desktop installed (recommended for dev containers)
- GitHub access (SSH or HTTPS)

### ServiceNow request (required in managed environments)

In many corporate environments, developers do **not** have admin rights to install or enable WSL2.

Before continuing, submit a ServiceNow request to have IT install/enable the following:

- **Windows Subsystem for Linux (WSL)** feature
- **Virtual Machine Platform** feature
- **WSL2** set as the default version
- A Linux distribution (typically **Ubuntu 22.04**)
- **Docker Desktop** with **WSL2 backend** enabled
- (If applicable) Any required corporate proxy/registry configuration

Once the request is completed, continue with the steps below.

## Step 1 — Install WSL2

Run in **PowerShell as Administrator**:

```powershell
wsl --install
wsl --set-default-version 2
```

If your organization requires manual enablement, follow the WSL2 section in:

- [docs/development/vscode/platform-specific.md](../development/vscode/platform-specific.md)

## Step 2 — Install a Linux distribution

List available distros:

```powershell
wsl --list --online
```

Install Ubuntu (recommended):

```powershell
wsl --install -d Ubuntu-22.04
```

Verify you’re on WSL2:

```powershell
wsl --list --verbose
```

## Step 3 — Update Linux packages

Open your WSL terminal (Ubuntu) and run:

```bash
sudo apt-get update
sudo apt-get -y upgrade
```

Install a minimal toolchain:

```bash
sudo apt-get install -y git curl ca-certificates make
```

## Step 3.1 — Create /data (owned by you)

Create a shared working directory at `/data` and ensure it is owned by your user:

```bash
sudo mkdir -p /data
sudo chown -R "$USER":"$USER" /data
```

Optional (recommended) permissions:

```bash
chmod 775 /data
```

## Step 3.2 — Install Docker (latest)

There are two common approaches on managed Windows laptops.

### Option A (recommended): Use Docker Desktop with WSL integration

If IT installs Docker Desktop via ServiceNow, you typically do not need to install Docker Engine inside WSL.
Enable WSL integration (Step 5) and verify from WSL:

```bash
docker version
```

### Option B: Install Docker Engine inside WSL (when Docker Desktop isn’t available)

This installs the latest stable Docker Engine via Docker’s official APT repository.

1. Install prerequisites:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
```

1. Add Docker’s official GPG key:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

1. Add the repository:

```bash
echo \
 "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
 $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
 sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

1. Install Docker:

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

1. Allow running Docker without `sudo`:

```bash
sudo usermod -aG docker "$USER"
```

Log out and back in (or restart the WSL distro) for group membership to apply.

1. Start Docker and verify:

Running Docker Engine inside WSL usually requires `systemd` support.
If your distro supports it, enable systemd in `/etc/wsl.conf`, then restart WSL.

Finally, verify:

```bash
docker version
docker run --rm hello-world
```

## Step 4 — Install VS Code + Remote WSL

1. Install VS Code on Windows.
2. Install the **Remote - WSL** extension.
3. (Recommended) Install the **Dev Containers** extension.

Open VS Code connected to WSL:

```bash
code .
```

If `code` is not available inside WSL, install the VS Code shell command (“Shell Command: Install 'code' command in PATH”).

## Step 5 — Configure Docker Desktop for WSL2

1. In Docker Desktop, enable **Use the WSL 2 based engine**.
2. Enable **WSL Integration** for your distro.

Verify Docker works from inside WSL:

```bash
docker version
```

If Docker is not available from WSL, re-check Docker Desktop WSL integration settings.

## Step 6 — Create an SSH key (for GitHub)

If your team uses SSH for GitHub access, create an SSH key in WSL and add it to GitHub before cloning.

For a deeper explanation and a recommended auto-start configuration, see:

- [docs/tutorials/ssh-agent/README.md](../tutorials/ssh-agent/README.md)

1. Check for existing keys:

```bash
ls -la ~/.ssh
```

1. Create a new Ed25519 key (recommended):

```bash
ssh-keygen -t ed25519 -C "you@example.com"
```

When prompted, set a strong **passphrase** (recommended). This keeps the private key encrypted on disk.

1. Start an SSH agent and add your key:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

1. Copy your public key and add it to GitHub:

```bash
cat ~/.ssh/id_ed25519.pub
```

1. Verify SSH connectivity:

```bash
ssh -T git@github.com
```

### Optional (recommended): Auto-start SSH agent on login

To avoid re-running `eval "$(ssh-agent -s)"` and `ssh-add` every time you open a new shell, configure your shell to auto-start (and reuse) an SSH agent.

Follow Section 4 (“Auto-starting SSH Agent”) in:

- [docs/tutorials/ssh-agent/README.md](../tutorials/ssh-agent/README.md)

Add the recommended script to your `~/.bashrc`:

```bash
# Define where to store the agent environment variables
SSH_ENV="$HOME/.ssh/agent-environment"

function start_agent {
 echo "Initializing new SSH agent..."
 # Start the agent and save the environment variables to a file
 /usr/bin/ssh-agent | sed 's/^echo/#echo/' > "${SSH_ENV}"
 chmod 600 "${SSH_ENV}"
 . "${SSH_ENV}" > /dev/null
 /usr/bin/ssh-add;
}

# Check if the environment file exists
if [ -f "${SSH_ENV}" ]; then
 . "${SSH_ENV}" > /dev/null
 # Check if the agent process is actually running
 ps -ef | grep ${SSH_AGENT_PID} | grep ssh-agent$ > /dev/null || {
  start_agent;
 }
else
 start_agent;
fi
```

## Step 7 — Create ~/src and clone GitHub repos

This is critical for performance.

- ✅ Clone into Linux paths like `~/src/...`
- ❌ Do not clone into Windows-mounted paths like `/mnt/c/...`

```bash
mkdir -p ~/src
cd ~/src

# Examples (replace <ORG> with your GitHub organization/user as needed)
git clone https://github.com/<ORG>/gds-tool_library.git
git clone https://github.com/<ORG>/gds-doc.git
```

If your team uses SSH cloning, use the SSH URLs instead:

```bash
git clone git@github.com:<ORG>/gds-tool_library.git
git clone git@github.com:<ORG>/gds-doc.git
```

If your team uses a corporate Docker registry proxy, configure Docker auth before building containers:

- [docs/how-to/configure-corporate-docker-registry.md](configure-corporate-docker-registry.md)

## Step 8 — Open in Dev Container

Follow the dev container docs:

- [docs/development/vscode/DEVCONTAINER.md](../development/vscode/DEVCONTAINER.md)
- [docs/development/vscode/devcontainer-beginners-guide.md](../development/vscode/devcontainer-beginners-guide.md)

In VS Code (connected to WSL), run:

- `Dev Containers: Rebuild and Reopen in Container`

## Step 9 — Verify the environment

In VS Code, run the default verification task:

- `Dev: Verify Dev Container`

Or from a terminal inside the container:

```bash
bash scripts/verify_devcontainer.sh
```

## Troubleshooting

### WSL is slow

The most common cause is working under `/mnt/c/`.

Move your repo into your WSL home directory and re-open it from there.

See:

- [docs/development/vscode/platform-specific.md](../development/vscode/platform-specific.md)

### Ports already in use

Windows and WSL2 share ports. Check conflicts as needed:

- Windows: `netstat -ano | findstr :5432`
- WSL: `sudo lsof -i :5432`
