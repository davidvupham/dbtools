# Recommended Directory Structure for Dev/Prod Environments

This document proposes a best-practice directory structure for organizing development environment setup and production runtime environment scripts and documentation.

## Current State Analysis

Your repository already has good foundations:
- ✅ `ansible/` with environment-separated inventory (development, test, staging, production)
- ✅ `docker/` for containerized environments
- ✅ `scripts/` for utility scripts
- ✅ `docs/development/` for developer documentation
- ✅ `.devcontainer/` for VS Code dev containers

## Proposed Structure

```
dbtools/
├── environments/                    # NEW: Environment-specific configurations
│   ├── development/
│   │   ├── README.md                # Dev environment setup guide
│   │   ├── requirements.txt         # Dev-specific dependencies
│   │   ├── setup.sh                 # Dev environment bootstrap script
│   │   ├── verify.sh                # Verify dev environment is correct
│   │   ├── scripts/                 # Dev-specific utility scripts
│   │   │   ├── setup-python-env.sh
│   │   │   ├── setup-docker.sh
│   │   │   └── setup-ide.sh
│   │   └── config/                  # Dev configuration files
│   │       ├── .env.example
│   │       ├── docker-compose.override.yml
│   │       └── ide-settings.json
│   │
│   ├── production/
│   │   ├── README.md                # Production deployment guide
│   │   ├── requirements.txt         # Production dependencies (pinned versions)
│   │   ├── deploy.sh                # Production deployment script
│   │   ├── healthcheck.sh           # Production health verification
│   │   ├── rollback.sh             # Rollback procedure
│   │   ├── scripts/                 # Production runtime scripts
│   │   │   ├── backup.sh
│   │   │   ├── monitoring-setup.sh
│   │   │   └── security-hardening.sh
│   │   └── config/                  # Production configuration
│   │       ├── docker-compose.prod.yml
│   │       ├── nginx.conf
│   │       └── prometheus.yml
│   │
│   ├── staging/                     # Similar structure to production
│   └── test/                        # Similar structure to development
│
├── ansible/                         # EXISTING: Infrastructure as Code
│   ├── inventory/
│   │   ├── development/             # Dev environment inventory
│   │   ├── production/              # Prod environment inventory
│   │   ├── staging/
│   │   └── test/
│   ├── playbooks/
│   │   ├── development/
│   │   │   ├── setup-dev-environment.yml
│   │   │   └── configure-dev-tools.yml
│   │   └── production/
│   │       ├── deploy-to-prod.yml
│   │       ├── configure-prod-environment.yml
│   │       └── backup-prod.yml
│   └── roles/
│       ├── dev-environment/         # Role for dev setup
│       └── prod-environment/        # Role for prod setup
│
├── docker/                          # EXISTING: Container definitions
│   ├── development/                 # NEW: Dev-specific Dockerfiles
│   │   ├── Dockerfile.dev
│   │   └── docker-compose.dev.yml
│   └── production/                  # NEW: Prod-specific Dockerfiles
│       ├── Dockerfile.prod
│       └── docker-compose.prod.yml
│
├── scripts/                         # EXISTING: General utility scripts
│   ├── development/                 # NEW: Dev-specific scripts
│   │   ├── setup-prompt.sh          # Shell prompt customization
│   │   ├── install-dependencies.sh
│   │   └── run-tests.sh
│   └── production/                  # NEW: Prod-specific scripts
│       ├── deploy.sh
│       ├── monitor.sh
│       └── backup.sh
│
└── docs/
    ├── development/                 # EXISTING: Dev documentation
    │   ├── environment-setup.md     # Main dev setup guide
    │   ├── onboarding.md
    │   └── tools/                   # Tool-specific guides
    │       ├── python-setup.md
    │       ├── docker-setup.md
    │       └── ide-setup.md
    │
    └── operations/                  # NEW: Operations/production docs
        ├── deployment.md            # Production deployment guide
        ├── monitoring.md            # Production monitoring setup
        ├── troubleshooting.md       # Production troubleshooting
        └── runbooks/                # Operational runbooks
            ├── deploy-to-prod.md
            ├── rollback-procedure.md
            └── incident-response.md
```

## Key Principles

### 1. Clear Separation of Concerns

**Development Environment:**
- Focus: Setup, local development, testing, IDE configuration
- Scripts: Setup/bootstrap, development tools, testing
- Documentation: Onboarding, local setup, developer guides

**Production Environment:**
- Focus: Deployment, runtime, monitoring, security, backup/recovery
- Scripts: Deployment, health checks, monitoring, backup, rollback
- Documentation: Deployment procedures, operational runbooks, troubleshooting

### 2. Environment-Specific Directories

Each environment (dev/test/staging/prod) should have:
- Its own configuration files
- Environment-specific scripts
- Environment-specific documentation
- Clear README explaining purpose and usage

### 3. Shared vs. Environment-Specific

**Shared (in root):**
- Common scripts used by all environments (`scripts/`)
- Shared documentation (`docs/`)
- Common configuration templates

**Environment-Specific:**
- Actual configuration values (don't commit secrets!)
- Environment-specific deployment procedures
- Environment-specific tooling

## Implementation Recommendations

### Phase 1: Create Base Structure

1. **Create `environments/` directory structure:**
   ```bash
   mkdir -p environments/{development,production}/{scripts,config}
   ```

2. **Move environment-specific scripts:**
   - Dev setup scripts → `environments/development/scripts/`
   - Prod deployment scripts → `environments/production/scripts/`

3. **Create environment README files** with clear purpose and usage

### Phase 2: Organize Documentation

1. **Create `docs/operations/` for production docs:**
   ```bash
   mkdir -p docs/operations/runbooks
   ```

2. **Separate dev docs from ops docs:**
   - Developer onboarding → `docs/development/`
   - Production deployment → `docs/operations/`

### Phase 3: Consolidate Scripts

1. **Move dev-specific scripts:**
   ```bash
   # Example: Move prompt script to dev environment
   mv scripts/set_prompt.sh environments/development/scripts/
   ```

2. **Keep shared utilities in `scripts/`:**
   - Scripts used by multiple environments
   - General-purpose utilities

## Example File Contents

### `environments/development/README.md`

```markdown
# Development Environment Setup

This directory contains scripts and configuration for setting up a local development environment.

## Quick Start

```bash
# Run the bootstrap script
./environments/development/setup.sh

# Verify your environment
./environments/development/verify.sh
```

## What Gets Installed

- Python development environment (via UV)
- Docker and Docker Compose
- Development tools (Git, editors, etc.)
- VS Code extensions
- Shell configuration

## Manual Setup

See [docs/development/environment-setup.md](../../docs/development/environment-setup.md) for detailed manual setup instructions.

## Scripts

- `setup.sh` - Complete environment bootstrap
- `verify.sh` - Verify environment is correctly configured
- `scripts/setup-python-env.sh` - Python environment only
- `scripts/setup-docker.sh` - Docker setup only
```

### `environments/production/README.md`

```markdown
# Production Environment

This directory contains scripts and configuration for deploying and operating the production environment.

⚠️ **SECURITY WARNING:** Never commit secrets or credentials to this repository!

## Deployment

See [docs/operations/deployment.md](../../docs/operations/deployment.md) for detailed deployment procedures.

## Quick Reference

```bash
# Deploy to production (requires proper authentication)
./environments/production/deploy.sh

# Verify deployment health
./environments/production/healthcheck.sh

# Rollback if needed
./environments/production/rollback.sh <version>
```

## Scripts

- `deploy.sh` - Full production deployment
- `healthcheck.sh` - Verify production health
- `rollback.sh` - Rollback to previous version
- `scripts/backup.sh` - Create backup
- `scripts/monitoring-setup.sh` - Setup monitoring
```

## Benefits of This Structure

1. **Clear Intent**: Easy to understand what's for dev vs prod
2. **Scalability**: Easy to add new environments (staging, test)
3. **Maintainability**: Changes to one environment don't affect others
4. **Onboarding**: New developers know exactly where to look
5. **Security**: Clear separation helps prevent accidental prod changes
6. **Documentation**: Organized docs match the code structure

## Migration Path

To migrate existing content:

1. **Identify environment-specific content:**
   - Ansible playbooks → Already well-organized ✅
   - Docker configs → Move environment-specific to `docker/{env}/`
   - Scripts → Move to `environments/{env}/scripts/` or `scripts/{env}/`

2. **Create new directories incrementally:**
   - Start with one environment (development) as a template
   - Copy structure for other environments

3. **Update references:**
   - Update README files to reference new locations
   - Update CI/CD pipelines if needed
   - Update documentation links

## Alternative: Simpler Structure (If Preferred)

If the above seems too complex, a simpler approach:

```
dbtools/
├── dev/                             # All dev setup
│   ├── setup.sh
│   ├── scripts/
│   └── README.md
├── prod/                            # All prod deployment
│   ├── deploy.sh
│   ├── scripts/
│   └── README.md
└── scripts/                         # Shared utilities
    └── ...
```

This simpler structure may be better for smaller teams or projects.

## Best Practices Checklist

- [ ] Clear separation between dev and prod
- [ ] Environment-specific configuration templates (no secrets!)
- [ ] README in each directory explaining purpose
- [ ] Version control for infrastructure as code (Ansible)
- [ ] Documentation for both setup and operations
- [ ] Scripts are idempotent (can run multiple times safely)
- [ ] Verification scripts to validate environment
- [ ] Clear rollback procedures for production
- [ ] Security considerations documented
- [ ] CI/CD integration points identified
