# How to Migrate from Python Distributions to UV

**🔗 [← Back to UV How-to Index](./README.md)** — Task-oriented guides for UV workflows

> **Document Version:** 1.0
> **Last Updated:** January 15, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Migration-purple)

> [!IMPORTANT]
> **Related Docs:** [Migration from pip/Poetry](./uv-migrate-from-pip.md) | [Python Management](./uv-python-management.md) | [Getting Started](../../../tutorials/python/uv/uv-getting-started.md)

This guide covers migrating from standalone Python distributions (Anaconda, python.org, Microsoft Store Python, system packages) to UV on Red Hat Enterprise Linux, Ubuntu, and Windows.

> [!NOTE]
> This guide complements the [pip/Poetry Migration Guide](./uv-migrate-from-pip.md). If you're migrating from pip, Poetry, or Pipenv workflows, see that guide instead.

## Table of contents

- [Overview](#overview)
  - [Why migrate?](#why-migrate)
  - [What UV replaces](#what-uv-replaces)
- [Pre-migration checklist](#pre-migration-checklist)
- [Migrating from Anaconda/Miniconda](#migrating-from-anacondaminiconda)
  - [Understanding the differences](#understanding-the-differences)
  - [Export your conda environment](#export-your-conda-environment)
  - [Install UV](#install-uv)
  - [Create UV project from conda export](#create-uv-project-from-conda-export)
  - [Handle conda-specific packages](#handle-conda-specific-packages)
  - [Uninstall Anaconda (optional)](#uninstall-anaconda-optional)
- [Migrating from python.org distribution](#migrating-from-pythonorg-distribution)
  - [Windows](#windows)
  - [macOS](#macos)
  - [Linux](#linux)
- [Migrating from Microsoft Store Python](#migrating-from-microsoft-store-python)
  - [Identify Microsoft Store Python](#identify-microsoft-store-python)
  - [Disable app execution aliases](#disable-app-execution-aliases)
  - [Install UV and migrate](#install-uv-and-migrate)
  - [Uninstall Microsoft Store Python (optional)](#uninstall-microsoft-store-python-optional)
- [Migrating from system Python](#migrating-from-system-python)
  - [Red Hat Enterprise Linux (RHEL) / CentOS / Rocky Linux](#red-hat-enterprise-linux-rhel--centos--rocky-linux)
  - [Ubuntu / Debian](#ubuntu--debian)
  - [Important: Do not remove system Python](#important-do-not-remove-system-python)
- [Platform-specific installation](#platform-specific-installation)
  - [Red Hat Enterprise Linux (RHEL)](#red-hat-enterprise-linux-rhel)
  - [Ubuntu / Debian](#ubuntu--debian-1)
  - [Windows](#windows-1)
- [Post-migration verification](#post-migration-verification)
- [Updating your workflow](#updating-your-workflow)
  - [Command mapping](#command-mapping)
  - [Environment activation changes](#environment-activation-changes)
- [Troubleshooting](#troubleshooting)
  - [PATH conflicts](#path-conflicts)
  - [Package not found on PyPI](#package-not-found-on-pypi)
  - [Permission errors](#permission-errors)
  - [SSL certificate errors](#ssl-certificate-errors)
- [Related guides](#related-guides)

---

## Overview

### Why migrate?

| Current Tool | Pain Points | UV Benefits |
|:---|:---|:---|
| **Anaconda** | Large installation (~3GB), slow environment creation, complex channel management | Single binary (~30MB), instant environments, PyPI-native |
| **python.org** | Manual version management, no lock files, PATH conflicts | Managed Python versions, universal lock file, isolated environments |
| **Microsoft Store** | App execution aliases cause conflicts, limited control | Full control, no alias conflicts, proper PATH management |
| **System Python** | Version locked to OS, risk of breaking system tools | Any Python version, isolated from system |

### What UV replaces

```
┌─────────────────────────────────────────────────────────────┐
│                    BEFORE (Multiple Tools)                   │
├─────────────────────────────────────────────────────────────┤
│  conda/pyenv     →  Python version management               │
│  conda/venv      →  Virtual environment creation            │
│  conda/pip       →  Package installation                    │
│  conda-lock/pip  →  Dependency locking                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     AFTER (Single Tool)                      │
├─────────────────────────────────────────────────────────────┤
│  uv              →  All of the above in one binary          │
└─────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of contents](#table-of-contents)

---

## Pre-migration checklist

Before migrating, gather information about your current setup:

- [ ] **Document installed packages**: Export your current environment
- [ ] **Identify non-PyPI packages**: Some conda packages have no PyPI equivalent
- [ ] **Check for compiled extensions**: Note packages with C/C++ dependencies
- [ ] **Backup critical projects**: Ensure you can restore if needed
- [ ] **Note Python versions in use**: List all Python versions your projects require

[↑ Back to Table of contents](#table-of-contents)

---

## Migrating from Anaconda/Miniconda

### Understanding the differences

| Aspect | Conda | UV |
|:---|:---|:---|
| Package source | conda-forge, defaults channels | PyPI (Python Package Index) |
| Environment location | `~/anaconda3/envs/` or `~/miniconda3/envs/` | Project-local `.venv/` |
| Activation | `conda activate myenv` | `uv run` (no activation needed) |
| Lock file | `environment.yml` or `conda-lock.yml` | `uv.lock` |
| Non-Python packages | Supported (e.g., `cudatoolkit`, `ffmpeg`) | Not supported (use system packages) |

> [!WARNING]
> **Conda-only packages**: Some packages like `cudatoolkit`, `mkl`, or `ffmpeg` are not available on PyPI. You must install these via your system package manager (`dnf`, `apt`) or from vendor sources.

### Export your conda environment

**Step 1: List your environments**

```bash
conda env list
```

**Step 2: Export the environment you want to migrate**

```bash
# Export with versions (recommended)
conda list -n myenv --export > conda-packages.txt

# Or export as YAML
conda env export -n myenv > environment.yml
```

**Step 3: Identify PyPI-compatible packages**

Review your export and categorize packages:

```bash
# View the export
cat conda-packages.txt
```

Example output:

```text
# packages in environment:
numpy=1.24.3=py311h64a7726_0
pandas=2.0.3=py311h320fe9a_0
cudatoolkit=11.8.0=h6a678d5_0    # ← NOT on PyPI
requests=2.31.0=pyhd8ed1ab_0
```

### Install UV

Choose your platform:

**RHEL / CentOS / Rocky Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

**Ubuntu / Debian:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

**Windows (PowerShell as Administrator):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# Restart your terminal
```

### Create UV project from conda export

**Step 1: Create a new project directory**

```bash
mkdir my-migrated-project
cd my-migrated-project
uv init
```

**Step 2: Add PyPI-compatible packages**

Extract package names from your conda export and add them:

```bash
# Add packages one by one or in bulk
uv add numpy pandas requests scikit-learn matplotlib
```

**Step 3: Pin the Python version**

```bash
# Match your conda environment's Python version
uv python pin 3.11
```

**Step 4: Sync and verify**

```bash
uv sync
uv run python -c "import numpy; print(numpy.__version__)"
```

### Handle conda-specific packages

Some conda packages require alternative approaches:

| Conda Package | PyPI Alternative | System Package Alternative |
|:---|:---|:---|
| `cudatoolkit` | None | NVIDIA CUDA Toolkit (vendor install) |
| `mkl` | `mkl` (Intel) | `intel-mkl` (dnf/apt) |
| `ffmpeg` | `ffmpeg-python` (wrapper only) | `ffmpeg` (dnf/apt) |
| `nodejs` | None | `nodejs` (dnf/apt) |
| `r-base` | None | `R` (dnf/apt) |
| `openblas` | None | `openblas` (dnf/apt) |

**Example: Installing CUDA on RHEL**

```bash
# Add NVIDIA repository and install
sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo
sudo dnf install cuda-toolkit-12-4
```

**Example: Installing CUDA on Ubuntu**

```bash
# Add NVIDIA repository and install
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install cuda-toolkit-12-4
```

### Uninstall Anaconda (optional)

After verifying your migration, you can remove Anaconda:

**Linux (RHEL/Ubuntu):**

```bash
# Remove conda initialization from shell
conda init --reverse --all

# Remove Anaconda directory
rm -rf ~/anaconda3
# Or for Miniconda:
rm -rf ~/miniconda3

# Remove conda configuration
rm -rf ~/.conda ~/.condarc
```

**Windows:**

1. Open **Settings** → **Apps** → **Installed apps**
2. Find **Anaconda3** or **Miniconda3**
3. Click **Uninstall**
4. Delete remaining folders: `%USERPROFILE%\anaconda3` and `%USERPROFILE%\.conda`

[↑ Back to Table of contents](#table-of-contents)

---

## Migrating from python.org distribution

The python.org installers provide standalone Python without package management. Migration is straightforward.

### Windows

**Step 1: Document your current setup**

```powershell
# Check installed Python versions
py --list

# Export installed packages (if any global packages)
py -m pip freeze > old-packages.txt
```

**Step 2: Install UV**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Step 3: Create project and migrate packages**

```powershell
mkdir my-project
cd my-project
uv init

# If you had global packages, add them to your project
# Review old-packages.txt and add needed packages:
uv add requests pandas numpy
```

**Step 4: Uninstall python.org Python (optional)**

1. Open **Settings** → **Apps** → **Installed apps**
2. Find entries like **Python 3.x.x** (not Microsoft Store versions)
3. Click **Uninstall** for each version
4. Clean up PATH: Remove entries like `C:\Python3x\` and `C:\Python3x\Scripts\`

### macOS

**Step 1: Identify python.org installation**

```bash
# Check if you have framework Python
ls /Library/Frameworks/Python.framework/Versions/

# Check which python is active
which python3
python3 --version
```

**Step 2: Install UV**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc  # or ~/.bashrc
```

**Step 3: Migrate your projects**

```bash
cd my-project
uv init
uv add <your-packages>
```

**Step 4: Uninstall python.org Python (optional)**

```bash
# Remove framework installation
sudo rm -rf /Library/Frameworks/Python.framework/Versions/3.x

# Remove symbolic links
sudo rm -f /usr/local/bin/python3*
sudo rm -f /usr/local/bin/pip3*

# Remove Applications folder entry
sudo rm -rf "/Applications/Python 3.x"
```

### Linux

On Linux, python.org distributions are typically compiled from source. If you installed Python this way:

```bash
# If installed to /usr/local (common default)
which python3
# /usr/local/bin/python3

# After installing UV, you can leave this in place
# UV manages its own Python versions in ~/.local/share/uv/python/
```

[↑ Back to Table of contents](#table-of-contents)

---

## Migrating from Microsoft Store Python

Microsoft Store Python can cause conflicts due to "app execution aliases" that intercept `python` commands.

### Identify Microsoft Store Python

**Check if you have Microsoft Store Python:**

```powershell
# This shows the path to your python
Get-Command python | Select-Object Source

# Microsoft Store Python shows a path like:
# C:\Users\<user>\AppData\Local\Microsoft\WindowsApps\python.exe
```

**Check for app execution aliases:**

```powershell
# List WindowsApps entries
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WindowsApps\python*.exe"
```

### Disable app execution aliases

**Step 1: Open Windows Settings**

1. Press `Win + I` to open Settings
2. Go to **Apps** → **Advanced app settings** → **App execution aliases**

**Step 2: Disable Python aliases**

Toggle **OFF** the following entries:
- `python.exe` → App Installer
- `python3.exe` → App Installer
- `python3.x.exe` → App Installer (if present)

### Install UV and migrate

**Step 1: Install UV**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Step 2: Restart your terminal**

Close and reopen PowerShell or Windows Terminal.

**Step 3: Verify UV manages Python**

```powershell
uv python list
uv python install 3.12
```

**Step 4: Create your project**

```powershell
mkdir my-project
cd my-project
uv init
uv run python --version
```

### Uninstall Microsoft Store Python (optional)

1. Open **Settings** → **Apps** → **Installed apps**
2. Search for **Python**
3. Find entries published by **Python Software Foundation** with source **Microsoft Store**
4. Click **Uninstall**

> [!NOTE]
> You can keep Microsoft Store Python installed if you prefer. Just ensure app execution aliases are disabled to prevent conflicts with UV.

[↑ Back to Table of contents](#table-of-contents)

---

## Migrating from system Python

System Python is pre-installed by the operating system. Many system tools depend on it.

### Red Hat Enterprise Linux (RHEL) / CentOS / Rocky Linux

**Step 1: Identify system Python**

```bash
# Check system Python
/usr/bin/python3 --version

# See what depends on it
rpm -q --whatrequires python3
```

**Step 2: Install UV alongside system Python**

```bash
# Install UV (does not affect system Python)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Verify UV is available
uv --version
```

**Step 3: Install UV-managed Python**

```bash
# Install a modern Python version
uv python install 3.12

# Verify
uv python list
```

**Step 4: Configure your projects to use UV Python**

```bash
cd my-project
uv init
uv python pin 3.12
uv sync
```

**Step 5: Update your shell profile (optional)**

Add to `~/.bashrc`:

```bash
# Use UV-managed Python by default
alias python='uv run python'
alias pip='uv pip'
```

### Ubuntu / Debian

**Step 1: Identify system Python**

```bash
# Check system Python
/usr/bin/python3 --version

# See what depends on it
apt-cache rdepends python3 | head -20
```

**Step 2: Install UV alongside system Python**

```bash
# Install UV (does not affect system Python)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Verify
uv --version
```

**Step 3: Install UV-managed Python**

```bash
uv python install 3.12
uv python list
```

**Step 4: Create projects with UV**

```bash
mkdir my-project
cd my-project
uv init
uv python pin 3.12
uv add requests
uv run python -c "import requests; print('Success!')"
```

### Important: Do not remove system Python

> [!WARNING]
> **Never uninstall system Python on Linux.** Critical system tools like `dnf`, `yum`, `apt`, and others depend on it. Removing it can break your operating system.

**Safe approach:**

- Leave `/usr/bin/python3` untouched
- Use UV for all development work
- UV's Python versions are stored in `~/.local/share/uv/python/`
- Project virtual environments are in each project's `.venv/`

[↑ Back to Table of contents](#table-of-contents)

---

## Platform-specific installation

### Red Hat Enterprise Linux (RHEL)

**Prerequisites:**

```bash
# Ensure curl is available
sudo dnf install curl -y
```

**Install UV:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Add to PATH permanently:**

```bash
# Add to ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Verify installation:**

```bash
uv --version
uv python install 3.12
```

**Enable shell completion (optional):**

```bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
source ~/.bashrc
```

**SELinux considerations:**

UV binaries and Python installations work normally under SELinux. No special configuration is required.

### Ubuntu / Debian

**Prerequisites:**

```bash
# Ensure curl is available
sudo apt update
sudo apt install curl -y
```

**Install UV:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Add to PATH permanently:**

```bash
# Add to ~/.bashrc (bash) or ~/.zshrc (zsh)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Verify installation:**

```bash
uv --version
uv python install 3.12
```

**Enable shell completion (optional):**

```bash
# For bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc

# For zsh
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc
```

### Windows

**Prerequisites:**

- Windows 10 version 1709 or later, or Windows 11
- PowerShell 5.1 or later

**Install UV (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**

```powershell
# Restart PowerShell first
uv --version
uv python install 3.12
```

**Add to PATH (if not automatic):**

The installer typically adds UV to your user PATH. If not:

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click **Advanced** tab → **Environment Variables**
3. Under **User variables**, edit **Path**
4. Add: `%USERPROFILE%\.local\bin`

**Enable shell completion (PowerShell):**

```powershell
# Add to your PowerShell profile
Add-Content $PROFILE 'Invoke-Expression (& uv generate-shell-completion powershell | Out-String)'
```

[↑ Back to Table of contents](#table-of-contents)

---

## Post-migration verification

After installing UV, verify your setup:

**Step 1: Check UV installation**

```bash
uv --version
# Example output: uv 0.5.10 (2a3b1234 2024-12-15)
```

**Step 2: Install and verify Python**

```bash
uv python install 3.12
uv python list
```

**Step 3: Create a test project**

```bash
mkdir uv-test
cd uv-test
uv init
uv add requests
uv run python -c "import requests; print(f'requests {requests.__version__} OK')"
```

**Step 4: Verify isolation from system/old Python**

```bash
# This should use UV's Python, not system Python
uv run which python
# Expected: /path/to/project/.venv/bin/python

# Verify it's not the old installation
uv run python -c "import sys; print(sys.executable)"
```

[↑ Back to Table of contents](#table-of-contents)

---

## Updating your workflow

### Command mapping

| Old Command (Conda) | New Command (UV) |
|:---|:---|
| `conda create -n myenv python=3.12` | `uv init && uv python pin 3.12` |
| `conda activate myenv` | Not needed (use `uv run`) |
| `conda deactivate` | Not needed |
| `conda install numpy` | `uv add numpy` |
| `conda remove numpy` | `uv remove numpy` |
| `conda list` | `uv pip list` |
| `conda env export` | `uv export` |
| `python script.py` | `uv run python script.py` |

| Old Command (python.org/pip) | New Command (UV) |
|:---|:---|
| `python -m venv .venv` | `uv init` (creates venv automatically) |
| `source .venv/bin/activate` | Not needed (use `uv run`) |
| `pip install package` | `uv add package` |
| `pip install -r requirements.txt` | `uv add -r requirements.txt` |
| `pip freeze > requirements.txt` | `uv export > requirements.txt` |
| `python script.py` | `uv run python script.py` |

### Environment activation changes

**Before (Conda/venv pattern):**

```bash
# Old workflow requiring activation
conda activate myenv      # or: source .venv/bin/activate
python script.py
pip install newpackage
python another_script.py
conda deactivate          # or: deactivate
```

**After (UV pattern):**

```bash
# New workflow - no activation needed
uv run python script.py
uv add newpackage
uv run python another_script.py
# No deactivation needed
```

> [!TIP]
> The `uv run` command automatically uses the correct Python environment for your project. You never need to "activate" or "deactivate" environments.

[↑ Back to Table of contents](#table-of-contents)

---

## Troubleshooting

### PATH conflicts

**Symptom:** Running `python` uses old installation instead of UV-managed Python.

**Solution:**

```bash
# Check what python is being used
which python
which python3

# Ensure UV's bin directory is first in PATH
export PATH="$HOME/.local/bin:$PATH"

# For projects, always use uv run
uv run python --version
```

**Windows-specific:**

```powershell
# Check PATH order
$env:PATH -split ';' | Select-String python

# Ensure UV path comes before other Python paths
# UV installs to: %USERPROFILE%\.local\bin
```

### Package not found on PyPI

**Symptom:** `uv add` fails for a package that worked in Conda.

**Cause:** The package is Conda-specific or has a different name on PyPI.

**Solution:**

```bash
# Search PyPI for the package
uv pip search <package-name>

# Common name differences:
# Conda: opencv        → PyPI: opencv-python
# Conda: pillow        → PyPI: Pillow (same)
# Conda: pytorch       → PyPI: torch
# Conda: tensorflow-gpu → PyPI: tensorflow (GPU support automatic)
```

**For packages not on PyPI:**

Install via system package manager:

```bash
# RHEL
sudo dnf install <package>

# Ubuntu
sudo apt install <package>
```

### Permission errors

**Symptom:** `Permission denied` when installing UV or packages.

**Solution:**

```bash
# UV should be installed to user directory, not system
# If you see permission errors, ensure you're not using sudo

# Correct (no sudo):
curl -LsSf https://astral.sh/uv/install.sh | sh

# Wrong (avoid sudo):
# sudo curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Fix ownership if needed:**

```bash
# If ~/.local is owned by root
sudo chown -R $USER:$USER ~/.local
```

### SSL certificate errors

**Symptom:** SSL errors when downloading packages.

**Solution (RHEL with corporate certificates):**

```bash
# Add corporate CA to system trust
sudo cp company-ca.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust

# Or set environment variable
export SSL_CERT_FILE=/path/to/ca-bundle.crt
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
```

**Solution (Ubuntu with corporate certificates):**

```bash
# Add corporate CA to system trust
sudo cp company-ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

[↑ Back to Table of contents](#table-of-contents)

---

## Related guides

| Guide | Description |
|:---|:---|
| [Migration from pip/Poetry](./uv-migrate-from-pip.md) | Migrate from pip, Poetry, Pipenv, pip-tools |
| [Getting Started with UV](../../../tutorials/python/uv/uv-getting-started.md) | Beginner tutorial for UV |
| [Python Management](./uv-python-management.md) | Install and manage Python versions |
| [Docker Integration](./uv-docker-integration.md) | Use UV in Docker containers |
| [CI/CD Integration](./uv-ci-cd-integration.md) | Set up UV in CI/CD pipelines |
| [UV Command Reference](../../../reference/python/uv/uv-reference.md) | Complete CLI reference |
| [Official UV Documentation](https://docs.astral.sh/uv/) | Astral's official docs |

[↑ Back to Table of contents](#table-of-contents)
