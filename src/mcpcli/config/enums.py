"""Configuration enums for type-safe settings in MCP CLI.

All enums inherit from str to allow use as string values while maintaining type safety.
"""

from __future__ import annotations

from enum import Enum


class TimeoutType(str, Enum):
    """Timeout configuration types."""

    STREAMING_CHUNK = "streaming_chunk"
    STREAMING_GLOBAL = "streaming_global"
    STREAMING_FIRST_CHUNK = "streaming_first_chunk"
    TOOL_EXECUTION = "tool_execution"
    SERVER_INIT = "server_init"
    HTTP_REQUEST = "http_request"
    HTTP_CONNECT = "http_connect"


class TokenBackend(str, Enum):
    """Token storage backend types."""

    AUTO = "auto"
    KEYCHAIN = "keychain"
    WINDOWS = "windows"
    SECRET_SERVICE = "secretservice"
    ENCRYPTED = "encrypted"
    VAULT = "vault"


class ConfigSource(str, Enum):
    """Configuration value source for priority resolution."""

    CLI = "cli"
    ENV = "env"
    FILE = "file"
    DEFAULT = "default"


class ServerStatus(str, Enum):
    """Server connection status values."""

    CONFIGURED = "configured"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class ConversationAction(str, Enum):
    """Actions for conversation management."""

    SHOW = "show"
    CLEAR = "clear"
    SAVE = "save"
    LOAD = "load"


class TokenAction(str, Enum):
    """Actions for token management."""

    LIST = "list"
    SET = "set"
    GET = "get"
    DELETE = "delete"
    CLEAR = "clear"
    BACKENDS = "backends"
    SET_PROVIDER = "set-provider"
    GET_PROVIDER = "get-provider"
    DELETE_PROVIDER = "delete-provider"


class OutputFormat(str, Enum):
    """Output format types for command results."""

    JSON = "json"
    TABLE = "table"
    TEXT = "text"
    TREE = "tree"


class TokenNamespace(str, Enum):
    """Token storage namespaces."""

    GENERIC = "generic"
    PROVIDER = "provider"
    BEARER = "bearer"
    API_KEY = "api-key"
    OAUTH = "oauth"


class SessionAction(str, Enum):
    """Actions for session management."""

    LIST = "list"
    SAVE = "save"
    LOAD = "load"
    DELETE = "delete"


class ServerAction(str, Enum):
    """Actions for server management."""

    ENABLE = "enable"
    DISABLE = "disable"
    STATUS = "status"
    INFO = "info"
    ADD = "add"
    REMOVE = "remove"
    LIST = "list"


class ToolAction(str, Enum):
    """Actions for tool management."""

    LIST = "list"
    ENABLE = "enable"
    DISABLE = "disable"
    CONFIRM = "confirm"
    INFO = "info"
    CALL = "call"


class ThemeAction(str, Enum):
    """Actions for theme management."""

    SET = "set"
    LIST = "list"
    SHOW = "show"


class TransportType(str, Enum):
    """MCP transport types."""

    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"
    UNKNOWN = "unknown"


__all__ = [
    "TimeoutType",
    "TokenBackend",
    "ConfigSource",
    "ServerStatus",
    "ConversationAction",
    "TokenAction",
    "OutputFormat",
    "TokenNamespace",
    "SessionAction",
    "ServerAction",
    "ToolAction",
    "ThemeAction",
    "TransportType",
]
