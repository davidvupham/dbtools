# Using Dev Containers with Cursor IDE

## Problem

Cursor IDE does not fully support the `extends` property in `devcontainer.json` files, which is the standard approach used by VS Code for managing multiple dev container variants.

## Solution: Symbolic Links

Instead of using `extends`, we use symbolic links to switch between Red Hat and Ubuntu variants.

## Quick Start

### Switch Variants

```bash
# Switch to Red Hat variant (default)
.devcontainer/switch-variant.sh redhat

# Switch to Ubuntu variant
.devcontainer/switch-variant.sh ubuntu

# Check current variant
.devcontainer/switch-variant.sh
```

After switching, **rebuild your dev container** in Cursor:

- Use Command Palette → `Dev Containers: Rebuild Container`
- Or restart Cursor

### How It Works

The main `.devcontainer/` directory now uses **two symbolic links**:

- `devcontainer.json` → points to either `redhat/devcontainer.json` or `ubuntu/devcontainer.json`
- `Dockerfile` → points to either `redhat/Dockerfile` or `ubuntu/Dockerfile`

Both variants have identical configuration except for:

- Container name
- Base image (Red Hat UBI 9 vs Ubuntu)
- Package managers (dnf vs apt)

## Git Considerations

Both symlinks (`.devcontainer/devcontainer.json` and `.devcontainer/Dockerfile`) **are tracked in Git**, so your team can see which variant is currently set as default. Each developer can run the switch script to use their preferred variant without affecting the repository.

To set a different default for your team, simply:

1. Run the switch script
2. Commit the symlink changes
3. Push to your repository

## Comparison with VS Code

| Feature | VS Code | Cursor IDE |
|---------|---------|------------|
| `extends` property | ✅ Supported | ❌ Not supported |
| Symbolic links | ✅ Works | ✅ Works |
| Multiple variants | ✅ Native support | ✅ Via symlinks |
| `devcontainer.local.json` | ✅ Supported | ❌ Not with `extends` |

## Troubleshooting

### "Dev container config is missing image/dockerFile properties"

This means the symlink isn't set up correctly. Run:

```bash
.devcontainer/switch-variant.sh redhat
```

### Changes Not Taking Effect

After switching variants or making changes to devcontainer.json:

1. Rebuild the container completely
2. Don't just reload the window

### Symlinks Show as Modified in Git

The symlinks should be committed to Git. If you see them as modified, it means you've switched variants. You can:

- Commit the changes if you want to set a new default for the team
- Revert them to keep the original default:

  ```bash
  git checkout .devcontainer/devcontainer.json .devcontainer/Dockerfile
  ```

## Additional Resources

- See [README.md](./README.md) for detailed documentation on both variants
- See [switch-variant.sh](./switch-variant.sh) for the switcher script implementation
