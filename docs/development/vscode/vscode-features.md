# VS Code Features for dbtools Development

This guide covers VS Code features, configurations, and best practices for developing with the dbtools project in a dev container.

## Table of Contents

- [Debugging](#debugging)
- [Tasks](#tasks)
- [Port Forwarding](#port-forwarding)
- [Testing Integration](#testing-integration)
- [Extensions](#extensions)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Tips and Tricks](#tips-and-tricks)

## Debugging

### Python Debugging Configurations

The dev container comes with VS Code's Python debugger (`debugpy`) pre-configured. Here are common debugging scenarios:

#### Debug Current File

Press `F5` or use the Run and Debug panel to debug the currently open Python file:

```json
{
  "name": "Python: Current File",
  "type": "debugpy",
  "request": "launch",
  "program": "${file}",
  "console": "integratedTerminal",
  "cwd": "${workspaceFolder}"
}
```

#### Debug with Arguments

```json
{
  "name": "Python: Current File with Args",
  "type": "debugpy",
  "request": "launch",
  "program": "${file}",
  "args": ["--debug", "--config", "config.json"],
  "console": "integratedTerminal"
}
```

#### Debug Module

```json
{
  "name": "Python: Module",
  "type": "debugpy",
  "request": "launch",
  "module": "gds_database",
  "console": "integratedTerminal"
}
```

#### Remote Debugging (Database Server)

```json
{
  "name": "Python: Attach to Remote",
  "type": "debugpy",
  "request": "attach",
  "connect": {
    "host": "localhost",
    "port": 5678
  },
  "pathMappings": [
    {
      "localRoot": "${workspaceFolder}",
      "remoteRoot": "/app"
    }
  ]
}
```

### PowerShell Debugging

Debug PowerShell scripts using the PowerShell extension:

```json
{
  "name": "PowerShell: Launch Script",
  "type": "PowerShell",
  "request": "launch",
  "script": "${file}",
  "cwd": "${workspaceFolder}"
}
```

### Debugging Best Practices

1. **Set Breakpoints**: Click in the gutter (left of line numbers) or press `F9`
2. **Conditional Breakpoints**: Right-click breakpoint → Edit Breakpoint → Add condition
3. **Logpoints**: Right-click → Add Logpoint (logs without stopping)
4. **Watch Variables**: Add variables to Watch panel during debugging
5. **Debug Console**: Use REPL to evaluate expressions during debugging

### Common Debug Commands

| Action | Shortcut |
|--------|----------|
| Start Debugging | F5 |
| Stop Debugging | Shift+F5 |
| Restart Debugging | Ctrl+Shift+F5 |
| Continue | F5 |
| Step Over | F10 |
| Step Into | F11 |
| Step Out | Shift+F11 |
| Toggle Breakpoint | F9 |

## Tasks

VS Code tasks automate common development workflows. Create tasks in `.vscode/tasks.json` or the workspace file.

### Testing Tasks

#### Run All Tests

```json
{
  "label": "Run All Tests",
  "type": "shell",
  "command": "pytest",
  "args": ["-v", "--cov=.", "--cov-report=term-missing"],
  "group": {
    "kind": "test",
    "isDefault": true
  },
  "problemMatcher": [],
  "presentation": {
    "reveal": "always",
    "panel": "dedicated"
  }
}
```

#### Run Tests with Coverage

```json
{
  "label": "Run Tests with Coverage HTML",
  "type": "shell",
  "command": "pytest",
  "args": ["--cov=.", "--cov-report=html", "--cov-report=term"],
  "group": "test",
  "problemMatcher": []
}
```

#### Run Specific Test File

```json
{
  "label": "Run Current Test File",
  "type": "shell",
  "command": "pytest",
  "args": ["-v", "${file}"],
  "group": "test",
  "problemMatcher": []
}
```

### Code Quality Tasks

#### Format with Ruff

```json
{
  "label": "Format Code (Ruff)",
  "type": "shell",
  "command": "ruff",
  "args": ["format", "."],
  "group": "build",
  "problemMatcher": []
}
```

#### Lint with Ruff

```json
{
  "label": "Lint (Ruff)",
  "type": "shell",
  "command": "ruff",
  "args": ["check", ".", "--fix"],
  "group": "build",
  "problemMatcher": {
    "owner": "ruff",
    "fileLocation": ["relative", "${workspaceFolder}"],
    "pattern": {
      "regexp": "^(.+):(\\d+):(\\d+):\\s+(\\w+):\\s+(.+)$",
      "file": 1,
      "line": 2,
      "column": 3,
      "severity": 4,
      "message": 5
    }
  }
}
```

#### Type Check with mypy

```json
{
  "label": "Type Check (mypy)",
  "type": "shell",
  "command": "mypy",
  "args": [".", "--ignore-missing-imports"],
  "group": "build",
  "problemMatcher": []
}
```

### Database Tasks

#### PostgreSQL Connection Test

```json
{
  "label": "Test PostgreSQL Connection",
  "type": "shell",
  "command": "python",
  "args": ["-c", "from gds_postgres import PostgresConnection; print('PostgreSQL OK')"],
  "group": "test"
}
```

#### Run Database Migration

```json
{
  "label": "Run Database Migration",
  "type": "shell",
  "command": "python",
  "args": ["scripts/migrate_database.py"],
  "group": "build"
}
```

### PowerShell Tasks

#### Run PowerShell Script

```json
{
  "label": "Run PowerShell Script",
  "type": "shell",
  "command": "pwsh",
  "args": ["-NoProfile", "-File", "${file}"],
  "group": "build"
}
```

#### Run Pester Tests

```json
{
  "label": "Run Pester Tests",
  "type": "shell",
  "command": "pwsh",
  "args": ["-NoProfile", "-Command", "Invoke-Pester -Path ./PowerShell/tests -Output Detailed"],
  "group": "test"
}
```

### Running Tasks

- **Quick Access**: Press `Ctrl+Shift+B` to run the default build task
- **Task Menu**: Press `Ctrl+Shift+P` → "Tasks: Run Task"
- **Configure**: Press `Ctrl+Shift+P` → "Tasks: Configure Task"

## Port Forwarding

VS Code automatically detects and forwards ports from the dev container to your local machine.

### Automatic Port Forwarding

Add to `devcontainer.json`:

```json
{
  "forwardPorts": [5432, 1433, 27017, 3000, 5000, 8000],
  "portsAttributes": {
    "5432": {
      "label": "PostgreSQL",
      "protocol": "tcp"
    },
    "1433": {
      "label": "SQL Server",
      "protocol": "tcp"
    },
    "27017": {
      "label": "MongoDB",
      "protocol": "tcp"
    },
    "8000": {
      "label": "Web Server",
      "protocol": "http"
    }
  }
}
```

### Manual Port Forwarding

1. Open **Ports** panel (View → Ports)
2. Click **Forward a Port**
3. Enter port number
4. Access via `localhost:<port>` or click the globe icon

### Common Database Ports

| Database | Default Port | Protocol |
|----------|-------------|----------|
| PostgreSQL | 5432 | TCP |
| SQL Server | 1433 | TCP |
| MongoDB | 27017 | TCP |
| MySQL | 3306 | TCP |
| Redis | 6379 | TCP |
| Snowflake | 443 | HTTPS |

### Port Forwarding Best Practices

- **Use labels** for easy identification
- **Set visibility** (private vs public) appropriately
- **Auto-forward** commonly used ports in devcontainer.json
- **Check conflicts** if ports don't forward (may be in use locally)

## Testing Integration

VS Code provides excellent integration with Python testing frameworks.

### Configure Python Testing

Add to workspace or `.vscode/settings.json`:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    ".",
    "-v",
    "--tb=short"
  ],
  "python.testing.autoTestDiscoverOnSaveEnabled": true
}
```

### Test Explorer

1. Open **Testing** view (beaker icon in sidebar or `Ctrl+; Ctrl+A`)
2. Tests are auto-discovered from your project
3. Click **Run** icon to run all tests
4. Click **Debug** icon to debug tests
5. Click individual test to run/debug specific test

### Running Tests

**From Test Explorer:**

- Click play button to run
- Click debug icon to debug
- Right-click for more options

**From Editor:**

- Hover over test function
- Click "Run Test" or "Debug Test" CodeLens

**From Command Palette:**

- `Ctrl+Shift+P` → "Python: Run All Tests"
- `Ctrl+Shift+P` → "Python: Debug All Tests"

### Test Output

- View test results in **Test Results** panel
- Failed tests show stack traces
- Click on failure to jump to code

### Coverage Integration

Install Coverage Gutters extension and add task:

```json
{
  "label": "Generate Coverage",
  "type": "shell",
  "command": "pytest",
  "args": ["--cov=.", "--cov-report=xml", "--cov-report=html"],
  "problemMatcher": []
}
```

Then use `Ctrl+Shift+P` → "Coverage Gutters: Display Coverage" to see coverage in editor gutters.

## Extensions

For a curated list of top recommended extensions for 2026, see [Must-Use VS Code Extensions](vscode-extensions.md).

### Recommended Extensions for dbtools

Add to `devcontainer.json`:

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        // Python Development
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "ms-python.debugpy",

        // Testing
        "littlefoxteam.vscode-python-test-adapter",
        "ryanluker.vscode-coverage-gutters",

        // Database Tools
        "mtxr.sqltools",
        "mtxr.sqltools-driver-pg",
        "mtxr.sqltools-driver-mssql",
        "mtxr.sqltools-driver-mysql",

        // PowerShell
        "ms-vscode.powershell",

        // Docker
        "ms-azuretools.vscode-docker",

        // Code Quality
        "editorconfig.editorconfig",
        "davidanson.vscode-markdownlint",

        // Utilities
        "streetsidesoftware.code-spell-checker",
        "visualstudioexptteam.vscodeintellicode",
        "github.copilot",

        // YAML/JSON
        "redhat.vscode-yaml",
        "tamasfe.even-better-toml"
      ]
    }
  }
}
```

### Extension Highlights

#### SQLTools

Connect to databases directly from VS Code:

1. Install SQLTools + driver extensions
2. Configure connection in SQLTools panel
3. Run queries in `.sql` files
4. Browse database schema

#### Coverage Gutters

Show test coverage in editor:

- Green: Covered lines
- Red: Uncovered lines
- Yellow: Partially covered

#### PowerShell

Full PowerShell development support:

- Syntax highlighting
- IntelliSense
- Debugging
- Integrated console

## Keyboard Shortcuts

### Essential Shortcuts

| Action | Windows/Linux | Mac |
|--------|--------------|-----|
| Command Palette | Ctrl+Shift+P | Cmd+Shift+P |
| Quick Open File | Ctrl+P | Cmd+P |
| Integrated Terminal | Ctrl+` | Ctrl+` |
| Go to Definition | F12 | F12 |
| Find References | Shift+F12 | Shift+F12 |
| Rename Symbol | F2 | F2 |
| Format Document | Shift+Alt+F | Shift+Option+F |
| Toggle Comment | Ctrl+/ | Cmd+/ |
| Search in Files | Ctrl+Shift+F | Cmd+Shift+F |
| Run Task | Ctrl+Shift+B | Cmd+Shift+B |

### Python-Specific Shortcuts

| Action | Shortcut |
|--------|----------|
| Run Python File | Ctrl+F5 |
| Debug Python File | F5 |
| Select Interpreter | Ctrl+Shift+P → "Python: Select Interpreter" |
| Run Selection in Terminal | Shift+Enter |
| Start REPL | Ctrl+Shift+P → "Python: Start REPL" |

### Testing Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Test Explorer | Ctrl+; Ctrl+A |
| Run All Tests | Ctrl+; A |
| Run Failed Tests | Ctrl+; F |
| Debug Last Test | Ctrl+; Ctrl+D |

## Tips and Tricks

### Multi-Cursor Editing

- **Add cursor**: Alt+Click
- **Add cursor above/below**: Ctrl+Alt+Up/Down
- **Select all occurrences**: Ctrl+Shift+L
- **Select next occurrence**: Ctrl+D

### Quick Fixes

- Press `Ctrl+.` on an error/warning for quick fixes
- Auto-import missing modules
- Fix linting issues

### Zen Mode

- Press `Ctrl+K Z` for distraction-free coding
- Press `Esc Esc` to exit

### Terminal Management

- **Split terminal**: Click split icon or `Ctrl+Shift+5`
- **New terminal**: Ctrl+Shift+`
- **Switch terminal**: Dropdown in terminal panel
- **Rename terminal**: Right-click → Rename

### IntelliSense

- `Ctrl+Space`: Trigger suggestions
- `Ctrl+Shift+Space`: Parameter hints
- Type and wait for automatic suggestions

### Snippets

Create custom snippets for common patterns:

1. `Ctrl+Shift+P` → "Configure User Snippets"
2. Select "python.json"
3. Add snippet:

```json
{
  "Database Connection": {
    "prefix": "dbconn",
    "body": [
      "from ${1:gds_postgres} import ${2:PostgresConnection}",
      "",
      "conn = ${2:PostgresConnection}(",
      "    host='${3:localhost}',",
      "    database='${4:mydb}',",
      "    user='${5:user}',",
      "    password='${6:password}'",
      ")",
      "$0"
    ],
    "description": "Database connection boilerplate"
  }
}
```

### Workspace Settings vs User Settings

- **User Settings**: Apply globally to all VS Code instances
- **Workspace Settings**: Apply only to this workspace (saved in workspace file)
- **Dev Container Settings**: Apply only in the dev container

Priority: Dev Container > Workspace > User

### Search and Replace

- **Find in file**: Ctrl+F
- **Replace in file**: Ctrl+H
- **Find in files**: Ctrl+Shift+F
- **Replace in files**: Ctrl+Shift+H
- **Use regex**: Click `.*` icon in search box

### Git Integration

- **Source Control panel**: Ctrl+Shift+G
- **Commit**: Ctrl+Enter in message box
- **Stage file**: Click + icon
- **View changes**: Click file in Source Control panel
- **Blame**: Install GitLens extension

### Debugging Tips

1. **Use logpoints** instead of print statements during debugging
2. **Step into** to dive into function calls
3. **Step over** to execute and move to next line
4. **Use Watch** panel to track variable changes
5. **Call Stack** shows execution path
6. **Debug Console** for REPL during debug session

### Performance

- **Disable unused extensions** in dev container
- **Exclude large directories** from search (node_modules, .venv, etc.)
- **Use workspace trust** for security
- **Close unused editor tabs** (set `workbench.editor.limit.enabled`)

### Remote Development

The dev container uses VS Code's Remote Development:

- Local VS Code connects to container
- Extensions run in container
- Files are in container filesystem
- Terminal is in container

**Benefits:**

- Consistent environment
- No local dependency conflicts
- Easy sharing with team

## Additional Resources

- [VS Code Python Documentation](https://code.visualstudio.com/docs/python/python-tutorial)
- [VS Code Debugging Guide](https://code.visualstudio.com/docs/editor/debugging)
- [VS Code Tips and Tricks](https://code.visualstudio.com/docs/getstarted/tips-and-tricks)
- [Remote Development Docs](https://code.visualstudio.com/docs/remote/remote-overview)
- [Python Testing in VS Code](https://code.visualstudio.com/docs/python/testing)
