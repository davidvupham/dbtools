# VS Code and Dev Container Documentation

Welcome to the VS Code and Dev Container documentation for the dbtools project. This guide will help you set up, use, and optimize your development environment.

## 📚 Documentation Index

### Getting Started

#### 1. [devcontainer.md](devcontainer.md) - Quick Reference

**Start here for a quick overview**

- What's included in the dev container
- How to open in VS Code
- Basic verification commands
- Kerberos configuration (optional)

**Best for**: Quick reference, experienced users

---

#### 2. [devcontainer-beginners-guide.md](devcontainer-beginners-guide.md) - Comprehensive Guide

**Detailed walkthrough for beginners**

- What is a dev container?
- Step-by-step setup instructions
- File-by-file explanation (Dockerfile, devcontainer.json, postCreate.sh)
- Building and running with Docker directly
- Verification procedures
- Troubleshooting common issues

**Best for**: First-time dev container users, understanding how everything works

---

### Development Workflows

#### 3. [features.md](features.md) - VS Code Features Guide

**Master VS Code for productive development**

- Debugging (Python & PowerShell)
  - 12 pre-configured debug scenarios
  - Breakpoints, logpoints, and debugging tips
- Tasks
  - 18+ predefined automation tasks
  - Testing, linting, formatting, building
- Port forwarding for databases
- Testing integration with Test Explorer
- Extensions and their usage
- Keyboard shortcuts
- Tips and tricks

**Best for**: Maximizing productivity in VS Code

---

#### 4. [devcontainer-sqltools.md](devcontainer-sqltools.md) - Database Connectivity

**Comprehensive database connectivity guide**

- Installed tools (Python & PowerShell)
- Verification commands
- Python examples:
  - PostgreSQL, Snowflake, SQL Server, MongoDB
  - Vault integration for credentials
- PowerShell examples:
  - dbatools for database administration
  - Pester for testing
- ODBC driver management
- Connection strings
- Troubleshooting

**Best for**: Working with databases, database connectivity issues

---

### Platform-Specific Guides

#### 5. [platform-specific.md](platform-specific.md) - Platform Optimization

**Platform-specific setup and optimization**

**WSL2 (Windows)**:

- Setup instructions
- Performance optimization
- File system best practices (critical!)
- Memory and CPU configuration
- WSL2-specific troubleshooting

**macOS**:

- Docker Desktop setup
- Apple Silicon (M1/M2/M3) considerations
- VirtioFS acceleration
- Performance optimization

**Linux**:

- Docker installation (Ubuntu, Fedora, RHEL)
- Non-root configuration
- SELinux and AppArmor
- Native Docker advantages

**Best for**: Platform-specific setup, performance issues, troubleshooting

---

### Advanced Topics

#### 6. [cicd-integration.md](cicd-integration.md) - CI/CD Integration

**Using dev containers in CI/CD pipelines**

- GitHub Actions workflows
- GitLab CI configurations
- Azure DevOps pipelines
- Jenkins pipeline examples
- Pre-commit hooks
- Caching strategies
- Matrix builds
- Best practices

**Best for**: Setting up CI/CD, ensuring consistency between local and remote

---

#### 7. [security-best-practices.md](security-best-practices.md) - Security Guide

**Security best practices and guidelines**

- Secrets management (environment variables, Vault)
- Container security
- Database credential handling
- SSH key protection
- Network security (TLS/SSL)
- Common security pitfalls
- Security checklist
- Incident response

**Best for**: Security-conscious development, production deployments

---

### Reference

#### 8. [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md) - Documentation Review

**Summary of documentation improvements**

- Issues identified and resolved
- New documentation created
- Changes made to existing docs
- Testing recommendations
- Maintenance guidelines

**Best for**: Understanding what changed, maintenance planning

---

## 🚀 Quick Start Paths

### Path 1: Beginner Setup (Recommended for First Time)

```
1. Read: devcontainer-beginners-guide.md
2. Setup: platform-specific.md (your platform section)
3. Security: security-best-practices.md (create .env file)
4. Features: features.md (learn debugging and tasks)
5. Database: devcontainer-sqltools.md (when needed)
```

### Path 2: Quick Start (Experienced Users)

```
1. Read: devcontainer.md
2. Review: platform-specific.md (platform optimization)
3. Reference: features.md (as needed)
```

### Path 3: Security-First Setup

```
1. Start: security-best-practices.md
2. Setup: devcontainer-beginners-guide.md
3. Platform: platform-specific.md
4. Reference: Other docs as needed
```

### Path 4: CI/CD Integration

```
1. Start: cicd-integration.md
2. Security: security-best-practices.md (secrets in CI)
3. Reference: devcontainer-beginners-guide.md (understanding the container)
```

---

## 🛠️ Common Tasks

### Setting Up for the First Time

1. **Install Prerequisites**
   - Docker Desktop (Windows/Mac) or Docker (Linux)
   - VS Code
   - Dev Containers extension
   - See: [devcontainer-beginners-guide.md](devcontainer-beginners-guide.md)

2. **Platform Optimization**
   - **WSL2 Users**: Critical to read [platform-specific.md](platform-specific.md) WSL2 section
   - Configure memory and file system properly

3. **Open in Dev Container**
   - Clone repository
   - Open in VS Code
   - Click "Reopen in Container" when prompted
   - See: [devcontainer.md](devcontainer.md)

4. **Configure Secrets**
   - Create `.env` file from template
   - See: [security-best-practices.md](security-best-practices.md)

### Running Tests

- **Via Task**: Press `Ctrl+Shift+B` → "Run All Tests"
- **Via Debug**: Press `F5` → Select test configuration
- **Via Terminal**: `pytest -v`
- See: [features.md](features.md#testing-integration)

### Debugging

- **Current File**: Press `F5`
- **Specific Module**: F5 → "Python: Module"
- **Tests**: F5 → "Debug: Current Test File"
- See: [features.md](features.md#debugging)

### Connecting to Databases

- **PostgreSQL**: See [devcontainer-sqltools.md](devcontainer-sqltools.md#postgresql-connection)
- **SQL Server**: See [devcontainer-sqltools.md](devcontainer-sqltools.md#sql-server-connection)
- **MongoDB**: See [devcontainer-sqltools.md](devcontainer-sqltools.md#mongodb-connection)
- **Snowflake**: See [devcontainer-sqltools.md](devcontainer-sqltools.md#snowflake-connection)

### Performance Issues

- **WSL2**: [platform-specific.md](platform-specific.md#wsl2-best-practices)
- **macOS**: [platform-specific.md](platform-specific.md#performance-optimization-for-macos)
- **Linux**: [platform-specific.md](platform-specific.md#performance-optimization-for-linux)
- **General**: [platform-specific.md](platform-specific.md#performance-optimization)

---

## 📋 What's Included in the Dev Container

### Core Tools

- **Python 3.13** via Miniconda (conda environment: `gds`)
- **PowerShell 7+** with database administration modules
- **Docker-in-Docker** for container operations
- **Git** with SSH key support

### Python Tools

- **Testing**: pytest, pytest-cov
- **Linting/Formatting**: ruff
- **Building**: wheel, build
- **Database**: pyodbc
- **Packages**: gds_database, gds_postgres, gds_snowflake, gds_vault, gds_mongodb, gds_mssql, gds_notification, gds_snmp_receiver

### PowerShell Modules

- **dbatools**: Database administration toolkit
- **Pester**: Testing framework
- **PSFramework**: Logging and configuration

### VS Code Extensions (20+)

- Python, Pylance, Debugpy
- PowerShell
- SQLTools + database drivers
- Jupyter
- Docker
- GitLens
- Coverage Gutters
- Testing adapters
- Code quality tools
- And more...

See: [devcontainer.md](devcontainer.md#what-you-get)

---

## 🔧 Workspace Configuration

The project includes a comprehensive VS Code workspace file: `dbtools.code-workspace`

**Features**:

- 12 pre-configured debug scenarios
- 18 automation tasks
- Optimized settings
- Extension recommendations
- Color theme (Peacock)

**Usage**:

```bash
code dbtools.code-workspace
```

See: [features.md](features.md)

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Document | Section |
|-------|----------|---------|
| Container won't build | [devcontainer-beginners-guide.md](devcontainer-beginners-guide.md) | Troubleshooting |
| Slow performance (WSL2) | [platform-specific.md](platform-specific.md) | WSL2 Best Practices |
| Database connection fails | [devcontainer-sqltools.md](devcontainer-sqltools.md) | Troubleshooting |
| Extension not working | [features.md](features.md) | Extensions |
| Port not forwarding | [features.md](features.md) | Port Forwarding |
| Tests not discovered | [features.md](features.md) | Testing Integration |
| Permission denied errors | [platform-specific.md](platform-specific.md) | Platform-specific issues |
| CI/CD pipeline failing | [cicd-integration.md](cicd-integration.md) | Troubleshooting |
| Secrets exposed | [security-best-practices.md](security-best-practices.md) | Incident Response |

---

## 🔐 Security Reminders

- ⚠️ Never commit `.env` files
- ⚠️ Use environment variables for secrets
- ⚠️ Rotate credentials regularly
- ⚠️ Use Vault for production secrets
- ⚠️ Keep SSH keys with correct permissions (600)
- ⚠️ Enable secret scanning in repository

See: [security-best-practices.md](security-best-practices.md)

---

## 📊 Documentation Map

```
docs/development/vscode/
├── README.md                           # This file - Start here
├── devcontainer.md                     # Quick reference
├── devcontainer-beginners-guide.md     # Detailed guide
├── devcontainer-sqltools.md            # Database connectivity
├── features.md                         # VS Code features
├── platform-specific.md                # Platform optimization
├── cicd-integration.md                 # CI/CD patterns
├── security-best-practices.md          # Security guide
└── REVIEW_SUMMARY.md                   # What changed
```

---

## 💡 Tips

1. **Use the workspace file**: `code dbtools.code-workspace` for best experience
2. **Learn keyboard shortcuts**: See [VSCODE_FEATURES.md](VSCODE_FEATURES.md#keyboard-shortcuts)
3. **Optimize for your platform**: Critical for WSL2 users
4. **Use tasks**: Press `Ctrl+Shift+B` for quick access
5. **Debug don't print**: Use VS Code debugging instead of print statements
6. **Test locally first**: Before pushing to CI/CD

---

## 🆘 Getting Help

1. **Check documentation**: Use this index to find relevant guide
2. **Search issues**: Check repository issues for similar problems
3. **Ask team**: Reach out to team members
4. **Create issue**: If problem persists, create a detailed issue

---

## 📝 Contributing to Documentation

When updating tools or configurations:

1. Update relevant documentation
2. Test changes in fresh container
3. Update [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md) if significant
4. Consider updating this README if structure changes

---

## 🎯 Summary

This documentation suite provides:

- ✅ Complete setup instructions for all platforms
- ✅ Comprehensive feature guides for VS Code
- ✅ Database connectivity examples
- ✅ Security best practices
- ✅ CI/CD integration patterns
- ✅ Troubleshooting guides
- ✅ Performance optimization tips

**Start with the Quick Start Path above, then dive into specific topics as needed.**

Happy coding! 🚀
