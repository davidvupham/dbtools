# Root Directory Cleanup Plan

## Overview

This document outlines how to organize the remaining files in the root directory now that the main code has been restructured into `gds_snowflake/` and `snowflake_monitoring/` directories.

## Current Root Directory Status

### Files to Organize

```
snowflake/
├── MANIFEST.in              # Old package manifest
├── NEW_STRUCTURE.md         # Documentation
├── PACKAGE_REFACTORING.md   # Documentation
├── PROJECT_STRUCTURE.md     # Documentation
├── PROMPT_COMPARISON.md     # Documentation
├── PROMPTS.md               # Documentation
├── pytest.ini               # Old test config
├── README.md                # Old README (replace)
├── REFACTORING.md           # Documentation
├── requirements-dev.txt     # Old dev requirements
├── requirements.txt         # Old requirements
├── run_tests.py             # Old test runner
├── setup.py                 # Old setup (delete)
├── test_modules.py          # Old test script
├── test_setup.py            # Old test script
├── TESTING_QUICK_REF.md     # Documentation
├── TESTING.md               # Documentation
├── UNIT_TESTING_SUMMARY.md  # Documentation
├── VSCODE_SETUP.md          # Documentation
├── VSCODE_WORKSPACE_SUMMARY.md  # Documentation
├── tests/                   # Old test directory
└── gds_snowflake.egg-info/  # Old build artifacts
```

### Files to Keep at Root

```
snowflake/
├── .git/                    # Git repository
├── .gitignore               # Git ignore file
├── README.md                # Workspace overview (replace with WORKSPACE_README.md)
├── RESTRUCTURING_SUMMARY.md # Restructuring documentation
├── WORKSPACE_README.md      # New workspace README
└── snowflake-monitor.code-workspace  # VS Code workspace
```

## Proposed Directory Structure

```
snowflake/
│
├── README.md                # Symlink or copy of WORKSPACE_README.md
├── RESTRUCTURING_SUMMARY.md # Summary of restructuring changes
├── .gitignore               # Git ignore file
├── snowflake-monitor.code-workspace  # VS Code workspace
│
├── gds_snowflake/           # 📦 Python Package (self-contained)
│   ├── gds_snowflake/
│   ├── tests/
│   ├── setup.py
│   ├── pyproject.toml
│   ├── README.md
│   ├── LICENSE
│   └── ...
│
├── snowflake_monitoring/    # 🔍 Monitoring Application (self-contained)
│   ├── monitor_snowflake_replication_v2.py
│   ├── README.md
│   ├── requirements.txt
│   └── ...
│
└── docs/                    # 📚 Project Documentation
    ├── development/
    │   ├── TESTING.md
    │   ├── TESTING_QUICK_REF.md
    │   ├── UNIT_TESTING_SUMMARY.md
    │   └── REFACTORING.md
    │
    ├── project_history/
    │   ├── PROMPTS.md
    │   ├── PROMPT_COMPARISON.md
    │   ├── PROJECT_STRUCTURE.md
    │   ├── NEW_STRUCTURE.md
    │   └── PACKAGE_REFACTORING.md
    │
    └── vscode/
        ├── VSCODE_SETUP.md
        └── VSCODE_WORKSPACE_SUMMARY.md
```

## Step-by-Step Cleanup Commands

### Step 1: Create Documentation Directory Structure

```bash
cd /home/dpham/src/snowflake

# Create documentation directories
mkdir -p docs/development
mkdir -p docs/project_history
mkdir -p docs/vscode
```

### Step 2: Move Development Documentation

```bash
# Move testing documentation
mv TESTING.md docs/development/
mv TESTING_QUICK_REF.md docs/development/
mv UNIT_TESTING_SUMMARY.md docs/development/

# Move refactoring documentation
mv REFACTORING.md docs/development/
```

### Step 3: Move Project History Documentation

```bash
# Move prompt and structure documentation
mv PROMPTS.md docs/project_history/
mv PROMPT_COMPARISON.md docs/project_history/
mv PROJECT_STRUCTURE.md docs/project_history/
mv NEW_STRUCTURE.md docs/project_history/
mv PACKAGE_REFACTORING.md docs/project_history/
```

### Step 4: Move VS Code Documentation

```bash
# Move VS Code setup documentation
mv VSCODE_SETUP.md docs/vscode/
mv VSCODE_WORKSPACE_SUMMARY.md docs/vscode/
```

### Step 5: Clean Up Old Files

```bash
# Remove old build artifacts
rm -rf gds_snowflake.egg-info/

# Remove old package files (now in gds_snowflake/)
rm -f setup.py
rm -f MANIFEST.in
rm -f requirements.txt
rm -f requirements-dev.txt
rm -f pytest.ini
rm -f run_tests.py
rm -f test_modules.py
rm -f test_setup.py

# Keep old tests directory or remove it (tests are now in gds_snowflake/tests/)
# Option 1: Remove it
rm -rf tests/

# Option 2: Keep it as archive
mkdir -p docs/archive
mv tests/ docs/archive/tests_original/
```

### Step 6: Update Root README

```bash
# Replace old README with workspace README
mv README.md docs/archive/README_old.md  # Archive old README
cp WORKSPACE_README.md README.md          # Use new README as main
```

### Step 7: Create docs/README.md

Create an index for the documentation:

```bash
cat > docs/README.md << 'EOF'
# Project Documentation

This directory contains all project documentation organized by category.

## 📚 Documentation Structure

### [development/](development/) - Development Documentation
- [TESTING.md](development/TESTING.md) - Complete testing guide
- [TESTING_QUICK_REF.md](development/TESTING_QUICK_REF.md) - Quick testing reference
- [UNIT_TESTING_SUMMARY.md](development/UNIT_TESTING_SUMMARY.md) - Unit testing summary
- [REFACTORING.md](development/REFACTORING.md) - Refactoring history

### [project_history/](project_history/) - Project History
- [PROMPTS.md](project_history/PROMPTS.md) - AI prompts used to generate project
- [PROMPT_COMPARISON.md](project_history/PROMPT_COMPARISON.md) - Prompt strategy comparison
- [PROJECT_STRUCTURE.md](project_history/PROJECT_STRUCTURE.md) - Original structure
- [NEW_STRUCTURE.md](project_history/NEW_STRUCTURE.md) - Updated structure
- [PACKAGE_REFACTORING.md](project_history/PACKAGE_REFACTORING.md) - Package refactoring notes

### [vscode/](vscode/) - VS Code Setup
- [VSCODE_SETUP.md](vscode/VSCODE_SETUP.md) - VS Code configuration guide
- [VSCODE_WORKSPACE_SUMMARY.md](vscode/VSCODE_WORKSPACE_SUMMARY.md) - Workspace summary

## Component Documentation

For component-specific documentation, see:
- **Package**: [../gds_snowflake/README.md](../gds_snowflake/README.md)
- **Application**: [../snowflake_monitoring/README.md](../snowflake_monitoring/README.md)

## Quick Links

- [Workspace Overview](../README.md)
- [Restructuring Summary](../RESTRUCTURING_SUMMARY.md)
EOF
```

## Final Directory Structure

After cleanup:

```
snowflake/
│
├── .git/
├── .gitignore
├── README.md                         # Main workspace README
├── RESTRUCTURING_SUMMARY.md          # Restructuring documentation
├── snowflake-monitor.code-workspace  # VS Code workspace
│
├── gds_snowflake/                    # 📦 Self-contained package
│   ├── gds_snowflake/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── replication.py
│   │   └── py.typed
│   ├── tests/
│   ├── setup.py
│   ├── pyproject.toml
│   ├── README.md
│   ├── LICENSE
│   └── ...
│
├── snowflake_monitoring/             # 🔍 Self-contained application
│   ├── monitor_snowflake_replication_v2.py
│   ├── monitor_snowflake_replication.py
│   ├── example_module_usage.py
│   ├── config.sh.example
│   ├── requirements.txt
│   ├── README.md
│   └── __init__.py
│
└── docs/                             # 📚 Project documentation
    ├── README.md
    ├── development/
    │   ├── TESTING.md
    │   ├── TESTING_QUICK_REF.md
    │   ├── UNIT_TESTING_SUMMARY.md
    │   └── REFACTORING.md
    ├── project_history/
    │   ├── PROMPTS.md
    │   ├── PROMPT_COMPARISON.md
    │   ├── PROJECT_STRUCTURE.md
    │   ├── NEW_STRUCTURE.md
    │   └── PACKAGE_REFACTORING.md
    └── vscode/
        ├── VSCODE_SETUP.md
        └── VSCODE_WORKSPACE_SUMMARY.md
```

## Execute All Cleanup Steps

Run this comprehensive script to perform all cleanup steps:

```bash
#!/bin/bash
# cleanup_root.sh - Clean up root directory

set -e  # Exit on error

cd /home/dpham/src/snowflake

echo "Creating documentation directories..."
mkdir -p docs/development
mkdir -p docs/project_history
mkdir -p docs/vscode
mkdir -p docs/archive

echo "Moving development documentation..."
mv -f TESTING.md docs/development/ 2>/dev/null || true
mv -f TESTING_QUICK_REF.md docs/development/ 2>/dev/null || true
mv -f UNIT_TESTING_SUMMARY.md docs/development/ 2>/dev/null || true
mv -f REFACTORING.md docs/development/ 2>/dev/null || true

echo "Moving project history documentation..."
mv -f PROMPTS.md docs/project_history/ 2>/dev/null || true
mv -f PROMPT_COMPARISON.md docs/project_history/ 2>/dev/null || true
mv -f PROJECT_STRUCTURE.md docs/project_history/ 2>/dev/null || true
mv -f NEW_STRUCTURE.md docs/project_history/ 2>/dev/null || true
mv -f PACKAGE_REFACTORING.md docs/project_history/ 2>/dev/null || true

echo "Moving VS Code documentation..."
mv -f VSCODE_SETUP.md docs/vscode/ 2>/dev/null || true
mv -f VSCODE_WORKSPACE_SUMMARY.md docs/vscode/ 2>/dev/null || true

echo "Archiving old files..."
mv -f README.md docs/archive/README_old.md 2>/dev/null || true
mv -f tests/ docs/archive/tests_original/ 2>/dev/null || true

echo "Removing old package files..."
rm -rf gds_snowflake.egg-info/ 2>/dev/null || true
rm -f setup.py MANIFEST.in 2>/dev/null || true
rm -f requirements.txt requirements-dev.txt 2>/dev/null || true
rm -f pytest.ini run_tests.py 2>/dev/null || true
rm -f test_modules.py test_setup.py 2>/dev/null || true

echo "Setting up new README..."
cp WORKSPACE_README.md README.md

echo "Creating docs index..."
cat > docs/README.md << 'EOF'
# Project Documentation

This directory contains all project documentation organized by category.

## 📚 Documentation Structure

### [development/](development/) - Development Documentation
- [TESTING.md](development/TESTING.md) - Complete testing guide
- [TESTING_QUICK_REF.md](development/TESTING_QUICK_REF.md) - Quick testing reference
- [UNIT_TESTING_SUMMARY.md](development/UNIT_TESTING_SUMMARY.md) - Unit testing summary
- [REFACTORING.md](development/REFACTORING.md) - Refactoring history

### [project_history/](project_history/) - Project History
- [PROMPTS.md](project_history/PROMPTS.md) - AI prompts used to generate project
- [PROMPT_COMPARISON.md](project_history/PROMPT_COMPARISON.md) - Prompt strategy comparison
- [PROJECT_STRUCTURE.md](project_history/PROJECT_STRUCTURE.md) - Original structure
- [NEW_STRUCTURE.md](project_history/NEW_STRUCTURE.md) - Updated structure
- [PACKAGE_REFACTORING.md](project_history/PACKAGE_REFACTORING.md) - Package refactoring notes

### [vscode/](vscode/) - VS Code Setup
- [VSCODE_SETUP.md](vscode/VSCODE_SETUP.md) - VS Code configuration guide
- [VSCODE_WORKSPACE_SUMMARY.md](vscode/VSCODE_WORKSPACE_SUMMARY.md) - Workspace summary

## Component Documentation

For component-specific documentation, see:
- **Package**: [../gds_snowflake/README.md](../gds_snowflake/README.md)
- **Application**: [../snowflake_monitoring/README.md](../snowflake_monitoring/README.md)

## Quick Links

- [Workspace Overview](../README.md)
- [Restructuring Summary](../RESTRUCTURING_SUMMARY.md)
EOF

echo ""
echo "✅ Root directory cleanup complete!"
echo ""
echo "Final structure:"
tree -L 2 -I '__pycache__|*.pyc|.git' .
```

## Verification

After cleanup, verify the structure:

```bash
# Check main directories exist
ls -la gds_snowflake/
ls -la snowflake_monitoring/
ls -la docs/

# Check documentation is organized
ls -la docs/development/
ls -la docs/project_history/
ls -la docs/vscode/

# Check root is clean
ls -la | grep -E '\.md$|\.txt$|\.py$'
# Should only see: README.md, RESTRUCTURING_SUMMARY.md, WORKSPACE_README.md
```

## Notes

- **Keep WORKSPACE_README.md**: This is the source file for README.md
- **Keep RESTRUCTURING_SUMMARY.md**: Documents the major changes
- **Archive old tests/**: The old tests directory can be archived since tests are now in `gds_snowflake/tests/`
- **Update .gitignore**: May need to update to ignore new build artifacts

## Benefits After Cleanup

1. ✅ **Clean root directory**: Only essential workspace files
2. ✅ **Organized documentation**: Easy to find and maintain
3. ✅ **Clear separation**: Package, application, and docs are separate
4. ✅ **Professional structure**: Follows best practices
5. ✅ **Maintainable**: New developers can quickly understand layout

---

**Note**: Save this file before running cleanup commands. Once executed, the root directory will be much cleaner and more professional.
