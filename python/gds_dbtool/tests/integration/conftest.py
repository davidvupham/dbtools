# ==============================================================================
# Integration Test Config (conftest.py)
# ==============================================================================
# "conftest.py" is a special pytest file that shares fixtures across multiple test files.
#
# EDUCATIONAL GOAL:
# Demonstrate how to manage external resources (like Docker containers)
# using pytest fixtures. This pattern ensures:
# 1. SETUP: The container starts before tests run.
# 2. TEARDOWN: The container stops after tests finish (even if they fail!).
# 3. ISOLATION: Tests run against a known clean state.

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Generator

import pytest
import requests
from gds_dbtool.config import GlobalConfig, ProfileConfig

# Constants for our test environment
TEST_DOCKER_DIR = Path(__file__).parent.parent / "docker"
VAULT_ADDR = "http://localhost:8200"
VAULT_TOKEN = "root"

def get_container_runtime() -> str:
    """
    Detects the best available container runtime based on OS and availability.
    
    Rules:
    - RedHat/Fedora/CentOS: Prefer Podman.
    - Ubuntu/Debian: Prefer Docker.
    - Fallback: Use whatever is installed.
    """
    preferred = None
    
    # 1. Detect OS preference
    try:
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                content = f.read().lower()
                if any(x in content for x in ["id=rhel", "id=fedora", "id=centos", "id=almalinux", "id=rocky"]):
                    preferred = "podman"
                elif any(x in content for x in ["id=ubuntu", "id=debian"]):
                    preferred = "docker"
    except Exception:
        pass # Ignore errors, fall back to availability check

    print(f"\n[setup] OS Preference: {preferred or 'None (Generic)'}")

    # 2. Try preferred runtime first
    if preferred == "podman" and shutil.which("podman"):
        return "podman"
    if preferred == "docker" and shutil.which("docker"):
        return "docker"
    
    # 3. Fallback to whatever is available
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    
    pytest.fail("Neither 'podman' nor 'docker' is installed. Cannot run integration tests.")


@pytest.fixture(scope="session")
def vault_container() -> Generator[None, None, None]:
    """
    Manages the lifecycle of the Vault container using raw Podman/Docker commands.
    
    We avoid 'compose' here because 'podman-compose' can be flaky or configured
    to use docker-compose, which might be missing. Direct 'run' commands are
    more robust for single-container tests.
    """
    runtime = get_container_runtime()
    print(f"\n[setup] Detected runtime: {runtime}")
    print("\n[setup] Building and starting Vault container...")
    
    container_name = "gds_dbtool_test_vault_integration"
    image_name = "gds_dbtool_test_vault:latest"

    # 0. Clean up any leftovers
    subprocess.run([runtime, "rm", "-f", container_name], capture_output=True)

    try:
        # 1. Build the image
        # We pass --format docker to ensure compatibility if using Podman
        build_cmd = [runtime, "build", "-t", image_name, "."]
        
        # Support for corporate proxies via REGISTRY_PREFIX build arg
        # This matches the pattern in other Dockerfiles in the repo
        registry_prefix = os.environ.get("REGISTRY_PREFIX")
        if registry_prefix:
            build_cmd.extend(["--build-arg", f"REGISTRY_PREFIX={registry_prefix}"])

        if runtime == "podman":
            build_cmd.extend(["--format", "docker"])
            
        subprocess.run(
            build_cmd,
            cwd=TEST_DOCKER_DIR,
            check=True
        )

        # 2. Run the container
        # Same flags as we had in compose.yml
        run_cmd = [
            runtime, "run", "-d",
            "--name", container_name,
            "-p", "8200:8200",
            "-e", "VAULT_DEV_ROOT_TOKEN_ID=root",
            "-e", "VAULT_ADDR=http://0.0.0.0:8200",
            image_name
        ]
        
        subprocess.run(run_cmd, check=True)

        # 3. Wait for readiness
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{VAULT_ADDR}/v1/sys/health")
                if response.status_code in (200, 429, 472, 473):
                    print(f"[setup] Vault ready after {i+1} attempts.")
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        else:
            subprocess.run([runtime, "logs", container_name])
            raise RuntimeError("Vault container failed to start within timeout.")

        yield

    finally:
        # 4. Teardown
        print("\n[teardown] Stopping Vault container...")
        subprocess.run(
            [runtime, "rm", "-f", container_name],
            check=False, # Don't error if it's already gone
            capture_output=True
        )


@pytest.fixture
def vault_config(vault_container, monkeypatch) -> GlobalConfig:
    """
    Provides a configured GlobalConfig pointing to our test container.
    """
    # 1. Inject Token
    monkeypatch.setenv("VAULT_TOKEN", VAULT_TOKEN)
    
    # 2. Configure GlobalConfig for Test
    config = GlobalConfig(
        current_profile="test",
        profile={
            "test": ProfileConfig(
                vault_url=VAULT_ADDR,
                vault_namespace=None
            )
        }
    )

    # 3. Patch load_config to return our test config
    # IMPORTANT: The app calls load_config() internally. We must intercept this call.
    # Since 'gds_dbtool.commands.vault' imports 'load_config' via 'from ..config import',
    # we must patch it in the namespace where it is USED, not where it is defined.
    monkeypatch.setattr("gds_dbtool.commands.vault.load_config", lambda: config)
    
    return config
