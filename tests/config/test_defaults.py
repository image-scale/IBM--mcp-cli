"""Tests for configuration defaults."""

from __future__ import annotations

import pytest

from mcpcli.config.defaults import (
    DEFAULT_TOOL_EXECUTION_TIMEOUT,
    DEFAULT_SERVER_INIT_TIMEOUT,
    DEFAULT_STREAMING_CHUNK_TIMEOUT,
    DEFAULT_STREAMING_GLOBAL_TIMEOUT,
    DEFAULT_STREAMING_FIRST_CHUNK_TIMEOUT,
    DEFAULT_HTTP_REQUEST_TIMEOUT,
    DEFAULT_HTTP_CONNECT_TIMEOUT,
    DEFAULT_MAX_TOOL_CONCURRENCY,
    DEFAULT_CONFIRM_TOOLS,
    DEFAULT_DYNAMIC_TOOLS_ENABLED,
    DEFAULT_MAX_TURNS,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    DEFAULT_THEME,
    DEFAULT_VERBOSE,
    DEFAULT_TOKEN_BACKEND,
    DEFAULT_CONFIG_FILENAME,
    APP_NAME,
    NAMESPACE,
    SUPPORTED_PROVIDERS,
    JSON_TYPES,
    PLATFORM_WINDOWS,
    PLATFORM_DARWIN,
    PLATFORM_LINUX,
)


class TestTimeoutDefaults:
    """Tests for timeout default values."""

    def test_tool_execution_timeout(self) -> None:
        """Tool execution timeout should be 120 seconds."""
        assert DEFAULT_TOOL_EXECUTION_TIMEOUT == 120.0

    def test_server_init_timeout(self) -> None:
        """Server initialization timeout should be 120 seconds."""
        assert DEFAULT_SERVER_INIT_TIMEOUT == 120.0

    def test_streaming_chunk_timeout(self) -> None:
        """Streaming chunk timeout should be 45 seconds."""
        assert DEFAULT_STREAMING_CHUNK_TIMEOUT == 45.0

    def test_streaming_global_timeout(self) -> None:
        """Streaming global timeout should be 300 seconds."""
        assert DEFAULT_STREAMING_GLOBAL_TIMEOUT == 300.0

    def test_streaming_first_chunk_timeout(self) -> None:
        """First chunk timeout should be 60 seconds."""
        assert DEFAULT_STREAMING_FIRST_CHUNK_TIMEOUT == 60.0

    def test_http_request_timeout(self) -> None:
        """HTTP request timeout should be 30 seconds."""
        assert DEFAULT_HTTP_REQUEST_TIMEOUT == 30.0

    def test_http_connect_timeout(self) -> None:
        """HTTP connect timeout should be 10 seconds."""
        assert DEFAULT_HTTP_CONNECT_TIMEOUT == 10.0

    def test_all_timeouts_are_positive(self) -> None:
        """All timeout values should be positive."""
        timeouts = [
            DEFAULT_TOOL_EXECUTION_TIMEOUT,
            DEFAULT_SERVER_INIT_TIMEOUT,
            DEFAULT_STREAMING_CHUNK_TIMEOUT,
            DEFAULT_STREAMING_GLOBAL_TIMEOUT,
            DEFAULT_STREAMING_FIRST_CHUNK_TIMEOUT,
            DEFAULT_HTTP_REQUEST_TIMEOUT,
            DEFAULT_HTTP_CONNECT_TIMEOUT,
        ]
        for timeout in timeouts:
            assert timeout > 0


class TestToolDefaults:
    """Tests for tool configuration defaults."""

    def test_max_tool_concurrency(self) -> None:
        """Max tool concurrency should be 5."""
        assert DEFAULT_MAX_TOOL_CONCURRENCY == 5

    def test_confirm_tools_default(self) -> None:
        """Tool confirmation should be enabled by default."""
        assert DEFAULT_CONFIRM_TOOLS is True

    def test_dynamic_tools_disabled(self) -> None:
        """Dynamic tools should be disabled by default."""
        assert DEFAULT_DYNAMIC_TOOLS_ENABLED is False


class TestConversationDefaults:
    """Tests for conversation defaults."""

    def test_max_turns(self) -> None:
        """Max turns should be 100."""
        assert DEFAULT_MAX_TURNS == 100

    def test_system_prompt_not_empty(self) -> None:
        """System prompt should not be empty."""
        assert len(DEFAULT_SYSTEM_PROMPT) > 0
        assert "assistant" in DEFAULT_SYSTEM_PROMPT.lower()


class TestProviderDefaults:
    """Tests for provider configuration defaults."""

    def test_default_provider(self) -> None:
        """Default provider should be openai."""
        assert DEFAULT_PROVIDER == "openai"

    def test_default_model(self) -> None:
        """Default model should be gpt-4o-mini."""
        assert DEFAULT_MODEL == "gpt-4o-mini"

    def test_supported_providers_includes_major_providers(self) -> None:
        """Supported providers should include major LLM providers."""
        assert "openai" in SUPPORTED_PROVIDERS
        assert "anthropic" in SUPPORTED_PROVIDERS
        assert "ollama" in SUPPORTED_PROVIDERS


class TestUIDefaults:
    """Tests for UI defaults."""

    def test_default_theme(self) -> None:
        """Default theme should be 'default'."""
        assert DEFAULT_THEME == "default"

    def test_verbose_mode_enabled(self) -> None:
        """Verbose mode should be enabled by default."""
        assert DEFAULT_VERBOSE is True


class TestTokenDefaults:
    """Tests for token and auth defaults."""

    def test_token_backend(self) -> None:
        """Default token backend should be 'auto'."""
        assert DEFAULT_TOKEN_BACKEND == "auto"


class TestPathDefaults:
    """Tests for path defaults."""

    def test_config_filename(self) -> None:
        """Default config filename should be server_config.json."""
        assert DEFAULT_CONFIG_FILENAME == "server_config.json"


class TestApplicationConstants:
    """Tests for application constants."""

    def test_app_name(self) -> None:
        """App name should be set."""
        assert APP_NAME == "mcpcli"

    def test_namespace(self) -> None:
        """Namespace should match app name."""
        assert NAMESPACE == "mcpcli"


class TestPlatformConstants:
    """Tests for platform constants."""

    def test_platform_windows(self) -> None:
        """Windows platform identifier should be win32."""
        assert PLATFORM_WINDOWS == "win32"

    def test_platform_darwin(self) -> None:
        """macOS platform identifier should be darwin."""
        assert PLATFORM_DARWIN == "darwin"

    def test_platform_linux(self) -> None:
        """Linux platform identifier should be linux."""
        assert PLATFORM_LINUX == "linux"


class TestJSONTypes:
    """Tests for JSON type constants."""

    def test_json_types_complete(self) -> None:
        """JSON types should include all standard types."""
        assert "string" in JSON_TYPES
        assert "number" in JSON_TYPES
        assert "integer" in JSON_TYPES
        assert "boolean" in JSON_TYPES
        assert "array" in JSON_TYPES
        assert "object" in JSON_TYPES
        assert "null" in JSON_TYPES
        assert len(JSON_TYPES) == 7
