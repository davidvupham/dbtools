#!/usr/bin/env python3
"""Unit tests for vault_secrets Ansible role.

These tests validate the role's variable handling, authentication logic,
and secret retrieval patterns without requiring a real Vault server.
"""

from pathlib import Path

import pytest
import yaml

# Get the role path
ROLE_PATH = Path(__file__).parent.parent.parent
DEFAULTS_FILE = ROLE_PATH / "defaults" / "main.yml"
VARS_FILE = ROLE_PATH / "vars" / "main.yml"
TASKS_DIR = ROLE_PATH / "tasks"


class TestRoleStructure:
    """Test that the role has the required file structure."""

    def test_defaults_file_exists(self):
        """Verify defaults/main.yml exists."""
        assert DEFAULTS_FILE.exists(), "defaults/main.yml must exist"

    def test_vars_file_exists(self):
        """Verify vars/main.yml exists."""
        assert VARS_FILE.exists(), "vars/main.yml must exist"

    def test_tasks_main_exists(self):
        """Verify tasks/main.yml exists."""
        assert (TASKS_DIR / "main.yml").exists(), "tasks/main.yml must exist"

    def test_authenticate_tasks_exist(self):
        """Verify authentication task file exists."""
        assert (TASKS_DIR / "authenticate.yml").exists(), "tasks/authenticate.yml must exist"

    def test_validate_auth_tasks_exist(self):
        """Verify validation task file exists."""
        assert (TASKS_DIR / "validate_auth.yml").exists(), "tasks/validate_auth.yml must exist"

    def test_get_secrets_tasks_exist(self):
        """Verify secret retrieval task file exists."""
        assert (TASKS_DIR / "get_secrets.yml").exists(), "tasks/get_secrets.yml must exist"

    def test_meta_file_exists(self):
        """Verify meta/main.yml exists."""
        meta_file = ROLE_PATH / "meta" / "main.yml"
        assert meta_file.exists(), "meta/main.yml must exist"


class TestDefaultVariables:
    """Test default variable definitions."""

    @pytest.fixture
    def defaults(self):
        """Load default variables."""
        with open(DEFAULTS_FILE) as f:
            return yaml.safe_load(f)

    def test_vault_addr_has_default(self, defaults):
        """Verify vault_addr has a fallback default."""
        assert "vault_addr" in defaults
        # The default uses lookup, so we check the structure
        assert "VAULT_ADDR" in str(defaults["vault_addr"])

    def test_vault_auth_method_default_is_approle(self, defaults):
        """Verify default auth method is AppRole (recommended for automation)."""
        assert defaults["vault_auth_method"] == "approle"

    def test_vault_validate_certs_default_is_true(self, defaults):
        """Verify SSL validation is enabled by default."""
        assert defaults["vault_validate_certs"] is True

    def test_vault_kv_version_default_is_2(self, defaults):
        """Verify KV v2 is the default secrets engine version."""
        assert defaults["vault_kv_version"] == 2

    def test_vault_secrets_to_fetch_is_empty_list(self, defaults):
        """Verify secrets list is empty by default."""
        assert defaults["vault_secrets_to_fetch"] == []

    def test_vault_missing_secret_behavior_default_is_fail(self, defaults):
        """Verify missing secrets cause failure by default."""
        assert defaults["vault_missing_secret_behavior"] == "fail"

    def test_vault_retries_has_default(self, defaults):
        """Verify retry settings exist."""
        assert defaults["vault_retries"] == 3
        assert defaults["vault_retry_delay"] == 1

    def test_vault_cache_secrets_default_is_true(self, defaults):
        """Verify caching is enabled by default."""
        assert defaults["vault_cache_secrets"] is True

    def test_all_auth_credentials_use_env_lookups(self, defaults):
        """Verify credentials can be loaded from environment variables."""
        env_vars = [
            ("vault_approle_role_id", "VAULT_ROLE_ID"),
            ("vault_approle_secret_id", "VAULT_SECRET_ID"),
            ("vault_token", "VAULT_TOKEN"),
            ("vault_jwt", "VAULT_JWT"),
            ("vault_username", "VAULT_USERNAME"),
            ("vault_password", "VAULT_PASSWORD"),
        ]
        for var_name, env_name in env_vars:
            assert env_name in str(defaults[var_name]), f"{var_name} should reference {env_name}"


class TestInternalVariables:
    """Test internal/vars variable definitions."""

    @pytest.fixture
    def vars_data(self):
        """Load internal variables."""
        with open(VARS_FILE) as f:
            return yaml.safe_load(f)

    def test_supported_auth_methods_defined(self, vars_data):
        """Verify supported auth methods are listed."""
        assert "vault_supported_auth_methods" in vars_data
        methods = vars_data["vault_supported_auth_methods"]
        assert "approle" in methods
        assert "token" in methods
        assert "jwt" in methods
        assert "kubernetes" in methods
        assert "ldap" in methods
        assert "userpass" in methods

    def test_auth_method_descriptions_exist(self, vars_data):
        """Verify each auth method has a description."""
        descriptions = vars_data["vault_auth_method_descriptions"]
        for method in vars_data["vault_supported_auth_methods"]:
            assert method in descriptions, f"Missing description for {method}"


class TestTaskFiles:
    """Test task file structure and content."""

    def load_tasks(self, filename: str) -> list:
        """Load tasks from a YAML file."""
        with open(TASKS_DIR / filename) as f:
            return yaml.safe_load(f)

    def test_main_tasks_include_validation(self):
        """Verify main.yml includes validation tasks."""
        tasks = self.load_tasks("main.yml")
        task_names = [t.get("name", "") for t in tasks]
        assert any("validate" in name.lower() for name in task_names)

    def test_main_tasks_include_authentication(self):
        """Verify main.yml includes authentication tasks."""
        tasks = self.load_tasks("main.yml")
        task_files = [t.get("ansible.builtin.include_tasks", "") for t in tasks]
        assert any("authenticate" in str(f) for f in task_files)

    def test_main_tasks_include_secrets_retrieval(self):
        """Verify main.yml includes secret retrieval tasks."""
        tasks = self.load_tasks("main.yml")
        task_files = [t.get("ansible.builtin.include_tasks", "") for t in tasks]
        assert any("secret" in str(f) for f in task_files)

    def test_authenticate_tasks_have_no_log(self):
        """Verify authentication tasks use no_log for sensitive data."""
        tasks = self.load_tasks("authenticate.yml")
        # Only check vault_login module tasks (not debug or set_fact)
        login_tasks = [t for t in tasks if "community.hashi_vault.vault_login" in str(t)]
        assert len(login_tasks) > 0, "Should have vault_login tasks"
        for task in login_tasks:
            assert task.get("no_log") is True, f"Task '{task.get('name')}' should have no_log: true"

    def test_authenticate_tasks_have_retries(self):
        """Verify authentication tasks have retry logic."""
        tasks = self.load_tasks("authenticate.yml")
        # Only check vault_login module tasks (not set_fact or debug)
        login_tasks = [t for t in tasks if "community.hashi_vault.vault_login" in str(t)]
        assert len(login_tasks) > 0, "Should have vault_login tasks"
        for task in login_tasks:
            assert "retries" in task, f"Task '{task.get('name')}' should have retries"
            assert "until" in task, f"Task '{task.get('name')}' should have until condition"

    def test_get_secrets_tasks_have_no_log(self):
        """Verify secret retrieval tasks use no_log."""
        tasks = self.load_tasks("get_secrets.yml")
        secret_tasks = [t for t in tasks if "vault_kv" in str(t) or "set_fact" in str(t)]
        for task in secret_tasks:
            if "set_fact" in str(task) or "vault_kv" in str(task):
                assert task.get("no_log") is True, f"Task '{task.get('name')}' should have no_log: true"

    def test_validate_auth_covers_all_methods(self):
        """Verify validation exists for all auth methods."""
        tasks = self.load_tasks("validate_auth.yml")
        # Check that we have validation for each method
        task_conditions = [str(t.get("when", "")) for t in tasks]
        auth_methods = ["approle", "token", "jwt", "kubernetes", "ldap", "userpass"]
        for method in auth_methods:
            assert any(method in cond for cond in task_conditions), f"Missing validation for {method}"


class TestMetaFile:
    """Test role metadata."""

    @pytest.fixture
    def meta(self):
        """Load role metadata."""
        with open(ROLE_PATH / "meta" / "main.yml") as f:
            return yaml.safe_load(f)

    def test_min_ansible_version_specified(self, meta):
        """Verify minimum Ansible version is specified."""
        assert "min_ansible_version" in meta["galaxy_info"]

    def test_collection_dependency_specified(self, meta):
        """Verify community.hashi_vault collection dependency."""
        collections = meta.get("collections", [])
        collection_names = [c.get("name", "") for c in collections]
        assert "community.hashi_vault" in collection_names

    def test_supported_platforms_specified(self, meta):
        """Verify supported platforms are listed."""
        platforms = meta["galaxy_info"]["platforms"]
        assert len(platforms) > 0

    def test_role_has_tags(self, meta):
        """Verify role has galaxy tags for discoverability."""
        tags = meta["galaxy_info"]["galaxy_tags"]
        assert "vault" in tags
        assert "secrets" in tags


class TestSecurityBestPractices:
    """Test that the role follows security best practices."""

    def test_no_hardcoded_credentials_in_defaults(self):
        """Verify no hardcoded credentials in defaults."""
        with open(DEFAULTS_FILE) as f:
            content = f.read()
        # Check for common credential patterns
        forbidden_patterns = [
            "password:",
            "secret:",
            "token:",
            "key:",
        ]
        for pattern in forbidden_patterns:
            # Allow patterns that are variable references or lookups
            if pattern in content:
                # Ensure it's a variable definition using lookup, not a hardcoded value
                lines = [ln for ln in content.split("\n") if pattern in ln]
                for line in lines:
                    # Skip comment lines
                    if line.strip().startswith("#"):
                        continue
                    assert (
                        "lookup" in line
                        or "{{ " in line
                        or '""' in line
                        or "default(" in line
                        or line.strip().endswith(":")
                    ), f"Possible hardcoded credential: {line}"

    def test_all_task_files_are_valid_yaml(self):
        """Verify all task files are valid YAML."""
        for task_file in TASKS_DIR.glob("*.yml"):
            with open(task_file) as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {task_file}: {e}")


class TestEnvironmentVariableMapping:
    """Test that environment variables are properly mapped."""

    @pytest.fixture
    def defaults(self):
        """Load default variables."""
        with open(DEFAULTS_FILE) as f:
            return yaml.safe_load(f)

    def test_vault_addr_env_mapping(self, defaults):
        """Verify VAULT_ADDR environment variable mapping."""
        assert "VAULT_ADDR" in str(defaults["vault_addr"])

    def test_vault_namespace_env_mapping(self, defaults):
        """Verify VAULT_NAMESPACE environment variable mapping."""
        assert "VAULT_NAMESPACE" in str(defaults["vault_namespace"])

    def test_approle_credentials_env_mapping(self, defaults):
        """Verify AppRole credentials use environment variables."""
        assert "VAULT_ROLE_ID" in str(defaults["vault_approle_role_id"])
        assert "VAULT_SECRET_ID" in str(defaults["vault_approle_secret_id"])

    def test_token_env_mapping(self, defaults):
        """Verify VAULT_TOKEN environment variable mapping."""
        assert "VAULT_TOKEN" in str(defaults["vault_token"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
