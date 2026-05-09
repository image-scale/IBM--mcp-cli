"""Tests for context manager."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from mcpcli.context.context_manager import (
    ApplicationContext,
    ContextManager,
    get_context,
    initialize_context,
)
from mcpcli.tools.models import ConversationMessage, ServerInfo, ToolInfo


def make_server(name: str = "test-server", **overrides: Any) -> ServerInfo:
    """Create a minimal ServerInfo for testing."""
    defaults = {
        "id": 0,
        "name": name,
        "status": "connected",
        "tool_count": 0,
        "namespace": "stdio",
    }
    defaults.update(overrides)
    return ServerInfo(**defaults)


def make_tool(name: str = "tool1", namespace: str = "ns", **overrides: Any) -> ToolInfo:
    """Create a minimal ToolInfo for testing."""
    defaults = {
        "name": name,
        "namespace": namespace,
        "description": "A test tool",
    }
    defaults.update(overrides)
    return ToolInfo(**defaults)


def make_mock_tool_manager(
    servers: list[ServerInfo] | None = None,
    tools: list[ToolInfo] | None = None,
) -> Any:
    """Return a mock tool manager with async methods."""
    manager = type("MockToolManager", (), {})()
    manager.get_server_info = AsyncMock(return_value=servers or [])
    manager.get_all_tools = AsyncMock(return_value=tools or [])
    return manager


@pytest.fixture(autouse=True)
def reset_context_manager() -> None:
    """Reset the ContextManager singleton before each test."""
    ContextManager._instance = None
    ContextManager._context = None


class TestApplicationContextConstruction:
    """Tests for ApplicationContext creation."""

    def test_default_construction(self) -> None:
        """Default construction uses default values."""
        ctx = ApplicationContext()
        assert ctx.provider == "openai"
        assert ctx.model == "gpt-4o-mini"
        assert ctx.conversation_history == []
        assert ctx.servers == []
        assert ctx.tools == []

    def test_create_factory(self) -> None:
        """Factory method creates context with specified values."""
        ctx = ApplicationContext.create(provider="anthropic", model="claude-3")
        assert ctx.provider == "anthropic"
        assert ctx.model == "claude-3"
        assert ctx.config_path == Path("server_config.json")

    def test_create_with_tool_manager(self) -> None:
        """Factory accepts tool manager."""
        tm = make_mock_tool_manager()
        ctx = ApplicationContext.create(tool_manager=tm)
        assert ctx.tool_manager is tm

    def test_create_with_config_path(self) -> None:
        """Factory accepts config path."""
        ctx = ApplicationContext.create(config_path=Path("/tmp/custom.json"))
        assert ctx.config_path == Path("/tmp/custom.json")

    def test_create_with_additional_kwargs(self) -> None:
        """Factory accepts additional keyword arguments."""
        ctx = ApplicationContext.create(verbose_mode=False, theme="dark")
        assert ctx.verbose_mode is False
        assert ctx.theme == "dark"


class TestApplicationContextInitialize:
    """Tests for async initialization."""

    @pytest.mark.asyncio
    async def test_initialize_loads_servers_and_tools(self) -> None:
        """Initialize loads servers and tools from tool manager."""
        server = make_server()
        tool = make_tool()
        tm = make_mock_tool_manager(servers=[server], tools=[tool])
        ctx = ApplicationContext.create(tool_manager=tm)

        await ctx.initialize()

        assert ctx.servers == [server]
        assert ctx.tools == [tool]
        assert ctx.current_server is server

    @pytest.mark.asyncio
    async def test_initialize_no_auto_current_when_multiple_servers(self) -> None:
        """Initialize doesn't auto-set current server with multiple servers."""
        s1 = make_server("s1")
        s2 = make_server("s2", id=1)
        tm = make_mock_tool_manager(servers=[s1, s2])
        ctx = ApplicationContext.create(tool_manager=tm)

        await ctx.initialize()

        assert ctx.current_server is None

    @pytest.mark.asyncio
    async def test_initialize_no_tool_manager(self) -> None:
        """Initialize with no tool manager is a no-op."""
        ctx = ApplicationContext.create()
        await ctx.initialize()
        assert ctx.servers == []
        assert ctx.tools == []


class TestCurrentServer:
    """Tests for current server management."""

    def test_get_current_server_none_by_default(self) -> None:
        """Current server is None by default."""
        ctx = ApplicationContext.create()
        assert ctx.get_current_server() is None

    def test_set_and_get_current_server(self) -> None:
        """Can set and get current server."""
        ctx = ApplicationContext.create()
        server = make_server("my-server")
        ctx.set_current_server(server)
        assert ctx.get_current_server() is server
        assert ctx.get_current_server().name == "my-server"


class TestFindServerAndTool:
    """Tests for server and tool lookup."""

    def test_find_server_by_name(self) -> None:
        """Find server by name (case-insensitive)."""
        s1 = make_server("Alpha")
        s2 = make_server("Beta", id=1)
        ctx = ApplicationContext.create()
        ctx.servers = [s1, s2]

        assert ctx.find_server("alpha") is s1
        assert ctx.find_server("BETA") is s2
        assert ctx.find_server("gamma") is None

    def test_find_tool_by_name(self) -> None:
        """Find tool by name."""
        t1 = make_tool("read_file", "fs")
        t2 = make_tool("write_file", "fs")
        ctx = ApplicationContext.create()
        ctx.tools = [t1, t2]

        assert ctx.find_tool("read_file") is t1
        assert ctx.find_tool("write_file") is t2
        assert ctx.find_tool("delete_file") is None

    def test_find_tool_by_fully_qualified_name(self) -> None:
        """Find tool by fully qualified name."""
        t1 = make_tool("read_file", "fs")
        ctx = ApplicationContext.create()
        ctx.tools = [t1]

        assert ctx.find_tool("fs.read_file") is t1

    def test_find_server_empty_list(self) -> None:
        """Find server returns None for empty list."""
        ctx = ApplicationContext.create()
        assert ctx.find_server("anything") is None

    def test_find_tool_empty_list(self) -> None:
        """Find tool returns None for empty list."""
        ctx = ApplicationContext.create()
        assert ctx.find_tool("anything") is None


class TestGetSet:
    """Tests for dict-like get/set access."""

    def test_get_known_attribute(self) -> None:
        """Get returns known attribute value."""
        ctx = ApplicationContext.create(provider="anthropic")
        assert ctx.get("provider") == "anthropic"

    def test_get_unknown_key_returns_default(self) -> None:
        """Get returns default for unknown key."""
        ctx = ApplicationContext.create()
        assert ctx.get("nonexistent") is None
        assert ctx.get("nonexistent", 42) == 42

    def test_set_known_attribute(self) -> None:
        """Set updates known attribute."""
        ctx = ApplicationContext.create()
        ctx.set("provider", "anthropic")
        assert ctx.provider == "anthropic"

    def test_set_unknown_key_stored_in_extra(self) -> None:
        """Set stores unknown key in extra dict."""
        ctx = ApplicationContext.create()
        ctx.set("custom_key", "custom_value")
        assert ctx.get("custom_key") == "custom_value"

    def test_get_from_extra(self) -> None:
        """Get retrieves values from extra dict."""
        ctx = ApplicationContext.create()
        ctx.set("my_extra", 123)
        assert ctx.get("my_extra") == 123


class TestToDict:
    """Tests for dictionary conversion."""

    def test_to_dict_basic(self) -> None:
        """to_dict returns dictionary with all fields."""
        ctx = ApplicationContext.create(provider="openai", model="gpt-4o-mini")
        d = ctx.to_dict()

        assert d["provider"] == "openai"
        assert d["model"] == "gpt-4o-mini"
        assert d["config_path"] == "server_config.json"
        assert d["servers"] == []
        assert d["tools"] == []
        assert d["conversation_history"] == []
        assert d["is_interactive"] is False

    def test_to_dict_includes_extra(self) -> None:
        """to_dict includes extra data."""
        ctx = ApplicationContext.create()
        ctx.set("bonus", "data")
        d = ctx.to_dict()
        assert d["bonus"] == "data"


class TestUpdateFromDict:
    """Tests for update_from_dict method."""

    def test_update_from_dict_known_keys(self) -> None:
        """update_from_dict updates known attributes."""
        ctx = ApplicationContext.create()
        ctx.update_from_dict({"provider": "anthropic", "model": "claude-3"})
        assert ctx.provider == "anthropic"
        assert ctx.model == "claude-3"

    def test_update_from_dict_unknown_keys(self) -> None:
        """update_from_dict stores unknown keys in extra."""
        ctx = ApplicationContext.create()
        ctx.update_from_dict({"custom_field": 99})
        assert ctx.get("custom_field") == 99

    def test_update_from_dict_mixed(self) -> None:
        """update_from_dict handles mixed known and unknown keys."""
        ctx = ApplicationContext.create()
        ctx.update_from_dict({"provider": "groq", "some_extra": "value"})
        assert ctx.provider == "groq"
        assert ctx.get("some_extra") == "value"


class TestUpdate:
    """Tests for update method."""

    def test_update_known_attributes(self) -> None:
        """update sets known attributes."""
        ctx = ApplicationContext.create()
        ctx.update(provider="deepseek", verbose_mode=False)
        assert ctx.provider == "deepseek"
        assert ctx.verbose_mode is False

    def test_update_unknown_attributes(self) -> None:
        """update stores unknown attributes in extra."""
        ctx = ApplicationContext.create()
        ctx.update(new_key="new_val")
        assert ctx.get("new_key") == "new_val"

    def test_update_mixed(self) -> None:
        """update handles mixed known and unknown attributes."""
        ctx = ApplicationContext.create()
        ctx.update(model="big-model", custom_flag=True)
        assert ctx.model == "big-model"
        assert ctx.get("custom_flag") is True


class TestConversationMessages:
    """Tests for conversation message management."""

    def test_add_message_dict(self) -> None:
        """add_message adds dict message."""
        ctx = ApplicationContext.create()
        ctx.add_message({"role": "user", "content": "hello"})
        assert len(ctx.conversation_history) == 1
        assert ctx.conversation_history[0]["role"] == "user"

    def test_add_message_conversation_message(self) -> None:
        """add_message converts ConversationMessage to dict."""
        ctx = ApplicationContext.create()
        msg = ConversationMessage.user_message("hi")
        ctx.add_message(msg)
        assert len(ctx.conversation_history) == 1
        assert ctx.conversation_history[0]["role"] == "user"
        assert ctx.conversation_history[0]["content"] == "hi"

    def test_add_user_message(self) -> None:
        """add_user_message adds user role message."""
        ctx = ApplicationContext.create()
        ctx.add_user_message("What is 2+2?")
        assert len(ctx.conversation_history) == 1
        assert ctx.conversation_history[0]["role"] == "user"
        assert ctx.conversation_history[0]["content"] == "What is 2+2?"

    def test_add_assistant_message_text_only(self) -> None:
        """add_assistant_message adds text content."""
        ctx = ApplicationContext.create()
        ctx.add_assistant_message(content="It is 4.")
        assert ctx.conversation_history[0]["role"] == "assistant"
        assert ctx.conversation_history[0]["content"] == "It is 4."

    def test_add_assistant_message_with_tool_calls(self) -> None:
        """add_assistant_message includes tool calls."""
        ctx = ApplicationContext.create()
        tool_calls = [
            {
                "id": "tc1",
                "type": "function",
                "function": {"name": "f", "arguments": "{}"},
            }
        ]
        ctx.add_assistant_message(content=None, tool_calls=tool_calls)
        msg = ctx.conversation_history[0]
        assert msg["role"] == "assistant"
        assert "tool_calls" in msg

    def test_add_system_message(self) -> None:
        """add_system_message adds system role message."""
        ctx = ApplicationContext.create()
        ctx.add_system_message("You are helpful.")
        assert ctx.conversation_history[0]["role"] == "system"
        assert ctx.conversation_history[0]["content"] == "You are helpful."

    def test_add_tool_message(self) -> None:
        """add_tool_message adds tool response message."""
        ctx = ApplicationContext.create()
        ctx.add_tool_message(content="result", tool_call_id="tc1", name="my_tool")
        msg = ctx.conversation_history[0]
        assert msg["role"] == "tool"
        assert msg["content"] == "result"
        assert msg["tool_call_id"] == "tc1"
        assert msg["name"] == "my_tool"

    def test_add_tool_message_without_name(self) -> None:
        """add_tool_message excludes name when None."""
        ctx = ApplicationContext.create()
        ctx.add_tool_message(content="result", tool_call_id="tc2")
        msg = ctx.conversation_history[0]
        assert msg["role"] == "tool"
        assert "name" not in msg

    def test_get_messages_returns_typed(self) -> None:
        """get_messages returns ConversationMessage objects."""
        ctx = ApplicationContext.create()
        ctx.add_user_message("Hello")
        ctx.add_assistant_message("Hi")
        msgs = ctx.get_messages()
        assert len(msgs) == 2
        assert all(isinstance(m, ConversationMessage) for m in msgs)
        assert msgs[0].role == "user"
        assert msgs[1].role == "assistant"

    def test_clear_conversation(self) -> None:
        """clear_conversation empties history."""
        ctx = ApplicationContext.create()
        ctx.add_user_message("a")
        ctx.add_user_message("b")
        assert len(ctx.conversation_history) == 2
        ctx.clear_conversation()
        assert ctx.conversation_history == []

    def test_multiple_messages_in_sequence(self) -> None:
        """Multiple messages preserve order and roles."""
        ctx = ApplicationContext.create()
        ctx.add_system_message("sys")
        ctx.add_user_message("usr")
        ctx.add_assistant_message("asst")
        ctx.add_tool_message("res", "tc1")
        assert len(ctx.conversation_history) == 4
        roles = [m["role"] for m in ctx.conversation_history]
        assert roles == ["system", "user", "assistant", "tool"]


class TestContextManager:
    """Tests for ContextManager singleton."""

    def test_singleton(self) -> None:
        """ContextManager is a singleton."""
        cm1 = ContextManager()
        cm2 = ContextManager()
        assert cm1 is cm2

    def test_get_context_before_initialize_raises(self) -> None:
        """get_context raises before initialization."""
        with pytest.raises(RuntimeError, match="Context not initialized"):
            ContextManager().get_context()

    def test_initialize_and_get_context(self) -> None:
        """Can initialize and get context."""
        cm = ContextManager()
        ctx = cm.initialize(provider="openai", model="gpt-4o-mini")
        assert isinstance(ctx, ApplicationContext)
        assert cm.get_context() is ctx

    def test_initialize_idempotent(self) -> None:
        """Second initialize returns same context."""
        cm = ContextManager()
        ctx1 = cm.initialize(provider="openai")
        ctx2 = cm.initialize(provider="anthropic")
        assert ctx1 is ctx2

    def test_reset_clears_context(self) -> None:
        """reset clears the context."""
        cm = ContextManager()
        cm.initialize()
        cm.reset()
        with pytest.raises(RuntimeError):
            cm.get_context()

    def test_initialize_with_tool_manager(self) -> None:
        """Can initialize with tool manager."""
        tm = make_mock_tool_manager()
        cm = ContextManager()
        ctx = cm.initialize(tool_manager=tm)
        assert ctx.tool_manager is tm


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_context_raises_when_uninitialized(self) -> None:
        """get_context raises when not initialized."""
        with pytest.raises(RuntimeError):
            get_context()

    def test_initialize_context_and_get_context(self) -> None:
        """initialize_context and get_context work together."""
        ctx = initialize_context(provider="openai")
        assert isinstance(ctx, ApplicationContext)
        retrieved = get_context()
        assert retrieved is ctx

    def test_initialize_context_with_kwargs(self) -> None:
        """initialize_context passes kwargs through."""
        ctx = initialize_context(
            provider="anthropic",
            model="claude-3",
            verbose_mode=False,
        )
        assert ctx.provider == "anthropic"
        assert ctx.model == "claude-3"
        assert ctx.verbose_mode is False
