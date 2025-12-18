# Jupyter Notebook Validation Guide

This guide walks you through validating that Jupyter notebooks are properly configured and working in the dev container environment.

## Prerequisites

- Dev container has been built and is running
- VS Code is connected to the dev container
- Jupyter extensions are installed (should be automatic via devcontainer.json)

## Quick Validation Checklist

- [ ] Jupyter packages installed in `.venv`
- [ ] Kernel registered and visible in VS Code
- [ ] Can create and run a test notebook
- [ ] Python executable points to correct environment
- [ ] JupyterLab server can start (optional)

---

## Step 1: Verify Jupyter Packages Installation

First, confirm that `ipykernel` is installed in the workspace venv (`.venv/`).

If you enabled `ENABLE_JUPYTERLAB=1`, confirm that `jupyterlab` is installed as well.

### Terminal Commands

```bash
# Verify ipykernel is installed
.venv/bin/python -c "import ipykernel; print(f'ipykernel version: {ipykernel.__version__}')"

# Verify jupyterlab is installed (optional)
.venv/bin/python -c "import jupyterlab; print(f'jupyterlab version: {jupyterlab.__version__}')"

# Alternative: Check via pip list
.venv/bin/python -m pip list | grep -E "ipykernel|jupyterlab"
```

### Expected Output

```
ipykernel version: 8.x.x
jupyterlab version: 4.x.x
```

### Troubleshooting

If packages are missing:

- Rebuild the dev container: Command Palette → "Dev Containers: Rebuild Container"
- Manually install: `.venv/bin/python -m pip install -e ".[devcontainer]"` (and optionally `-e ".[devcontainer-jupyter]"`)

---

## Step 2: Verify Kernel Registration

Check that the `Python (gds)` kernel is registered and discoverable.

### Terminal Commands

```bash
# List all registered kernels
jupyter kernelspec list

# Check if the 'gds' kernel exists
ls -la ~/.local/share/jupyter/kernels/

# View kernel configuration
cat ~/.local/share/jupyter/kernels/gds/kernel.json
```

### Expected Output

```
Available kernels:
  gds    /home/<user>/.local/share/jupyter/kernels/gds
```

The `kernel.json` should contain:

```json
{
  "argv": [
    "/workspaces/devcontainer/dbtools/.venv/bin/python",
    "-m",
    "ipykernel_launcher",
    "-f",
    "{connection_file}"
  ],
  "display_name": "Python (gds)",
  "language": "python",
  "metadata": {
    "debugger": true
  }
}
```

### VS Code Verification

1. Open any `.ipynb` file (or create a new one)
2. Click the kernel selector in the top-right of the notebook
3. Look for `Python (gds)` in the list
4. Select it if not already selected

### Troubleshooting

If kernel is missing:

- Run the postCreate script manually: `bash .devcontainer/postCreate.sh`
- Manually register: `.venv/bin/python -m ipykernel install --user --name gds --display-name "Python (gds)"`

---

## Step 3: Create and Run a Test Notebook

Create a simple test notebook to verify end-to-end functionality.

### Create Test Notebook

1. In VS Code, create a new file: `test_jupyter.ipynb`
2. VS Code should automatically recognize it as a Jupyter notebook
3. Select the `Python (gds)` kernel if prompted

### Test Cells

Add and run these cells:

**Cell 1: Verify Python Environment**

```python
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Expected path: /workspaces/devcontainer/dbtools/.venv/bin/python")
```

**Cell 2: Verify Jupyter Packages**

```python
import ipykernel
print(f"ipykernel: {ipykernel.__version__}")

try:
  import jupyterlab
  print(f"jupyterlab: {jupyterlab.__version__}")
except Exception as e:
  print(f"jupyterlab not installed (this is OK unless ENABLE_JUPYTERLAB=1): {e}")
```

**Cell 3: Test Basic Operations**

```python
import pandas as pd
import numpy as np

# Create a simple DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [10, 20, 30, 40]
})

print("DataFrame created successfully:")
print(df)
print(f"\nSum of column A: {df['A'].sum()}")
```

**Cell 4: Verify Environment Packages**

```python
# Check that local packages are available (if installed)
try:
    import gds_database
    print("✓ gds_database available")
except ImportError:
    print("⚠ gds_database not installed (this is OK if not needed)")

# List some installed packages
import pkg_resources
packages = [d.project_name for d in pkg_resources.working_set]
print(f"\nTotal packages installed: {len(packages)}")
print(f"Sample packages: {', '.join(sorted(packages)[:10])}")
```

### Expected Results

- All cells execute without errors
- Python executable shows: `/workspaces/devcontainer/dbtools/.venv/bin/python`
- Packages import successfully
- Output displays correctly in notebook cells

### Troubleshooting

**Cell execution fails:**

- Check kernel is selected: Look at top-right of notebook
- Verify Python path matches expected: `/workspaces/devcontainer/dbtools/.venv/bin/python`
- Check terminal for error messages

**Import errors:**

- Verify packages are installed: `pip list | grep <package-name>`
- Reinstall if needed: `pip install <package-name>`

---

## Step 4: Verify Python Executable Path

Ensure notebooks are using the correct Python interpreter.

### In Notebook

Run this in a notebook cell:

```python
import sys
print(f"Python executable: {sys.executable}")
print(f"Expected: /workspaces/devcontainer/dbtools/.venv/bin/python")
print(f"Match: {sys.executable == '/workspaces/devcontainer/dbtools/.venv/bin/python'}")
```

### Expected Output

```
Python executable: /workspaces/devcontainer/dbtools/.venv/bin/python
Expected: /workspaces/devcontainer/dbtools/.venv/bin/python
Match: True
```

### VS Code Settings Check

Verify VS Code is configured correctly:

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type: "Python: Select Interpreter"
3. Verify `/workspaces/devcontainer/dbtools/.venv/bin/python` is selected

Or check settings:

- File → Preferences → Settings
- Search for `python.defaultInterpreterPath`
- Should be: `/workspaces/devcontainer/dbtools/.venv/bin/python`

---

## Step 5: Test JupyterLab Server (Optional)

If you want to run a standalone JupyterLab server, verify port forwarding works.

### Start JupyterLab Server

In a terminal inside the dev container:

```bash
# Start JupyterLab server
jupyter lab --ip 0.0.0.0 --port 8888 --no-browser
```

### Expected Behavior

1. Server starts and shows output like:

   ```

  [I 2024-XX-XX XX:XX:XX.XXX ServerApp] Serving notebooks from local directory: /workspaces/devcontainer/dbtools
   [I 2024-XX-XX XX:XX:XX.XXX ServerApp] JupyterLab is running at:
   [I 2024-XX-XX XX:XX:XX.XXX ServerApp] <http://0.0.0.0:8888/lab?token=><token>

   ```

2. VS Code should show a notification: "Port 8888 is being forwarded"
3. Click "Open in Browser" or access: `http://localhost:8888`

### Access JupyterLab

- Use the token from the terminal output
- Or access via VS Code's port forwarding panel
- JupyterLab interface should load in your browser

### Stop Server

Press `Ctrl+C` in the terminal to stop the server.

### Troubleshooting

**Port not forwarding:**
- Check `devcontainer.json` has `8888` in `forwardPorts`
- Verify `portsAttributes` includes Jupyter configuration
- Manually forward: VS Code → Ports tab → Forward Port → `8888`

**Connection refused:**
- Verify server is running: Check terminal output
- Check firewall settings (usually not an issue in dev containers)
- Try accessing via VS Code's forwarded port URL

---

## Step 6: Advanced Validation (Optional)

### Test Multiple Kernels

If you have multiple Python environments, verify kernel selection works:

```bash
# List all available kernels
jupyter kernelspec list

# Test switching kernels in a notebook
# (Use kernel selector in VS Code notebook UI)
```

### Test Notebook Features

Verify these notebook features work:

1. **Markdown cells**: Create a markdown cell with formatting
2. **Code completion**: Type `import pandas as pd` then `pd.` and verify autocomplete
3. **Variable explorer**: Check if VS Code shows notebook variables
4. **Output rendering**: Test plots, tables, and rich output

### Test with Real Data

If you have database connectivity configured:

```python
# Test database connectivity from notebook
from gds_database import DatabaseConnection
# ... your connection code ...
```

---

## Common Issues and Solutions

### Issue: "No kernel found" or kernel selector is empty

**Solution:**

1. Verify `ipykernel` is installed: `python -c "import ipykernel"`
2. Register kernel manually: `python -m ipykernel install --user --name gds --display-name "Python (gds)"`
3. Reload VS Code window: Command Palette → "Developer: Reload Window"

### Issue: Wrong Python interpreter in notebook

**Solution:**

1. Select correct kernel: Click kernel selector → Choose "Python (gds)"
2. Verify VS Code interpreter: Command Palette → "Python: Select Interpreter" → Choose `/workspaces/devcontainer/dbtools/.venv/bin/python`
3. Check `devcontainer.json` setting: `python.defaultInterpreterPath` should be `/workspaces/devcontainer/dbtools/.venv/bin/python`

### Issue: Packages not available in notebook

**Solution:**

1. Verify packages are installed in `.venv`:

  ```bash
  .venv/bin/python -m pip list | grep <package-name>
  ```

2. Install missing packages: `.venv/bin/python -m pip install <package-name>`
2. Restart kernel in notebook: Kernel menu → "Restart Kernel"

### Issue: Kernel dies or crashes

**Solution:**

1. Check kernel logs: View → Output → Select "Jupyter" from dropdown
2. Verify Python environment is healthy:

   ```bash

  .venv/bin/python -c "import sys; print(sys.executable)"

   ```
3. Rebuild dev container if environment is corrupted

### Issue: JupyterLab server won't start

**Solution:**
1. Verify `jupyterlab` is installed: `pip list | grep jupyterlab`
2. Check port 8888 is available: `netstat -tuln | grep 8888` (should be empty)
3. Try different port: `jupyter lab --ip 0.0.0.0 --port 8889 --no-browser`
4. Check VS Code port forwarding configuration

---

## Validation Summary

After completing all steps, you should have:

- ✅ Jupyter packages installed and importable
- ✅ Kernel registered and visible in VS Code
- ✅ Can create and execute notebook cells
- ✅ Python executable points to `/workspaces/devcontainer/dbtools/.venv/bin/python`
- ✅ Notebooks can import required packages
- ✅ JupyterLab server can start (if needed)

## Next Steps

- Start creating your notebooks in `docs/tutorials/python/modules/pandas/notebooks/`
- Explore VS Code's Jupyter features: variable explorer, interactive debugging
- Set up database connections for data analysis notebooks
- Review [features.md](features.md) for more VS Code productivity tips

## Related Documentation

- [DEVCONTAINER.md](DEVCONTAINER.md) - Dev container overview
- [devcontainer-beginners-guide.md](devcontainer-beginners-guide.md) - Detailed setup guide
- [features.md](features.md) - VS Code features and productivity tips
- [devcontainer-sqltools.md](devcontainer-sqltools.md) - Database connectivity from notebooks
