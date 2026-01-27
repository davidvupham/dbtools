# ==============================================================================
# Integration Tests: Vault CLI
# ==============================================================================
# These tests run against the REAL Vault container spun up by 'conftest.py'.
#
# EDUCATIONAL GOAL:
# Demonstrate "Black Box Testing" of a CLI tool. We don't call internal functions;
# instead, we invoke the CLI command just like a user would and check the output.

from gds_dbtool.main import app
from gds_dbtool.constants import ExitCode
from typer.testing import CliRunner
import pytest

# Initialize the test runner
runner = CliRunner()

# Override the persistent token storage for tests
# We don't want tests to overwrite the developer's actual token file!
@pytest.fixture(autouse=True)
def mock_token_store(monkeypatch, tmp_path):
    """
    Automatically redirect token storage to a temporary file.
    'autouse=True' means this runs for every test in this file.
    """
    # Create a temp file path
    test_token_file = tmp_path / ".dbtool_token"
    test_token_file.write_text("root") # Pre-seed with root token
    
    # Patch the function in 'gds_dbtool.token_store' that returns the path
    monkeypatch.setattr("gds_dbtool.token_store.get_token_location", lambda: test_token_file)
    
    # IMPORTANT: 'commands.vault' imports 'load_token' directly.
    # We must patch it where it is USED.
    monkeypatch.setattr("gds_dbtool.commands.vault.load_token", lambda: "root")
    
    # Also patch the original source just in case other modules use it
    monkeypatch.setattr("gds_dbtool.token_store.load_token", lambda: "root")


def test_vault_lifecycle(vault_config):
    """
    SCENARIO 1: Basic Lifecycle (Happy Path)
    Verifies that we can Perform CRUD (Create, Read, Update, Delete) operations.
    """
    
    # 1. PUT (Create)
    # We write a secret to 'secret/data/test-lifecycle'
    # Note: In KV v2, the path is 'secret/data/...', but the CLI handles the 'data' part if configured.
    # For raw put, we just use the full path.
    result = runner.invoke(app, ["vault", "put", "secret/data/integration-test", "foo=bar", "--force"])
    if result.exit_code != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    assert result.exit_code == 0
    assert "Successfully wrote" in result.output

    # 2. GET (Read)
    result = runner.invoke(app, ["vault", "get", "secret/data/integration-test"])
    assert result.exit_code == 0
    assert "foo" in result.output
    assert "bar" in result.output

    # 3. LIST (Discover)
    # Listing the parent directory should show our secret
    result = runner.invoke(app, ["vault", "list", "secret/data"])
    assert result.exit_code == 0
    assert "integration-test" in result.output

    # 4. DELETE (Cleanup)
    # Default delete is "soft" (versioned), but cleans up the latest version
    result = runner.invoke(app, ["vault", "delete", "secret/data/integration-test", "--force"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_overwrite_protection(vault_config):
    """
    SCENARIO 2: Overwrite Protection
    Verifies that the CLI prompts the user before overwriting existing data.
    """
    
    # Setup: Create a secret first
    runner.invoke(app, ["vault", "put", "secret/data/overwrite-test", "safe=true", "--force"])

    # Attempt to overwrite WITHOUT --force
    # We pass input="n\n" to simulate typing 'n' (No) at the prompt
    result = runner.invoke(app, ["vault", "put", "secret/data/overwrite-test", "unsafe=true"], input="n\n")
    
    # Expectation: The process aborted because we said No
    assert result.exit_code != 0
    assert "Overwrite/Update?" in result.output
    assert "Aborted" in result.output or result.exit_code == 1

    # verify original data is untouched
    result = runner.invoke(app, ["vault", "get", "secret/data/overwrite-test"])
    assert "safe" in result.output


def test_deletion_modes(vault_config):
    """
    SCENARIO 3: Deletion Modes (Soft vs Hard)
    Verifies the difference between version deletion and metadata destruction.
    """
    path = "secret/data/delete-mode-test"
    
    # Setup
    runner.invoke(app, ["vault", "put", path, "v=1", "--force"])

    # 1. Soft Delete
    result = runner.invoke(app, ["vault", "delete", path, "--force"])
    assert result.exit_code == 0
    assert "Deleted" in result.output
    assert "recovered" in result.output
    
    # Verify it's gone from GET
    result = runner.invoke(app, ["vault", "get", path])
    # Vault soft-delete behavior: the *latest version* is deleted, reading it might fail or return metadata stating deletion.
    # Our CLI wrapper usually throws 404 or a clear message.
    assert result.exit_code != 0 # Should fail to read the deleted version

    # 2. Hard Delete (Destroy Metadata)
    # Re-create to have something to destroy
    runner.invoke(app, ["vault", "put", path, "v=2", "--force"])
    
    result = runner.invoke(app, ["vault", "delete", path, "--hard", "--force"])
    assert result.exit_code == 0
    assert "Permanently destroyed" in result.output


def test_error_handling(vault_config):
    """
    SCENARIO 4: Error Handling
    Verifies the tool behaves correctly when things go wrong.
    """
    
    # 1. Non-existent path
    result = runner.invoke(app, ["vault", "get", "secret/data/non-existent-ghost"])
    assert result.exit_code == ExitCode.RESOURCE_NOT_FOUND
    assert "Secret not found" in result.output

    # 2. Invalid Mount Point
    # 'sys' is a system mount, usually read-only or restricted for KV operations
    result = runner.invoke(app, ["vault", "put", "sys/protected", "foo=bar", "--force"])
    # This might return Forbidden (403) or Invalid Path depending on Vault config
    assert result.exit_code != 0 


def test_output_formats(vault_config):
    """
    SCENARIO 5: Output Formats
    Verifies that JSON output is machine-readable and Table output is human-readable.
    """
    path = "secret/data/fmt-test"
    runner.invoke(app, ["vault", "put", path, "color=blue", "--force"])

    # 1. JSON Format
    result = runner.invoke(app, ["vault", "get", path, "--format", "json"])
    assert result.exit_code == 0
    # Use standard library to parse output and verify it's valid JSON
    import json
    data = json.loads(result.output)
    assert data["color"] == "blue"

    # 2. Table Format
    result = runner.invoke(app, ["vault", "get", path, "--format", "table"])
    assert result.exit_code == 0
    # Rich tables usually contain box drawing characters or headers
    assert "Key" in result.output
    assert "Value" in result.output
    assert "blue" in result.output
