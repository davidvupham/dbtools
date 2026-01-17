# AWX Execution Environment

Custom execution environment for AWX/Ansible Automation Platform.

## Overview

This directory contains the Dockerfile for building a custom AWX execution environment with additional dependencies required for the dbtools project.

## Usage

Build the execution environment:

```bash
docker build -t awx-ee:latest .
```

## Related

- [AWX Setup](../awx/README.md) - Main AWX configuration
- [Ansible Docker](../ansible/README.md) - Standalone Ansible container
