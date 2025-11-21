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

## Working with Multiple Repositories (Per-Developer)

Each developer can work with their own set of sibling repositories (for example `sqlserver`, `linux-dev-setup`, etc.) without forcing a single list on the whole team.

### Workspace Layout

The dev container mounts the **parent** of the `dbtools` repo as `/workspaces`, so the layout inside the container looks like:

```text
/workspaces/
  dbtools/            # this repo
  sqlserver/          # optional, per-developer
  linux-dev-setup/    # optional, per-developer
  ...                 # any other clones under the same parent directory
```

If you already have clones under the same parent on the host (for example `~/src/dbtools`, `~/src/sqlserver`, `~/src/linux-dev-setup`), they will automatically appear as siblings under `/workspaces` in the container.

### Per-Developer Repo List (additional-repos.json)

To avoid forcing a single list of repos on everyone, the devcontainer uses a **per-developer** configuration file:

- Template (tracked in git): `.devcontainer/additional-repos.json.template`
- Your local copy (ignored by git): `.devcontainer/additional-repos.json`

The script `.devcontainer/scripts/clone-additional-repos.sh` reads from `additional-repos.json` and clones any missing repositories into `/workspaces`.

#### 1. Create your personal config

From the repo root:

```bash
cp .devcontainer/additional-repos.json.template .devcontainer/additional-repos.json
```

Then edit `.devcontainer/additional-repos.json` to list the repos you care about. Two entry forms are supported:

- **String form** (directory name inferred from repo name):

```json
{
  "repos": [
    "git@github.com:your-org/sqlserver.git",
    "git@github.com:your-org/linux-dev-setup.git"
  ]
}
```

- **Object form** (explicit directory name):

```json
{
  "repos": [
    {
      "url": "git@github.com:your-org/sqlserver.git",
      "directory": "sqlserver"
    },
    {
      "url": "git@github.com:your-org/linux-dev-setup.git",
      "directory": "linux-dev-setup"
    }
  ]
}
```

> Note: `.devcontainer/additional-repos.json` is git-ignored so each developer can maintain their own list.

#### 2. Behavior with already-cloned repos

If a repository directory already exists under `/workspaces` (for example you cloned `~/src/sqlserver` on the host), the script will detect `/workspaces/sqlserver/.git` and **skip cloning**:

- This allows you to:
  - Keep using your existing clones.
  - Still list them in `additional-repos.json` so new machines will clone them automatically.

#### 3. When cloning happens

- On initial container creation (or full rebuild), the devcontainer runs:
  - `.devcontainer/postCreate.sh`
  - `.devcontainer/scripts/clone-additional-repos.sh`
- The clone script is **idempotent**:
  - New repos in your JSON are cloned.
  - Existing repos (with a `.git` directory) are skipped.

#### 4. Clone or update repos manually (no rebuild required)

You can run the clone script manually from inside the running dev container at any time:

```bash
cd /workspaces/dbtools
bash .devcontainer/scripts/clone-additional-repos.sh
```

Typical workflows:

- **Add a new repo to your environment:**
  1. Add it to `.devcontainer/additional-repos.json`.
  2. Run the script as above.

- **Use an existing host clone (for example `~/src/sqlserver`):**
  - Ensure `dbtools` and `sqlserver` share the same parent directory on the host.
  - Add `sqlserver` to `additional-repos.json` if desired (for new machines).
  - The script will see `/workspaces/sqlserver/.git` and skip cloning.

#### 5. Removing a repo from your workspace

To stop using a repo:

1. Delete or comment out the entry from `.devcontainer/additional-repos.json`.
2. Optionally remove the directory:

   - From inside the container:

     ```bash
     cd /workspaces
     rm -rf sqlserver
     ```

   - Or from the host (for example):

     ```bash
     cd ~/src
     rm -rf sqlserver
     ```

3. The next time `clone-additional-repos.sh` runs, it will no longer recreate that repo (because it’s no longer in your JSON).

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
