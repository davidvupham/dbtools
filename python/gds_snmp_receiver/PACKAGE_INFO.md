# GDS SNMP Receiver - Self-Contained Package

This directory contains a **fully self-contained** SNMP trap receiver package with all necessary files for development, testing, deployment, and documentation.

## 📁 Package Structure

```
gds_snmp_receiver/
├── Core Application Files
│   ├── __init__.py              # Package initialization
│   ├── receiver.py              # CLI entry point
│   └── core.py                  # Main SNMPReceiver class
│
├── Docker & Deployment
│   ├── Dockerfile               # Container image definition
│   ├── entrypoint.sh            # Container entrypoint script
│   ├── healthcheck.py           # Container health check
│   ├── docker-compose.yml       # Production deployment config
│   ├── docker-compose.e2e.yml   # E2E test environment
│   └── requirements.txt         # Python dependencies
│
├── Testing & Tools
│   ├── tools/
│   │   ├── e2e_send_and_check.py  # E2E test script
│   │   └── E2E_README.md          # E2E test documentation
│   └── tests/                     # Unit tests
│
└── Documentation
    ├── README.md                # Quick start & overview
    ├── TUTORIAL.md              # Comprehensive learning guide
    ├── ARCHITECTURE.md          # Design & internal documentation
    ├── DEVELOPER_GUIDE.md       # Code-level developer guide
    ├── QUICK_REFERENCE.md       # Command cheat sheet
    ├── DOCKER_E2E_HOWTO.md      # Containerization guide
    └── PACKAGE_INFO.md          # This file
```

## 🚀 Quick Start

All commands should be run from **within this directory** (`gds_snmp_receiver/`).

### Installation & Local Development

```bash
# Option 1: Install as package (recommended)
pip install .

# Option 2: Install from wheel
pip install dist/gds_snmp_receiver-0.1.0-py3-none-any.whl

# Option 3: Development mode (editable install)
pip install -e .

# Then run with CLI tool
gds-snmp-receiver --host 0.0.0.0 --port 9162
```

### Docker Deployment

```bash
# Build container
docker build -t gds-snmp-receiver:latest .

# Run with Docker Compose (production)
docker compose up -d

# Or run standalone
docker run -d -p 162:162/udp \
  -e RABBIT_URL="amqp://guest:guest@rabbitmq:5672/" \
  gds-snmp-receiver:latest
```

### Testing

```bash
# Run E2E test
docker compose -f docker-compose.e2e.yml up -d
docker compose -f docker-compose.e2e.yml run --rm snmp-sender \
  python tools/e2e_send_and_check.py
docker compose -f docker-compose.e2e.yml down

# Run unit tests
pytest tests/
```

## 📖 Documentation Guide

Choose your documentation based on your needs:

- **New to the package?** Start with [README.md](README.md)
- **Learning how it works?** Read [TUTORIAL.md](TUTORIAL.md)
- **Understanding the design?** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Modifying the code?** Check [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **Need quick commands?** Use [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Docker & E2E testing?** Read [DOCKER_E2E_HOWTO.md](DOCKER_E2E_HOWTO.md)
- **Building & distributing?** See [BUILD_GUIDE.md](BUILD_GUIDE.md)
- **Implementing CLI tools?** See [CLI_IMPLEMENTATION_GUIDE.md](CLI_IMPLEMENTATION_GUIDE.md)

## ✨ Key Features

- **✅ Self-Contained**: Everything needed is in this directory
- **✅ Production Ready**: Docker support with health checks
- **✅ Fully Tested**: E2E test framework included
- **✅ Well Documented**: Multiple docs for different needs
- **✅ Easy to Deploy**: Docker Compose configurations included

## 🔧 Configuration

All configuration via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SNMP_LISTEN_HOST` | `0.0.0.0` | Interface to bind |
| `SNMP_LISTEN_PORT` | `162` | UDP port for SNMP traps |
| `RABBIT_URL` | `amqp://guest:guest@rabbitmq:5672/` | RabbitMQ connection |
| `SNMP_QUEUE` | `alerts` | Queue name |
| `GDS_SNMP_LOG_LEVEL` | `INFO` | Log level |

## 🏗️ Development Workflow

1. **Modify code** in `gds_snmp_receiver/core.py` or `gds_snmp_receiver/receiver.py`
2. **Run tests** with pytest or E2E framework
3. **Update docs** if adding features
4. **Build package** with `python -m build`
5. **Test installation** with `pip install dist/*.whl`
6. **Build & test Docker** with `docker build`
7. **Deploy** using docker-compose.yml

## 📦 Building & Distribution

### Build Wheel Package

```bash
# Install build tools
pip install build

# Build source distribution and wheel
python -m build

# Output files in dist/:
# - gds_snmp_receiver-0.1.0-py3-none-any.whl
# - gds_snmp_receiver-0.1.0.tar.gz
```

### Install Package

```bash
# From wheel
pip install dist/gds_snmp_receiver-0.1.0-py3-none-any.whl

# From source (development mode)
pip install -e .

# From PyPI (once published)
pip install gds-snmp-receiver
```

### Test Installation

```bash
# Verify CLI tool works
gds-snmp-receiver --help

# Import in Python
python -c "from gds_snmp_receiver import SNMPReceiver; print('OK')"
```

## 📦 Dependencies

All Python dependencies are specified in `requirements.txt`:
- `pysnmp >= 7.1.0` - SNMP protocol support
- `pika >= 1.3.0` - RabbitMQ client

## 🤝 Integration

This package can be used as:
- **Standalone service**: Deploy with Docker
- **Library**: Import `SNMPReceiver` from Python code
- **Part of larger system**: Use with your RabbitMQ infrastructure

## 📝 License

See LICENSE file in repository root.

## 🆘 Support

- Check [README.md](README.md) troubleshooting section
- Review [TUTORIAL.md](TUTORIAL.md) testing section
- See [DOCKER_E2E_HOWTO.md](DOCKER_E2E_HOWTO.md) for E2E issues

---

**Note**: This package is fully self-contained. You don't need any files from parent directories to build, test, or deploy.
