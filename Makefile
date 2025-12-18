.PHONY: help all lint format test clean \
        build-all build-gds-snmp build-gds-notification \
        dev-build dev-run dev-shell dev-stop \
        infra-vault-up infra-vault-down \
        liquibase-validate liquibase-update-sql \
        test-pwsh install coverage pre-commit ci

.DELETE_ON_ERROR:

# Default shell
SHELL := /bin/bash

# Python variables
PYTHON_FILES := .
PYTEST_ARGS ?= -v

# Dynamically discover src directories for PYTHONPATH
SRC_DIRS := $(shell find $(PWD) -maxdepth 3 -type d -name "src")
PYTHONPATH_DIRS := $(if $(SRC_DIRS),$(shell echo $(SRC_DIRS) | tr ' ' ':')):.

# Discover test directories (excluding hidden/venv)
TEST_DIRS := $(shell find . -name "tests" -type d -not -path "*/.*" -not -path "./tests")

# Image definitions
SNMP_IMAGE ?= gds_snmp_receiver:latest
NOTIF_IMAGE ?= gds_notification:latest
DEV_IMAGE_NAME ?= dbtools-dev
DEV_IMAGE_TAG ?= latest
DEV_IMAGE := $(DEV_IMAGE_NAME):$(DEV_IMAGE_TAG)

# Liquibase variables
LB_COMPOSE := docker/liquibase/docker-compose.yml
LB_DEFAULTS ?= /data/liquibase/env/liquibase.dev.properties
LB_CHANGELOG ?= /data/liquibase/platforms/postgres/databases/app/db.changelog-master.yaml

## --- Main Tasks ---

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

all: lint test build-all ## Run lint, test, and build everything

## --- Python Development ---

lint: ## Run Python linting (Ruff)
	ruff check $(PYTHON_FILES)

format: ## Run Python formatting (Ruff)
	ruff format $(PYTHON_FILES)

test: ## Run Python tests (Pytest) per directory to avoid namespace collisions
	@for dir in $(TEST_DIRS); do \
		echo "----------------------------------------------------------------------"; \
		echo "Running tests in $$dir"; \
		echo "----------------------------------------------------------------------"; \
		(cd $$dir && PYTHONPATH=$(PYTHONPATH_DIRS) pytest $(PYTEST_ARGS)); \
		exit_code=$$?; \
		if [ $$exit_code -eq 5 ]; then \
			echo "No tests found in $$dir (skipping)"; \
		elif [ $$exit_code -ne 0 ]; then \
			exit 1; \
		fi; \
	done
	@echo "----------------------------------------------------------------------"
	@echo "Running root tests"
	@echo "----------------------------------------------------------------------"
	@PYTHONPATH=$(PYTHONPATH_DIRS) pytest $(PYTEST_ARGS) tests/; \
	exit_code=$$?; \
	if [ $$exit_code -eq 5 ]; then \
		echo "No tests found in tests/ (skipping)"; \
	elif [ $$exit_code -ne 0 ]; then \
		exit 1; \
	fi




clean: ## Clean up Python cache and artifacts
	rm -rf .pytest_cache .ruff_cache __pycache__ .coverage htmlcov dist build
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true


## --- Docker Builds ---

build-all: build-gds-snmp build-gds-notification ## Build all GDS application images

build-gds-snmp: ## Build SNMP Receiver image
	docker build -t $(SNMP_IMAGE) gds_snmp_receiver/

build-gds-notification: ## Build Notification Service image
	@if [ -d gds_notification ]; then \
	  docker build -t $(NOTIF_IMAGE) gds_notification/; \
	else \
	  echo "gds_notification/ not present, skipping"; \
	fi

## --- Dev Container ---

dev-build: ## Build the dev container image
	docker build -f .devcontainer/Dockerfile -t $(DEV_IMAGE) .

dev-run: ## Run dev container in background
	docker run --rm -d --name $(DEV_IMAGE_NAME) \
		-v "$$(pwd)":/workspaces/dbtools \
		-w /workspaces/dbtools \
		$(DEV_IMAGE) tail -f /dev/null

dev-shell: ## Open shell in dev container
	@if ! docker exec -it $(DEV_IMAGE_NAME) bash 2>/dev/null; then \
		$(MAKE) dev-run && sleep 1 && docker exec -it $(DEV_IMAGE_NAME) bash; \
	fi

dev-stop: ## Stop dev container
	docker stop $(DEV_IMAGE_NAME)

## --- Infrastructure (Vault, Liquibase) ---

infra-vault-up: ## Start Vault via Docker Compose
	docker compose -f docker/docker-compose.yml up -d vault

infra-vault-down: ## Stop Vault
	docker compose -f docker/docker-compose.yml down

liquibase-validate: ## Validate Liquibase changelogs
	docker compose -f $(LB_COMPOSE) run --rm liquibase \
		--defaults-file $(LB_DEFAULTS) \
		--changelog-file $(LB_CHANGELOG) \
		validate

liquibase-update-sql: ## Preview Liquibase SQL
	docker compose -f $(LB_COMPOSE) run --rm liquibase \
		--defaults-file $(LB_DEFAULTS) \
		--changelog-file $(LB_CHANGELOG) \
		updateSQL

## --- PowerShell ---

test-pwsh: ## Run PowerShell Pester tests (requires pwsh)
	pwsh -Command "Invoke-Pester -Output Detailed"

## --- Additional Utilities ---

install: ## Install all packages in development mode
	@for pkg in gds_*/; do \
		if [ -f "$$pkg/pyproject.toml" ]; then \
			echo "Installing $$pkg..."; \
			pip install -e "$$pkg"; \
		fi \
	done

coverage: ## Run tests with coverage report
	PYTHONPATH=$(PYTHONPATH_DIRS) pytest --cov=. --cov-report=html --cov-report=term tests/

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

ci: lint test ## Run all CI checks (lint + test)

verify-devcontainer: ## Run the unified devcontainer verification suite
	bash scripts/verify_devcontainer.sh
