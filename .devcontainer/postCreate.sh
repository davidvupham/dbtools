#!/usr/bin/env bash
set -euo pipefail

echo "[postCreate] Activating conda environment 'gds' and installing local packages..."

source /opt/conda/etc/profile.d/conda.sh
conda activate gds

python --version
pip --version

# Upgrade pip and install dev tooling
pip install --upgrade pip
pip install -U ruff pytest pytest-cov black mypy

# Install workspace packages in editable mode
if [ -f gds_database/pyproject.toml ]; then
  echo "Installing gds_database in editable mode"
  pip install -e ./gds_database[dev]
fi

if [ -f gds_postgres/pyproject.toml ]; then
  echo "Installing gds_postgres in editable mode"
  pip install -e ./gds_postgres[dev]
fi

if [ -f gds_snowflake/pyproject.toml ]; then
  echo "Installing gds_snowflake in editable mode"
  pip install -e ./gds_snowflake[dev]
fi

if [ -f gds_vault/pyproject.toml ]; then
  echo "Installing gds_vault in editable mode"
  pip install -e ./gds_vault
fi

echo "[postCreate] Completed setup for conda env 'gds'"
