"""Tests for tool filtering."""

from __future__ import annotations

import pytest

from mcpcli.tools.filter import DisabledReason, FilterStats, ToolFilter


class TestDisabledReason:
    """Tests for DisabledReason enum."""

    def test_validation_reason(self) -> None:
        """VALIDATION reason exists."""
        assert DisabledReason.VALIDATION.value == "validation"

    def test_user_reason(self) -> None:
        """USER reason exists."""
        assert DisabledReason.USER.value == "user"

    def test_unknown_reason(self) -> None:
        """UNKNOWN reason exists."""
        assert DisabledReason.UNKNOWN.value == "unknown"

    def test_is_string_enum(self) -> None:
        """DisabledReason is a string enum."""
        assert isinstance(DisabledReason.VALIDATION.value, str)


class TestFilterStats:
    """Tests for FilterStats model."""

    def test_default_values(self) -> None:
        """Default values are zero."""
        stats = FilterStats()
        assert stats.attempted == 0
        assert stats.successful == 0
        assert stats.failed == 0

    def test_increment_attempted(self) -> None:
        """increment_attempted increases attempted count."""
        stats = FilterStats()
        stats.increment_attempted()
        assert stats.attempted == 1

    def test_increment_successful(self) -> None:
        """increment_successful increases successful count."""
        stats = FilterStats()
        stats.increment_successful()
        assert stats.successful == 1

    def test_increment_failed(self) -> None:
        """increment_failed increases failed count."""
        stats = FilterStats()
        stats.increment_failed()
        assert stats.failed == 1

    def test_reset(self) -> None:
        """reset clears all counters."""
        stats = FilterStats()
        stats.attempted = 10
        stats.successful = 8
        stats.failed = 2
        stats.reset()
        assert stats.attempted == 0
        assert stats.successful == 0
        assert stats.failed == 0

    def test_to_dict(self) -> None:
        """to_dict returns dictionary representation."""
        stats = FilterStats()
        stats.attempted = 5
        stats.successful = 3
        stats.failed = 2
        result = stats.to_dict()
        assert result == {"attempted": 5, "successful": 3, "failed": 2}


class TestToolFilter:
    """Tests for ToolFilter class."""

    def test_initialization(self) -> None:
        """Filter initializes with empty sets."""
        tf = ToolFilter()
        assert tf.disabled_tools == set()
        assert tf.disabled_by_validation == set()
        assert tf.disabled_by_user == set()
        assert tf.auto_fix_enabled is True
        assert tf._validation_cache == {}
        assert tf._fix_stats.to_dict() == {"attempted": 0, "successful": 0, "failed": 0}

    def test_is_tool_enabled(self) -> None:
        """is_tool_enabled returns True for enabled tools."""
        tf = ToolFilter()
        assert tf.is_tool_enabled("test_tool") is True

        tf.disabled_tools.add("test_tool")
        assert tf.is_tool_enabled("test_tool") is False

    def test_disable_tool_user_reason(self) -> None:
        """disable_tool with USER reason."""
        tf = ToolFilter()
        tf.disable_tool("tool1", reason=DisabledReason.USER)

        assert "tool1" in tf.disabled_tools
        assert "tool1" in tf.disabled_by_user
        assert "tool1" not in tf.disabled_by_validation

    def test_disable_tool_validation_reason(self) -> None:
        """disable_tool with VALIDATION reason."""
        tf = ToolFilter()
        tf.disable_tool("tool2", reason=DisabledReason.VALIDATION)

        assert "tool2" in tf.disabled_tools
        assert "tool2" in tf.disabled_by_validation
        assert "tool2" not in tf.disabled_by_user

    def test_enable_tool(self) -> None:
        """enable_tool removes tool from all disabled sets."""
        tf = ToolFilter()
        tf.disable_tool("tool1", reason=DisabledReason.USER)
        tf.disable_tool("tool2", reason=DisabledReason.VALIDATION)

        tf.enable_tool("tool1")
        assert "tool1" not in tf.disabled_tools
        assert "tool1" not in tf.disabled_by_user

        tf.enable_tool("tool2")
        assert "tool2" not in tf.disabled_tools
        assert "tool2" not in tf.disabled_by_validation

    def test_get_disabled_tools(self) -> None:
        """get_disabled_tools returns tools with reasons."""
        tf = ToolFilter()
        tf.disable_tool("tool1", reason=DisabledReason.USER)
        tf.disable_tool("tool2", reason=DisabledReason.VALIDATION)

        disabled = tf.get_disabled_tools()
        assert disabled["tool1"] == "user"
        assert disabled["tool2"] == "validation"

    def test_get_disabled_tools_by_reason(self) -> None:
        """get_disabled_tools_by_reason filters by reason."""
        tf = ToolFilter()
        tf.disable_tool("tool1", reason=DisabledReason.USER)
        tf.disable_tool("tool2", reason=DisabledReason.USER)
        tf.disable_tool("tool3", reason=DisabledReason.VALIDATION)

        user_disabled = tf.get_disabled_tools_by_reason("user")
        assert "tool1" in user_disabled
        assert "tool2" in user_disabled
        assert "tool3" not in user_disabled

        validation_disabled = tf.get_disabled_tools_by_reason("validation")
        assert "tool3" in validation_disabled
        assert "tool1" not in validation_disabled

        unknown_disabled = tf.get_disabled_tools_by_reason("unknown")
        assert unknown_disabled == set()

    def test_clear_validation_disabled(self) -> None:
        """clear_validation_disabled clears validation disabled tools."""
        tf = ToolFilter()
        tf.disable_tool("tool1", reason=DisabledReason.VALIDATION)
        tf.disable_tool("tool2", reason=DisabledReason.USER)

        tf.clear_validation_disabled()

        assert "tool1" not in tf.disabled_tools
        assert "tool1" not in tf.disabled_by_validation
        assert "tool2" in tf.disabled_tools
        assert tf._validation_cache == {}
        assert tf._fix_stats.to_dict() == {"attempted": 0, "successful": 0, "failed": 0}


class TestToolFilterFilterTools:
    """Tests for ToolFilter.filter_tools method."""

    def test_filter_tools_with_valid_openai_tools(self) -> None:
        """filter_tools accepts valid OpenAI tools."""
        tf = ToolFilter()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "valid_tool",
                    "description": "A valid tool",
                    "parameters": {
                        "type": "object",
                        "properties": {"arg1": {"type": "string"}},
                    },
                },
            }
        ]

        valid, invalid = tf.filter_tools(tools, provider="openai")

        assert len(valid) == 1
        assert len(invalid) == 0
        assert valid[0]["function"]["name"] == "valid_tool"

    def test_filter_tools_with_invalid_openai_tools(self) -> None:
        """filter_tools rejects tools with invalid names."""
        tf = ToolFilter()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "invalid@tool",
                    "description": "Invalid tool",
                },
            }
        ]

        valid, invalid = tf.filter_tools(tools, provider="openai")

        assert len(valid) == 0
        assert len(invalid) == 1
        assert "invalid@tool" in tf.disabled_by_validation

    def test_filter_tools_auto_fix_enabled(self) -> None:
        """filter_tools auto-fixes tools with unsupported properties."""
        tf = ToolFilter()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "tool_with_extras",
                    "description": "Tool with unsupported props",
                    "title": "Should be removed",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ]

        valid, invalid = tf.filter_tools(tools, provider="openai")

        assert len(valid) == 1
        assert "title" not in valid[0]["function"]
        assert tf._fix_stats.successful > 0

    def test_filter_tools_auto_fix_disabled(self) -> None:
        """filter_tools without auto-fix."""
        tf = ToolFilter()
        tf.set_auto_fix_enabled(False)

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "tool",
                    "description": "Tool",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ]

        valid, invalid = tf.filter_tools(tools, provider="openai")

        assert len(valid) == 1
        assert tf._fix_stats.attempted == 0

    def test_filter_tools_with_manually_disabled(self) -> None:
        """filter_tools skips manually disabled tools."""
        tf = ToolFilter()
        tf.disable_tool("disabled_tool", reason=DisabledReason.USER)

        tools = [
            {
                "type": "function",
                "function": {"name": "disabled_tool", "description": "Will be skipped"},
            }
        ]

        valid, invalid = tf.filter_tools(tools, provider="openai")

        assert len(valid) == 0
        assert len(invalid) == 1
        assert invalid[0]["_disabled_reason"] == "user"

    def test_filter_tools_non_openai_provider(self) -> None:
        """filter_tools passes through for non-OpenAI providers."""
        tf = ToolFilter()
        tools = [
            {
                "type": "function",
                "function": {"name": "any_tool", "description": "Any tool"},
            }
        ]

        valid, invalid = tf.filter_tools(tools, provider="anthropic")

        assert len(valid) == 1
        assert len(invalid) == 0

    def test_filter_tools_mixed_valid_invalid(self) -> None:
        """filter_tools handles mix of valid and invalid tools."""
        tf = ToolFilter()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "valid_tool",
                    "description": "Valid",
                    "parameters": {"type": "object"},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "invalid@tool",
                    "description": "Invalid",
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "another_valid",
                    "description": "Valid",
                    "parameters": {"type": "object"},
                },
            },
        ]

        valid, invalid = tf.filter_tools(tools, provider="openai")

        assert len(valid) == 2
        assert len(invalid) == 1
        assert any(t["function"]["name"] == "valid_tool" for t in valid)
        assert any(t["function"]["name"] == "another_valid" for t in valid)


class TestToolFilterHelpers:
    """Tests for ToolFilter helper methods."""

    def test_extract_tool_name_with_function(self) -> None:
        """_extract_tool_name extracts from function structure."""
        tf = ToolFilter()
        tool = {"function": {"name": "test_tool"}}
        assert tf._extract_tool_name(tool) == "test_tool"

    def test_extract_tool_name_without_function(self) -> None:
        """_extract_tool_name extracts from direct name."""
        tf = ToolFilter()
        tool = {"name": "direct_tool"}
        assert tf._extract_tool_name(tool) == "direct_tool"

    def test_extract_tool_name_unknown(self) -> None:
        """_extract_tool_name returns unknown for missing name."""
        tf = ToolFilter()
        tool = {}
        assert tf._extract_tool_name(tool) == "unknown"

    def test_get_validation_summary(self) -> None:
        """get_validation_summary returns summary dict."""
        tf = ToolFilter()
        tf.disable_tool("tool1", reason=DisabledReason.USER)
        tf.disable_tool("tool2", reason=DisabledReason.VALIDATION)

        summary = tf.get_validation_summary()

        assert summary["total_disabled"] == 2
        assert summary["disabled_by_validation"] == 1
        assert summary["disabled_by_user"] == 1
        assert summary["auto_fix_enabled"] is True
        assert "fix_stats" in summary

    def test_get_fix_statistics(self) -> None:
        """get_fix_statistics returns stats dict."""
        tf = ToolFilter()
        stats = tf.get_fix_statistics()

        assert "attempted" in stats
        assert "successful" in stats
        assert "failed" in stats
        assert stats["attempted"] == 0

    def test_reset_statistics(self) -> None:
        """reset_statistics clears fix stats."""
        tf = ToolFilter()
        tf._fix_stats.attempted = 10
        tf._fix_stats.successful = 8
        tf._fix_stats.failed = 2

        tf.reset_statistics()

        assert tf._fix_stats.to_dict() == {"attempted": 0, "successful": 0, "failed": 0}

    def test_set_auto_fix_enabled(self) -> None:
        """set_auto_fix_enabled changes auto_fix_enabled."""
        tf = ToolFilter()
        assert tf.auto_fix_enabled is True

        tf.set_auto_fix_enabled(False)
        assert tf.auto_fix_enabled is False

        tf.set_auto_fix_enabled(True)
        assert tf.auto_fix_enabled is True

    def test_is_auto_fix_enabled(self) -> None:
        """is_auto_fix_enabled returns auto_fix_enabled state."""
        tf = ToolFilter()
        assert tf.is_auto_fix_enabled() is True

        tf.auto_fix_enabled = False
        assert tf.is_auto_fix_enabled() is False
