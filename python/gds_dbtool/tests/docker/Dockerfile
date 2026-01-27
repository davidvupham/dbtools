# ==============================================================================
# Testing Dockerfile for gds_dbtool
# ==============================================================================
# This Dockerfile is designed specifically for running a confined Vault instance
# for integration testing. It is NOT intended for production use.
#
# Key differences from production:
# 1. Runs in "Dev" mode by default (in-memory storage, auto-unsealed).
# 2. Simplified configuration for speed and ease of testing.
#
# EDUCATIONAL NOTE:
# "Dev mode" in Vault is a special mode that:
# - Stores all data in memory (lost on restart).
# - Automatically unseals the Vault (no manual key entry needed).
# - Uses a single root token if specified.
# This makes it perfect for ephemeral testing environments.

# ARG REGISTRY_PREFIX allow specifying a private registry (e.g. for RedHat/Corporate environments)
# Defaults to docker.io/ for public Docker Hub access
ARG REGISTRY_PREFIX=docker.io/

# Use the official HashiCorp Vault image as our base
FROM ${REGISTRY_PREFIX}hashicorp/vault:latest

# Metadata helps other developers understand what this image is for
LABEL description="Ephemeral Vault instance for gds_dbtool integration testing"
LABEL maintainer="GDS Team"

# Expose the standard Vault API port
EXPOSE 8200

# EDUCATIONAL NOTE:
# The CMD instruction defines the default command run when the container starts.
# Here we verify that we are running the 'server' in 'dev' mode.
# -dev: Enables development mode
# -dev-listen-address: Binds to all interfaces (0.0.0.0) so the host can reach it
CMD ["server", "-dev", "-dev-listen-address=0.0.0.0:8200"]
