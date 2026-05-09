"""Tests for configuration enums."""

from __future__ import annotations

import pytest

from mcpcli.config.enums import (
    TimeoutType,
    TokenBackend,
    ConfigSource,
    ServerStatus,
    ConversationAction,
    TokenAction,
    OutputFormat,
    TokenNamespace,
    SessionAction,
    ServerAction,
    ToolAction,
    ThemeAction,
    TransportType,
)


class TestTimeoutType:
    """Tests for TimeoutType enum."""

    def test_streaming_chunk_value(self) -> None:
        """Streaming chunk timeout type should have correct value."""
        assert TimeoutType.STREAMING_CHUNK.value == "streaming_chunk"

    def test_tool_execution_value(self) -> None:
        """Tool execution timeout type should have correct value."""
        assert TimeoutType.TOOL_EXECUTION.value == "tool_execution"

    def test_server_init_value(self) -> None:
        """Server init timeout type should have correct value."""
        assert TimeoutType.SERVER_INIT.value == "server_init"

    def test_http_timeouts_exist(self) -> None:
        """HTTP timeout types should exist."""
        assert TimeoutType.HTTP_REQUEST.value == "http_request"
        assert TimeoutType.HTTP_CONNECT.value == "http_connect"

    def test_is_string_enum(self) -> None:
        """TimeoutType should be usable as string."""
        assert isinstance(TimeoutType.STREAMING_CHUNK.value, str)
        assert f"{TimeoutType.STREAMING_CHUNK.value}" == "streaming_chunk"


class TestTokenBackend:
    """Tests for TokenBackend enum."""

    def test_auto_value(self) -> None:
        """AUTO backend should have correct value."""
        assert TokenBackend.AUTO.value == "auto"

    def test_keychain_value(self) -> None:
        """KEYCHAIN backend should have correct value."""
        assert TokenBackend.KEYCHAIN.value == "keychain"

    def test_windows_value(self) -> None:
        """WINDOWS backend should have correct value."""
        assert TokenBackend.WINDOWS.value == "windows"

    def test_encrypted_value(self) -> None:
        """ENCRYPTED backend should have correct value."""
        assert TokenBackend.ENCRYPTED.value == "encrypted"

    def test_vault_value(self) -> None:
        """VAULT backend should have correct value."""
        assert TokenBackend.VAULT.value == "vault"

    def test_all_backends_are_strings(self) -> None:
        """All token backends should be usable as strings."""
        for backend in TokenBackend:
            assert isinstance(backend.value, str)


class TestConfigSource:
    """Tests for ConfigSource enum."""

    def test_cli_value(self) -> None:
        """CLI source should have correct value."""
        assert ConfigSource.CLI.value == "cli"

    def test_env_value(self) -> None:
        """ENV source should have correct value."""
        assert ConfigSource.ENV.value == "env"

    def test_file_value(self) -> None:
        """FILE source should have correct value."""
        assert ConfigSource.FILE.value == "file"

    def test_default_value(self) -> None:
        """DEFAULT source should have correct value."""
        assert ConfigSource.DEFAULT.value == "default"

    def test_priority_order_conceptual(self) -> None:
        """ConfigSource values should represent priority order conceptually."""
        sources = [ConfigSource.CLI, ConfigSource.ENV, ConfigSource.FILE, ConfigSource.DEFAULT]
        assert len(sources) == 4


class TestServerStatus:
    """Tests for ServerStatus enum."""

    def test_configured_value(self) -> None:
        """CONFIGURED status should have correct value."""
        assert ServerStatus.CONFIGURED.value == "configured"

    def test_connected_value(self) -> None:
        """CONNECTED status should have correct value."""
        assert ServerStatus.CONNECTED.value == "connected"

    def test_disconnected_value(self) -> None:
        """DISCONNECTED status should have correct value."""
        assert ServerStatus.DISCONNECTED.value == "disconnected"

    def test_error_value(self) -> None:
        """ERROR status should have correct value."""
        assert ServerStatus.ERROR.value == "error"

    def test_healthy_value(self) -> None:
        """HEALTHY status should have correct value."""
        assert ServerStatus.HEALTHY.value == "healthy"


class TestConversationAction:
    """Tests for ConversationAction enum."""

    def test_show_value(self) -> None:
        """SHOW action should have correct value."""
        assert ConversationAction.SHOW.value == "show"

    def test_clear_value(self) -> None:
        """CLEAR action should have correct value."""
        assert ConversationAction.CLEAR.value == "clear"

    def test_save_value(self) -> None:
        """SAVE action should have correct value."""
        assert ConversationAction.SAVE.value == "save"

    def test_load_value(self) -> None:
        """LOAD action should have correct value."""
        assert ConversationAction.LOAD.value == "load"


class TestTokenAction:
    """Tests for TokenAction enum."""

    def test_list_value(self) -> None:
        """LIST action should have correct value."""
        assert TokenAction.LIST.value == "list"

    def test_set_value(self) -> None:
        """SET action should have correct value."""
        assert TokenAction.SET.value == "set"

    def test_get_value(self) -> None:
        """GET action should have correct value."""
        assert TokenAction.GET.value == "get"

    def test_delete_value(self) -> None:
        """DELETE action should have correct value."""
        assert TokenAction.DELETE.value == "delete"

    def test_clear_value(self) -> None:
        """CLEAR action should have correct value."""
        assert TokenAction.CLEAR.value == "clear"

    def test_backends_value(self) -> None:
        """BACKENDS action should have correct value."""
        assert TokenAction.BACKENDS.value == "backends"


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_json_value(self) -> None:
        """JSON format should have correct value."""
        assert OutputFormat.JSON.value == "json"

    def test_table_value(self) -> None:
        """TABLE format should have correct value."""
        assert OutputFormat.TABLE.value == "table"

    def test_text_value(self) -> None:
        """TEXT format should have correct value."""
        assert OutputFormat.TEXT.value == "text"

    def test_tree_value(self) -> None:
        """TREE format should have correct value."""
        assert OutputFormat.TREE.value == "tree"


class TestTokenNamespace:
    """Tests for TokenNamespace enum."""

    def test_generic_value(self) -> None:
        """GENERIC namespace should have correct value."""
        assert TokenNamespace.GENERIC.value == "generic"

    def test_provider_value(self) -> None:
        """PROVIDER namespace should have correct value."""
        assert TokenNamespace.PROVIDER.value == "provider"

    def test_bearer_value(self) -> None:
        """BEARER namespace should have correct value."""
        assert TokenNamespace.BEARER.value == "bearer"

    def test_oauth_value(self) -> None:
        """OAUTH namespace should have correct value."""
        assert TokenNamespace.OAUTH.value == "oauth"


class TestServerAction:
    """Tests for ServerAction enum."""

    def test_enable_value(self) -> None:
        """ENABLE action should have correct value."""
        assert ServerAction.ENABLE.value == "enable"

    def test_disable_value(self) -> None:
        """DISABLE action should have correct value."""
        assert ServerAction.DISABLE.value == "disable"

    def test_status_value(self) -> None:
        """STATUS action should have correct value."""
        assert ServerAction.STATUS.value == "status"

    def test_list_value(self) -> None:
        """LIST action should have correct value."""
        assert ServerAction.LIST.value == "list"


class TestToolAction:
    """Tests for ToolAction enum."""

    def test_list_value(self) -> None:
        """LIST action should have correct value."""
        assert ToolAction.LIST.value == "list"

    def test_enable_value(self) -> None:
        """ENABLE action should have correct value."""
        assert ToolAction.ENABLE.value == "enable"

    def test_call_value(self) -> None:
        """CALL action should have correct value."""
        assert ToolAction.CALL.value == "call"


class TestThemeAction:
    """Tests for ThemeAction enum."""

    def test_set_value(self) -> None:
        """SET action should have correct value."""
        assert ThemeAction.SET.value == "set"

    def test_list_value(self) -> None:
        """LIST action should have correct value."""
        assert ThemeAction.LIST.value == "list"

    def test_show_value(self) -> None:
        """SHOW action should have correct value."""
        assert ThemeAction.SHOW.value == "show"


class TestTransportType:
    """Tests for TransportType enum."""

    def test_stdio_value(self) -> None:
        """STDIO transport should have correct value."""
        assert TransportType.STDIO.value == "stdio"

    def test_http_value(self) -> None:
        """HTTP transport should have correct value."""
        assert TransportType.HTTP.value == "http"

    def test_sse_value(self) -> None:
        """SSE transport should have correct value."""
        assert TransportType.SSE.value == "sse"

    def test_unknown_value(self) -> None:
        """UNKNOWN transport should have correct value."""
        assert TransportType.UNKNOWN.value == "unknown"


class TestEnumStringBehavior:
    """Tests for enum string behavior."""

    def test_all_enums_are_string_enums(self) -> None:
        """All enums should be usable as strings."""
        enums_to_test = [
            TimeoutType,
            TokenBackend,
            ConfigSource,
            ServerStatus,
            ConversationAction,
            TokenAction,
            OutputFormat,
            TokenNamespace,
            ServerAction,
            ToolAction,
            ThemeAction,
            TransportType,
        ]
        for enum_class in enums_to_test:
            for member in enum_class:
                assert isinstance(member.value, str), f"{enum_class.__name__}.{member.name} is not a string"
