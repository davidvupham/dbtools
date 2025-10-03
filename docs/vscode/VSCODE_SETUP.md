# VS Code Setup Guide for Snowflake Replication Monitor

## Quick Start

1. **Open the workspace in VS Code**
   ```bash
   code snowflake-monitor.code-workspace
   ```

2. **Install recommended extensions**
   - VS Code will prompt you to install recommended extensions
   - Or manually install from the Extensions panel (Ctrl+Shift+X)

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

4. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Features Included

### 🐛 Debug Configurations

Access from Run and Debug panel (Ctrl+Shift+D):

- **Python: Current File** - Debug the currently open file
- **Monitor: Run Once** - Run monitoring script once
- **Monitor: Continuous** - Run continuous monitoring
- **Tests: Run All** - Debug all tests
- **Tests: Current File** - Debug current test file
- **Tests: With Coverage** - Run tests with coverage
- **Example: Module Usage** - Run example script
- **Python: Debug Tests** - Debug unittest tests

### 🎯 Tasks

Access via Terminal → Run Task (Ctrl+Shift+B):

- **Run All Tests** (Default test task)
- **Run Tests with Coverage**
- **Run Specific Test Module**
- **Format Code (Black)**
- **Lint with Flake8**
- **Type Check (mypy)**
- **Install Dependencies**
- **Install Dev Dependencies**
- **Generate Coverage Report**
- **Open Coverage Report**
- **Validate Module Structure**

### ⚙️ Settings Configured

- **Python linting**: pylint, flake8, mypy enabled
- **Formatting**: Black with 120 character line length
- **Auto-format on save**: Enabled
- **Import organization**: Automatic
- **Testing**: Both unittest and pytest enabled
- **Test discovery**: Automatic on save
- **PYTHONPATH**: Set to workspace folder

### 🔌 Recommended Extensions

- **Python** - Microsoft's Python language support
- **Pylance** - Fast Python language server
- **Black Formatter** - Code formatting
- **Pylint** - Python linting
- **Flake8** - Additional linting
- **Python Test Adapter** - Better test visualization
- **Python Environment Manager** - Virtual environment management
- **autoDocstring** - Generate docstrings
- **Jinja** - Template support
- **YAML** - YAML file support
- **GitHub Actions** - Workflow file support

## Common Workflows

### Running Tests

**Method 1: Using Test Explorer**
1. Open Test Explorer (beaker icon in sidebar)
2. Click refresh to discover tests
3. Click play button to run tests
4. Click debug icon to debug tests

**Method 2: Using Debug Configuration**
1. Press F5 or Ctrl+Shift+D
2. Select "Tests: Run All" or "Tests: Current File"
3. Press F5 to start

**Method 3: Using Tasks**
1. Press Ctrl+Shift+B
2. Select "Run All Tests"

**Method 4: Using Terminal**
```bash
python run_tests.py
```

### Running the Monitor

**Method 1: Using Debug Configuration**
1. Press F5
2. Select "Monitor: Run Once" or "Monitor: Continuous"
3. Enter account name when prompted
4. Press F5 to start

**Method 2: Using Terminal**
```bash
./monitor_snowflake_replication_v2.py myaccount --once
```

### Code Formatting

**Automatic (on save)**
- Just save the file (Ctrl+S)
- Black will format automatically

**Manual**
1. Press Ctrl+Shift+P
2. Type "Format Document"
3. Press Enter

**Using Task**
1. Press Ctrl+Shift+B
2. Select "Format Code (Black)"

### Viewing Coverage

**Method 1: Using Task**
1. Press Ctrl+Shift+B
2. Select "Run Tests with Coverage"
3. Select "Open Coverage Report"

**Method 2: Using Terminal**
```bash
pytest --cov=. --cov-report=html
xdg-open htmlcov/index.html  # Linux
```

### Debugging

**Set breakpoints**
- Click in the gutter (left of line numbers)
- Or press F9 on a line

**Start debugging**
- Press F5 with a debug configuration selected
- Or right-click and select "Debug Python File"

**Debug controls**
- F5: Continue
- F10: Step Over
- F11: Step Into
- Shift+F11: Step Out
- Ctrl+Shift+F5: Restart
- Shift+F5: Stop

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Command Palette | Ctrl+Shift+P |
| Open File | Ctrl+P |
| Open Terminal | Ctrl+` |
| Run Task | Ctrl+Shift+B |
| Debug | F5 |
| Toggle Breakpoint | F9 |
| Format Document | Shift+Alt+F |
| Go to Definition | F12 |
| Find References | Shift+F12 |
| Rename Symbol | F2 |
| Open Test Explorer | Ctrl+; then T |
| Search in Files | Ctrl+Shift+F |

## Troubleshooting

### Python Interpreter Not Found

1. Press Ctrl+Shift+P
2. Type "Python: Select Interpreter"
3. Choose your virtual environment or Python installation

### Tests Not Discovered

1. Open Command Palette (Ctrl+Shift+P)
2. Type "Python: Discover Tests"
3. Or check the Test Explorer and click refresh

### Import Errors in Tests

1. Make sure PYTHONPATH is set correctly
2. Restart VS Code
3. Or add to settings:
   ```json
   "terminal.integrated.env.linux": {
     "PYTHONPATH": "${workspaceFolder}"
   }
   ```

### Linting Errors

1. Install dev dependencies: `pip install -r requirements-dev.txt`
2. Restart VS Code
3. Check Output panel for linter errors

### Debugging Not Working

1. Make sure debugpy is installed: `pip install debugpy`
2. Check launch.json configuration
3. Try "Python: Current File" configuration first

## Tips

### Exclude Files from Search

Already configured in workspace:
- `__pycache__`
- `.pytest_cache`
- `htmlcov`
- `*.pyc`

### Multi-Root Workspace

Add more folders:
1. File → Add Folder to Workspace
2. File → Save Workspace As

### Custom Tasks

Add to `tasks.json` in workspace file:
```json
{
  "label": "My Custom Task",
  "type": "shell",
  "command": "python my_script.py"
}
```

### Environment Variables per Configuration

Edit `.env` file:
```bash
SNOWFLAKE_USER=myuser
SNOWFLAKE_PASSWORD=mypassword
```

## Additional Resources

- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [VS Code Testing](https://code.visualstudio.com/docs/python/testing)
- [VS Code Debugging](https://code.visualstudio.com/docs/python/debugging)
- [Python in VS Code](https://code.visualstudio.com/docs/languages/python)

## Project-Specific Notes

### Log Files

Monitor logs are written to `/var/log/monitor_snowflake_replication.log`

Ensure write permissions:
```bash
sudo touch /var/log/monitor_snowflake_replication.log
sudo chown $USER /var/log/monitor_snowflake_replication.log
```

### Testing Without Snowflake

All tests use mocking - no Snowflake connection required:
```bash
python run_tests.py
```

### Code Quality

Before committing:
```bash
# Format code
black . --line-length=120

# Check linting
flake8 . --max-line-length=120

# Type check
mypy --ignore-missing-imports *.py
```
