# CLI Tool Implementation Guide

This guide explains how the `gds-snmp-receiver` command-line tool is implemented, from entry point declaration to execution. Use this as a reference for implementing CLI tools in your own Python packages.

---

## Table of Contents

1. [Overview](#overview)
2. [Entry Point Declaration](#entry-point-declaration)
3. [The Main Function](#the-main-function)
4. [Argument Parsing](#argument-parsing)
5. [Auto-Generated Wrapper Script](#auto-generated-wrapper-script)
6. [Configuration Layering](#configuration-layering)
7. [Installation and Usage](#installation-and-usage)
8. [Testing the CLI](#testing-the-cli)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The CLI tool uses Python's **console scripts** entry point mechanism, which automatically creates executable scripts when your package is installed via pip. This is the modern, standard way to create command-line tools in Python.

**Key Components:**

```
pyproject.toml          → Declares the CLI entry point
receiver.py:main()      → Contains CLI logic
pip install             → Creates executable script
/bin/gds-snmp-receiver  → Auto-generated wrapper
```

**Flow:**

```
User types: gds-snmp-receiver --port 9162
    ↓
Shell executes: /path/to/bin/gds-snmp-receiver
    ↓
Python runs: gds_snmp_receiver.receiver.main()
    ↓
argparse parses: ['--port', '9162']
    ↓
SNMPReceiver created and started
```

---

## Entry Point Declaration

Entry points are declared in **`pyproject.toml`** (modern) or **`setup.py`** (legacy). We use both for maximum compatibility.

### In `pyproject.toml`:

```toml
[project.scripts]
gds-snmp-receiver = "gds_snmp_receiver.receiver:main"
```

**Format:** `command-name = "package.module:function"`

- **`gds-snmp-receiver`** - The command users will type
- **`gds_snmp_receiver.receiver`** - Python module path
- **`main`** - Function to call when command is executed

### In `setup.py` (equivalent):

```python
setup(
    name="gds-snmp-receiver",
    # ... other settings ...
    entry_points={
        "console_scripts": [
            "gds-snmp-receiver=gds_snmp_receiver.receiver:main",
        ],
    },
)
```

**Important Notes:**

- Entry point name (`gds-snmp-receiver`) can differ from package name
- Use hyphens for CLI commands (shell-friendly)
- Use underscores for Python modules (Python requirement)
- The function (`main`) will be called with no arguments by default

---

## The Main Function

The `main()` function in `gds_snmp_receiver/receiver.py` is the entry point for the CLI.

### Basic Structure:

```python
def main(argv: Optional[list[str]] = None) -> None:
    """Entry point for the CLI tool.
    
    Args:
        argv: Optional list of arguments. If None, sys.argv is used.
              This parameter enables testing without modifying sys.argv.
    """
    # 1. Create argument parser
    parser = argparse.ArgumentParser(description="gds_snmp_receiver CLI")
    
    # 2. Define arguments with defaults from environment
    parser.add_argument(
        "--host",
        default=os.environ.get("SNMP_LISTEN_HOST", "0.0.0.0"),
        help="Host/interface to listen on"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("SNMP_LISTEN_PORT", 162)),
        help="UDP port to listen on"
    )
    parser.add_argument(
        "--rabbit",
        default=os.environ.get("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/"),
        help="RabbitMQ URL"
    )
    parser.add_argument(
        "--queue",
        default=os.environ.get("SNMP_QUEUE", "alerts"),
        help="RabbitMQ queue name"
    )
    parser.add_argument(
        "--log-level",
        default=os.environ.get("SNMP_LOG_LEVEL", "INFO"),
        help="Logging level"
    )
    
    # 3. Parse arguments
    args = parser.parse_args(argv)
    
    # 4. Configure logging
    numeric_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    
    # 5. Create and run the service
    receiver = SNMPReceiver(
        listen_host=args.host,
        listen_port=args.port,
        rabbit_url=args.rabbit,
        queue_name=args.queue
    )
    receiver.run()


# Allow running as script: python -m gds_snmp_receiver.receiver
if __name__ == "__main__":
    main()
```

### Key Design Decisions:

**1. Optional `argv` parameter:**
```python
def main(argv: Optional[list[str]] = None) -> None:
```
- Enables unit testing without modifying `sys.argv`
- If `None`, `argparse` automatically uses `sys.argv[1:]`

**2. Environment variable fallbacks:**
```python
default=os.environ.get("SNMP_LISTEN_HOST", "0.0.0.0")
```
- Configuration priority: CLI args > Env vars > Hardcoded defaults
- User-friendly: can configure via environment or CLI

**3. Thin wrapper pattern:**
```python
receiver = SNMPReceiver(...)
receiver.run()
```
- CLI code is minimal - just argument parsing
- Business logic in `SNMPReceiver` class
- Easy to test, maintain, and use as library

**4. `if __name__ == "__main__"` guard:**
```python
if __name__ == "__main__":
    main()
```
- Allows running as: `python -m gds_snmp_receiver.receiver`
- Not required for CLI tool, but helpful during development

---

## Argument Parsing

### Basic Argument Types

**String argument (default):**
```python
parser.add_argument("--host", default="0.0.0.0", help="Bind address")
# Usage: --host 192.168.1.100
```

**Integer argument:**
```python
parser.add_argument("--port", type=int, default=162, help="UDP port")
# Usage: --port 9162
```

**Boolean flag:**
```python
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
# Usage: --debug (True if present, False otherwise)
```

**Choice from list:**
```python
parser.add_argument(
    "--log-level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    default="INFO"
)
# Usage: --log-level DEBUG
```

**Positional argument:**
```python
parser.add_argument("config_file", help="Path to configuration file")
# Usage: gds-snmp-receiver /path/to/config.yml
```

### Environment Variable Integration

**Pattern:**
```python
parser.add_argument(
    "--option",
    default=os.environ.get("ENV_VAR_NAME", "hardcoded_default"),
    help="Description (env: ENV_VAR_NAME)"
)
```

**Example:**
```python
parser.add_argument(
    "--rabbit",
    default=os.environ.get("RABBIT_URL", "amqp://localhost:5672/"),
    help="RabbitMQ connection URL (env: RABBIT_URL)"
)
```

**Benefits:**
- Users can choose configuration method
- Env vars useful for Docker/containers
- CLI args useful for quick testing
- Help text documents the env var

---

## Auto-Generated Wrapper Script

When you run `pip install`, setuptools creates an executable script automatically.

### Installation Process:

```bash
$ pip install gds_snmp_receiver/
Processing /path/to/gds_snmp_receiver
...
Installing collected packages: gds-snmp-receiver
Successfully installed gds-snmp-receiver-0.1.0
```

### Generated Script Location:

```
Virtual environment:
/path/to/venv/bin/gds-snmp-receiver

System-wide (Linux):
/usr/local/bin/gds-snmp-receiver

User install (Linux):
~/.local/bin/gds-snmp-receiver

Windows:
C:\PythonXX\Scripts\gds-snmp-receiver.exe
```

### Script Contents:

**On Linux/macOS:**
```python
#!/path/to/python
# -*- coding: utf-8 -*-
import re
import sys
from gds_snmp_receiver.receiver import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
```

**Key Features:**
- **Shebang**: Uses the correct Python interpreter
- **Import**: Imports your `main()` function
- **sys.exit()**: Propagates exit code properly
- **Executable**: Made executable via `chmod +x`

---

## Configuration Layering

Configuration priority (highest to lowest):

```
1. Command-line arguments    (--port 9162)
2. Environment variables      (SNMP_LISTEN_PORT=9162)
3. Hardcoded defaults         (port=162 in code)
```

### Example Scenarios:

**Scenario 1: All defaults**
```bash
$ gds-snmp-receiver
# Result: host=0.0.0.0, port=162, rabbit=amqp://guest:guest@rabbitmq:5672/
```

**Scenario 2: Environment variable**
```bash
$ export SNMP_LISTEN_PORT=9162
$ gds-snmp-receiver
# Result: port=9162 (from env var)
```

**Scenario 3: CLI argument overrides env var**
```bash
$ export SNMP_LISTEN_PORT=9162
$ gds-snmp-receiver --port 1162
# Result: port=1162 (CLI arg wins)
```

**Scenario 4: Mix of all three**
```bash
$ export SNMP_LISTEN_PORT=9162
$ export RABBIT_URL="amqp://prod:5672/"
$ gds-snmp-receiver --port 1162 --log-level DEBUG
# Result:
#   port=1162        (from CLI)
#   rabbit=...prod   (from env)
#   host=0.0.0.0     (default)
#   log-level=DEBUG  (from CLI)
```

### Implementation Pattern:

```python
# In main()
parser.add_argument(
    "--option",
    default=os.environ.get("ENV_VAR", "hardcoded_default")
)
args = parser.parse_args()
# args.option now contains the value with proper priority
```

**How it works:**
1. `default=` sets the fallback if argument not provided
2. `os.environ.get("ENV_VAR", "hardcoded_default")` checks env var first
3. If user provides CLI arg, it overrides the default
4. argparse handles the priority automatically

---

## Installation and Usage

### Development Installation:

```bash
# Editable install - changes to code take effect immediately
cd gds_snmp_receiver/
pip install -e .

# Verify installation
gds-snmp-receiver --help
```

### Production Installation:

```bash
# From wheel
pip install dist/gds_snmp_receiver-0.1.0-py3-none-any.whl

# From source
pip install gds_snmp_receiver/

# From PyPI (once published)
pip install gds-snmp-receiver
```

### Usage Examples:

**Basic usage:**
```bash
gds-snmp-receiver
```

**Custom configuration:**
```bash
gds-snmp-receiver \
  --host 0.0.0.0 \
  --port 9162 \
  --rabbit amqp://admin:pass@broker.example.com:5672/ \
  --queue snmp_alerts \
  --log-level DEBUG
```

**With environment variables:**
```bash
export SNMP_LISTEN_PORT=9162
export RABBIT_URL="amqp://user:pass@broker:5672/"
export SNMP_QUEUE="alerts"
gds-snmp-receiver
```

**In systemd service:**
```ini
[Unit]
Description=GDS SNMP Receiver
After=network.target

[Service]
Type=simple
User=snmp
Environment="SNMP_LISTEN_PORT=162"
Environment="RABBIT_URL=amqp://localhost:5672/"
ExecStart=/usr/local/bin/gds-snmp-receiver
Restart=always

[Install]
WantedBy=multi-user.target
```

**In Docker:**
```dockerfile
CMD ["gds-snmp-receiver", "--host", "0.0.0.0", "--port", "162"]
```

---

## Testing the CLI

### Unit Testing with pytest:

```python
# tests/test_cli.py
import pytest
from gds_snmp_receiver.receiver import main

def test_cli_help():
    """Test that --help works."""
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0

def test_cli_parses_arguments():
    """Test argument parsing without actually running."""
    # Mock SNMPReceiver.run() to prevent actual execution
    with patch('gds_snmp_receiver.receiver.SNMPReceiver') as mock:
        main(["--port", "9162", "--host", "127.0.0.1"])
        
        # Verify SNMPReceiver was called with correct args
        mock.assert_called_once_with(
            listen_host="127.0.0.1",
            listen_port=9162,
            rabbit_url="amqp://guest:guest@rabbitmq:5672/",
            queue_name="alerts"
        )

def test_environment_variable_defaults():
    """Test that environment variables are used as defaults."""
    import os
    os.environ["SNMP_LISTEN_PORT"] = "1234"
    
    with patch('gds_snmp_receiver.receiver.SNMPReceiver') as mock:
        main([])  # No CLI args
        
        # Should use env var for port
        assert mock.call_args[1]['listen_port'] == 1234
```

### Manual Testing:

```bash
# Test help
gds-snmp-receiver --help

# Test with mock RabbitMQ (will fail to connect but tests argument parsing)
gds-snmp-receiver \
  --host 127.0.0.1 \
  --port 9162 \
  --rabbit amqp://fake:5672/ \
  --log-level DEBUG

# Test environment variables
export SNMP_LISTEN_PORT=9162
gds-snmp-receiver --log-level DEBUG

# Verify it's in PATH
which gds-snmp-receiver
type gds-snmp-receiver
```

### Verify Installation:

```bash
# Check if command exists
command -v gds-snmp-receiver

# Check pip installation
pip show gds-snmp-receiver

# Test import
python -c "from gds_snmp_receiver.receiver import main; print('OK')"

# Test CLI
gds-snmp-receiver --version  # if you implement --version
```

---

## Best Practices

### 1. **Use Type Hints**

```python
from typing import Optional

def main(argv: Optional[list[str]] = None) -> None:
    """Entry point with proper type hints."""
    pass
```

### 2. **Provide Good Help Text**

```python
parser = argparse.ArgumentParser(
    description="SNMP trap receiver with RabbitMQ integration",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  %(prog)s --port 9162
  %(prog)s --rabbit amqp://localhost/ --log-level DEBUG
  
Environment variables:
  SNMP_LISTEN_PORT    UDP port (default: 162)
  RABBIT_URL          RabbitMQ URL
  SNMP_QUEUE          Queue name (default: alerts)
    """
)

parser.add_argument(
    "--port",
    type=int,
    metavar="PORT",
    help="UDP port to listen on (env: SNMP_LISTEN_PORT, default: 162)"
)
```

### 3. **Validate Arguments**

```python
args = parser.parse_args(argv)

# Validate port range
if not (1 <= args.port <= 65535):
    parser.error(f"Port must be between 1 and 65535, got {args.port}")

# Validate log level
if args.log_level.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
    parser.error(f"Invalid log level: {args.log_level}")
```

### 4. **Handle Keyboard Interrupt Gracefully**

```python
def main(argv: Optional[list[str]] = None) -> None:
    args = parser.parse_args(argv)
    
    receiver = SNMPReceiver(...)
    
    try:
        receiver.run()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        receiver.stop()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

### 5. **Keep CLI Code Thin**

```python
# ❌ Bad: Business logic in CLI
def main(argv=None):
    args = parser.parse_args(argv)
    # 100 lines of SNMP trap handling code here...

# ✅ Good: Delegate to class
def main(argv=None):
    args = parser.parse_args(argv)
    receiver = SNMPReceiver(...)  # Business logic in class
    receiver.run()
```

### 6. **Support Configuration Files**

```python
parser.add_argument(
    "--config",
    type=str,
    help="Path to configuration file"
)

args = parser.parse_args(argv)

if args.config:
    # Load config file and merge with args
    config = load_config(args.config)
    # CLI args override config file
```

### 7. **Document the Entry Point**

```python
def main(argv: Optional[list[str]] = None) -> None:
    """Main entry point for the gds-snmp-receiver CLI tool.
    
    This function is called when users run 'gds-snmp-receiver' command.
    It parses command-line arguments, configures logging, creates an
    SNMPReceiver instance, and starts the service.
    
    Args:
        argv: Optional list of command-line arguments. If None,
              sys.argv is used. This parameter exists to enable
              testing without modifying sys.argv.
    
    Returns:
        None. The function blocks until the service is terminated.
    
    Raises:
        SystemExit: On argument parsing errors or --help/--version.
    
    Examples:
        # Run with defaults
        $ gds-snmp-receiver
        
        # Run with custom port
        $ gds-snmp-receiver --port 9162
        
        # Run with environment variables
        $ SNMP_LISTEN_PORT=9162 gds-snmp-receiver
    """
    # Implementation...
```

---

## Troubleshooting

### Problem: Command not found

```bash
$ gds-snmp-receiver
-bash: gds-snmp-receiver: command not found
```

**Solutions:**

1. **Check installation:**
   ```bash
   pip show gds-snmp-receiver
   ```

2. **Check if script exists:**
   ```bash
   find $(python -m site --user-base) -name gds-snmp-receiver
   ```

3. **Update PATH:**
   ```bash
   export PATH="$HOME/.local/bin:$PATH"  # Linux
   # Add to ~/.bashrc or ~/.zshrc
   ```

4. **Reinstall:**
   ```bash
   pip uninstall gds-snmp-receiver
   pip install gds_snmp_receiver/
   ```

### Problem: Wrong Python version

```bash
$ gds-snmp-receiver
python: No module named gds_snmp_receiver
```

**Solutions:**

1. **Check shebang in script:**
   ```bash
   head -1 $(which gds-snmp-receiver)
   # Should point to your Python
   ```

2. **Reinstall in correct environment:**
   ```bash
   # Activate virtual environment first
   source venv/bin/activate
   pip install --force-reinstall gds_snmp_receiver/
   ```

### Problem: Import errors

```bash
$ gds-snmp-receiver
ModuleNotFoundError: No module named 'pysnmp'
```

**Solutions:**

1. **Install dependencies:**
   ```bash
   pip install pysnmp pika
   ```

2. **Check requirements are declared:**
   ```toml
   # In pyproject.toml
   dependencies = [
       "pysnmp>=4.4.12",
       "pika>=1.3.0",
   ]
   ```

3. **Reinstall package:**
   ```bash
   pip install --force-reinstall gds_snmp_receiver/
   ```

### Problem: Entry point not working after code changes

**Solution:**
```bash
# Development mode ensures changes take effect
pip install -e gds_snmp_receiver/

# Or reinstall
pip uninstall gds-snmp-receiver
pip install gds_snmp_receiver/
```

### Problem: Multiple versions installed

```bash
$ which gds-snmp-receiver
/usr/local/bin/gds-snmp-receiver
$ pip list | grep gds-snmp
gds-snmp-receiver  0.1.0
gds-snmp-receiver  0.2.0
```

**Solution:**
```bash
# Uninstall all versions
pip uninstall gds-snmp-receiver -y
pip uninstall gds-snmp-receiver -y  # Repeat until "not installed"

# Reinstall correct version
pip install gds_snmp_receiver/
```

---

## Summary

The CLI tool implementation follows these steps:

1. **Declare entry point** in `pyproject.toml`
2. **Write `main()` function** with argparse
3. **Install package** with pip
4. **Auto-generated script** appears in `bin/`
5. **Users run command** from anywhere

**Key Files:**
- `pyproject.toml` - Entry point declaration
- `gds_snmp_receiver/receiver.py` - CLI implementation
- `/bin/gds-snmp-receiver` - Auto-generated wrapper

**Key Concepts:**
- Entry points create executable scripts automatically
- Configuration layering: CLI > Env vars > Defaults
- Thin wrapper pattern: CLI delegates to business logic
- Cross-platform: Works on Linux, macOS, Windows

This approach is the Python standard for creating command-line tools and is used by thousands of packages including pip, pytest, black, and many others.
