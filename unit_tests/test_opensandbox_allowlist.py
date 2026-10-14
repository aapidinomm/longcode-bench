import logging
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from harbor.environments.opensandbox import OpenSandboxEnvironment
from harbor.models.task.config import NetworkMode, NetworkPolicy, TaskOS
from opensandbox.models.sandboxes import (
    NetworkPolicy as OpenSandboxNetworkPolicy,
    NetworkRule,
)

from longcode_bench.opensandbox_allowlist import (
    AllowlistOpenSandboxEnvironment,
)


def uninitialized(environment_type, policy):
    environment = object.__new__(environment_type)
    environment._network_policy = policy
    environment._phase_network_policies = []
    return environment


SDK = {
    "NetworkPolicy": OpenSandboxNetworkPolicy,
    "NetworkRule": NetworkRule,
}


class OpenSandboxAllowlistTests(unittest.TestCase):
    def test_builtin_adapter_rejects_allowlist(self):
        environment = uninitialized(
            OpenSandboxEnvironment,
            NetworkPolicy(
                network_mode=NetworkMode.ALLOWLIST,
                allowed_hosts=["example.com"],
            ),
        )
        with self.assertRaisesRegex(ValueError, "allowlist.*not supported"):
            environment.validate_network_policy_support()

    def test_custom_adapter_accepts_hostnames_and_wildcards(self):
        environment = uninitialized(
            AllowlistOpenSandboxEnvironment,
            NetworkPolicy(
                network_mode=NetworkMode.ALLOWLIST,
                allowed_hosts=["example.com", "*.python.org"],
            ),
        )
        environment.validate_network_policy_support()

    def test_custom_adapter_rejects_ip_allowlist_entries(self):
        environment = uninitialized(
            AllowlistOpenSandboxEnvironment,
            NetworkPolicy(
                network_mode=NetworkMode.ALLOWLIST,
                allowed_hosts=["192.0.2.1"],
            ),
        )
        with self.assertRaisesRegex(ValueError, "IPv4 addresses.*not supported"):
            environment.validate_network_policy_support()

    def test_allowlist_translates_to_default_deny_rules(self):
        environment = uninitialized(
            AllowlistOpenSandboxEnvironment,
            NetworkPolicy(
                network_mode=NetworkMode.ALLOWLIST,
                allowed_hosts=["example.com", "*.python.org"],
            ),
        )
        result = environment._build_network_policy(SDK)
        self.assertEqual(
            result.model_dump(by_alias=True),
            {
                "defaultAction": "deny",
                "egress": [
                    {"action": "allow", "target": "example.com"},
                    {"action": "allow", "target": "*.python.org"},
                ],
            },
        )

    def test_no_network_translates_to_empty_default_deny(self):
        environment = uninitialized(
            AllowlistOpenSandboxEnvironment,
            NetworkPolicy(network_mode=NetworkMode.NO_NETWORK),
        )
        result = environment._build_network_policy(SDK)
        self.assertEqual(
            result.model_dump(by_alias=True),
            {"defaultAction": "deny", "egress": []},
        )

    def test_public_network_omits_policy(self):
        environment = uninitialized(
            AllowlistOpenSandboxEnvironment,
            NetworkPolicy(network_mode=NetworkMode.PUBLIC),
        )
        self.assertIsNone(environment._build_network_policy(SDK))

    def test_dynamic_policy_switching_is_not_advertised(self):
        environment = uninitialized(
            AllowlistOpenSandboxEnvironment,
            NetworkPolicy(network_mode=NetworkMode.PUBLIC),
        )
        self.assertFalse(environment.capabilities.dynamic_network_policy)

    def test_separate_verifier_context_uploads_to_tests_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            tests_dir = Path(directory) / "tests"
            tests_dir.mkdir()
            (tests_dir / "test.sh").write_text("#!/bin/sh\n")

            environment = object.__new__(AllowlistOpenSandboxEnvironment)
            environment.environment_dir = tests_dir
            environment.task_env_config = SimpleNamespace(os=TaskOS.LINUX)
            environment.logger = logging.getLogger("test")
            environment.upload_dir = AsyncMock()

            import asyncio

            asyncio.run(environment._upload_environment_dir_after_start())
            environment.upload_dir.assert_awaited_once_with(tests_dir, "/tests")

    def test_agent_environment_context_preserves_workdir_upload(self):
        with tempfile.TemporaryDirectory() as directory:
            agent_dir = Path(directory) / "environment"
            agent_dir.mkdir()
            (agent_dir / "egress_canary.py").write_text("# canary\n")

            environment = object.__new__(AllowlistOpenSandboxEnvironment)
            environment.environment_dir = agent_dir
            environment.task_env_config = SimpleNamespace(
                docker_image="example@sha256:digest",
                workdir="/app",
                os=TaskOS.LINUX,
            )
            environment.logger = logging.getLogger("test")
            environment.upload_dir = AsyncMock()

            import asyncio

            asyncio.run(environment._upload_environment_dir_after_start())
            environment.upload_dir.assert_awaited_once_with(agent_dir, "/app")


if __name__ == "__main__":
    unittest.main()

