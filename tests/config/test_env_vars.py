"""Tests for environment variable helpers."""

from __future__ import annotations

import os
import pytest

from mcpcli.config.env_vars import (
    EnvVar,
    get_env,
    set_env,
    unset_env,
    is_set,
    get_env_int,
    get_env_float,
    get_env_bool,
    get_env_list,
)


class TestEnvVar:
    """Tests for EnvVar enum."""

    def test_tool_timeout_value(self) -> None:
        """TOOL_TIMEOUT should have correct string value."""
        assert EnvVar.TOOL_TIMEOUT.value == "MCP_TOOL_TIMEOUT"

    def test_llm_provider_value(self) -> None:
        """LLM_PROVIDER should have correct string value."""
        assert EnvVar.LLM_PROVIDER.value == "LLM_PROVIDER"

    def test_path_value(self) -> None:
        """PATH should have correct string value."""
        assert EnvVar.PATH.value == "PATH"

    def test_is_string_enum(self) -> None:
        """EnvVar should be usable as strings."""
        assert EnvVar.TOOL_TIMEOUT.value == "MCP_TOOL_TIMEOUT"
        assert f"{EnvVar.TOOL_TIMEOUT.value}" == "MCP_TOOL_TIMEOUT"


class TestGetEnv:
    """Tests for get_env function."""

    def test_returns_value_when_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env returns environment variable value."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "300")
        assert get_env(EnvVar.TOOL_TIMEOUT) == "300"

    def test_returns_default_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env returns default when variable not set."""
        monkeypatch.delenv("MCP_TOOL_TIMEOUT", raising=False)
        assert get_env(EnvVar.TOOL_TIMEOUT, "120") == "120"

    def test_returns_none_when_not_set_no_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env returns None when variable not set and no default."""
        monkeypatch.delenv("MCP_TOOL_TIMEOUT", raising=False)
        assert get_env(EnvVar.TOOL_TIMEOUT) is None


class TestSetEnv:
    """Tests for set_env function."""

    def test_sets_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """set_env sets environment variable."""
        monkeypatch.delenv("MCP_TOOL_TIMEOUT", raising=False)
        set_env(EnvVar.TOOL_TIMEOUT, "600")
        assert os.environ["MCP_TOOL_TIMEOUT"] == "600"

    def test_overwrites_existing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """set_env overwrites existing value."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "100")
        set_env(EnvVar.TOOL_TIMEOUT, "200")
        assert os.environ["MCP_TOOL_TIMEOUT"] == "200"


class TestUnsetEnv:
    """Tests for unset_env function."""

    def test_removes_variable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """unset_env removes environment variable."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "300")
        unset_env(EnvVar.TOOL_TIMEOUT)
        assert "MCP_TOOL_TIMEOUT" not in os.environ

    def test_no_error_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """unset_env doesn't error when variable not set."""
        monkeypatch.delenv("MCP_TOOL_TIMEOUT", raising=False)
        unset_env(EnvVar.TOOL_TIMEOUT)
        assert "MCP_TOOL_TIMEOUT" not in os.environ


class TestIsSet:
    """Tests for is_set function."""

    def test_returns_true_when_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """is_set returns True when variable is set."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "300")
        assert is_set(EnvVar.TOOL_TIMEOUT) is True

    def test_returns_false_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """is_set returns False when variable is not set."""
        monkeypatch.delenv("MCP_TOOL_TIMEOUT", raising=False)
        assert is_set(EnvVar.TOOL_TIMEOUT) is False

    def test_returns_true_for_empty_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """is_set returns True even when value is empty string."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "")
        assert is_set(EnvVar.TOOL_TIMEOUT) is True


class TestGetEnvInt:
    """Tests for get_env_int function."""

    def test_returns_int_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_int returns integer value."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "300")
        assert get_env_int(EnvVar.TOOL_TIMEOUT) == 300

    def test_returns_default_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_int returns default when not set."""
        monkeypatch.delenv("MCP_TOOL_TIMEOUT", raising=False)
        assert get_env_int(EnvVar.TOOL_TIMEOUT, 120) == 120

    def test_returns_none_when_not_set_no_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_int returns None when not set and no default."""
        monkeypatch.delenv("MCP_TOOL_TIMEOUT", raising=False)
        assert get_env_int(EnvVar.TOOL_TIMEOUT) is None

    def test_returns_default_for_invalid_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_int returns default for invalid integer."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "not_a_number")
        assert get_env_int(EnvVar.TOOL_TIMEOUT, 120) == 120

    def test_handles_negative_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_int handles negative values."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "-50")
        assert get_env_int(EnvVar.TOOL_TIMEOUT) == -50


class TestGetEnvFloat:
    """Tests for get_env_float function."""

    def test_returns_float_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_float returns float value."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "120.5")
        assert get_env_float(EnvVar.TOOL_TIMEOUT) == 120.5

    def test_returns_default_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_float returns default when not set."""
        monkeypatch.delenv("MCP_TOOL_TIMEOUT", raising=False)
        assert get_env_float(EnvVar.TOOL_TIMEOUT, 60.0) == 60.0

    def test_returns_none_when_not_set_no_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_float returns None when not set and no default."""
        monkeypatch.delenv("MCP_TOOL_TIMEOUT", raising=False)
        assert get_env_float(EnvVar.TOOL_TIMEOUT) is None

    def test_returns_default_for_invalid_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_float returns default for invalid float."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "not_a_float")
        assert get_env_float(EnvVar.TOOL_TIMEOUT, 60.0) == 60.0

    def test_handles_integer_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_float handles integer values."""
        monkeypatch.setenv("MCP_TOOL_TIMEOUT", "120")
        assert get_env_float(EnvVar.TOOL_TIMEOUT) == 120.0


class TestGetEnvBool:
    """Tests for get_env_bool function."""

    def test_returns_true_for_1(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns True for '1'."""
        monkeypatch.setenv("MCP_DEBUG", "1")
        assert get_env_bool(EnvVar.DEBUG) is True

    def test_returns_true_for_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns True for 'true'."""
        monkeypatch.setenv("MCP_DEBUG", "true")
        assert get_env_bool(EnvVar.DEBUG) is True

    def test_returns_true_for_yes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns True for 'yes'."""
        monkeypatch.setenv("MCP_DEBUG", "yes")
        assert get_env_bool(EnvVar.DEBUG) is True

    def test_returns_true_for_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns True for 'on'."""
        monkeypatch.setenv("MCP_DEBUG", "on")
        assert get_env_bool(EnvVar.DEBUG) is True

    def test_returns_false_for_0(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns False for '0'."""
        monkeypatch.setenv("MCP_DEBUG", "0")
        assert get_env_bool(EnvVar.DEBUG) is False

    def test_returns_false_for_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns False for 'false'."""
        monkeypatch.setenv("MCP_DEBUG", "false")
        assert get_env_bool(EnvVar.DEBUG) is False

    def test_returns_false_for_no(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns False for 'no'."""
        monkeypatch.setenv("MCP_DEBUG", "no")
        assert get_env_bool(EnvVar.DEBUG) is False

    def test_returns_false_for_off(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns False for 'off'."""
        monkeypatch.setenv("MCP_DEBUG", "off")
        assert get_env_bool(EnvVar.DEBUG) is False

    def test_returns_false_for_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns False for empty string."""
        monkeypatch.setenv("MCP_DEBUG", "")
        assert get_env_bool(EnvVar.DEBUG) is False

    def test_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool is case insensitive."""
        monkeypatch.setenv("MCP_DEBUG", "TRUE")
        assert get_env_bool(EnvVar.DEBUG) is True
        monkeypatch.setenv("MCP_DEBUG", "False")
        assert get_env_bool(EnvVar.DEBUG) is False

    def test_returns_default_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns default when not set."""
        monkeypatch.delenv("MCP_DEBUG", raising=False)
        assert get_env_bool(EnvVar.DEBUG) is False
        assert get_env_bool(EnvVar.DEBUG, True) is True

    def test_returns_default_for_invalid_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_bool returns default for unrecognized value."""
        monkeypatch.setenv("MCP_DEBUG", "maybe")
        assert get_env_bool(EnvVar.DEBUG) is False
        assert get_env_bool(EnvVar.DEBUG, True) is True


class TestGetEnvList:
    """Tests for get_env_list function."""

    def test_returns_list_from_comma_separated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_list returns list from comma-separated values."""
        monkeypatch.setenv("MCP_CONFIG_PATH", "a,b,c")
        assert get_env_list(EnvVar.CONFIG_PATH) == ["a", "b", "c"]

    def test_strips_whitespace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_list strips whitespace from items."""
        monkeypatch.setenv("MCP_CONFIG_PATH", " a , b , c ")
        assert get_env_list(EnvVar.CONFIG_PATH) == ["a", "b", "c"]

    def test_filters_empty_items(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_list filters out empty items."""
        monkeypatch.setenv("MCP_CONFIG_PATH", "a,,b,  ,c")
        assert get_env_list(EnvVar.CONFIG_PATH) == ["a", "b", "c"]

    def test_returns_empty_list_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_list returns empty list when not set."""
        monkeypatch.delenv("MCP_CONFIG_PATH", raising=False)
        assert get_env_list(EnvVar.CONFIG_PATH) == []

    def test_returns_default_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_list returns default when not set."""
        monkeypatch.delenv("MCP_CONFIG_PATH", raising=False)
        assert get_env_list(EnvVar.CONFIG_PATH, default=["x", "y"]) == ["x", "y"]

    def test_returns_empty_list_for_empty_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_list returns empty list for empty string."""
        monkeypatch.setenv("MCP_CONFIG_PATH", "")
        assert get_env_list(EnvVar.CONFIG_PATH) == []

    def test_returns_empty_list_for_whitespace_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_list returns empty list for whitespace only."""
        monkeypatch.setenv("MCP_CONFIG_PATH", "   ")
        assert get_env_list(EnvVar.CONFIG_PATH) == []

    def test_custom_separator(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_list works with custom separator."""
        monkeypatch.setenv("MCP_CONFIG_PATH", "a:b:c")
        assert get_env_list(EnvVar.CONFIG_PATH, separator=":") == ["a", "b", "c"]

    def test_single_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_env_list works with single value."""
        monkeypatch.setenv("MCP_CONFIG_PATH", "single")
        assert get_env_list(EnvVar.CONFIG_PATH) == ["single"]
