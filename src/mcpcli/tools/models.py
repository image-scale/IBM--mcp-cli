"""Data models for tools, servers, and conversation messages.

Provides Pydantic models for representing MCP tools, server state,
tool execution results, and conversation messages.
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from mcpcli.config.enums import TransportType


class ToolType(str, Enum):
    """Tool definition types for LLM APIs."""

    FUNCTION = "function"


class FunctionDefinition(BaseModel):
    """Function definition for LLM tool calling.

    Follows the OpenAI function calling format.
    """

    name: str = Field(description="Function name")
    description: str = Field(description="Function description")
    parameters: dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}},
        description="JSON Schema for function parameters",
    )

    model_config = {"frozen": False}


class LLMToolDefinition(BaseModel):
    """LLM-compatible tool definition.

    Follows OpenAI function calling format, compatible with other providers.
    """

    type: ToolType = Field(
        default=ToolType.FUNCTION,
        description="Tool type (always 'function')",
    )
    function: FunctionDefinition = Field(description="Function definition")

    model_config = {"frozen": False}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format for LLM API calls."""
        return self.model_dump(mode="json")


class ToolInfo(BaseModel):
    """Information about a tool.

    Represents a tool discovered from an MCP server.
    """

    name: str = Field(description="Tool name")
    namespace: str = Field(default="default", description="Tool namespace")
    description: str | None = Field(default=None, description="Tool description")
    parameters: dict[str, Any] | None = Field(
        default=None, description="JSON Schema for tool parameters"
    )
    is_async: bool = Field(default=False, description="Whether tool is async")
    tags: list[str] = Field(default_factory=list, description="Tool tags")
    supports_streaming: bool = Field(
        default=False, description="Whether tool supports streaming"
    )

    model_config = {"frozen": False}

    @property
    def fully_qualified_name(self) -> str:
        """Get the fully qualified tool name (namespace.name)."""
        return f"{self.namespace}.{self.name}" if self.namespace else self.name

    @property
    def display_name(self) -> str:
        """Get a user-friendly display name."""
        return self.name

    @property
    def has_parameters(self) -> bool:
        """Check if the tool has parameters defined."""
        return bool(self.parameters and self.parameters.get("properties"))

    @property
    def required_parameters(self) -> list[str]:
        """Get list of required parameter names."""
        if not self.parameters:
            return []
        required = self.parameters.get("required", [])
        return required if isinstance(required, list) else []

    def to_llm_format(self) -> LLMToolDefinition:
        """Convert to LLM function calling format (OpenAI compatible)."""
        return LLMToolDefinition(
            function=FunctionDefinition(
                name=self.name,
                description=self.description or "No description provided",
                parameters=self.parameters or {"type": "object", "properties": {}},
            )
        )


class ServerCapabilities(BaseModel):
    """MCP server capabilities."""

    tools: bool = Field(default=False, description="Tools support")
    prompts: bool = Field(default=False, description="Prompts support")
    resources: bool = Field(default=False, description="Resources support")

    model_config = {"frozen": False, "extra": "allow"}


class ServerInfo(BaseModel):
    """Information about a connected server instance."""

    id: int = Field(description="Server identifier")
    name: str = Field(description="Server name")
    status: str = Field(description="Server status")
    tool_count: int = Field(default=0, description="Number of tools")
    namespace: str = Field(default="", description="Server namespace")
    enabled: bool = Field(default=True, description="Whether server is enabled")
    connected: bool = Field(default=False, description="Whether server is connected")
    transport: TransportType = Field(
        default=TransportType.STDIO, description="Transport type"
    )
    capabilities: dict[str, Any] = Field(
        default_factory=dict, description="Server capabilities"
    )
    description: str | None = Field(default=None, description="Server description")
    version: str | None = Field(default=None, description="Server version")
    command: str | None = Field(default=None, description="Server command (stdio)")
    url: str | None = Field(default=None, description="Server URL (http/sse)")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    env: dict[str, str] = Field(default_factory=dict, description="Environment vars")

    model_config = {"frozen": False}

    @property
    def is_healthy(self) -> bool:
        """Check if server is healthy and ready."""
        return self.status == "healthy" and self.connected

    @property
    def display_status(self) -> str:
        """Get a user-friendly status string."""
        if not self.enabled:
            return "disabled"
        elif not self.connected:
            return "disconnected"
        else:
            return self.status

    @property
    def display_description(self) -> str:
        """Get description or a default based on name."""
        if self.description:
            return self.description
        return f"{self.name} MCP server"

    @property
    def has_tools(self) -> bool:
        """Check if server has any tools."""
        return self.tool_count > 0


class ToolCallResult(BaseModel):
    """Outcome of a tool execution."""

    tool_name: str = Field(description="Name of the tool that was called")
    success: bool = Field(description="Whether the call succeeded")
    result: Any = Field(default=None, description="Result data if successful")
    error: str | None = Field(default=None, description="Error message if failed")
    execution_time: float | None = Field(
        default=None, description="Execution time in seconds"
    )

    model_config = {"frozen": False, "extra": "allow"}

    @property
    def is_cached(self) -> bool:
        """Check if result was cached (if tracking is available)."""
        return False

    @property
    def display_result(self) -> str:
        """Get a display-friendly result string."""
        if not self.success:
            return f"Error: {self.error or 'Unknown error'}"

        if isinstance(self.result, dict):
            try:
                return json.dumps(self.result, indent=2)
            except (TypeError, ValueError):
                return str(self.result)
        elif isinstance(self.result, str):
            return self.result
        elif self.result is not None:
            return str(self.result)
        else:
            return ""

    @property
    def has_error(self) -> bool:
        """Check if the result contains an error."""
        return not self.success or self.error is not None


class ToolCallMessage(BaseModel):
    """Tool call within a message (OpenAI format)."""

    id: str = Field(min_length=1, description="Tool call ID")
    type: str = Field(default="function", description="Call type")
    function: dict[str, Any] = Field(description="Function call details")

    model_config = {"frozen": False}


class ConversationMessage(BaseModel):
    """A single message in the conversation history.

    Compatible with OpenAI/Anthropic message format.
    """

    role: str = Field(description="Message role: user, assistant, system, or tool")
    content: str | None = Field(default=None, description="Message content")
    name: str | None = Field(default=None, description="Name for tool responses")
    tool_calls: list[ToolCallMessage] | None = Field(
        default=None, description="Tool calls made by assistant"
    )
    tool_call_id: str | None = Field(
        default=None, description="ID of tool call being responded to"
    )

    model_config = {"frozen": False}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return self.model_dump(exclude_none=True, mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationMessage:
        """Create from dictionary."""
        return cls.model_validate(data)

    @classmethod
    def user_message(cls, content: str) -> ConversationMessage:
        """Create a user message."""
        return cls(role="user", content=content)

    @classmethod
    def assistant_message(
        cls,
        content: str | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> ConversationMessage:
        """Create an assistant message."""
        parsed_tool_calls = None
        if tool_calls:
            parsed_tool_calls = [
                ToolCallMessage.model_validate(tc) for tc in tool_calls
            ]
        return cls(role="assistant", content=content, tool_calls=parsed_tool_calls)

    @classmethod
    def system_message(cls, content: str) -> ConversationMessage:
        """Create a system message."""
        return cls(role="system", content=content)

    @classmethod
    def tool_message(
        cls,
        content: str,
        tool_call_id: str,
        name: str | None = None,
    ) -> ConversationMessage:
        """Create a tool response message."""
        return cls(role="tool", content=content, tool_call_id=tool_call_id, name=name)


class ValidationResult(BaseModel):
    """Result of tool schema validation."""

    is_valid: bool = Field(description="Whether the tool schema is valid")
    error_message: str | None = Field(
        default=None, description="Error message if validation failed"
    )
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings")

    model_config = {"frozen": False}

    @classmethod
    def success(cls) -> ValidationResult:
        """Create a successful validation result."""
        return cls(is_valid=True)

    @classmethod
    def failure(cls, error: str) -> ValidationResult:
        """Create a failed validation result."""
        return cls(is_valid=False, error_message=error)

    @property
    def display_result(self) -> str:
        """Get a display-friendly result string."""
        if self.is_valid:
            return "Validation successful"
        return f"Error: {self.error_message or 'Unknown error'}"

    @property
    def has_error(self) -> bool:
        """Check if the result contains an error."""
        return not self.is_valid


__all__ = [
    "ToolType",
    "FunctionDefinition",
    "LLMToolDefinition",
    "ToolInfo",
    "ServerCapabilities",
    "ServerInfo",
    "ToolCallResult",
    "ToolCallMessage",
    "ConversationMessage",
    "ValidationResult",
]
