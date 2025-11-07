# Coding Standards Enforcement Guide

> Version: 1.0.0
>
> Purpose: Define tools, processes, and CI/CD practices to enforce coding standards
>
> Last Updated: 2025-11-07

## Overview

This guide provides practical strategies and tools to automatically enforce the Python and PowerShell coding standards defined in this repository. Automated enforcement is more effective than manual code reviews alone.

## Table of Contents

- [Enforcement Philosophy](#enforcement-philosophy)
  - [The Enforcement Pyramid](#the-enforcement-pyramid)
  - [Key Principles](#key-principles)
- [Python Enforcement](#python-enforcement)
  - [Python Tools](#python-tools)
    - [Ruff (Linter + Formatter)](#1-ruff-linter--formatter)
    - [Black (Code Formatter)](#2-black-code-formatter)
    - [mypy (Type Checker)](#3-mypy-type-checker)
    - [bandit (Security Linter)](#4-bandit-security-linter)
    - [pytest (Testing Framework)](#5-pytest-testing-framework)
    - [pip-audit (Dependency Security)](#6-pip-audit-dependency-security)
  - [Python Makefile](#python-makefile)
- [PowerShell Enforcement](#powershell-enforcement)
  - [PowerShell Tools](#powershell-tools)
    - [PSScriptAnalyzer (Linter)](#1-psscriptanalyzer-linter)
    - [Pester (Testing Framework)](#2-pester-testing-framework)
    - [PSCodeHealth (Code Quality Metrics)](#3-pscodehealth-code-quality-metrics)
  - [PowerShell Build Script](#powershell-build-script)
- [Pre-Commit Hooks](#pre-commit-hooks)
  - [Using pre-commit Framework](#using-pre-commit-framework)
  - [Git Hooks Without pre-commit](#git-hooks-without-pre-commit)
- [CI/CD Integration](#cicd-integration)
  - [GitHub Actions](#github-actions)
  - [Azure DevOps](#azure-devops)
  - [GitLab CI](#gitlab-ci)
- [IDE Integration](#ide-integration)
  - [Visual Studio Code (VS Code)](#visual-studio-code-vs-code)
  - [PyCharm / IntelliJ](#pycharm--intellij)
- [Code Review Process](#code-review-process)
  - [Pull Request Template](#pull-request-template)
  - [Code Review Checklist](#code-review-checklist)
- [Metrics and Reporting](#metrics-and-reporting)
  - [SonarQube Integration](#sonarqube-integration)
  - [Code Climate](#code-climate)
  - [Custom Metrics Dashboard](#custom-metrics-dashboard)
- [Enforcement Levels](#enforcement-levels)
- [Best Practices Summary](#best-practices-summary)
- [Troubleshooting](#troubleshooting)

## Enforcement Philosophy

### The Enforcement Pyramid

```text
                    ╱╲
                   ╱  ╲
                  ╱    ╲  Manual Code Review
                 ╱      ╲ (Focus on logic & architecture)
                ╱────────╲
               ╱          ╲
              ╱   CI/CD    ╲
             ╱   Pipeline   ╲
            ╱    Checks      ╲
           ╱  (Quality gates) ╲
          ╱────────────────────╲
         ╱                      ╲
        ╱    Pre-Commit Hooks    ╲
       ╱  (Catch before commit)   ╲
      ╱────────────────────────────╲
     ╱                              ╲
    ╱      IDE Integration           ╲
   ╱     (Real-time feedback)         ╲
  ╱────────────────────────────────────╲
```

### Key Principles

1. **Fail Fast**: Catch issues as early as possible (IDE > pre-commit > CI/CD > review)
2. **Automate Everything**: If it can be checked automatically, it should be
3. **Make it Easy**: Provide auto-fix tools, not just error messages
4. **Be Consistent**: Same rules everywhere (local, CI, all developers)
5. **Educate**: Explain why rules exist, don't just enforce them

## Python Enforcement

### Python Tools

#### 1. **Ruff** (Linter + Formatter)

**What it is:** Ultra-fast Python linter and formatter that replaces multiple tools.

**Configuration:** `pyproject.toml`

```toml
[tool.ruff]
# Enable pycodestyle (`E`), Pyflakes (`F`), and isort (`I`)
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "S",      # flake8-bandit (security)
    "T20",    # flake8-print
    "PT",     # flake8-pytest-style
    "RET",    # flake8-return
    "SIM",    # flake8-simplify
    "ARG",    # flake8-unused-arguments
]

ignore = [
    "E501",   # Line too long (handled by formatter)
]

# Allow autofix for all enabled rules
fixable = ["ALL"]
unfixable = []

line-length = 88
target-version = "py38"

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py
"tests/**/*.py" = ["S101"]  # Allow assert in tests

[tool.ruff.isort]
known-first-party = ["myapp"]
```

**Usage:**

```bash
# Check code
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

#### 2. **Black** (Code Formatter)

**What it is:** Opinionated code formatter (alternative to ruff format).

**Configuration:** `pyproject.toml`

```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
)/
'''
```

**Usage:**

```bash
# Format code
black .

# Check without modifying
black --check .

# Show diff
black --diff .
```

#### 3. **mypy** (Type Checker)

**What it is:** Static type checker for Python.

**Configuration:** `pyproject.toml`

```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
check_untyped_defs = true
strict_equality = true

# Per-module options
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "third_party_lib.*"
ignore_missing_imports = true
```

**Usage:**

```bash
# Type check all files
mypy .

# Type check specific file
mypy myapp/module.py

# Generate HTML report
mypy --html-report ./mypy-report .
```

#### 4. **bandit** (Security Linter)

**What it is:** Security vulnerability scanner.

**Configuration:** Prefer a `bandit.yaml` (or integrate into `pyproject.toml` with `bandit[toml]`).

```yaml
# bandit.yaml
exclude_dirs:
  - /tests/
  - /venv/

tests:
  - B201  # flask_debug_true
  - B301  # pickle
  - B302  # marshal
  - B303  # md5
  - B304  # ciphers
  - B305  # cipher_modes
  - B306  # mktemp_q
  - B307  # eval
  - B308  # mark_safe
  - B309  # httpsconnection
  - B310  # urllib_urlopen
  - B311  # random
  - B312  # telnetlib
  - B313  # xml_bad_cElementTree
  - B314  # xml_bad_ElementTree
  - B315  # xml_bad_expatreader
  - B316  # xml_bad_expatbuilder
  - B317  # xml_bad_sax
  - B318  # xml_bad_minidom
  - B319  # xml_bad_pulldom
  - B320  # xml_bad_etree
  - B321  # ftplib
  - B323  # unverified_context
  - B324  # hashlib_new_insecure_functions
  - B325  # tempnam
  - B401  # import_telnetlib
  - B402  # import_ftplib
  - B403  # import_pickle
  - B404  # import_subprocess
  - B405  # import_xml_etree
  - B406  # import_xml_sax
  - B407  # import_xml_expat
  - B408  # import_xml_minidom
  - B409  # import_xml_pulldom
  - B410  # import_lxml
  - B411  # import_xmlrpclib
  - B412  # import_httpoxy
  - B413  # import_pycrypto
  - B501  # request_with_no_cert_validation
  - B502  # ssl_with_bad_version
  - B503  # ssl_with_bad_defaults
  - B504  # ssl_with_no_version
  - B505  # weak_cryptographic_key
  - B506  # yaml_load
  - B507  # ssh_no_host_key_verification
  - B601  # paramiko_calls
  - B602  # shell_injection_subprocess_popen
  - B603  # subprocess_without_shell_equals_true
  - B604  # any_other_function_with_shell_equals_true
  - B605  # start_process_with_a_shell
  - B606  # start_process_with_no_shell
  - B607  # start_process_with_partial_path
  - B608  # hardcoded_sql_expressions
  - B609  # linux_commands_wildcard_injection
  - B610  # django_extra_used
  - B611  # django_rawsql_used
  - B701  # jinja2_autoescape_false
  - B702  # use_of_mako_templates
  - B703  # django_mark_safe
```

**Usage:**

```bash
# Scan for security issues
bandit -c bandit.yaml -r myapp/

# Generate JSON report
bandit -c bandit.yaml -r myapp/ -f json -o bandit-report.json

# Exclude tests
bandit -c bandit.yaml -r myapp/ -x tests/
```

#### 5. **pytest** (Testing Framework)

**Configuration:** `pyproject.toml`

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=myapp",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

**Usage:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=myapp --cov-report=html

# Run only unit tests
pytest -m unit

# Run in parallel
pytest -n auto
```

#### 6. **pip-audit** (Dependency Security)

**What it is:** Scans dependencies for known vulnerabilities.

**Usage:**

```bash
# Audit installed packages
pip-audit

# Audit requirements file
pip-audit -r requirements.txt

# Generate report
pip-audit --format json --output audit-report.json
```

### Python Makefile

Create a `Makefile` for common tasks:

```makefile
.PHONY: format lint typecheck security test all clean

format:
	ruff format .
	ruff check --fix .

lint:
	ruff check .

typecheck:
	mypy .

security:
	bandit -r myapp/
	pip-audit

test:
	pytest --cov=myapp --cov-report=html --cov-report=term

all: format lint typecheck security test

clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
```

**Usage:**

```bash
make format    # Format code
make lint      # Run linter
make typecheck # Type check
make security  # Security scan
make test      # Run tests
make all       # Run everything
```

## PowerShell Enforcement

### PowerShell Tools

#### 1. **PSScriptAnalyzer** (Linter)

**What it is:** PowerShell static code analyzer.

**Configuration:** `.vscode/settings.json` or `PSScriptAnalyzerSettings.psd1`

```powershell
# PSScriptAnalyzerSettings.psd1
@{
    # Enable all rules by default
    IncludeDefaultRules = $true

    # Severity levels to include
    Severity = @('Error', 'Warning', 'Information')

    # Exclude specific rules
    ExcludeRules = @(
        'PSAvoidUsingWriteHost'  # Allow Write-Host for interactive scripts
    )

    # Custom rules
    Rules = @{
        PSPlaceOpenBrace = @{
            Enable = $true
            OnSameLine = $true
            NewLineAfter = $true
            IgnoreOneLineBlock = $true
        }

        PSPlaceCloseBrace = @{
            Enable = $true
            NewLineAfter = $true
            IgnoreOneLineBlock = $true
            NoEmptyLineBefore = $false
        }

        PSUseConsistentIndentation = @{
            Enable = $true
            IndentationSize = 4
            PipelineIndentation = 'IncreaseIndentationForFirstPipeline'
            Kind = 'space'
        }

        PSUseConsistentWhitespace = @{
            Enable = $true
            CheckInnerBrace = $true
            CheckOpenBrace = $true
            CheckOpenParen = $true
            CheckOperator = $true
            CheckPipe = $true
            CheckPipeForRedundantWhitespace = $true
            CheckSeparator = $true
            CheckParameter = $false
        }

        PSAlignAssignmentStatement = @{
            Enable = $true
            CheckHashtable = $true
        }

        PSAvoidUsingCmdletAliases = @{
            Enable = $true
            Whitelist = @()
        }

        PSProvideCommentHelp = @{
            Enable = $true
            ExportedOnly = $true
            BlockComment = $true
            VSCodeSnippetCorrection = $true
            Placement = 'before'
        }
    }
}
```

**Usage:**

```powershell
# Install PSScriptAnalyzer
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force

# Analyze a script
Invoke-ScriptAnalyzer -Path ./MyScript.ps1

# Analyze all scripts in directory
Get-ChildItem -Path . -Filter *.ps1 -Recurse |
    Invoke-ScriptAnalyzer

# Use custom settings
Invoke-ScriptAnalyzer -Path ./MyScript.ps1 -Settings ./PSScriptAnalyzerSettings.psd1

# Fix auto-fixable issues
Invoke-ScriptAnalyzer -Path ./MyScript.ps1 -Fix

# Generate report
Invoke-ScriptAnalyzer -Path . -Recurse |
    Export-Csv -Path analysis-report.csv -NoTypeInformation
```

#### 2. **Pester** (Testing Framework)

**Configuration:** `PesterConfiguration.psd1`

```powershell
@{
    Run = @{
        Path = './tests'
        Exit = $true
        PassThru = $true
    }

    CodeCoverage = @{
        Enabled = $true
        Path = './src/*.ps1'
        OutputPath = './coverage.xml'
        OutputFormat = 'JaCoCo'
        CoveragePercentTarget = 80
    }

    TestResult = @{
        Enabled = $true
        OutputPath = './test-results.xml'
        OutputFormat = 'NUnitXml'
    }

    Output = @{
        Verbosity = 'Detailed'
    }
}
```

**Usage:**

```powershell
# Install Pester
Install-Module -Name Pester -MinimumVersion 5.0 -Scope CurrentUser -Force

# Run tests
Invoke-Pester

# Run with configuration
$config = New-PesterConfiguration -Hashtable @{
    Run = @{ Path = './tests' }
    CodeCoverage = @{ Enabled = $true }
}
Invoke-Pester -Configuration $config

# Run specific tests
Invoke-Pester -Path ./tests/MyScript.Tests.ps1

# Generate HTML report
Invoke-Pester | ConvertTo-Html | Out-File test-results.html
```

#### 3. **PSCodeHealth** (Code Quality Metrics)

**What it is:** Analyzes PowerShell code for quality metrics.

**Usage:**

```powershell
# Install PSCodeHealth
Install-Module -Name PSCodeHealth -Scope CurrentUser -Force

# Analyze code
Invoke-PSCodeHealth -Path ./src

# Generate HTML report
Invoke-PSCodeHealth -Path ./src -HtmlReportPath ./health-report.html

# Set compliance rules
$complianceRules = @{
    LinesOfCodeAverage = 50
    ScriptAnalyzerFindingsAverage = 0
    TestCoverage = 80
}
Invoke-PSCodeHealth -Path ./src -ComplianceRule $complianceRules
```

### PowerShell Build Script

Create a `build.ps1` script:

```powershell
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="PSScriptAnalyzer"; ModuleVersion="1.21.0" }
#Requires -Modules @{ ModuleName="Pester"; ModuleVersion="5.0.0" }

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('Analyze', 'Test', 'All')]
    [string]$Task = 'All',

    [switch]$Fix
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptRoot = $PSScriptRoot
$SourcePath = Join-Path $ScriptRoot 'src'
$TestPath = Join-Path $ScriptRoot 'tests'

function Invoke-Analysis {
    Write-Host "Running PSScriptAnalyzer..." -ForegroundColor Cyan

    $analysisParams = @{
        Path = $SourcePath
        Recurse = $true
        Settings = Join-Path $ScriptRoot 'PSScriptAnalyzerSettings.psd1'
    }

    if ($Fix) {
        $analysisParams['Fix'] = $true
    }

    $results = Invoke-ScriptAnalyzer @analysisParams

    if ($results) {
        $results | Format-Table -AutoSize
        throw "PSScriptAnalyzer found $($results.Count) issue(s)"
    }

    Write-Host "✓ PSScriptAnalyzer passed" -ForegroundColor Green
}

function Invoke-Tests {
    Write-Host "Running Pester tests..." -ForegroundColor Cyan

    $config = New-PesterConfiguration
    $config.Run.Path = $TestPath
    $config.Run.Exit = $false
    $config.Run.PassThru = $true
    $config.CodeCoverage.Enabled = $true
    $config.CodeCoverage.Path = "$SourcePath/*.ps1"
    $config.CodeCoverage.CoveragePercentTarget = 80
    $config.TestResult.Enabled = $true
    $config.TestResult.OutputPath = Join-Path $ScriptRoot 'test-results.xml'

    $result = Invoke-Pester -Configuration $config

    if ($result.FailedCount -gt 0) {
        throw "Pester tests failed: $($result.FailedCount) test(s)"
    }

    $coverage = [math]::Round($result.CodeCoverage.CoveragePercent, 2)
    Write-Host "✓ All tests passed (Coverage: $coverage%)" -ForegroundColor Green

    if ($coverage -lt 80) {
        Write-Warning "Code coverage ($coverage%) is below target (80%)"
    }
}

try {
    switch ($Task) {
        'Analyze' { Invoke-Analysis }
        'Test' { Invoke-Tests }
        'All' {
            Invoke-Analysis
            Invoke-Tests
        }
    }

    Write-Host "`n✓ Build completed successfully!" -ForegroundColor Green
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
```

**Usage:**

```powershell
# Run all checks
./build.ps1

# Run only analysis
./build.ps1 -Task Analyze

# Run analysis with auto-fix
./build.ps1 -Task Analyze -Fix

# Run only tests
./build.ps1 -Task Test
```

## Pre-Commit Hooks

### Using pre-commit Framework

**Install pre-commit:**

```bash
pip install pre-commit
```

**Configuration:** `.pre-commit-config.yaml`

```yaml
repos:
  # Python formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
        # If you prefer Ruff as the formatter, set editor.defaultFormatter to "charliermarsh.ruff"

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]

  # Security scanning
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-c, pyproject.toml]
        additional_dependencies: ["bandit[toml]"]

  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key
      - id: check-case-conflict

  # PowerShell linting
  - repo: local
    hooks:
      - id: psscriptanalyzer
        name: PSScriptAnalyzer
        entry: pwsh -NoProfile -Command "Invoke-ScriptAnalyzer -Path $args"
        language: system
        files: \.ps1$
        pass_filenames: true
```

**Setup:**

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

### Git Hooks Without pre-commit

**`.git/hooks/pre-commit`** (Python):

```bash
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Format code
echo "→ Formatting code..."
ruff format .
ruff check --fix .

# Type check
echo "→ Type checking..."
mypy .

# Security scan
echo "→ Security scan..."
bandit -r myapp/ -ll

echo "✓ Pre-commit checks passed!"
```

**`.git/hooks/pre-commit`** (PowerShell):

```powershell
#!/usr/bin/env pwsh
#Requires -Version 7.0

$ErrorActionPreference = 'Stop'

Write-Host "Running pre-commit checks..." -ForegroundColor Cyan

# Get staged .ps1 files
$stagedFiles = git diff --cached --name-only --diff-filter=ACM |
    Where-Object { $_ -match '\.ps1$' }

if ($stagedFiles) {
    Write-Host "→ Analyzing PowerShell files..." -ForegroundColor Yellow

    foreach ($file in $stagedFiles) {
        $results = Invoke-ScriptAnalyzer -Path $file -Settings ./PSScriptAnalyzerSettings.psd1

        if ($results) {
            $results | Format-Table -AutoSize
            throw "PSScriptAnalyzer found issues in $file"
        }
    }
}

Write-Host "✓ Pre-commit checks passed!" -ForegroundColor Green
```

**Make executable:**

```bash
chmod +x .git/hooks/pre-commit
```

## CI/CD Integration

### GitHub Actions

**`.github/workflows/python-ci.yml`**

```yaml
name: Python CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  quality:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Format check
      run: |
        ruff format --check .

    - name: Lint
      run: |
        ruff check .

    - name: Type check
      run: |
        mypy .

    - name: Security scan
      run: |
        bandit -r myapp/ -ll
        pip-audit

    - name: Run tests
      run: |
        pip install pytest-xdist
        pytest -n auto --cov=myapp --cov-report=xml --cov-report=term

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

    - name: Check coverage threshold
      run: |
        coverage report --fail-under=80
```

**`.github/workflows/powershell-ci.yml`**

```yaml
name: PowerShell CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  quality:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
    - uses: actions/checkout@v4

    - name: Install PSScriptAnalyzer
      shell: pwsh
      run: |
        Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser

    - name: Install Pester
      shell: pwsh
      run: |
        Install-Module -Name Pester -MinimumVersion 5.0 -Force -Scope CurrentUser

    - name: Run PSScriptAnalyzer
      shell: pwsh
      run: |
        $results = Invoke-ScriptAnalyzer -Path ./src -Recurse -Settings ./PSScriptAnalyzerSettings.psd1
        if ($results) {
          $results | Format-Table -AutoSize
          throw "PSScriptAnalyzer found $($results.Count) issue(s)"
        }

    - name: Run Pester tests
      shell: pwsh
      run: |
        $config = New-PesterConfiguration
        $config.Run.Path = './tests'
        $config.Run.Exit = $true
        $config.CodeCoverage.Enabled = $true
        $config.CodeCoverage.Path = './src/*.ps1'
        $config.CodeCoverage.CoveragePercentTarget = 80
        $config.TestResult.Enabled = $true
        $config.TestResult.OutputPath = './test-results.xml'

        Invoke-Pester -Configuration $config

    - name: Publish test results
      uses: EnricoMi/publish-unit-test-result-action@v2
      if: always()
      with:
        files: test-results.xml
```

### Azure DevOps

**`azure-pipelines.yml`**

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: Python_Quality
  displayName: 'Python Code Quality'
  jobs:
  - job: Lint_and_Test
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.11'
      displayName: 'Use Python 3.11'

    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
      displayName: 'Install dependencies'

    - script: |
        ruff format --check .
        ruff check .
      displayName: 'Lint with Ruff'

    - script: |
        mypy .
      displayName: 'Type check with mypy'

    - script: |
        bandit -r myapp/ -ll
      displayName: 'Security scan with Bandit'

    - script: |
        pytest --cov=myapp --cov-report=xml --cov-report=html --junitxml=test-results.xml
      displayName: 'Run tests'

    - task: PublishTestResults@2
      inputs:
        testResultsFiles: 'test-results.xml'
        testRunTitle: 'Python Tests'
      displayName: 'Publish test results'

    - task: PublishCodeCoverageResults@1
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: 'coverage.xml'
      displayName: 'Publish coverage'

- stage: PowerShell_Quality
  displayName: 'PowerShell Code Quality'
  jobs:
  - job: Lint_and_Test
    steps:
    - pwsh: |
        Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser
        Install-Module -Name Pester -MinimumVersion 5.0 -Force -Scope CurrentUser
      displayName: 'Install PowerShell modules'

    - pwsh: |
        $results = Invoke-ScriptAnalyzer -Path ./src -Recurse
        if ($results) {
          $results | Format-Table -AutoSize
          throw "PSScriptAnalyzer found issues"
        }
      displayName: 'Run PSScriptAnalyzer'

    - pwsh: |
        ./build.ps1 -Task Test
      displayName: 'Run Pester tests'

    - task: PublishTestResults@2
      inputs:
        testResultsFormat: 'NUnit'
        testResultsFiles: 'test-results.xml'
      displayName: 'Publish test results'
```

### GitLab CI

**`.gitlab-ci.yml`**

```yaml
stages:
  - lint
  - test
  - security

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip

# Python jobs
python:lint:
  stage: lint
  image: python:3.11
  script:
    - pip install ruff mypy
    - ruff format --check .
    - ruff check .
    - mypy .

python:test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
    - pytest --cov=myapp --cov-report=xml --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

python:security:
  stage: security
  image: python:3.11
  script:
    - pip install bandit pip-audit
    - bandit -r myapp/ -ll
    - pip-audit

# PowerShell jobs
powershell:lint:
  stage: lint
  image: mcr.microsoft.com/powershell:latest
  script:
    - pwsh -Command "Install-Module -Name PSScriptAnalyzer -Force"
    - pwsh -Command "Invoke-ScriptAnalyzer -Path ./src -Recurse"

powershell:test:
  stage: test
  image: mcr.microsoft.com/powershell:latest
  script:
    - pwsh -Command "Install-Module -Name Pester -MinimumVersion 5.0 -Force"
    - pwsh -File ./build.ps1 -Task Test
  artifacts:
    reports:
      junit: test-results.xml
```

## IDE Integration

### Visual Studio Code (VS Code)

**`.vscode/settings.json`**

```json
{
  // Python settings
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "ms-python.black-formatter",
  "ruff.lint.run": "onSave",
  "python.analysis.typeCheckingMode": "basic",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,

  // Code actions on save
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll": true
  },

  // PowerShell settings
  "powershell.codeFormatting.preset": "OTBS",
  "powershell.codeFormatting.openBraceOnSameLine": true,
  "powershell.codeFormatting.newLineAfterOpenBrace": true,
  "powershell.codeFormatting.whitespaceBeforeOpenBrace": true,
  "powershell.scriptAnalysis.enable": true,
  "powershell.scriptAnalysis.settingsPath": "PSScriptAnalyzerSettings.psd1",

  // File associations
  "files.associations": {
    "*.ps1": "powershell",
    "*.psm1": "powershell",
    "*.psd1": "powershell"
  },

  // Rulers
  "editor.rulers": [88, 115],

  // Trailing whitespace
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true
}
```

**`.vscode/extensions.json`**

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "ms-vscode.powershell",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

### PyCharm / IntelliJ

#### Settings → Tools → External Tools

Add tools for Ruff, Black, mypy:

```xml
<tool name="Ruff Check" showInMainMenu="true" showInEditor="true">
  <exec>
    <option name="COMMAND" value="ruff" />
    <option name="PARAMETERS" value="check $FilePath$" />
    <option name="WORKING_DIRECTORY" value="$ProjectFileDir$" />
  </exec>
</tool>
```

## Code Review Process

### Pull Request Template

**`.github/pull_request_template.md`**

```markdown
## Description
<!-- Describe your changes -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Code follows coding standards
- [ ] All linters pass locally (`make lint`)
- [ ] All tests pass locally (`make test`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Security scan passes (`make security`)
- [ ] Added/updated tests for changes
- [ ] Added/updated documentation
- [ ] No secrets or credentials in code
- [ ] Code coverage maintained or improved

## Testing
<!-- Describe testing performed -->

## Screenshots (if applicable)
<!-- Add screenshots -->
```

### Code Review Checklist

#### For Reviewers

1. **Automated Checks**
   - ✅ All CI/CD checks pass
   - ✅ Code coverage meets threshold
   - ✅ No security vulnerabilities

2. **Code Quality**
   - ✅ Follows naming conventions
   - ✅ Functions are appropriately sized
   - ✅ No code duplication
   - ✅ Proper error handling

3. **Documentation**
   - ✅ Docstrings/comment-based help present
   - ✅ Complex logic explained
   - ✅ README updated if needed

4. **Testing**
   - ✅ Tests cover new functionality
   - ✅ Edge cases considered
   - ✅ Tests are deterministic

5. **Security**
   - ✅ No hard-coded secrets
   - ✅ Input validation present
   - ✅ Dependencies up to date

## Metrics and Reporting

### SonarQube Integration

**`sonar-project.properties`**

```properties
sonar.projectKey=myproject
sonar.projectName=My Project
sonar.projectVersion=1.0

# Source code
sonar.sources=src,myapp
sonar.tests=tests

# Python specific
sonar.python.version=3.8,3.9,3.10,3.11
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results.xml

# Exclusions
sonar.exclusions=**/*_test.py,**/test_*.py,**/__pycache__/**

# Coverage exclusions
sonar.coverage.exclusions=**/tests/**,**/__init__.py

# Quality gates
sonar.qualitygate.wait=true
```

### Code Climate

**`.codeclimate.yml`**

```yaml
version: "2"

checks:
  argument-count:
    enabled: true
    config:
      threshold: 5
  complex-logic:
    enabled: true
    config:
      threshold: 4
  file-lines:
    enabled: true
    config:
      threshold: 500
  method-complexity:
    enabled: true
    config:
      threshold: 10
  method-lines:
    enabled: true
    config:
      threshold: 50

plugins:
  ruff:
    enabled: true
  bandit:
    enabled: true
  pep8:
    enabled: true

exclude_patterns:
  - "tests/"
  - "**/__pycache__/"
  - "*.pyc"
```

### Custom Metrics Dashboard

Create a metrics collection script:

**`collect_metrics.py`**

```python
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

def collect_metrics() -> Dict[str, Any]:
    """Collect code quality metrics."""
    metrics = {}

    # Ruff violations
    result = subprocess.run(
        ["ruff", "check", ".", "--output-format=json"],
        capture_output=True,
        text=True
    )
    ruff_data = json.loads(result.stdout) if result.stdout else []
    metrics["ruff_violations"] = len(ruff_data)

    # Test coverage
    result = subprocess.run(
        ["pytest", "--cov=myapp", "--cov-report=json"],
        capture_output=True
    )
    if Path("coverage.json").exists():
        with open("coverage.json") as f:
            cov_data = json.load(f)
            metrics["coverage_percent"] = cov_data["totals"]["percent_covered"]

    # Lines of code
    result = subprocess.run(
        ["find", ".", "-name", "*.py", "-exec", "wc", "-l", "{}", "+"],
        capture_output=True,
        text=True
    )
    total_lines = sum(int(line.split()[0]) for line in result.stdout.strip().split("\n") if line)
    metrics["total_lines"] = total_lines

    # Save metrics
    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    return metrics

if __name__ == "__main__":
    metrics = collect_metrics()
    print(json.dumps(metrics, indent=2))
```

## Enforcement Levels

### Level 1: Advisory (Warnings)

- Style violations
- Minor naming issues
- Missing docstrings

**Action:** Warn but don't block

### Level 2: Required (Errors)

- Syntax errors
- Type errors
- Security vulnerabilities
- Test failures
- Coverage below threshold

**Action:** Block merge/deployment

### Level 3: Critical (Immediate)

- Hard-coded secrets
- SQL injection vulnerabilities
- Known CVEs in dependencies

**Action:** Block immediately, alert security team

## Best Practices Summary

1. **Start Early**: Integrate tools from day one
2. **Automate Everything**: Manual checks are forgotten
3. **Fail Fast**: Catch issues in IDE, not in production
4. **Make it Easy**: Provide auto-fix, not just detection
5. **Educate**: Explain why rules exist
6. **Be Consistent**: Same rules everywhere
7. **Measure**: Track metrics over time
8. **Iterate**: Adjust rules based on team feedback
9. **Don't Block Unnecessarily**: Balance quality with velocity
10. **Lead by Example**: Senior developers follow standards too

## Troubleshooting

## Adoption Checklist and Waivers

### Adopting Standards in an Existing Repository

1. Add configuration files: `pyproject.toml`, `bandit.yaml`, `PSScriptAnalyzerSettings.psd1`, `.pre-commit-config.yaml`.
2. Install and run auto-fixers locally: `ruff format`, `ruff check --fix`, `black` (if used), `Invoke-ScriptAnalyzer -Fix`.
3. Stage minimal, focused diffs (avoid mass reformat alongside logic changes).
4. Enable pre-commit hooks and fix any remaining issues.
5. Introduce CI quality gates (lint, typecheck, tests, security, coverage).
6. Communicate formatter/line-length choice (PEP 8 79 vs Black 88) and enforce consistently.

### Exceptions and Waivers Policy

- Prefer targeted suppressions with rationale and scope limitations:
  - Python: `# noqa: <rule>` with a comment explaining why.
  - PowerShell: `[Diagnostics.CodeAnalysis.SuppressMessageAttribute('RuleId','Reason')]`.
- File/line waivers must include:
  - Why the rule is inappropriate in this context
  - Evidence that alternatives were considered
  - A review date to revisit the suppression
- Avoid global, permanent disables; use per-file/per-line where possible.

### Common Issues

**Pre-commit hooks not running:**

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

**Ruff/Black conflicts:**

```toml
# In pyproject.toml, ensure Black line length matches Ruff
[tool.black]
line-length = 88

[tool.ruff]
line-length = 88
```

**PSScriptAnalyzer false positives:**

```powershell
# Suppress specific warnings
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '')]
param()
```

## Version History

### 1.0.0 (2025-11-07)

- Initial publication
- Python enforcement tools and configuration
- PowerShell enforcement tools and configuration
- Pre-commit hooks setup
- CI/CD integration examples
- IDE configuration
- Metrics and reporting guidance

<!-- End of document -->
