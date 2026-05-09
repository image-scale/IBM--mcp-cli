"""Tests for runtime configuration with override resolution."""

from __future__ import annotations

import pytest

from mcpcli.config.runtime import RuntimeConfig, ResolvedValue
from mcpcli.config.models import MCPConfig, ConfigOverride, ServerDefinition
from mcpcli.config.enums import ConfigSource, TimeoutType
from mcpcli.config.defaults import (
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    DEFAULT_THEME,
    DEFAULT_TOOL_EXECUTION_TIMEOUT,
    DEFAULT_SERVER_INIT_TIMEOUT,
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clean environment variables that might interfere with tests."""
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("MCP_TOOL_TIMEOUT", raising=False)


class TestResolvedValue:
    """Tests for ResolvedValue dataclass."""

    def test_stores_value_and_source(self) -> None:
        """ResolvedValue should store value and source."""
        resolved = ResolvedValue("openai", ConfigSource.CLI)
        assert resolved.value == "openai"
        assert resolved.source == ConfigSource.CLI

    def test_repr(self) -> None:
        """ResolvedValue should have readable repr."""
        resolved = ResolvedValue("gpt-4", ConfigSource.FILE)
        assert "gpt-4" in repr(resolved)
        assert "file" in repr(resolved)


class TestRuntimeConfigProvider:
    """Tests for provider resolution."""

    def test_default_provider(self) -> None:
        """RuntimeConfig should return default provider when nothing set."""
        config = RuntimeConfig()
        assert config.provider == DEFAULT_PROVIDER
        assert config.get_provider().source == ConfigSource.DEFAULT

    def test_file_provider_override(self) -> None:
        """RuntimeConfig should use file config provider."""
        file_config = MCPConfig(default_provider="anthropic")
        config = RuntimeConfig(file_config=file_config)
        assert config.provider == "anthropic"
        assert config.get_provider().source == ConfigSource.FILE

    def test_cli_provider_override(self) -> None:
        """CLI override should take precedence over file config."""
        file_config = MCPConfig(default_provider="anthropic")
        cli_overrides = ConfigOverride(provider="openai")
        config = RuntimeConfig(file_config=file_config, cli_overrides=cli_overrides)
        assert config.provider == "openai"
        assert config.get_provider().source == ConfigSource.CLI

    def test_env_provider_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Environment variable should override file config."""
        file_config = MCPConfig(default_provider="anthropic")
        monkeypatch.setenv("LLM_PROVIDER", "groq")
        config = RuntimeConfig(file_config=file_config)
        assert config.provider == "groq"
        assert config.get_provider().source == ConfigSource.ENV

    def test_cli_overrides_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """CLI should override environment variable."""
        monkeypatch.setenv("LLM_PROVIDER", "groq")
        cli_overrides = ConfigOverride(provider="ollama")
        config = RuntimeConfig(cli_overrides=cli_overrides)
        assert config.provider == "ollama"
        assert config.get_provider().source == ConfigSource.CLI


class TestRuntimeConfigModel:
    """Tests for model resolution."""

    def test_default_model(self) -> None:
        """RuntimeConfig should return default model when nothing set."""
        config = RuntimeConfig()
        assert config.model == DEFAULT_MODEL
        assert config.get_model().source == ConfigSource.DEFAULT

    def test_file_model_override(self) -> None:
        """RuntimeConfig should use file config model."""
        file_config = MCPConfig(default_model="claude-3")
        config = RuntimeConfig(file_config=file_config)
        assert config.model == "claude-3"
        assert config.get_model().source == ConfigSource.FILE

    def test_cli_model_override(self) -> None:
        """CLI override should take precedence."""
        file_config = MCPConfig(default_model="claude-3")
        cli_overrides = ConfigOverride(model="gpt-4")
        config = RuntimeConfig(file_config=file_config, cli_overrides=cli_overrides)
        assert config.model == "gpt-4"
        assert config.get_model().source == ConfigSource.CLI


class TestRuntimeConfigTheme:
    """Tests for theme resolution."""

    def test_default_theme(self) -> None:
        """RuntimeConfig should return default theme."""
        config = RuntimeConfig()
        assert config.theme == DEFAULT_THEME

    def test_file_theme_override(self) -> None:
        """RuntimeConfig should use file config theme."""
        file_config = MCPConfig(default_theme="dark")
        config = RuntimeConfig(file_config=file_config)
        assert config.theme == "dark"

    def test_cli_theme_override(self) -> None:
        """CLI override should take precedence."""
        cli_overrides = ConfigOverride(theme="monokai")
        config = RuntimeConfig(cli_overrides=cli_overrides)
        assert config.theme == "monokai"


class TestRuntimeConfigTimeouts:
    """Tests for timeout resolution."""

    def test_default_tool_timeout(self) -> None:
        """RuntimeConfig should return default tool timeout."""
        config = RuntimeConfig()
        result = config.get_timeout(TimeoutType.TOOL_EXECUTION)
        assert result.value == DEFAULT_TOOL_EXECUTION_TIMEOUT
        assert result.source == ConfigSource.DEFAULT

    def test_cli_tool_timeout_override(self) -> None:
        """CLI should override tool timeout."""
        cli_overrides = ConfigOverride(tool_timeout=60.0)
        config = RuntimeConfig(cli_overrides=cli_overrides)
        result = config.get_timeout(TimeoutType.TOOL_EXECUTION)
        assert result.value == 60.0
        assert result.source == ConfigSource.CLI

    def test_env_tool_timeout_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Environment variable should override tool timeout."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "90.0")
        config = RuntimeConfig()
        result = config.get_timeout(TimeoutType.TOOL_EXECUTION)
        assert result.value == 90.0
        assert result.source == ConfigSource.ENV

    def test_server_init_timeout(self) -> None:
        """RuntimeConfig should return server init timeout."""
        config = RuntimeConfig()
        result = config.get_timeout(TimeoutType.SERVER_INIT)
        assert result.value == DEFAULT_SERVER_INIT_TIMEOUT

    def test_cli_init_timeout_override(self) -> None:
        """CLI should override init timeout."""
        cli_overrides = ConfigOverride(init_timeout=30.0)
        config = RuntimeConfig(cli_overrides=cli_overrides)
        result = config.get_timeout(TimeoutType.SERVER_INIT)
        assert result.value == 30.0
        assert result.source == ConfigSource.CLI


class TestRuntimeConfigServerTimeouts:
    """Tests for server-specific timeout resolution."""

    def test_server_timeout_fallback_to_global(self) -> None:
        """Server timeout should fall back to global when not set."""
        file_config = MCPConfig(
            servers={"test": ServerDefinition(command="echo")}
        )
        config = RuntimeConfig(file_config=file_config)
        timeout = config.get_server_timeout("test", TimeoutType.TOOL_EXECUTION)
        assert timeout == DEFAULT_TOOL_EXECUTION_TIMEOUT

    def test_server_specific_tool_timeout(self) -> None:
        """Server-specific tool timeout should be used when set."""
        file_config = MCPConfig(
            servers={"test": ServerDefinition(command="echo", tool_timeout=45.0)}
        )
        config = RuntimeConfig(file_config=file_config)
        timeout = config.get_server_timeout("test", TimeoutType.TOOL_EXECUTION)
        assert timeout == 45.0

    def test_server_specific_init_timeout(self) -> None:
        """Server-specific init timeout should be used when set."""
        file_config = MCPConfig(
            servers={"test": ServerDefinition(command="echo", init_timeout=15.0)}
        )
        config = RuntimeConfig(file_config=file_config)
        timeout = config.get_server_timeout("test", TimeoutType.SERVER_INIT)
        assert timeout == 15.0

    def test_nonexistent_server_returns_global(self) -> None:
        """Nonexistent server should return global timeout."""
        config = RuntimeConfig()
        timeout = config.get_server_timeout("nonexistent", TimeoutType.TOOL_EXECUTION)
        assert timeout == DEFAULT_TOOL_EXECUTION_TIMEOUT


class TestRuntimeConfigApiSettings:
    """Tests for API settings resolution."""

    def test_api_base_default_none(self) -> None:
        """API base should be None by default."""
        config = RuntimeConfig()
        assert config.api_base is None

    def test_api_base_from_cli(self) -> None:
        """API base should come from CLI override."""
        cli_overrides = ConfigOverride(api_base="https://api.example.com")
        config = RuntimeConfig(cli_overrides=cli_overrides)
        assert config.api_base == "https://api.example.com"
        assert config.get_api_base().source == ConfigSource.CLI

    def test_api_key_default_none(self) -> None:
        """API key should be None by default."""
        config = RuntimeConfig()
        assert config.api_key is None

    def test_api_key_from_cli(self) -> None:
        """API key should come from CLI override."""
        cli_overrides = ConfigOverride(api_key="sk-test")
        config = RuntimeConfig(cli_overrides=cli_overrides)
        assert config.api_key == "sk-test"
        assert config.get_api_key().source == ConfigSource.CLI


class TestRuntimeConfigServers:
    """Tests for server access."""

    def test_get_server(self) -> None:
        """RuntimeConfig should provide access to servers."""
        file_config = MCPConfig(
            servers={"sqlite": ServerDefinition(command="sqlite-server")}
        )
        config = RuntimeConfig(file_config=file_config)
        server = config.get_server("sqlite")
        assert server is not None
        assert server.command == "sqlite-server"

    def test_get_nonexistent_server(self) -> None:
        """get_server should return None for nonexistent server."""
        config = RuntimeConfig()
        assert config.get_server("nonexistent") is None

    def test_get_enabled_servers(self) -> None:
        """RuntimeConfig should filter enabled servers."""
        file_config = MCPConfig(
            servers={
                "enabled": ServerDefinition(command="cmd1", enabled=True),
                "disabled": ServerDefinition(command="cmd2", enabled=False),
            }
        )
        config = RuntimeConfig(file_config=file_config)
        enabled = config.get_enabled_servers()
        assert "enabled" in enabled
        assert "disabled" not in enabled

    def test_servers_property(self) -> None:
        """RuntimeConfig.servers should return all servers."""
        file_config = MCPConfig(
            servers={
                "a": ServerDefinition(command="cmd1"),
                "b": ServerDefinition(command="cmd2"),
            }
        )
        config = RuntimeConfig(file_config=file_config)
        assert len(config.servers) == 2
