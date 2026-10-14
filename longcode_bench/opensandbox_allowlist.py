"""Harbor OpenSandbox adapter with creation-time hostname allowlists.

Harbor 0.23.0's built-in OpenSandbox adapter supports public networking and
deny-all networking. It does not advertise allowlist support, although the
OpenSandbox SDK accepts a NetworkPolicy when a sandbox is created.

This subclass only adds the missing creation-time translation. It deliberately
does not advertise dynamic network-policy switching.
"""

from typing import Any, override

from harbor.environments.capabilities import EnvironmentCapabilities
from harbor.environments.opensandbox import OpenSandboxEnvironment
from harbor.models.task.config import NetworkMode
from harbor.models.trial.paths import EnvironmentPaths


class AllowlistOpenSandboxEnvironment(OpenSandboxEnvironment):
    """OpenSandbox environment with FQDN and wildcard FQDN allowlists."""

    @property
    @override
    def capabilities(self) -> EnvironmentCapabilities:
        return EnvironmentCapabilities(
            gpus=True,
            disable_internet=True,
            network_allowlist=True,
            network_allowlist_hostnames=True,
            network_allowlist_wildcard_hostnames=True,
            dynamic_network_policy=False,
            mounted=False,
        )

    @override
    def _load_opensandbox(self) -> dict[str, Any]:
        sdk = super()._load_opensandbox()
        from opensandbox.models.sandboxes import NetworkRule

        sdk["NetworkRule"] = NetworkRule
        return sdk

    @override
    def _build_network_policy(self, sdk: dict[str, Any]) -> Any | None:
        policy = self.network_policy

        if policy.network_mode == NetworkMode.PUBLIC:
            return None

        if policy.network_mode == NetworkMode.NO_NETWORK:
            return sdk["NetworkPolicy"](
                defaultAction="deny",
                egress=[],
            )

        rules = [
            sdk["NetworkRule"](action="allow", target=host)
            for host in policy.allowed_hosts
        ]
        return sdk["NetworkPolicy"](
            defaultAction="deny",
            egress=rules,
        )

    @override
    async def _upload_environment_dir_after_start(self) -> None:
        """Place Harbor's separate-verifier context at its expected path.

        Harbor passes task/tests as the environment build context for a
        separate verifier and then asks the verifier to skip its normal tests
        upload. The built-in prebuilt-image path uploads every context to the
        task workdir, leaving /tests empty. Detect that verifier context and
        upload it to Harbor's reserved tests directory.
        """
        verifier_scripts = ("test.sh", "test.bat", "test.cmd", "test.ps1")
        is_verifier_context = (
            self.environment_dir.name == "tests"
            and any(
                (self.environment_dir / script).is_file()
                for script in verifier_scripts
            )
        )
        if not is_verifier_context:
            await super()._upload_environment_dir_after_start()
            return

        tests_dir = EnvironmentPaths.for_os(self.os).tests_dir
        self.logger.debug(
            "Uploading separate verifier tests/ to %s",
            tests_dir,
        )
        await self.upload_dir(self.environment_dir, str(tests_dir))

