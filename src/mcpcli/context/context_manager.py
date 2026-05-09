"""Centralized context manager for MCP CLI.

Provides a centralized way to manage application context for servers,
tools, conversation state, and configuration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from mcpcli.config.defaults import DEFAULT_MODEL, DEFAULT_PROVIDER, DEFAULT_THEME
from mcpcli.tools.models import ConversationMessage, ServerInfo, ToolInfo


@runtime_checkable
class ToolManagerProtocol(Protocol):
    """Protocol for tool manager interface."""

    async def get_server_info(self) -> list[ServerInfo]:
        """Get information about connected servers."""
        ...

    async def get_all_tools(self) -> list[ToolInfo]:
        """Get all available tools."""
        ...


class ApplicationContext(BaseModel):
    """Centralized application context holding all state and managers.

    Replaces dictionary-based context passing with a typed model.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    tool_manager: Any = Field(default=None, description="Tool manager instance")

    config_path: Path = Field(
        default_factory=lambda: Path("server_config.json"),
        description="Path to server configuration file",
    )
    provider: str = Field(default=DEFAULT_PROVIDER, description="LLM provider name")
    model: str = Field(default=DEFAULT_MODEL, description="LLM model name")
    api_base: str | None = Field(default=None, description="API base URL")
    api_key: str | None = Field(default=None, description="API key")

    servers: list[ServerInfo] = Field(
        default_factory=list, description="Connected servers"
    )
    tools: list[ToolInfo] = Field(default_factory=list, description="Available tools")
    current_server: ServerInfo | None = Field(
        default=None, description="Currently active server"
    )

    verbose_mode: bool = Field(default=True, description="Verbose output mode")
    confirm_tools: bool = Field(
        default=True, description="Require confirmation for tool calls"
    )
    theme: str = Field(default=DEFAULT_THEME, description="UI theme name")

    session_id: str | None = Field(default=None, description="Current session ID")
    is_interactive: bool = Field(default=False, description="Interactive mode flag")
    exit_requested: bool = Field(default=False, description="Exit was requested")

    conversation_history: list[dict[str, Any]] = Field(
        default_factory=list, description="Conversation message history"
    )

    _extra: dict[str, Any] = PrivateAttr(default_factory=dict)

    @classmethod
    def create(
        cls,
        tool_manager: Any | None = None,
        config_path: Path | None = None,
        provider: str | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> ApplicationContext:
        """Factory method to create a context with defaults.

        Args:
            tool_manager: Optional tool manager instance.
            config_path: Path to configuration file.
            provider: LLM provider name.
            model: LLM model name.
            **kwargs: Additional context attributes.

        Returns:
            New ApplicationContext instance.
        """
        return cls(
            tool_manager=tool_manager,
            config_path=config_path or Path("server_config.json"),
            provider=provider or DEFAULT_PROVIDER,
            model=model or DEFAULT_MODEL,
            **kwargs,
        )

    async def initialize(self) -> None:
        """Initialize the context by loading servers and tools.

        If a tool manager is configured, loads servers and tools from it.
        When exactly one server is available, it becomes the current server.
        """
        if self.tool_manager is not None:
            if isinstance(self.tool_manager, ToolManagerProtocol):
                self.servers = await self.tool_manager.get_server_info()
                self.tools = await self.tool_manager.get_all_tools()

                if len(self.servers) == 1:
                    self.current_server = self.servers[0]

    def get_current_server(self) -> ServerInfo | None:
        """Get the currently active server."""
        return self.current_server

    def set_current_server(self, server: ServerInfo) -> None:
        """Set the currently active server."""
        self.current_server = server

    def find_server(self, name: str) -> ServerInfo | None:
        """Find a server by name (case-insensitive).

        Args:
            name: Server name to search for.

        Returns:
            ServerInfo if found, None otherwise.
        """
        for server in self.servers:
            if server.name.lower() == name.lower():
                return server
        return None

    def find_tool(self, name: str) -> ToolInfo | None:
        """Find a tool by name or fully qualified name.

        Args:
            name: Tool name or fully_qualified_name to search for.

        Returns:
            ToolInfo if found, None otherwise.
        """
        for tool in self.tools:
            if tool.name == name or tool.fully_qualified_name == name:
                return tool
        return None

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context (dict-like access).

        Checks direct attributes first, then extra data.

        Args:
            key: Attribute name to get.
            default: Default value if not found.

        Returns:
            Attribute value or default.
        """
        if hasattr(self, key) and not key.startswith("_"):
            return getattr(self, key)
        return self._extra.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in context (dict-like access).

        Sets direct attributes if they exist, otherwise stores in extra.

        Args:
            key: Attribute name to set.
            value: Value to set.
        """
        if hasattr(self, key) and not key.startswith("_"):
            setattr(self, key, value)
        else:
            self._extra[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary.

        Returns:
            Dictionary representation of the context.
        """
        result = {
            "tool_manager": self.tool_manager,
            "config_path": str(self.config_path),
            "provider": self.provider,
            "model": self.model,
            "api_base": self.api_base,
            "api_key": self.api_key,
            "servers": self.servers,
            "tools": self.tools,
            "current_server": self.current_server,
            "verbose_mode": self.verbose_mode,
            "confirm_tools": self.confirm_tools,
            "theme": self.theme,
            "session_id": self.session_id,
            "is_interactive": self.is_interactive,
            "exit_requested": self.exit_requested,
            "conversation_history": self.conversation_history,
        }
        result.update(self._extra)
        return result

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """Update context from a dictionary.

        Args:
            data: Dictionary with values to update.
        """
        for key, value in data.items():
            self.set(key, value)

    def update(self, **kwargs: Any) -> None:
        """Update context with keyword arguments.

        Args:
            **kwargs: Attribute values to update.
        """
        for key, value in kwargs.items():
            self.set(key, value)

    def add_message(self, message: ConversationMessage | dict[str, Any]) -> None:
        """Add a message to conversation history.

        Args:
            message: Message as ConversationMessage or dict.
        """
        if isinstance(message, ConversationMessage):
            self.conversation_history.append(message.to_dict())
        else:
            self.conversation_history.append(message)

    def add_user_message(self, content: str) -> None:
        """Add a user message to conversation history.

        Args:
            content: Message content.
        """
        self.add_message(ConversationMessage.user_message(content))

    def add_assistant_message(
        self,
        content: str | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> None:
        """Add an assistant message to conversation history.

        Args:
            content: Message content.
            tool_calls: Optional tool calls made by assistant.
        """
        self.add_message(ConversationMessage.assistant_message(content, tool_calls))

    def add_system_message(self, content: str) -> None:
        """Add a system message to conversation history.

        Args:
            content: Message content.
        """
        self.add_message(ConversationMessage.system_message(content))

    def add_tool_message(
        self,
        content: str,
        tool_call_id: str,
        name: str | None = None,
    ) -> None:
        """Add a tool response message to conversation history.

        Args:
            content: Tool response content.
            tool_call_id: ID of the tool call being responded to.
            name: Optional tool name.
        """
        self.add_message(ConversationMessage.tool_message(content, tool_call_id, name))

    def get_messages(self) -> list[ConversationMessage]:
        """Get conversation history as typed ConversationMessage objects.

        Returns:
            List of ConversationMessage objects.
        """
        return [
            ConversationMessage.from_dict(msg) for msg in self.conversation_history
        ]

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history.clear()


class ContextManager:
    """Singleton manager for application context.

    Provides a global access point for the application context.
    """

    _instance: ContextManager | None = None
    _context: ApplicationContext | None = None

    def __new__(cls) -> ContextManager:
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        tool_manager: Any | None = None,
        config_path: Path | None = None,
        **kwargs: Any,
    ) -> ApplicationContext:
        """Initialize or get the application context.

        Args:
            tool_manager: Optional tool manager instance.
            config_path: Path to configuration file.
            **kwargs: Additional context attributes.

        Returns:
            The initialized ApplicationContext.
        """
        if self._context is None:
            self._context = ApplicationContext.create(
                tool_manager=tool_manager,
                config_path=config_path,
                **kwargs,
            )
        return self._context

    def get_context(self) -> ApplicationContext:
        """Get the current application context.

        Returns:
            The current ApplicationContext.

        Raises:
            RuntimeError: If context hasn't been initialized.
        """
        if self._context is None:
            raise RuntimeError("Context not initialized. Call initialize() first.")
        return self._context

    def reset(self) -> None:
        """Reset the context (useful for testing)."""
        self._context = None


def get_context() -> ApplicationContext:
    """Convenience function to get the current application context.

    Returns:
        The current ApplicationContext.

    Raises:
        RuntimeError: If context hasn't been initialized.
    """
    return ContextManager().get_context()


def initialize_context(**kwargs: Any) -> ApplicationContext:
    """Convenience function to initialize the application context.

    Args:
        **kwargs: Arguments to pass to ApplicationContext.create().

    Returns:
        The initialized ApplicationContext.
    """
    return ContextManager().initialize(**kwargs)


__all__ = [
    "ApplicationContext",
    "ContextManager",
    "ToolManagerProtocol",
    "get_context",
    "initialize_context",
]
