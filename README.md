# DBTools Workspace

This workspace contains multiple database tools and packages:

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
python monitor_snowflake_replication.py myaccount
```

**Documentation:** See [snowflake_monitoring/README.md](snowflake_monitoring/README.md)

## Project Structure

```
dbtools/
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
│   ├── monitor_snowflake_replication.py     # Main script
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

# Run monitor
python monitor_snowflake_replication.py myaccount
```

### 3. Use the Package in Your Code

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

conn = SnowflakeConnection(
    account='myaccount', 
    user='myuser', 
    vault_secret_path='data/snowflake',
    vault_mount_point='secret'
)
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
# Option A: unittest runner
python run_tests.py

# Option B: pytest with coverage (recommended)
pytest -q --maxfail=1 --disable-warnings --cov=gds_snowflake --cov-report=term-missing
```
### Linting and Formatting

Use the repo lint helper script (Ruff):

```bash
# From repo root
./lint.sh                 # Check only
./lint.sh --stats         # Check with statistics
./lint.sh --fix           # Auto-fix where safe
./lint.sh --fix --format  # Auto-fix + format code
```

Notes:
- The script runs Ruff across the entire repo.
- Some legacy subpackages may require manual fixes for examples/tests.
- For iterative work, you can lint a specific file with: `./lint.sh --file path/to/file.py`


### VS Code Setup

Open the workspace:
```bash
code snowflake-monitor.code-workspace
```

See [VSCODE_SETUP.md](VSCODE_SETUP.md) for detailed setup instructions.

## Documentation

- **Package API**: [gds_snowflake/README.md](gds_snowflake/README.md)
- **Monitoring App**: [snowflake_monitoring/README.md](snowflake_monitoring/README.md)
- **Python Tutorials**: [docs/tutorials/README.md](docs/tutorials/README.md) - Learn Python through this codebase
- **OOP Guide**: [docs/tutorials/02_OBJECT_ORIENTED_PROGRAMMING_GUIDE.md](docs/tutorials/02_OBJECT_ORIENTED_PROGRAMMING_GUIDE.md) - Complete OOP tutorial
- **Advanced OOP**: [docs/tutorials/04_ADVANCED_OOP_CONCEPTS.md](docs/tutorials/04_ADVANCED_OOP_CONCEPTS.md) - Advanced OOP concepts
- **VS Code Setup**: [VSCODE_SETUP.md](VSCODE_SETUP.md)
- **Testing Guide**: [TESTING.md](TESTING.md)
- **Project History**: [PROMPTS.md](PROMPTS.md)

## License

MIT License - See [gds_snowflake/LICENSE](gds_snowflake/LICENSE)

## Contributing

Contributions welcome! Please see individual component READMEs for specific guidelines.

## Support

- GitHub Issues: https://github.com/davidvupham/dbtools/issues
- Email: gds@example.com

---

**Note:** This workspace was generated using AI-assisted development. See [PROMPTS.md](PROMPTS.md) for the complete generation history.
