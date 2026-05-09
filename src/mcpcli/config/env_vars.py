"""Environment variable helpers for MCP CLI.

Provides type-safe access to environment variables with an enum-based interface.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import TypeVar


class EnvVar(str, Enum):
    """Environment variable names used by the CLI."""

    # Tool configuration
    TOOL_TIMEOUT = "MCP_TOOL_TIMEOUT"
    MAX_TOOL_CONCURRENCY = "MCP_MAX_TOOL_CONCURRENCY"

    # Provider configuration
    LLM_PROVIDER = "LLM_PROVIDER"
    LLM_MODEL = "LLM_MODEL"

    # API keys
    OPENAI_API_KEY = "OPENAI_API_KEY"
    ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"
    GROQ_API_KEY = "GROQ_API_KEY"

    # Paths and configuration
    CONFIG_PATH = "MCP_CONFIG_PATH"
    LOG_LEVEL = "MCP_LOG_LEVEL"

    # Standard environment variables
    PATH = "PATH"
    HOME = "HOME"

    # Debug and development
    DEBUG = "MCP_DEBUG"
    VERBOSE = "MCP_VERBOSE"


T = TypeVar("T")


def get_env(var: EnvVar, default: str | None = None) -> str | None:
    """Get an environment variable value.

    Args:
        var: The environment variable enum member.
        default: Default value if not set.

    Returns:
        The environment variable value or default if not set.
    """
    return os.environ.get(var.value, default)


def set_env(var: EnvVar, value: str) -> None:
    """Set an environment variable.

    Args:
        var: The environment variable enum member.
        value: The value to set.
    """
    os.environ[var.value] = value


def unset_env(var: EnvVar) -> None:
    """Unset (remove) an environment variable.

    Args:
        var: The environment variable enum member.
    """
    os.environ.pop(var.value, None)


def is_set(var: EnvVar) -> bool:
    """Check if an environment variable is set.

    Args:
        var: The environment variable enum member.

    Returns:
        True if the variable is set, False otherwise.
    """
    return var.value in os.environ


def get_env_int(var: EnvVar, default: int | None = None) -> int | None:
    """Get an environment variable as an integer.

    Args:
        var: The environment variable enum member.
        default: Default value if not set or invalid.

    Returns:
        The integer value or default if not set or invalid.
    """
    value = get_env(var)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_env_float(var: EnvVar, default: float | None = None) -> float | None:
    """Get an environment variable as a float.

    Args:
        var: The environment variable enum member.
        default: Default value if not set or invalid.

    Returns:
        The float value or default if not set or invalid.
    """
    value = get_env(var)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def get_env_bool(var: EnvVar, default: bool = False) -> bool:
    """Get an environment variable as a boolean.

    Truthy values: "1", "true", "yes", "on" (case-insensitive)
    Falsy values: "0", "false", "no", "off", "" (case-insensitive)

    Args:
        var: The environment variable enum member.
        default: Default value if not set.

    Returns:
        The boolean value or default if not set.
    """
    value = get_env(var)
    if value is None:
        return default

    truthy_values = {"1", "true", "yes", "on"}
    falsy_values = {"0", "false", "no", "off", ""}

    lower_value = value.lower()
    if lower_value in truthy_values:
        return True
    elif lower_value in falsy_values:
        return False
    else:
        return default


def get_env_list(var: EnvVar, separator: str = ",", default: list[str] | None = None) -> list[str]:
    """Get an environment variable as a list of strings.

    Args:
        var: The environment variable enum member.
        separator: The separator to split on (default: comma).
        default: Default value if not set.

    Returns:
        The list of values or default if not set.
    """
    value = get_env(var)
    if value is None:
        return default if default is not None else []

    if not value.strip():
        return []

    return [item.strip() for item in value.split(separator) if item.strip()]


__all__ = [
    "EnvVar",
    "get_env",
    "set_env",
    "unset_env",
    "is_set",
    "get_env_int",
    "get_env_float",
    "get_env_bool",
    "get_env_list",
]
