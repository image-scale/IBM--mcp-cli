"""Configuration models using Pydantic for type-safe configuration.

Provides validated, type-safe configuration models for the CLI.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from mcpcli.config.enums import TimeoutType
from mcpcli.config.defaults import (
    DEFAULT_HTTP_CONNECT_TIMEOUT,
    DEFAULT_HTTP_REQUEST_TIMEOUT,
    DEFAULT_SERVER_INIT_TIMEOUT,
    DEFAULT_STREAMING_CHUNK_TIMEOUT,
    DEFAULT_STREAMING_FIRST_CHUNK_TIMEOUT,
    DEFAULT_STREAMING_GLOBAL_TIMEOUT,
    DEFAULT_TOOL_EXECUTION_TIMEOUT,
    DEFAULT_MAX_TOOL_CONCURRENCY,
    DEFAULT_CONFIRM_TOOLS,
    DEFAULT_DYNAMIC_TOOLS_ENABLED,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    DEFAULT_THEME,
    DEFAULT_VERBOSE,
)


class TimeoutConfig(BaseModel):
    """Timeout configuration with validated defaults.

    All values are in seconds. The model is immutable after creation.
    """

    streaming_chunk: float = Field(
        default=DEFAULT_STREAMING_CHUNK_TIMEOUT,
        gt=0,
        description="Timeout for each streaming chunk",
    )
    streaming_global: float = Field(
        default=DEFAULT_STREAMING_GLOBAL_TIMEOUT,
        gt=0,
        description="Maximum total streaming duration",
    )
    streaming_first_chunk: float = Field(
        default=DEFAULT_STREAMING_FIRST_CHUNK_TIMEOUT,
        gt=0,
        description="Timeout for first chunk",
    )
    tool_execution: float = Field(
        default=DEFAULT_TOOL_EXECUTION_TIMEOUT,
        gt=0,
        description="Tool execution timeout",
    )
    server_init: float = Field(
        default=DEFAULT_SERVER_INIT_TIMEOUT,
        gt=0,
        description="Server initialization timeout",
    )
    http_request: float = Field(
        default=DEFAULT_HTTP_REQUEST_TIMEOUT,
        gt=0,
        description="HTTP request timeout",
    )
    http_connect: float = Field(
        default=DEFAULT_HTTP_CONNECT_TIMEOUT,
        gt=0,
        description="HTTP connection timeout",
    )

    model_config = {"frozen": True}

    def get(self, timeout_type: TimeoutType) -> float:
        """Get timeout by enum type.

        Args:
            timeout_type: The timeout type to retrieve.

        Returns:
            The timeout value in seconds.
        """
        return getattr(self, timeout_type.value)


class ToolConfig(BaseModel):
    """Tool behavior configuration."""

    include_tools: list[str] | None = Field(
        default=None,
        description="Whitelist of tool names to include (None = all)",
    )
    exclude_tools: list[str] | None = Field(
        default=None,
        description="Blacklist of tool names to exclude",
    )
    confirm_tools: bool = Field(
        default=DEFAULT_CONFIRM_TOOLS,
        description="Require confirmation before executing tools",
    )
    max_concurrency: int = Field(
        default=DEFAULT_MAX_TOOL_CONCURRENCY,
        ge=1,
        description="Maximum concurrent tool executions",
    )
    dynamic_tools_enabled: bool = Field(
        default=DEFAULT_DYNAMIC_TOOLS_ENABLED,
        description="Enable dynamic tool discovery",
    )

    model_config = {"frozen": False}


class ConfigOverride(BaseModel):
    """CLI argument overrides for configuration.

    Captures command-line arguments that override file/default config.
    """

    provider: str | None = None
    model: str | None = None
    api_base: str | None = None
    api_key: str | None = None
    theme: str | None = None
    verbose: bool | None = None
    quiet: bool | None = None
    log_level: str | None = None
    token_backend: str | None = None
    tool_timeout: float | None = None
    init_timeout: float | None = None
    max_turns: int | None = None

    model_config = {"frozen": False}

    def has_override(self, field: str) -> bool:
        """Check if a specific field has an override value.

        Args:
            field: The field name to check.

        Returns:
            True if the field has a non-None value.
        """
        return getattr(self, field, None) is not None


class ServerDefinition(BaseModel):
    """Definition of an MCP server from configuration.

    Represents a server entry in the server_config.json file.
    """

    command: str | None = Field(default=None, description="Command to run (for stdio)")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    url: str | None = Field(default=None, description="Server URL (for http/sse)")
    headers: dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    enabled: bool = Field(default=True, description="Whether server is enabled")
    tool_timeout: float | None = Field(default=None, description="Server-specific tool timeout")
    init_timeout: float | None = Field(default=None, description="Server-specific init timeout")

    model_config = {"frozen": False, "extra": "allow"}


class MCPConfig(BaseModel):
    """Main MCP CLI configuration loaded from file.

    Handles loading and validation of the server configuration file.
    """

    servers: dict[str, ServerDefinition] = Field(
        default_factory=dict,
        alias="mcpServers",
        description="Server definitions by name",
    )
    default_provider: str = Field(
        default=DEFAULT_PROVIDER,
        alias="defaultProvider",
        description="Default LLM provider",
    )
    default_model: str = Field(
        default=DEFAULT_MODEL,
        alias="defaultModel",
        description="Default LLM model",
    )
    default_theme: str = Field(
        default=DEFAULT_THEME,
        alias="defaultTheme",
        description="Default UI theme",
    )
    verbose: bool = Field(
        default=DEFAULT_VERBOSE,
        description="Default verbose mode",
    )

    model_config = {"frozen": False, "populate_by_name": True, "extra": "ignore"}

    @classmethod
    def load_sync(cls, path: Path) -> MCPConfig:
        """Load configuration from a JSON file synchronously.

        Args:
            path: Path to the configuration file.

        Returns:
            The loaded configuration, or defaults if file doesn't exist.
        """
        if not path.exists():
            return cls()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.model_validate(data)
        except (json.JSONDecodeError, OSError):
            return cls()

    @classmethod
    async def load_async(cls, path: Path) -> MCPConfig:
        """Load configuration from a JSON file asynchronously.

        Args:
            path: Path to the configuration file.

        Returns:
            The loaded configuration, or defaults if file doesn't exist.
        """
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, cls.load_sync, path
        )

    def get_server(self, name: str) -> ServerDefinition | None:
        """Get a server definition by name.

        Args:
            name: The server name.

        Returns:
            The server definition or None if not found.
        """
        return self.servers.get(name)

    def get_enabled_servers(self) -> dict[str, ServerDefinition]:
        """Get all enabled server definitions.

        Returns:
            Dictionary of enabled servers by name.
        """
        return {
            name: server
            for name, server in self.servers.items()
            if server.enabled
        }


class VaultConfig(BaseModel):
    """HashiCorp Vault configuration for token storage."""

    address: str = Field(description="Vault server address")
    token: str | None = Field(default=None, description="Vault authentication token")
    mount_path: str = Field(default="secret", description="KV secrets engine mount path")
    namespace: str | None = Field(default=None, description="Vault namespace")

    model_config = {"frozen": False}


class TokenStorageConfig(BaseModel):
    """Token storage backend configuration."""

    backend: str = Field(default="auto", description="Storage backend type")
    vault: VaultConfig | None = Field(default=None, description="Vault configuration")
    encrypted_file_path: str | None = Field(
        default=None, description="Path for encrypted file storage"
    )

    model_config = {"frozen": False}


__all__ = [
    "TimeoutConfig",
    "ToolConfig",
    "ConfigOverride",
    "ServerDefinition",
    "MCPConfig",
    "VaultConfig",
    "TokenStorageConfig",
]
