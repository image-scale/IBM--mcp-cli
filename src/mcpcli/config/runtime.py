"""Runtime configuration with override resolution.

Combines file configuration with CLI overrides and environment variables,
tracking the source of each resolved value.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from mcpcli.config.enums import ConfigSource, TimeoutType
from mcpcli.config.env_vars import EnvVar, get_env, get_env_float
from mcpcli.config.defaults import (
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    DEFAULT_THEME,
    DEFAULT_VERBOSE,
    DEFAULT_TOOL_EXECUTION_TIMEOUT,
    DEFAULT_SERVER_INIT_TIMEOUT,
)
from mcpcli.config.models import (
    MCPConfig,
    ConfigOverride,
    TimeoutConfig,
    ServerDefinition,
)


T = TypeVar("T")


@dataclass
class ResolvedValue(Generic[T]):
    """A configuration value with its source tracked.

    Attributes:
        value: The resolved configuration value.
        source: Where the value came from (CLI, ENV, FILE, DEFAULT).
    """

    value: T
    source: ConfigSource

    def __repr__(self) -> str:
        return f"ResolvedValue({self.value!r}, source={self.source.value})"


class RuntimeConfig:
    """Runtime configuration that resolves values from multiple sources.

    Resolution priority (highest to lowest):
    1. CLI overrides (ConfigOverride)
    2. Environment variables
    3. Configuration file (MCPConfig)
    4. Default values

    Example:
        config = RuntimeConfig(file_config, cli_overrides)
        provider = config.provider  # Returns resolved provider string
        provider_info = config.get_provider()  # Returns ResolvedValue with source
    """

    def __init__(
        self,
        file_config: MCPConfig | None = None,
        cli_overrides: ConfigOverride | None = None,
    ):
        """Initialize runtime configuration.

        Args:
            file_config: Configuration loaded from file.
            cli_overrides: CLI argument overrides.
        """
        self._file_config = file_config or MCPConfig()
        self._cli_overrides = cli_overrides or ConfigOverride()
        self._timeout_config = TimeoutConfig()

    def _resolve(
        self,
        cli_value: Any | None,
        env_var: EnvVar | None,
        file_value: Any | None,
        default_value: T,
    ) -> ResolvedValue[T]:
        """Resolve a configuration value from multiple sources.

        Args:
            cli_value: Value from CLI override (highest priority).
            env_var: Environment variable to check.
            file_value: Value from configuration file.
            default_value: Default value (lowest priority).

        Returns:
            ResolvedValue with the resolved value and its source.
        """
        if cli_value is not None:
            return ResolvedValue(cli_value, ConfigSource.CLI)

        if env_var is not None:
            env_value = get_env(env_var)
            if env_value is not None:
                return ResolvedValue(env_value, ConfigSource.ENV)

        if file_value is not None and file_value != default_value:
            return ResolvedValue(file_value, ConfigSource.FILE)

        return ResolvedValue(default_value, ConfigSource.DEFAULT)

    def get_provider(self) -> ResolvedValue[str]:
        """Get the resolved provider with source tracking.

        Returns:
            ResolvedValue containing the provider name and source.
        """
        return self._resolve(
            self._cli_overrides.provider,
            EnvVar.LLM_PROVIDER,
            self._file_config.default_provider,
            DEFAULT_PROVIDER,
        )

    @property
    def provider(self) -> str:
        """Get the resolved provider name."""
        return self.get_provider().value

    def get_model(self) -> ResolvedValue[str]:
        """Get the resolved model with source tracking.

        Returns:
            ResolvedValue containing the model name and source.
        """
        return self._resolve(
            self._cli_overrides.model,
            EnvVar.LLM_MODEL,
            self._file_config.default_model,
            DEFAULT_MODEL,
        )

    @property
    def model(self) -> str:
        """Get the resolved model name."""
        return self.get_model().value

    def get_theme(self) -> ResolvedValue[str]:
        """Get the resolved theme with source tracking."""
        return self._resolve(
            self._cli_overrides.theme,
            None,
            self._file_config.default_theme,
            DEFAULT_THEME,
        )

    @property
    def theme(self) -> str:
        """Get the resolved theme name."""
        return self.get_theme().value

    def get_verbose(self) -> ResolvedValue[bool]:
        """Get the resolved verbose mode with source tracking."""
        return self._resolve(
            self._cli_overrides.verbose,
            None,
            self._file_config.verbose,
            DEFAULT_VERBOSE,
        )

    @property
    def verbose(self) -> bool:
        """Get the resolved verbose mode."""
        return self.get_verbose().value

    def get_api_base(self) -> ResolvedValue[str | None]:
        """Get the resolved API base URL with source tracking."""
        if self._cli_overrides.api_base is not None:
            return ResolvedValue(self._cli_overrides.api_base, ConfigSource.CLI)
        return ResolvedValue(None, ConfigSource.DEFAULT)

    @property
    def api_base(self) -> str | None:
        """Get the resolved API base URL."""
        return self.get_api_base().value

    def get_api_key(self) -> ResolvedValue[str | None]:
        """Get the resolved API key with source tracking."""
        if self._cli_overrides.api_key is not None:
            return ResolvedValue(self._cli_overrides.api_key, ConfigSource.CLI)
        return ResolvedValue(None, ConfigSource.DEFAULT)

    @property
    def api_key(self) -> str | None:
        """Get the resolved API key."""
        return self.get_api_key().value

    def get_timeout(self, timeout_type: TimeoutType) -> ResolvedValue[float]:
        """Get a timeout value with source tracking.

        Args:
            timeout_type: The type of timeout to retrieve.

        Returns:
            ResolvedValue containing the timeout and source.
        """
        cli_timeout = None
        env_var = None

        if timeout_type == TimeoutType.TOOL_EXECUTION:
            cli_timeout = self._cli_overrides.tool_timeout
            env_var = EnvVar.TOOL_TIMEOUT
        elif timeout_type == TimeoutType.SERVER_INIT:
            cli_timeout = self._cli_overrides.init_timeout

        if cli_timeout is not None:
            return ResolvedValue(cli_timeout, ConfigSource.CLI)

        if env_var is not None:
            env_value = get_env_float(env_var)
            if env_value is not None:
                return ResolvedValue(env_value, ConfigSource.ENV)

        default_value = self._timeout_config.get(timeout_type)
        return ResolvedValue(default_value, ConfigSource.DEFAULT)

    def get_server_timeout(
        self,
        server_name: str,
        timeout_type: TimeoutType,
    ) -> float:
        """Get timeout for a specific server, falling back to global.

        Args:
            server_name: The server name.
            timeout_type: The type of timeout.

        Returns:
            The server-specific timeout if set, else global timeout.
        """
        server = self._file_config.get_server(server_name)
        if server is not None:
            if timeout_type == TimeoutType.TOOL_EXECUTION and server.tool_timeout is not None:
                return server.tool_timeout
            if timeout_type == TimeoutType.SERVER_INIT and server.init_timeout is not None:
                return server.init_timeout

        return self.get_timeout(timeout_type).value

    def get_server(self, name: str) -> ServerDefinition | None:
        """Get a server definition by name.

        Args:
            name: The server name.

        Returns:
            The server definition or None.
        """
        return self._file_config.get_server(name)

    def get_enabled_servers(self) -> dict[str, ServerDefinition]:
        """Get all enabled server definitions.

        Returns:
            Dictionary of enabled servers.
        """
        return self._file_config.get_enabled_servers()

    @property
    def servers(self) -> dict[str, ServerDefinition]:
        """Get all server definitions."""
        return self._file_config.servers


__all__ = [
    "ResolvedValue",
    "RuntimeConfig",
]
