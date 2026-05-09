"""Tests for tool and server data models."""

from __future__ import annotations

import pytest

from mcpcli.tools.models import (
    ToolInfo,
    ServerInfo,
    ToolCallResult,
    ConversationMessage,
    ValidationResult,
    FunctionDefinition,
    LLMToolDefinition,
    ToolType,
    ToolCallMessage,
)
from mcpcli.config.enums import TransportType


class TestFunctionDefinition:
    """Tests for FunctionDefinition model."""

    def test_basic_function(self) -> None:
        """FunctionDefinition should store name and description."""
        func = FunctionDefinition(
            name="get_weather",
            description="Get current weather",
        )
        assert func.name == "get_weather"
        assert func.description == "Get current weather"

    def test_default_parameters(self) -> None:
        """FunctionDefinition should have default empty parameters."""
        func = FunctionDefinition(name="test", description="Test")
        assert func.parameters == {"type": "object", "properties": {}}

    def test_with_parameters(self) -> None:
        """FunctionDefinition should accept custom parameters."""
        params = {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
            },
            "required": ["city"],
        }
        func = FunctionDefinition(
            name="get_weather",
            description="Get weather",
            parameters=params,
        )
        assert func.parameters == params


class TestLLMToolDefinition:
    """Tests for LLMToolDefinition model."""

    def test_default_type(self) -> None:
        """LLMToolDefinition should default to function type."""
        func = FunctionDefinition(name="test", description="Test")
        tool = LLMToolDefinition(function=func)
        assert tool.type == ToolType.FUNCTION

    def test_to_dict(self) -> None:
        """LLMToolDefinition.to_dict should return dict format."""
        func = FunctionDefinition(name="test", description="Test function")
        tool = LLMToolDefinition(function=func)
        result = tool.to_dict()
        assert result["type"] == "function"
        assert result["function"]["name"] == "test"


class TestToolInfo:
    """Tests for ToolInfo model."""

    def test_basic_tool(self) -> None:
        """ToolInfo should store name and namespace."""
        tool = ToolInfo(name="get_data", namespace="server1")
        assert tool.name == "get_data"
        assert tool.namespace == "server1"

    def test_fully_qualified_name(self) -> None:
        """fully_qualified_name should return namespace.name format."""
        tool = ToolInfo(name="get_data", namespace="myserver")
        assert tool.fully_qualified_name == "myserver.get_data"

    def test_fully_qualified_name_no_namespace(self) -> None:
        """fully_qualified_name should handle empty namespace."""
        tool = ToolInfo(name="get_data", namespace="")
        assert tool.fully_qualified_name == "get_data"

    def test_display_name(self) -> None:
        """display_name should return the tool name."""
        tool = ToolInfo(name="get_weather", namespace="weather")
        assert tool.display_name == "get_weather"

    def test_has_parameters_false(self) -> None:
        """has_parameters should be False when no parameters."""
        tool = ToolInfo(name="test")
        assert tool.has_parameters is False

    def test_has_parameters_true(self) -> None:
        """has_parameters should be True when parameters exist."""
        tool = ToolInfo(
            name="test",
            parameters={"type": "object", "properties": {"x": {"type": "string"}}},
        )
        assert tool.has_parameters is True

    def test_required_parameters(self) -> None:
        """required_parameters should return required parameter names."""
        tool = ToolInfo(
            name="test",
            parameters={
                "type": "object",
                "properties": {"a": {}, "b": {}},
                "required": ["a"],
            },
        )
        assert tool.required_parameters == ["a"]

    def test_required_parameters_empty(self) -> None:
        """required_parameters should return empty list when none required."""
        tool = ToolInfo(name="test")
        assert tool.required_parameters == []

    def test_to_llm_format(self) -> None:
        """to_llm_format should convert to OpenAI format."""
        tool = ToolInfo(
            name="get_weather",
            namespace="weather",
            description="Get current weather for a city",
            parameters={
                "type": "object",
                "properties": {"city": {"type": "string"}},
            },
        )
        llm_format = tool.to_llm_format()
        assert isinstance(llm_format, LLMToolDefinition)
        assert llm_format.type == ToolType.FUNCTION
        assert llm_format.function.name == "get_weather"
        assert llm_format.function.description == "Get current weather for a city"

    def test_to_llm_format_default_description(self) -> None:
        """to_llm_format should use default description if none provided."""
        tool = ToolInfo(name="test")
        llm_format = tool.to_llm_format()
        assert llm_format.function.description == "No description provided"


class TestServerInfo:
    """Tests for ServerInfo model."""

    def test_basic_server(self) -> None:
        """ServerInfo should store basic fields."""
        server = ServerInfo(
            id=1,
            name="sqlite",
            status="healthy",
            tool_count=5,
        )
        assert server.id == 1
        assert server.name == "sqlite"
        assert server.status == "healthy"
        assert server.tool_count == 5

    def test_is_healthy_true(self) -> None:
        """is_healthy should be True when healthy and connected."""
        server = ServerInfo(
            id=1, name="test", status="healthy", connected=True
        )
        assert server.is_healthy is True

    def test_is_healthy_false_status(self) -> None:
        """is_healthy should be False when status is not healthy."""
        server = ServerInfo(
            id=1, name="test", status="error", connected=True
        )
        assert server.is_healthy is False

    def test_is_healthy_false_disconnected(self) -> None:
        """is_healthy should be False when disconnected."""
        server = ServerInfo(
            id=1, name="test", status="healthy", connected=False
        )
        assert server.is_healthy is False

    def test_display_status_disabled(self) -> None:
        """display_status should show disabled when not enabled."""
        server = ServerInfo(id=1, name="test", status="healthy", enabled=False)
        assert server.display_status == "disabled"

    def test_display_status_disconnected(self) -> None:
        """display_status should show disconnected when not connected."""
        server = ServerInfo(
            id=1, name="test", status="healthy", enabled=True, connected=False
        )
        assert server.display_status == "disconnected"

    def test_display_status_normal(self) -> None:
        """display_status should show status when enabled and connected."""
        server = ServerInfo(
            id=1, name="test", status="healthy", enabled=True, connected=True
        )
        assert server.display_status == "healthy"

    def test_display_description_custom(self) -> None:
        """display_description should return custom description."""
        server = ServerInfo(
            id=1, name="test", status="healthy", description="My custom server"
        )
        assert server.display_description == "My custom server"

    def test_display_description_default(self) -> None:
        """display_description should return default based on name."""
        server = ServerInfo(id=1, name="sqlite", status="healthy")
        assert server.display_description == "sqlite MCP server"

    def test_has_tools(self) -> None:
        """has_tools should check tool_count."""
        server = ServerInfo(id=1, name="test", status="healthy", tool_count=3)
        assert server.has_tools is True

        server_empty = ServerInfo(id=1, name="test", status="healthy", tool_count=0)
        assert server_empty.has_tools is False

    def test_transport_type(self) -> None:
        """ServerInfo should support different transport types."""
        server = ServerInfo(
            id=1, name="http-server", status="healthy", transport=TransportType.HTTP
        )
        assert server.transport == TransportType.HTTP


class TestToolCallResult:
    """Tests for ToolCallResult model."""

    def test_successful_result(self) -> None:
        """ToolCallResult should represent successful execution."""
        result = ToolCallResult(
            tool_name="get_data",
            success=True,
            result={"data": "value"},
            execution_time=0.5,
        )
        assert result.tool_name == "get_data"
        assert result.success is True
        assert result.result == {"data": "value"}
        assert result.execution_time == 0.5

    def test_failed_result(self) -> None:
        """ToolCallResult should represent failed execution."""
        result = ToolCallResult(
            tool_name="get_data",
            success=False,
            error="Connection failed",
        )
        assert result.success is False
        assert result.error == "Connection failed"
        assert result.has_error is True

    def test_display_result_dict(self) -> None:
        """display_result should format dict as JSON."""
        result = ToolCallResult(
            tool_name="test", success=True, result={"key": "value"}
        )
        display = result.display_result
        assert "key" in display
        assert "value" in display

    def test_display_result_string(self) -> None:
        """display_result should return string result directly."""
        result = ToolCallResult(
            tool_name="test", success=True, result="Hello world"
        )
        assert result.display_result == "Hello world"

    def test_display_result_error(self) -> None:
        """display_result should show error message on failure."""
        result = ToolCallResult(
            tool_name="test", success=False, error="Something went wrong"
        )
        assert "Error" in result.display_result
        assert "Something went wrong" in result.display_result

    def test_has_error_false(self) -> None:
        """has_error should be False for successful result."""
        result = ToolCallResult(tool_name="test", success=True)
        assert result.has_error is False


class TestConversationMessage:
    """Tests for ConversationMessage model."""

    def test_user_message(self) -> None:
        """user_message should create user role message."""
        msg = ConversationMessage.user_message("Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_assistant_message(self) -> None:
        """assistant_message should create assistant role message."""
        msg = ConversationMessage.assistant_message("Hi there!")
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"

    def test_system_message(self) -> None:
        """system_message should create system role message."""
        msg = ConversationMessage.system_message("You are a helpful assistant")
        assert msg.role == "system"
        assert msg.content == "You are a helpful assistant"

    def test_tool_message(self) -> None:
        """tool_message should create tool role message."""
        msg = ConversationMessage.tool_message(
            content="Result data",
            tool_call_id="call_123",
            name="get_weather",
        )
        assert msg.role == "tool"
        assert msg.content == "Result data"
        assert msg.tool_call_id == "call_123"
        assert msg.name == "get_weather"

    def test_assistant_message_with_tool_calls(self) -> None:
        """assistant_message should accept tool_calls."""
        tool_calls = [
            {"id": "call_1", "type": "function", "function": {"name": "test"}}
        ]
        msg = ConversationMessage.assistant_message(
            content=None, tool_calls=tool_calls
        )
        assert msg.role == "assistant"
        assert msg.tool_calls is not None
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0].id == "call_1"

    def test_to_dict(self) -> None:
        """to_dict should exclude None values."""
        msg = ConversationMessage.user_message("Hello")
        result = msg.to_dict()
        assert "role" in result
        assert "content" in result
        assert "tool_calls" not in result  # Should be excluded (None)

    def test_from_dict(self) -> None:
        """from_dict should create message from dictionary."""
        data = {"role": "user", "content": "Hello"}
        msg = ConversationMessage.from_dict(data)
        assert msg.role == "user"
        assert msg.content == "Hello"


class TestValidationResult:
    """Tests for ValidationResult model."""

    def test_success(self) -> None:
        """success should create valid result."""
        result = ValidationResult.success()
        assert result.is_valid is True
        assert result.error_message is None

    def test_failure(self) -> None:
        """failure should create invalid result with error."""
        result = ValidationResult.failure("Invalid schema")
        assert result.is_valid is False
        assert result.error_message == "Invalid schema"

    def test_display_result_valid(self) -> None:
        """display_result should show success message."""
        result = ValidationResult.success()
        assert result.display_result == "Validation successful"

    def test_display_result_invalid(self) -> None:
        """display_result should show error message."""
        result = ValidationResult.failure("Schema error")
        assert "Error" in result.display_result
        assert "Schema error" in result.display_result

    def test_has_error(self) -> None:
        """has_error should check validity."""
        assert ValidationResult.success().has_error is False
        assert ValidationResult.failure("err").has_error is True

    def test_warnings(self) -> None:
        """ValidationResult should support warnings."""
        result = ValidationResult(
            is_valid=True,
            warnings=["Consider adding description"],
        )
        assert result.is_valid is True
        assert len(result.warnings) == 1
