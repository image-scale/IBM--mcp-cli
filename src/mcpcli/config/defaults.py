"""Default configuration values for MCP CLI.

All default constants are defined here to avoid magic numbers throughout the codebase.
"""

from __future__ import annotations


# Streaming timeouts (seconds)
DEFAULT_STREAMING_CHUNK_TIMEOUT = 45.0
DEFAULT_STREAMING_GLOBAL_TIMEOUT = 300.0
DEFAULT_STREAMING_FIRST_CHUNK_TIMEOUT = 60.0

# Tool execution timeouts (seconds)
DEFAULT_TOOL_EXECUTION_TIMEOUT = 120.0

# Server timeouts (seconds)
DEFAULT_SERVER_INIT_TIMEOUT = 120.0

# HTTP timeouts (seconds)
DEFAULT_HTTP_REQUEST_TIMEOUT = 30.0
DEFAULT_HTTP_CONNECT_TIMEOUT = 10.0

# Tool configuration
DEFAULT_MAX_TOOL_CONCURRENCY = 5
DEFAULT_CONFIRM_TOOLS = True
DEFAULT_DYNAMIC_TOOLS_ENABLED = False

# Conversation settings
DEFAULT_MAX_TURNS = 100
DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant with access to tools."

# Context management
DEFAULT_MAX_TOOL_RESULT_CHARS = 100_000
DEFAULT_MAX_HISTORY_MESSAGES = 200

# Provider and model defaults
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4o-mini"

# UI defaults
DEFAULT_THEME = "default"
DEFAULT_VERBOSE = True

# Token/Auth defaults
DEFAULT_TOKEN_BACKEND = "auto"

# Path defaults
DEFAULT_CONFIG_DIR = "~/.mcpcli"
DEFAULT_CONFIG_FILENAME = "server_config.json"

# Application constants
APP_NAME = "mcpcli"
NAMESPACE = "mcpcli"
OAUTH_NAMESPACE = NAMESPACE
PROVIDER_NAMESPACE = "provider"
GENERIC_NAMESPACE = "generic"

# Platform identifiers
PLATFORM_WINDOWS = "win32"
PLATFORM_DARWIN = "darwin"
PLATFORM_LINUX = "linux"

# Supported providers
PROVIDER_OLLAMA = "ollama"
PROVIDER_OPENAI = "openai"
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_GROQ = "groq"

SUPPORTED_PROVIDERS = [
    PROVIDER_OLLAMA,
    PROVIDER_OPENAI,
    PROVIDER_ANTHROPIC,
    PROVIDER_GROQ,
]

# JSON Schema type constants
JSON_TYPE_STRING = "string"
JSON_TYPE_NUMBER = "number"
JSON_TYPE_INTEGER = "integer"
JSON_TYPE_BOOLEAN = "boolean"
JSON_TYPE_ARRAY = "array"
JSON_TYPE_OBJECT = "object"
JSON_TYPE_NULL = "null"

JSON_TYPES = [
    JSON_TYPE_STRING,
    JSON_TYPE_NUMBER,
    JSON_TYPE_INTEGER,
    JSON_TYPE_BOOLEAN,
    JSON_TYPE_ARRAY,
    JSON_TYPE_OBJECT,
    JSON_TYPE_NULL,
]

# Logging defaults
DEFAULT_LOG_DIR = "~/.mcpcli/logs"
DEFAULT_LOG_MAX_BYTES = 10_485_760
DEFAULT_LOG_BACKUP_COUNT = 3

# Session defaults
DEFAULT_SESSIONS_DIR = "~/.mcpcli/sessions"
DEFAULT_AUTO_SAVE_INTERVAL = 10
