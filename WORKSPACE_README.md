# Snowflake Monitoring Workspace

This workspace contains two main components:

## 📦 [gds_snowflake/](gds_snowflake/) - Python Package

A reusable Python package for Snowflake database operations developed by the GDS team.

**Features:**
- Connection management with auto-reconnection
- Replication monitoring
- Failover group management
- Latency detection
- Type hints support (PEP 561)

**Installation:**
```bash
cd gds_snowflake
pip install .
```

**Documentation:** See [gds_snowflake/README.md](gds_snowflake/README.md)

## 🔍 [snowflake_monitoring/](snowflake_monitoring/) - Monitoring Application

A complete application for monitoring Snowflake replication with email notifications.

**Features:**
- Continuous replication monitoring
- Failure and latency detection
- Email alerts
- Systemd service support
- Docker-ready

**Quick Start:**
```bash
cd snowflake_monitoring
pip install -r requirements.txt
python monitor_snowflake_replication_v2.py myaccount
```

**Documentation:** See [snowflake_monitoring/README.md](snowflake_monitoring/README.md)

## Project Structure

```
snowflake/
├── gds_snowflake/              # 📦 Python Package
│   ├── gds_snowflake/          # Package source code
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── replication.py
│   │   └── py.typed
│   ├── tests/                  # Package tests
│   ├── setup.py                # Package setup
│   ├── pyproject.toml          # Modern Python packaging
│   ├── README.md               # Package documentation
│   ├── LICENSE                 # MIT License
│   └── MANIFEST.in             # Package manifest
│
├── snowflake_monitoring/       # 🔍 Monitoring Application
│   ├── monitor_snowflake_replication_v2.py  # Main script
│   ├── monitor_snowflake_replication.py     # Legacy script
│   ├── example_module_usage.py              # Usage examples
│   ├── config.sh.example                    # Config template
│   ├── requirements.txt                     # App dependencies
│   └── README.md                            # App documentation
│
├── tests/                      # 🧪 Shared tests (legacy)
├── .github/                    # GitHub Actions
└── snowflake-monitor.code-workspace  # VS Code workspace
```

## Quick Start

### 1. Install the Package

```bash
cd gds_snowflake
pip install .
```

### 2. Run the Monitoring Application

```bash
cd ../snowflake_monitoring

# Set credentials
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_PASSWORD="your_password"

# Run monitor
python monitor_snowflake_replication_v2.py myaccount
```

### 3. Use the Package in Your Code

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

conn = SnowflakeConnection(account='myaccount', user='myuser', password='mypass')
conn.connect()

repl = SnowflakeReplication(conn)
groups = repl.get_failover_groups()

for group in groups:
    print(f"{group.name}: {group.type}")
```

## Development

### Install in Development Mode

```bash
cd gds_snowflake
pip install -e ".[dev]"
```

### Run Tests

```bash
cd gds_snowflake
python run_tests.py
```

### VS Code Setup

Open the workspace:
```bash
code snowflake-monitor.code-workspace
```

See [VSCODE_SETUP.md](VSCODE_SETUP.md) for detailed setup instructions.

## Documentation

- **Package API**: [gds_snowflake/README.md](gds_snowflake/README.md)
- **Monitoring App**: [snowflake_monitoring/README.md](snowflake_monitoring/README.md)
- **VS Code Setup**: [VSCODE_SETUP.md](VSCODE_SETUP.md)
- **Testing Guide**: [TESTING.md](TESTING.md)
- **Project History**: [PROMPTS.md](PROMPTS.md)

## License

MIT License - See [gds_snowflake/LICENSE](gds_snowflake/LICENSE)

## Contributing

Contributions welcome! Please see individual component READMEs for specific guidelines.

## Support

- GitHub Issues: https://github.com/davidvupham/snowflake/issues
- Email: gds@example.com

---

**Note:** This workspace was generated using AI-assisted development. See [PROMPTS.md](PROMPTS.md) for the complete generation history.
