# VS Code Workspace Configuration Summary

## Files Created

### 1. `snowflake-monitor.code-workspace` (Main Workspace File)

A comprehensive VS Code workspace configuration including:

#### Workspace Settings
- **Python Configuration**
  - Default interpreter path (.venv)
  - Linting enabled (pylint, flake8, mypy)
  - Black formatter with 120 char line length
  - Auto-format on save
  - Automatic import organization

- **Testing Configuration**
  - Both unittest and pytest enabled
  - Auto test discovery on save
  - Test paths configured

- **Editor Settings**
  - File exclusions (__pycache__, .pytest_cache, etc.)
  - Python-specific tab/indent settings
  - File associations

- **Terminal Configuration**
  - PYTHONPATH set to workspace folder
  - Cross-platform support (Linux, macOS, Windows)

#### Debug Configurations (8 configurations)
1. **Python: Current File** - Debug any Python file
2. **Monitor: Run Once** - Run monitor in one-time mode
3. **Monitor: Continuous** - Run continuous monitoring
4. **Tests: Run All** - Debug all tests
5. **Tests: Current File** - Debug current test file
6. **Tests: With Coverage** - Run tests with coverage reporting
7. **Example: Module Usage** - Run example scripts
8. **Python: Debug Tests** - Debug unittest tests

All configurations:
- Use `debugpy` (modern Python debugger)
- Support environment variables from `.env` file
- Include input prompts for dynamic values
- Properly configured for integrated terminal

#### Tasks (11 tasks)
1. **Run All Tests** (Default test task)
2. **Run Tests with Coverage** 
3. **Run Specific Test Module** (with picker)
4. **Format Code (Black)**
5. **Lint with Flake8**
6. **Type Check (mypy)**
7. **Install Dependencies**
8. **Install Dev Dependencies**
9. **Generate Coverage Report**
10. **Open Coverage Report** (cross-platform)
11. **Validate Module Structure**

#### Extension Recommendations
- ms-python.python (Python support)
- ms-python.vscode-pylance (Fast language server)
- ms-python.black-formatter (Code formatting)
- ms-python.pylint (Linting)
- ms-python.flake8 (Additional linting)
- littlefoxteam.vscode-python-test-adapter (Test visualization)
- donjayamanne.python-environment-manager (Env management)
- njpwerner.autodocstring (Docstring generation)
- wholroyd.jinja (Template support)
- redhat.vscode-yaml (YAML support)
- github.vscode-github-actions (CI/CD support)

### 2. `.env.example` (Environment Variables Template)

Template file for environment configuration including:
- Snowflake credentials (user, password, account, warehouse, role)
- Email/SMTP configuration
- Logging configuration
- Monitoring settings

Users can copy to `.env` and fill in actual values.

### 3. `VSCODE_SETUP.md` (Comprehensive Setup Guide)

Detailed documentation covering:
- Quick start instructions
- Feature overview (debug configs, tasks, settings)
- Common workflows (testing, running, debugging)
- Keyboard shortcuts reference
- Troubleshooting guide
- Tips and best practices
- Additional resources

### 4. Updated `.gitignore`

Added exclusions for:
- `.env` and `.env.local` (sensitive data)
- `.vscode/` directory
- `config.sh` (credentials)
- `*.code-workspace.backup` (backup files)

## Benefits

### 1. **One-Click Operations**
- Press F5 to run/debug any configuration
- Press Ctrl+Shift+B to run default test task
- Single command to format, lint, or type-check

### 2. **Integrated Debugging**
- Set breakpoints in code and tests
- Step through execution
- Inspect variables
- Debug test failures easily

### 3. **Automated Testing**
- Tests auto-discovered on save
- Run/debug tests from Test Explorer
- Coverage reports with one click

### 4. **Code Quality**
- Auto-format on save
- Real-time linting
- Type checking
- Import organization

### 5. **Team Consistency**
- Shared workspace settings
- Same linting/formatting rules
- Recommended extensions
- Consistent development environment

### 6. **Productivity Boost**
- Quick task access
- Keyboard shortcuts
- Test explorer integration
- Intelligent code completion

## Usage Examples

### Open the Workspace
```bash
cd /home/dpham/src/snowflake
code snowflake-monitor.code-workspace
```

### Run Tests
- **Method 1**: Press Ctrl+Shift+B → "Run All Tests"
- **Method 2**: Press F5 → Select "Tests: Run All"
- **Method 3**: Open Test Explorer → Click Run
- **Method 4**: Terminal → `python run_tests.py`

### Debug the Monitor
1. Press F5 or Ctrl+Shift+D
2. Select "Monitor: Run Once"
3. Enter account name when prompted
4. Set breakpoints as needed
5. Press F5 to start debugging

### Format Code
- **Automatic**: Just save (Ctrl+S)
- **Manual**: Ctrl+Shift+P → "Format Document"
- **Task**: Ctrl+Shift+B → "Format Code (Black)"

### View Coverage
1. Ctrl+Shift+B → "Run Tests with Coverage"
2. Ctrl+Shift+B → "Open Coverage Report"

## Configuration Highlights

### Smart Features

**Input Prompts**
- Account name prompt for monitor configurations
- Test module picker for selective test runs

**Cross-Platform Support**
- Different commands for Linux/macOS/Windows
- Platform-specific terminal environment variables

**Environment Variables**
- All debug configs support `.env` file
- Secure credential management

**Problem Matchers**
- Automatic error detection from output
- Click errors to jump to code

## Files Organization

```
snowflake/
├── snowflake-monitor.code-workspace  # Main workspace file
├── .env.example                       # Environment template
├── .env                              # Your credentials (gitignored)
├── VSCODE_SETUP.md                   # Setup guide
├── .gitignore                        # Updated exclusions
└── [project files...]
```

## Integration with CI/CD

The workspace configuration aligns with:
- GitHub Actions workflow (`.github/workflows/tests.yml`)
- Pre-commit hooks (if configured)
- Same linting/formatting rules as CI

This ensures:
- Code formatted locally passes CI
- Tests that pass locally pass in CI
- Consistent code quality standards

## Getting Started Checklist

- [ ] Open workspace: `code snowflake-monitor.code-workspace`
- [ ] Install recommended extensions (VS Code will prompt)
- [ ] Copy `.env.example` to `.env` and configure
- [ ] Create virtual environment: `python -m venv .venv`
- [ ] Activate environment: `source .venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements-dev.txt`
- [ ] Run tests: Press Ctrl+Shift+B → "Run All Tests"
- [ ] Set up Snowflake credentials in `.env`
- [ ] Try debug configuration: F5 → "Monitor: Run Once"

## Next Steps

1. **Read VSCODE_SETUP.md** for detailed instructions
2. **Customize workspace** if needed (add more tasks/configs)
3. **Set up pre-commit hooks** for automatic checks
4. **Configure Git** to use VS Code as editor:
   ```bash
   git config --global core.editor "code --wait"
   ```

## Troubleshooting Quick Fixes

**Extensions not loading?**
- Reload window: Ctrl+Shift+P → "Reload Window"

**Tests not discovered?**
- Refresh Test Explorer
- Ctrl+Shift+P → "Python: Discover Tests"

**Linting not working?**
- Install dev deps: `pip install -r requirements-dev.txt`
- Restart VS Code

**Debugger not starting?**
- Check Python interpreter: Ctrl+Shift+P → "Python: Select Interpreter"
- Install debugpy: `pip install debugpy`

## Customization

### Add Custom Debug Configuration

Edit workspace file, add to `launch.configurations`:
```json
{
  "name": "My Custom Debug",
  "type": "debugpy",
  "request": "launch",
  "program": "${workspaceFolder}/my_script.py",
  "args": ["--my-arg"],
  "console": "integratedTerminal"
}
```

### Add Custom Task

Edit workspace file, add to `tasks.tasks`:
```json
{
  "label": "My Custom Task",
  "type": "shell",
  "command": "python",
  "args": ["my_script.py"],
  "group": "test"
}
```

### Modify Settings

Add to workspace `settings`:
```json
"python.linting.pylintArgs": [
  "--disable=missing-docstring"
]
```

## Summary

The VS Code workspace configuration provides:

✅ **8 debug configurations** for various scenarios
✅ **11 tasks** for common operations
✅ **11 recommended extensions** for Python development
✅ **Comprehensive settings** for linting, formatting, testing
✅ **Environment variable support** for secure credentials
✅ **Cross-platform compatibility** (Linux, macOS, Windows)
✅ **Integrated testing** with Test Explorer
✅ **One-click operations** for productivity
✅ **Complete documentation** for setup and usage
✅ **CI/CD alignment** for consistent quality

This creates a professional, productive development environment that's ready to use out of the box!
