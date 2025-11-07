# GDS.Common Testing Guide

## Overview

This guide explains how to execute the Pester test suite for the `GDS.Common` PowerShell module.

## Prerequisites

- PowerShell 7.0 or later
- [Pester 5](https://github.com/pester/Pester) installed (`Install-Module Pester -Scope CurrentUser -Force`)
- The `PSFramework` module is mocked by the tests, so it is **not** required on the host machine

## Running the Tests

1. Ensure the `GDS_LOG_DIR` environment variable is defined. The tests use `TestDrive:` automatically, so any placeholder value is acceptable.

    ```powershell
    pwsh
    $env:GDS_LOG_DIR = Join-Path (Get-Location) 'logs'
    ```

2. From the repository root, invoke Pester against the module test directory:

    ```powershell
    Invoke-Pester -Path 'PowerShell/Modules/GDS.Common/Tests'
    ```

3. Review the output. All tests should pass with zero failures.

## What the Tests Cover

- `Initialize-Logging` respects `GDS_LOG_DIR` and validates required configuration
- `Set-GDSLogging` stores module-scoped configuration and uses the shared log directory
- `Write-Log` enforces the configured minimum log level before forwarding to `PSFramework`

## Troubleshooting

- **`GDS_LOG_DIR` not set**: Ensure the environment variable exists in the session where you run Pester.
- **Pester not found**: Install Pester 5 using `Install-Module Pester -Scope CurrentUser`.
- **Path conflicts**: The suite uses `TestDrive:` isolation, but if custom paths are introduced, make sure they are writable.
