"""Tests for configuration models."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from mcpcli.config.models import (
    TimeoutConfig,
    ToolConfig,
    ConfigOverride,
    ServerDefinition,
    MCPConfig,
    VaultConfig,
    TokenStorageConfig,
)
from mcpcli.config.enums import TimeoutType
from mcpcli.config.defaults import (
    DEFAULT_STREAMING_CHUNK_TIMEOUT,
    DEFAULT_TOOL_EXECUTION_TIMEOUT,
    DEFAULT_SERVER_INIT_TIMEOUT,
    DEFAULT_MAX_TOOL_CONCURRENCY,
    DEFAULT_CONFIRM_TOOLS,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
)


class TestTimeoutConfig:
    """Tests for TimeoutConfig model."""

    def test_default_values(self) -> None:
        """TimeoutConfig should have proper defaults."""
        config = TimeoutConfig()
        assert config.streaming_chunk == DEFAULT_STREAMING_CHUNK_TIMEOUT
        assert config.tool_execution == DEFAULT_TOOL_EXECUTION_TIMEOUT
        assert config.server_init == DEFAULT_SERVER_INIT_TIMEOUT

    def test_get_by_enum(self) -> None:
        """TimeoutConfig.get should return value by TimeoutType enum."""
        config = TimeoutConfig()
        assert config.get(TimeoutType.STREAMING_CHUNK) == DEFAULT_STREAMING_CHUNK_TIMEOUT
        assert config.get(TimeoutType.TOOL_EXECUTION) == DEFAULT_TOOL_EXECUTION_TIMEOUT
        assert config.get(TimeoutType.SERVER_INIT) == DEFAULT_SERVER_INIT_TIMEOUT

    def test_custom_values(self) -> None:
        """TimeoutConfig should accept custom values."""
        config = TimeoutConfig(
            streaming_chunk=30.0,
            tool_execution=60.0,
            server_init=90.0,
        )
        assert config.streaming_chunk == 30.0
        assert config.tool_execution == 60.0
        assert config.server_init == 90.0

    def test_immutable(self) -> None:
        """TimeoutConfig should be immutable (frozen)."""
        config = TimeoutConfig()
        with pytest.raises(Exception):
            config.streaming_chunk = 100.0

    def test_validation_positive_values(self) -> None:
        """TimeoutConfig should reject non-positive values."""
        with pytest.raises(ValueError):
            TimeoutConfig(streaming_chunk=0)
        with pytest.raises(ValueError):
            TimeoutConfig(tool_execution=-10)


class TestToolConfig:
    """Tests for ToolConfig model."""

    def test_default_values(self) -> None:
        """ToolConfig should have proper defaults."""
        config = ToolConfig()
        assert config.include_tools is None
        assert config.exclude_tools is None
        assert config.confirm_tools == DEFAULT_CONFIRM_TOOLS
        assert config.max_concurrency == DEFAULT_MAX_TOOL_CONCURRENCY

    def test_include_tools(self) -> None:
        """ToolConfig should accept include_tools list."""
        config = ToolConfig(include_tools=["tool1", "tool2"])
        assert config.include_tools == ["tool1", "tool2"]

    def test_exclude_tools(self) -> None:
        """ToolConfig should accept exclude_tools list."""
        config = ToolConfig(exclude_tools=["tool3"])
        assert config.exclude_tools == ["tool3"]

    def test_max_concurrency_validation(self) -> None:
        """ToolConfig should reject max_concurrency < 1."""
        with pytest.raises(ValueError):
            ToolConfig(max_concurrency=0)


class TestConfigOverride:
    """Tests for ConfigOverride model."""

    def test_all_none_by_default(self) -> None:
        """ConfigOverride fields should be None by default."""
        override = ConfigOverride()
        assert override.provider is None
        assert override.model is None
        assert override.api_base is None
        assert override.api_key is None

    def test_has_override_returns_false_for_none(self) -> None:
        """has_override should return False for None values."""
        override = ConfigOverride()
        assert override.has_override("provider") is False
        assert override.has_override("model") is False

    def test_has_override_returns_true_for_set_values(self) -> None:
        """has_override should return True for set values."""
        override = ConfigOverride(provider="openai", model="gpt-4")
        assert override.has_override("provider") is True
        assert override.has_override("model") is True
        assert override.has_override("api_base") is False

    def test_accepts_all_override_fields(self) -> None:
        """ConfigOverride should accept all override fields."""
        override = ConfigOverride(
            provider="anthropic",
            model="claude-3",
            api_base="https://api.example.com",
            api_key="sk-test",
            theme="dark",
            verbose=True,
            quiet=False,
            log_level="DEBUG",
            token_backend="keychain",
            tool_timeout=60.0,
            init_timeout=30.0,
            max_turns=50,
        )
        assert override.provider == "anthropic"
        assert override.model == "claude-3"
        assert override.tool_timeout == 60.0


class TestServerDefinition:
    """Tests for ServerDefinition model."""

    def test_default_values(self) -> None:
        """ServerDefinition should have proper defaults."""
        server = ServerDefinition()
        assert server.command is None
        assert server.args == []
        assert server.env == {}
        assert server.enabled is True

    def test_stdio_server(self) -> None:
        """ServerDefinition should support stdio servers."""
        server = ServerDefinition(
            command="python",
            args=["-m", "mcp_server"],
            env={"DEBUG": "1"},
        )
        assert server.command == "python"
        assert server.args == ["-m", "mcp_server"]
        assert server.env == {"DEBUG": "1"}

    def test_http_server(self) -> None:
        """ServerDefinition should support HTTP servers."""
        server = ServerDefinition(
            url="https://api.example.com/mcp",
            headers={"Authorization": "Bearer token"},
        )
        assert server.url == "https://api.example.com/mcp"
        assert server.headers == {"Authorization": "Bearer token"}

    def test_disabled_server(self) -> None:
        """ServerDefinition should support disabled servers."""
        server = ServerDefinition(enabled=False)
        assert server.enabled is False


class TestMCPConfig:
    """Tests for MCPConfig model."""

    def test_default_values(self) -> None:
        """MCPConfig should have proper defaults."""
        config = MCPConfig()
        assert config.servers == {}
        assert config.default_provider == DEFAULT_PROVIDER
        assert config.default_model == DEFAULT_MODEL

    def test_load_sync_missing_file(self, tmp_path: Path) -> None:
        """MCPConfig.load_sync should return defaults for missing file."""
        config = MCPConfig.load_sync(tmp_path / "nonexistent.json")
        assert config.servers == {}
        assert config.default_provider == DEFAULT_PROVIDER

    def test_load_sync_valid_file(self, tmp_path: Path) -> None:
        """MCPConfig.load_sync should load from valid JSON file."""
        config_data = {
            "mcpServers": {
                "sqlite": {
                    "command": "python",
                    "args": ["-m", "sqlite_server"],
                }
            },
            "defaultProvider": "anthropic",
            "defaultModel": "claude-3",
        }
        config_file = tmp_path / "server_config.json"
        config_file.write_text(json.dumps(config_data))

        config = MCPConfig.load_sync(config_file)
        assert "sqlite" in config.servers
        assert config.servers["sqlite"].command == "python"
        assert config.default_provider == "anthropic"
        assert config.default_model == "claude-3"

    def test_load_sync_invalid_json(self, tmp_path: Path) -> None:
        """MCPConfig.load_sync should return defaults for invalid JSON."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("not valid json")

        config = MCPConfig.load_sync(config_file)
        assert config.servers == {}

    @pytest.mark.asyncio
    async def test_load_async(self, tmp_path: Path) -> None:
        """MCPConfig.load_async should load configuration asynchronously."""
        config_data = {
            "mcpServers": {
                "test": {"command": "echo", "args": ["hello"]}
            },
            "defaultProvider": "openai",
        }
        config_file = tmp_path / "async_config.json"
        config_file.write_text(json.dumps(config_data))

        config = await MCPConfig.load_async(config_file)
        assert "test" in config.servers
        assert config.default_provider == "openai"

    def test_get_server(self) -> None:
        """MCPConfig.get_server should return server by name."""
        config = MCPConfig(
            servers={
                "sqlite": ServerDefinition(command="python"),
                "echo": ServerDefinition(command="echo"),
            }
        )
        assert config.get_server("sqlite") is not None
        assert config.get_server("sqlite").command == "python"
        assert config.get_server("nonexistent") is None

    def test_get_enabled_servers(self) -> None:
        """MCPConfig.get_enabled_servers should return only enabled servers."""
        config = MCPConfig(
            servers={
                "enabled1": ServerDefinition(command="cmd1", enabled=True),
                "disabled": ServerDefinition(command="cmd2", enabled=False),
                "enabled2": ServerDefinition(command="cmd3", enabled=True),
            }
        )
        enabled = config.get_enabled_servers()
        assert len(enabled) == 2
        assert "enabled1" in enabled
        assert "enabled2" in enabled
        assert "disabled" not in enabled

    def test_snake_case_fields_work(self, tmp_path: Path) -> None:
        """MCPConfig should accept snake_case field names."""
        config_data = {
            "default_provider": "anthropic",
            "default_model": "claude-3",
        }
        config_file = tmp_path / "snake_config.json"
        config_file.write_text(json.dumps(config_data))

        config = MCPConfig.load_sync(config_file)
        assert config.default_provider == "anthropic"


class TestVaultConfig:
    """Tests for VaultConfig model."""

    def test_required_address(self) -> None:
        """VaultConfig should require address."""
        config = VaultConfig(address="https://vault.example.com")
        assert config.address == "https://vault.example.com"
        assert config.mount_path == "secret"
        assert config.token is None

    def test_full_config(self) -> None:
        """VaultConfig should accept all fields."""
        config = VaultConfig(
            address="https://vault.example.com",
            token="s.token",
            mount_path="kv",
            namespace="org",
        )
        assert config.token == "s.token"
        assert config.mount_path == "kv"
        assert config.namespace == "org"


class TestTokenStorageConfig:
    """Tests for TokenStorageConfig model."""

    def test_default_backend(self) -> None:
        """TokenStorageConfig should default to auto backend."""
        config = TokenStorageConfig()
        assert config.backend == "auto"
        assert config.vault is None

    def test_with_vault(self) -> None:
        """TokenStorageConfig should accept vault configuration."""
        vault = VaultConfig(address="https://vault.example.com")
        config = TokenStorageConfig(backend="vault", vault=vault)
        assert config.backend == "vault"
        assert config.vault.address == "https://vault.example.com"
