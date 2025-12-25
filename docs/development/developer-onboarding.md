# Developer Onboarding: Personal Linux Environment (WSL2 or Red Hat)

This guide helps new team members set up a **personal Linux development environment** for this repo.

**Recommended approach:** use the repo's **Ansible playbook** for automated environment setup, then open the repo in the **VS Code Dev Container** for a consistent toolchain.

## Table of Contents

- [What you'll end up with](#what-youll-end-up-with)
- [Choose your platform](#choose-your-platform)
- [Step 0 — Windows SSH key setup (Windows users)](#step-0--windows-ssh-key-setup-windows-users)
- [Step 1 — Platform setup (WSL2 or RHEL)](#step-1--platform-setup-wsl2-or-rhel)
- [Step 2 — Deploy Windows SSH key to Linux (Recommended)](#step-2--deploy-windows-ssh-key-to-linux-recommended)
- [Step 3 — Automated environment setup](#step-3--automated-environment-setup)
- [Step 4 — Manual setup (Alternative)](#step-4--manual-setup-alternative)
- [Step 5 — Open dbtools in the Dev Container (recommended)](#step-5--open-dbtools-in-the-dev-container-recommended)
- [Step 6 — Verify your environment](#step-6--verify-your-environment)
- [Troubleshooting](#troubleshooting)
- [What's next](#whats-next)

## What you'll end up with

- A working Linux shell environment (WSL2 or RHEL)
- Git + GitHub access (SSH keys configured)
- Docker available for dev containers
- Development tools (UV for Python, NVM for Node.js)
- VS Code configured to open this repo in the dev container
- A verified dev setup using the repo's built-in verification scripts/tasks

## Choose your platform

- **WSL2 (Windows Subsystem for Linux):** personal Linux environment on a Windows laptop
- **Red Hat Enterprise Linux (or compatible):** shared Linux server environment

If you're unsure: pick **WSL2 + Ubuntu**.

### Shared RHEL server checklist

If you are developing on a **shared Red Hat Linux server**, verify these basics before proceeding:

- **Access**: You can SSH to the server and have a home directory (`$HOME`) with enough space.
- **Sudo access**: You need sudo to run the Ansible playbook (or ask DevOps to run it for you).
- **Editor workflow**: Decide whether you will use:
  - VS Code Remote SSH (recommended for a shared server), or
  - CLI-only editing (vim/emacs) if you prefer.
- **Docker availability**: Confirm whether Docker is available on the shared server.
  - Many shared servers do not allow Docker for non-admin users; if Docker is not available, skip dev container steps and use host-side tools.

---

## Step 0 — Windows SSH key setup (Windows users)

> **Skip this step** if you are working directly on a Linux machine (not Windows with WSL).

Generate an SSH key on Windows and configure the SSH agent. This key will be used for:
- GitHub authentication from Windows
- SSH access to WSL and RHEL servers
- VS Code Remote SSH connections

### 0.1) Install OpenSSH (if not already installed)

Windows 10/11 includes OpenSSH, but it may not be enabled. Run **PowerShell as Administrator**:

```powershell
# Check if OpenSSH client is installed
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Client*'

# Install if not present (State: NotPresent)
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

### 0.2) Generate SSH key with passphrase

Run in **regular PowerShell** (not as admin):

```powershell
# Generate Ed25519 key (recommended)
ssh-keygen -t ed25519 -C "you@example.com"
```

When prompted:
- **File location**: Press Enter for default (`C:\Users\<you>\.ssh\id_ed25519`)
- **Passphrase**: Enter a strong passphrase (recommended for security)

### 0.3) Start the SSH Agent service

The SSH agent runs as a Windows service. Enable and start it (**PowerShell as Administrator**):

```powershell
# Enable the ssh-agent service to start automatically
Get-Service ssh-agent | Set-Service -StartupType Automatic

# Start the service now
Start-Service ssh-agent

# Verify it's running
Get-Service ssh-agent
```

### 0.4) Add your key to the agent

Back in **regular PowerShell**:

```powershell
# Add your private key to the agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

Enter your passphrase when prompted. The agent remembers it until you log out.

### 0.5) Verify the setup

```powershell
# List keys loaded in the agent
ssh-add -l

# Display your public key (you'll need this later)
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
```

### 0.6) Add SSH key to GitHub

1. Copy your public key:

   ```powershell
   Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
   ```

2. Go to https://github.com/settings/keys
3. Click **New SSH key**
4. Paste the key and save

5. Verify GitHub connectivity:

   ```powershell
   ssh -T git@github.com
   ```

---

## Step 1 — Platform setup (WSL2 or RHEL)

### For WSL2 users

Follow the WSL2 setup guide to install WSL2 and a Linux distribution:

- [docs/how-to/setup-wsl2.md](../how-to/setup-wsl2.md)

Complete **Steps 1-2** (Install WSL2 and Linux distribution), then return here for Step 2.

> **Note (managed Windows laptops):** If you do not have admin rights, you may need to submit a ServiceNow request to have IT enable WSL2 and install Docker Desktop. The WSL2 setup guide includes a checklist of what to request.

### For RHEL users

Ensure you have:
- SSH access to the server
- A home directory with sufficient space
- Sudo access (or coordinate with DevOps)

---

## Step 2 — Deploy Windows SSH key to Linux (Recommended)

> **Skip this step** if you generated SSH keys directly in WSL/Linux (not Windows), or if you want separate keys for Windows and Linux.

Deploy your Windows SSH public key to WSL and/or RHEL so you can:
- SSH from Windows to your Linux environments
- Use VS Code Remote SSH
- Have a single SSH key for all environments

### Option A: Using Ansible Playbook (Recommended)

This repo includes a playbook for deploying SSH keys. Run from your WSL terminal:

```bash
# 1. First, install Ansible in WSL if not already installed
sudo apt-get update && sudo apt-get install -y ansible

# 2. Install required collection
ansible-galaxy collection install ansible.posix

# 3. Clone the repo (if not already cloned)
git clone https://github.com/<ORG>/dbtools.git ~/dev/dbtools

# 4. Get your Windows username and key path
WINDOWS_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r')
WINDOWS_PUBKEY="/mnt/c/Users/${WINDOWS_USER}/.ssh/id_ed25519.pub"

# Verify the key exists
cat "$WINDOWS_PUBKEY"

# 5. Deploy to WSL (localhost)
cd ~/dev/dbtools/ansible
ansible-playbook deploy_ssh_key.yml -i inventory/localhost.yml \
  -e "ssh_public_key_file=$WINDOWS_PUBKEY"
```

### Deploy to RHEL server

From WSL, deploy your Windows SSH key to the RHEL server:

```bash
# Using the deploy_ssh_key.yml playbook with password auth
cd ~/dev/dbtools/ansible
ansible-playbook deploy_ssh_key.yml \
  -i "rhel-server.example.com," \
  -e "ssh_public_key_file=$WINDOWS_PUBKEY" \
  -e "ansible_user=your-username" \
  --ask-pass

# Or use ssh-copy-id (simpler alternative)
ssh-copy-id -i "$WINDOWS_PUBKEY" your-username@rhel-server.example.com
```

### Option B: Manual deployment

<details>
<summary>Click to expand manual instructions</summary>

#### Deploy to WSL

From WSL terminal:

```bash
# Get Windows username
WINDOWS_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r')

# Create .ssh directory if needed
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Copy Windows public key to WSL authorized_keys
cat "/mnt/c/Users/${WINDOWS_USER}/.ssh/id_ed25519.pub" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### Deploy to RHEL

From Windows PowerShell:

```powershell
# Copy public key to RHEL server
$pubkey = Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
ssh your-username@rhel-server.example.com "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$pubkey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Or use ssh-copy-id from WSL:

```bash
ssh-copy-id -i /mnt/c/Users/$WINDOWS_USER/.ssh/id_ed25519.pub your-username@rhel-server.example.com
```

</details>

### Verify SSH access

From **Windows PowerShell**, test SSH to both environments:

```powershell
# Test SSH to WSL (if you set up SSH server in WSL)
ssh localhost

# Test SSH to RHEL
ssh your-username@rhel-server.example.com
```

---

## Step 3 — Automated environment setup

Use the Ansible playbook to automatically configure your development environment. This installs:

- System packages (git, curl, jq, make, build tools)
- Docker CE with compose plugin
- Development tools (UV for Python, NVM for Node.js)
- Shell configuration (bash aliases, PATH setup)
- SSH keys for GitHub (skip if using Windows key from Step 2)
- VS Code extensions

> **Note:** If you deployed your Windows SSH key in Step 2, you can skip the SSH key generation by adding `--skip-tags ssh` to the ansible-playbook command.

### WSL2 (Ubuntu)

Run these commands in your WSL terminal:

```bash
# 1. Install prerequisites
sudo apt-get update && sudo apt-get install -y git ansible

# 2. Install required Ansible collections
ansible-galaxy collection install community.general community.crypto

# 3. Clone repo via HTTPS (no SSH key needed yet)
git clone https://github.com/<ORG>/dbtools.git ~/dev/dbtools

# 4. Run the Ansible playbook
cd ~/dev/dbtools/ansible
ansible-playbook linux_dev_environment.yml -i inventory/localhost.yml --ask-become-pass
```

### RHEL

Run these commands on the RHEL server:

```bash
# 1. Install prerequisites
sudo dnf install -y git ansible-core

# 2. Install required Ansible collections
ansible-galaxy collection install community.general community.crypto

# 3. Clone repo via HTTPS (no SSH key needed yet)
git clone https://github.com/<ORG>/dbtools.git ~/dev/dbtools

# 4. Run the Ansible playbook
cd ~/dev/dbtools/ansible
ansible-playbook linux_dev_environment.yml -i inventory/localhost.yml --ask-become-pass
```

> **Note:** Replace `<ORG>` with your GitHub organization.

### After the playbook completes

1. **Log out and log back in** (or run `newgrp docker`) for Docker group membership to take effect

2. **Add your SSH key to GitHub** (skip if you already did this in Step 0):
   - If the playbook generated a new key, it displays your public key at the end
   - Copy it and add at https://github.com/settings/keys

3. **Switch git remote to SSH**:

   ```bash
   cd ~/dev/dbtools
   git remote set-url origin git@github.com:<ORG>/dbtools.git
   ```

4. **Verify Docker works**:

   ```bash
   docker run --rm hello-world
   ```

5. **Verify SSH to GitHub**:

   ```bash
   ssh -T git@github.com
   ```

**Skip to [Step 5 — Open dbtools in the Dev Container](#step-5--open-dbtools-in-the-dev-container-recommended)** after the automated setup.

---

## Step 4 — Manual setup (Alternative)

> **Use this section only if** you cannot use the Ansible playbook, need to troubleshoot, or want to understand what the automated setup does.

<details>
<summary>Click to expand manual setup instructions</summary>

These steps apply whether you develop on **WSL2** or on a **shared RHEL server**.

### 4.1) Install Git and basic tooling

Make sure you have:

- `git`
- `curl`
- `make`

**Ubuntu/WSL:**

```bash
sudo apt-get update
sudo apt-get install -y git curl make ca-certificates
```

**RHEL:**

```bash
sudo dnf install -y git curl make
```

### 4.2) Configure Git identity

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 4.3) Set up SSH keys for GitHub

GitHub access is a shared prerequisite for both WSL2 and shared RHEL environments.

1. Check for an existing key:

```bash
ls -la ~/.ssh
```

2. If you don't have one, create an Ed25519 key:

```bash
ssh-keygen -t ed25519 -C "you@example.com"
```

3. Start an agent and add the key:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

4. Add the public key to GitHub:

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the output and add it at https://github.com/settings/keys

5. Verify SSH connectivity:

```bash
ssh -T git@github.com
```

### 4.4) Clone the repository

```bash
mkdir -p ~/dev
cd ~/dev
git clone https://github.com/<ORG>/dbtools.git
cd dbtools
```

If your team uses SSH cloning instead of HTTPS, use the SSH URL instead.

### 4.5) Install Docker (if not available)

See the Docker installation instructions in:

- WSL2: [docs/how-to/setup-wsl2.md](../how-to/setup-wsl2.md) (Step 4 - Manual Setup)
- RHEL: Follow Docker's official RHEL installation guide

### 4.6) Corporate Docker registry (if applicable)

If your network requires pulling images through a corporate registry, follow:

- [docs/how-to/configure-corporate-docker-registry.md](../how-to/configure-corporate-docker-registry.md)

### 4.7) Set up UV Python environment (if not using dev container)

This repo uses **UV** as the primary Python package manager.

- UV how-to index: [docs/how-to/python/uv/README.md](../how-to/python/uv/README.md)

**Important:** If you will use the VS Code dev container (recommended), you do **not** need to set up UV on your host OS. The dev container provisions the repo's `.venv/` during `postCreate` using UV.

If you are NOT using the dev container:

1. Install UV:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. From the repo root, create/sync the workspace environment:

```bash
cd ~/dev/dbtools

# Install tools for typical local development
uv sync --group dev

# If you want the fuller toolchain used by the dev container
uv sync --group devcontainer
```

</details>

---

## Step 5 — Open dbtools in the Dev Container (recommended)

This repo ships a dev container based on **Red Hat UBI 9**, with Python provisioned via `uv`.

Reference docs:

- [docs/development/vscode/DEVCONTAINER.md](vscode/DEVCONTAINER.md)
- [docs/development/vscode/devcontainer-beginners-guide.md](vscode/devcontainer-beginners-guide.md)

### Prerequisites

1. **VS Code** installed with the **Dev Containers** extension
2. **Docker** available (Docker Desktop on Windows, or Docker Engine on RHEL)

### Steps

1. Open the repo folder in VS Code:

   ```bash
   cd ~/dev/dbtools
   code .
   ```

2. Use the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`):
   - `Dev Containers: Rebuild and Reopen in Container`

3. Wait for the container build to finish.

---

## Step 6 — Verify your environment

### Option 1 (recommended): Run the VS Code task

Run the default task:

- `Dev: Verify Dev Container`

This runs the repo's verification script and checks Python, Jupyter kernel registration, ODBC tooling, `sqlcmd`, and optional SQL Server checks.

### Option 2: Run verification from a terminal inside the container

From the repo root:

```bash
bash scripts/verify_devcontainer.sh
```

### Optional: SQL Server verification

If you are using the local SQL Server container in this repo, set `MSSQL_SA_PASSWORD` and run:

- `Dev: Verify SQL Server (sqlcmd + pyodbc)`

---

## Troubleshooting

### Ansible playbook fails

If the automated setup fails:

1. Check the error message for the specific task that failed
2. Try running with verbose output: `ansible-playbook ... -vvv`
3. Fall back to [Step 4 — Manual setup](#step-4--manual-setup-alternative) for the specific component that failed
4. Report the issue so the playbook can be improved

### Slow performance on WSL2

You are probably working under `/mnt/c/`. Move the repo to your WSL home directory.

See the WSL2 guidance in:

- [docs/development/vscode/platform-specific.md](vscode/platform-specific.md)

### Dev container builds, but Python packages look wrong

The container provisions `.venv/` during `postCreate`. If you previously had a stale `.venv/`, remove it and rebuild the container:

```bash
rm -rf .venv
```

### Docker not available on shared RHEL server

If Docker is not available to non-admin users on your shared RHEL server:

1. Skip the dev container steps
2. Use the host-side UV environment (see Step 4.7 in Manual Setup)
3. Coordinate with DevOps about Docker access

---

## What's next

- Read the team's development entrypoints:
  - [docs/development/README.md](README.md)
  - [docs/development/vscode/README.md](vscode/README.md)
- Follow coding standards:
  - [docs/development/coding-standards/README.md](coding-standards/README.md)
- Review the Ansible playbook documentation:
  - [ansible/README.md](../../ansible/README.md)
