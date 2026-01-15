# ==============================================================================
# Custom Ansible Execution Environment (EE)
# ==============================================================================
#
# PURPOSE:
# This Dockerfile creates a custom Ansible Execution Environment (EE) compatible 
# with Ansible AWX / Automation Controller. It serves as a portable container
# image that bundles Ansible Core with specific Python dependencies and 
# System Libraries required for automation tasks.
#
# SYSTEM REQUIREMENTS:
# - Host: Linux (RHEL, CentOS, Ubuntu) or WSL 2
# - Engine: Docker or Podman
#
# LEARNING OBJECTIVES FOR BEGINNERS:
# 1. Understanding Execution Environments (EE) vs Legacy Virtualenvs
# 2. Extending corporate base images with Proxy support
# 3. Managing User Contexts (root vs non-root) for security
# 4. Preparing python dependencies for isolated automation
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Registry Configuration - Support for Corporate Proxies
# ------------------------------------------------------------------------------
# REGISTRY_PREFIX: Allows the base image to be pulled from a corporate proxy
#                  (e.g., JFrog Artifactory, Nexus).
#
# USAGE:
#   Corporate proxy:
#     docker build --build-arg REGISTRY_PREFIX=xyz.jfrog.io/docker-proxy/ -t awx-ee:latest .
#       (requires docker login to the proxy)
#
#   Default (Quay.io):
#     docker build -t awx-ee:latest .
#
# NOTE: The trailing slash is required in the prefix!
#
ARG REGISTRY_PREFIX=quay.io/

# ------------------------------------------------------------------------------
# Base Image Selection
# ------------------------------------------------------------------------------
# FROM: Specifies the base image to build upon
#
# awx-ee:latest:
#   - Official Ansible Execution Environment
#   - Based on CentOS Stream (RHEL compatible)
#   - Includes Ansible Runner, Ansible Core, and Python
#   - Verified compatible with RHEL/WSL 2 environments
#
ARG BASE_IMAGE=ansible/awx-ee:latest
FROM ${REGISTRY_PREFIX}${BASE_IMAGE}

# ------------------------------------------------------------------------------
# Environment Variables
# ------------------------------------------------------------------------------
# ENV: Sets environment variables for Ansible configuration
#
# ANSIBLE_COLLECTIONS_PATH: Defines where Ansible looks for installed collections.
# ANSIBLE_ROLES_PATH: Defines where Ansible looks for installed roles.
#
# WHY: ensuring these are set explicitly guarantees that collections installed
# via ansible-galaxy in the build step are found at runtime.
#
ENV ANSIBLE_COLLECTIONS_PATH=/usr/share/ansible/collections \
    ANSIBLE_ROLES_PATH=/usr/share/ansible/roles

# ------------------------------------------------------------------------------
# User Context Switch: root
# ------------------------------------------------------------------------------
# USER root:
#   - Switches to root user for administrative tasks
#   - Required for: installing system packages (dnf), python libraries (pip)
#   - The base image usually runs as 'runner' (1000), so we escalate temporarily.
#
USER root

# ------------------------------------------------------------------------------
# System Dependencies
# ------------------------------------------------------------------------------
# RUN: Executes commands during image build (creates new layer in image)
#
# Upgrade pip: ensures we have the latest dependency resolver.
#
# NOTE: If you need system-level dependencies (like gcc, git, openldap-devel),
#       install them here using 'dnf'.
#       Example: RUN dnf install -y git && dnf clean all
#
RUN pip install --upgrade pip

# ------------------------------------------------------------------------------
# Python Dependencies
# ------------------------------------------------------------------------------
# Install Python libraries required by your custom automation.
#
# EXAMPLES:
#   - pandas: Data manipulation
#   - requests: HTTP requests
#   - psycopg2-binary: PostgreSQL interaction
#
# RUN pip install requests pandas
#

# ------------------------------------------------------------------------------
# Ansible Collections
# ------------------------------------------------------------------------------
# Install collections from Ansible Galaxy.
# Use --upgrade to ensure we get the latest stable version.
#
# EXAMPLES:
#   - community.general: Broad set of modules
#   - community.postgresql: Postgres automation
#
# RUN ansible-galaxy collection install community.general --upgrade

# ------------------------------------------------------------------------------
# Files / Configuration
# ------------------------------------------------------------------------------
# Copy any local configuration files or requirement lists.
#
# PATTERN:
#   1. COPY requirements.txt /tmp/requirements.txt
#   2. RUN pip install -r /tmp/requirements.txt
#

# ------------------------------------------------------------------------------
# User Context Switch: Runner User
# ------------------------------------------------------------------------------
# USER 1000:
#   - Switches back to the standard 'runner' user
#   - This is the default user for AWX Execution Environments
#
# SECURITY BEST PRACTICE:
#   - Never run automation containers as root unless strictly necessary
#   - 'runner' (UID 1000) prevents accidental system modifications
#
USER 1000

# ------------------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------------------
# Verify the build environment has the core tools expected.
#
RUN ansible --version && \
    python3 --version

# ==============================================================================
# BUILD INSTRUCTIONS:
# ==============================================================================
#
#   docker build -t my-registry/awx-custom-ee:latest .
#
# WITH PROXY:
#   docker build \
#     --build-arg REGISTRY_PREFIX=artifactory.corp.net/docker-remote/ \
#     -t my-registry/awx-custom-ee:latest .
#
# ==============================================================================
