"""Tool filtering and management for MCP CLI.

Manages tool validation, auto-fixing, and disabling based on various criteria.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from mcpcli.tools.validation import ToolSchemaValidator

logger = logging.getLogger(__name__)


class DisabledReason(str, Enum):
    """Reason why a tool was disabled."""

    VALIDATION = "validation"
    USER = "user"
    UNKNOWN = "unknown"


class FilterStats(BaseModel):
    """Auto-fix statistics for tool filtering."""

    attempted: int = Field(default=0, description="Number of fix attempts")
    successful: int = Field(default=0, description="Number of successful fixes")
    failed: int = Field(default=0, description="Number of failed fixes")

    model_config = {"frozen": False}

    def increment_attempted(self) -> None:
        """Increment attempted counter."""
        self.attempted += 1

    def increment_successful(self) -> None:
        """Increment successful counter."""
        self.successful += 1

    def increment_failed(self) -> None:
        """Increment failed counter."""
        self.failed += 1

    def reset(self) -> None:
        """Reset all counters."""
        self.attempted = 0
        self.successful = 0
        self.failed = 0

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary."""
        return {
            "attempted": self.attempted,
            "successful": self.successful,
            "failed": self.failed,
        }


class ToolFilter:
    """Manages tool filtering and disabling based on validation and user preferences."""

    def __init__(self) -> None:
        """Initialize the tool filter."""
        self.disabled_tools: set[str] = set()
        self.disabled_by_validation: set[str] = set()
        self.disabled_by_user: set[str] = set()
        self.auto_fix_enabled: bool = True
        self._validation_cache: dict[str, tuple[bool, str | None]] = {}
        self._fix_stats = FilterStats()

    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled (not disabled).

        Args:
            tool_name: The tool name to check.

        Returns:
            True if enabled, False if disabled.
        """
        return tool_name not in self.disabled_tools

    def disable_tool(
        self,
        tool_name: str,
        reason: DisabledReason = DisabledReason.USER,
    ) -> None:
        """Disable a tool for a specific reason.

        Args:
            tool_name: The tool name to disable.
            reason: The reason for disabling.
        """
        self.disabled_tools.add(tool_name)
        if reason == DisabledReason.VALIDATION:
            self.disabled_by_validation.add(tool_name)
        elif reason == DisabledReason.USER:
            self.disabled_by_user.add(tool_name)
        logger.info(f"Disabled tool '{tool_name}' (reason: {reason.value})")

    def enable_tool(self, tool_name: str) -> None:
        """Re-enable a previously disabled tool.

        Args:
            tool_name: The tool name to enable.
        """
        self.disabled_tools.discard(tool_name)
        self.disabled_by_validation.discard(tool_name)
        self.disabled_by_user.discard(tool_name)
        logger.info(f"Enabled tool '{tool_name}'")

    def get_disabled_tools(self) -> dict[str, str]:
        """Get all disabled tools with their reasons.

        Returns:
            Dictionary mapping tool name to reason string.
        """
        result: dict[str, str] = {}
        for tool in self.disabled_by_validation:
            result[tool] = DisabledReason.VALIDATION.value
        for tool in self.disabled_by_user:
            result[tool] = DisabledReason.USER.value
        return result

    def get_disabled_tools_by_reason(self, reason: DisabledReason | str) -> set[str]:
        """Get disabled tools by specific reason.

        Args:
            reason: The reason to filter by.

        Returns:
            Set of tool names disabled for that reason.
        """
        reason_value = reason.value if isinstance(reason, DisabledReason) else reason

        if reason_value == DisabledReason.VALIDATION.value:
            return self.disabled_by_validation.copy()
        elif reason_value == DisabledReason.USER.value:
            return self.disabled_by_user.copy()
        return set()

    def clear_validation_disabled(self) -> None:
        """Clear all validation-disabled tools for re-validation."""
        self.disabled_tools -= self.disabled_by_validation
        self.disabled_by_validation.clear()
        self._validation_cache.clear()
        self._fix_stats.reset()
        logger.info("Cleared all validation-disabled tools")

    def filter_tools(
        self,
        tools: list[dict[str, Any]],
        provider: str = "openai",
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Filter tools, separating valid from invalid ones.

        For OpenAI provider, validates and auto-fixes tools. Other providers
        pass through without validation.

        Args:
            tools: List of tool definitions.
            provider: The LLM provider name.

        Returns:
            Tuple of (valid_tools, invalid_tools).
        """
        valid_tools: list[dict[str, Any]] = []
        invalid_tools: list[dict[str, Any]] = []

        for tool in tools:
            tool_name = self._extract_tool_name(tool)

            if not self.is_tool_enabled(tool_name):
                invalid_tools.append({
                    **tool,
                    "_disabled_reason": self.get_disabled_tools().get(
                        tool_name, DisabledReason.UNKNOWN.value
                    ),
                })
                continue

            if provider == "openai":
                if self.auto_fix_enabled:
                    self._fix_stats.increment_attempted()

                    is_valid, fixed_tool, error_msg = (
                        ToolSchemaValidator.validate_and_fix_tool(tool, provider)
                    )

                    if is_valid:
                        self._fix_stats.increment_successful()

                        if fixed_tool != tool:
                            logger.info(
                                f"Auto-fixed tool '{tool_name}' - removed unsupported properties"
                            )

                        valid_tools.append(fixed_tool)
                    else:
                        self._fix_stats.increment_failed()
                        logger.warning(
                            f"Tool '{tool_name}' failed validation: {error_msg}"
                        )

                        self.disable_tool(tool_name, DisabledReason.VALIDATION)
                        invalid_tools.append({
                            **tool,
                            "_validation_error": error_msg,
                            "_disabled_reason": DisabledReason.VALIDATION.value,
                        })
                else:
                    validation = ToolSchemaValidator.validate_openai_schema(tool)

                    if validation.is_valid:
                        valid_tools.append(tool)
                    else:
                        logger.warning(
                            f"Tool '{tool_name}' failed validation: {validation.error_message}"
                        )
                        self.disable_tool(tool_name, DisabledReason.VALIDATION)
                        invalid_tools.append({
                            **tool,
                            "_validation_error": validation.error_message,
                            "_disabled_reason": DisabledReason.VALIDATION.value,
                        })
            else:
                valid_tools.append(tool)

        if self._fix_stats.attempted > 0:
            logger.info(
                f"Auto-fix results: {self._fix_stats.successful}/{self._fix_stats.attempted} tools fixed"
            )

        return valid_tools, invalid_tools

    def _extract_tool_name(self, tool: dict[str, Any]) -> str:
        """Extract tool name from tool definition.

        Args:
            tool: Tool definition dictionary.

        Returns:
            The tool name or "unknown".
        """
        if "function" in tool:
            return str(tool["function"].get("name", "unknown"))
        return str(tool.get("name", "unknown"))

    def get_validation_summary(self) -> dict[str, Any]:
        """Get a summary of validation results.

        Returns:
            Dictionary with validation statistics.
        """
        return {
            "total_disabled": len(self.disabled_tools),
            "disabled_by_validation": len(self.disabled_by_validation),
            "disabled_by_user": len(self.disabled_by_user),
            "auto_fix_enabled": self.auto_fix_enabled,
            "cache_size": len(self._validation_cache),
            "fix_stats": self._fix_stats.to_dict(),
        }

    def get_fix_statistics(self) -> dict[str, int]:
        """Get auto-fix statistics.

        Returns:
            Dictionary with fix attempt counts.
        """
        return self._fix_stats.to_dict()

    def reset_statistics(self) -> None:
        """Reset fix statistics."""
        self._fix_stats.reset()

    def set_auto_fix_enabled(self, enabled: bool) -> None:
        """Enable or disable auto-fixing.

        Args:
            enabled: Whether to enable auto-fixing.
        """
        self.auto_fix_enabled = enabled
        logger.info(f"Auto-fix {'enabled' if enabled else 'disabled'}")

    def is_auto_fix_enabled(self) -> bool:
        """Check if auto-fix is enabled.

        Returns:
            True if auto-fix is enabled.
        """
        return self.auto_fix_enabled


__all__ = [
    "DisabledReason",
    "FilterStats",
    "ToolFilter",
]
