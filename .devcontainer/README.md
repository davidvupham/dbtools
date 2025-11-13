# dbtools Dev Container Variants

This workspace now ships with two dev container environments:

- **Red Hat (default):** `./devcontainer.json` extends `./redhat/devcontainer.json` and builds a UBI 9–based image.
- **Ubuntu:** `./ubuntu/devcontainer.json` matches the prior Miniconda image and is available on demand.

## Selecting a Variant

### VS Code

1. **Default (Red Hat):** Open the repository normally with Dev Containers. VS Code automatically uses the Red Hat definition.
2. **Ubuntu (one-time choice):**
   - Create a personal override `.devcontainer/devcontainer.local.json` (git-ignored) with:
     ```json
     {
       "extends": "./ubuntu/devcontainer.json"
     }
     ```
   - Reopen the folder in a container. VS Code will remember your preference on subsequent opens.
3. **Temporary switch:** Use the command palette → `Dev Containers: Open Folder in Container...` and choose the desired variant file.

### Cursor IDE

**Note:** Cursor IDE does not fully support the `extends` property in devcontainer.json. Use the symlink approach instead:

```bash
# Switch to Red Hat variant
.devcontainer/switch-variant.sh redhat

# Switch to Ubuntu variant
.devcontainer/switch-variant.sh ubuntu

# Check current variant
.devcontainer/switch-variant.sh
```

After switching variants, rebuild your dev container in Cursor. The main `.devcontainer/devcontainer.json` will be a symlink pointing to your chosen variant.

## Keeping Variants in Sync

Shared settings (extensions, forwarded ports, etc.) live in both variant files. When you change those sections in one variant, run the sync helper to mirror the change in the other variant.

### Scripts

All tooling lives in `.devcontainer/scripts/`:

- `sync_devcontainers.py` – Core Python utility that copies a curated set of keys from one variant to the other.
- `sync-devcontainers.sh` – Thin Bash wrapper for convenience (runs the Python script with the same arguments).

### Usage

```bash
# From the repo root – sync Ubuntu changes into Red Hat (default direction)
.devcontainer/scripts/sync-devcontainers.sh

# Reverse direction (Red Hat → Ubuntu)
.devcontainer/scripts/sync-devcontainers.sh --source redhat --target ubuntu

# Preview differences without writing
.devcontainer/scripts/sync-devcontainers.sh --dry-run

# Limit syncing to specific top-level keys
.devcontainer/scripts/sync-devcontainers.sh --keys customizations features
```

The script rewrites the target `devcontainer.json` with canonical JSON (comments are removed). Keep shared configuration edits in the authoritative source variant to minimize churn.

## Adding New Variants

1. Create a new folder under `.devcontainer/<variant>/` with a Dockerfile and `devcontainer.json`.
2. Update `.devcontainer/devcontainer.json` if you want the new variant to be the default (via `extends`).
3. Extend the sync scripts if the new variant should share settings with the existing ones.

## Post-Create Workflow

Both variants leverage the shared `.devcontainer/postCreate.sh` script, so any tooling changes there automatically apply to every container build.

## Troubleshooting & Notes

### Copilot in Dev Containers
- Remote extensions: The dev containers install `GitHub.copilot` and `GitHub.copilot-chat`. If they don’t appear after a pull, run “Dev Containers: Rebuild Container”.
- Sign in: In the Dev Container window (green corner status), use Accounts → GitHub → Sign in and approve the remote sign-in prompt.
- Quick checks if sign-in fails:

```bash
curl -I https://api.github.com
nslookup github.com || getent hosts github.com
env | grep -iE 'http_proxy|https_proxy|no_proxy'
```

- Corporate proxy/CA:
  - Set VS Code `http.proxy` in the Dev Container window and reload.
  - Trust your corporate root CA and expose to Node-based extensions:

```bash
sudo cp /path/to/corp-root-ca.crt /usr/local/share/ca-certificates/corp.crt
sudo update-ca-certificates
echo 'export NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/corp.crt' | sudo tee -a /etc/profile.d/node-extra-ca.sh >/dev/null
```

  - Optionally set `HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY` in the container environment.

### Red Hat build failure: Anaconda Terms of Service (TOS)
If you previously saw a build error like `CondaToSNonInteractiveError: Terms of Service have not been accepted...`, it was due to the Red Hat image using the default Anaconda channels in a non-interactive build. The Red Hat `Dockerfile` has been updated to:

- Switch conda to `conda-forge` as the primary channel
- Enforce strict channel priority

This bypasses the interactive TOS acceptance requirement and aligns both variants on conda-forge.

### Devcontainer.json key casing
The Red Hat variant originally used `dockerFile` (camelCase). The correct property name is `dockerfile`. This has been fixed along with the build `context` (now `../..` to match Ubuntu). If VS Code reports it cannot resolve the dev container, ensure you have pulled latest changes.

### Adding packages across distros
Prefer installing Python tooling via the conda environment (`conda run -n gds pip install ...`) inside the Dockerfile for parity. System packages should use `apt-get` (Ubuntu) and `dnf` (Red Hat). Keep lists minimal and consistent.

### Sync script scope
The sync helper only mirrors predefined top-level keys. Build-specific fields (`build.dockerfile`, `build.context`, `name`) are intentionally excluded to allow variants to diverge. Extend `SYNC_KEYS` in `sync_devcontainers.py` if you need additional unified fields.

### Selecting distro per project
If you contribute tooling dependent on Debian packaging (e.g., `.deb` based installation), test in the Ubuntu container. For RPM-focused tasks, use the Red Hat variant. Shared Python libraries and tests should pass in both.
