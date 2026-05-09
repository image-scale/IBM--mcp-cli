"""Tests for command registry."""

from __future__ import annotations

from typing import Any

import pytest

from mcpcli.commands.base import CommandMode, CommandParameter, CommandResult, UnifiedCommand
from mcpcli.commands.registry import CommandRegistry, registry


class MockCommand(UnifiedCommand):
    """A mock command for testing."""

    def __init__(
        self,
        name: str = "mock",
        aliases: list[str] | None = None,
        description: str = "Mock command",
        modes: CommandMode = CommandMode.ALL,
        hidden: bool = False,
    ) -> None:
        self._name = name
        self._aliases = aliases or []
        self._description = description
        self._modes = modes
        self._hidden = hidden

    @property
    def name(self) -> str:
        return self._name

    @property
    def aliases(self) -> list[str]:
        return self._aliases

    @property
    def description(self) -> str:
        return self._description

    @property
    def modes(self) -> CommandMode:
        return self._modes

    @property
    def hidden(self) -> bool:
        return self._hidden

    async def execute(self, **kwargs: Any) -> CommandResult:
        return CommandResult(success=True, output=f"{self._name} executed")


class TestCommandRegistry:
    """Tests for CommandRegistry class."""

    def test_registry_starts_empty(self) -> None:
        """Registry starts with no commands."""
        reg = CommandRegistry()
        assert reg.get_names() == []

    def test_register_command(self) -> None:
        """Can register a command."""
        reg = CommandRegistry()
        cmd = MockCommand()
        reg.register(cmd)
        assert reg.has_command("mock")

    def test_get_command_by_name(self) -> None:
        """Can get command by name."""
        reg = CommandRegistry()
        cmd = MockCommand()
        reg.register(cmd)
        assert reg.get("mock") is cmd

    def test_get_command_by_alias(self) -> None:
        """Can get command by alias."""
        reg = CommandRegistry()
        cmd = MockCommand(name="test", aliases=["t", "tst"])
        reg.register(cmd)
        assert reg.get("t") is cmd
        assert reg.get("tst") is cmd

    def test_get_nonexistent_command(self) -> None:
        """Returns None for nonexistent command."""
        reg = CommandRegistry()
        assert reg.get("nonexistent") is None

    def test_has_command_by_name(self) -> None:
        """has_command works with name."""
        reg = CommandRegistry()
        cmd = MockCommand()
        reg.register(cmd)
        assert reg.has_command("mock") is True
        assert reg.has_command("nonexistent") is False

    def test_has_command_by_alias(self) -> None:
        """has_command works with alias."""
        reg = CommandRegistry()
        cmd = MockCommand(name="test", aliases=["t"])
        reg.register(cmd)
        assert reg.has_command("t") is True

    def test_get_all_commands(self) -> None:
        """get_all returns all registered commands."""
        reg = CommandRegistry()
        cmd1 = MockCommand(name="cmd1")
        cmd2 = MockCommand(name="cmd2")
        reg.register(cmd1)
        reg.register(cmd2)
        all_cmds = reg.get_all()
        assert len(all_cmds) == 2
        assert "cmd1" in all_cmds
        assert "cmd2" in all_cmds

    def test_get_all_returns_copy(self) -> None:
        """get_all returns a copy, not the internal dict."""
        reg = CommandRegistry()
        cmd = MockCommand()
        reg.register(cmd)
        all_cmds = reg.get_all()
        all_cmds.clear()
        assert reg.has_command("mock")

    def test_get_names(self) -> None:
        """get_names returns command names only, not aliases."""
        reg = CommandRegistry()
        cmd = MockCommand(name="test", aliases=["t"])
        reg.register(cmd)
        names = reg.get_names()
        assert names == ["test"]

    def test_get_aliases(self) -> None:
        """get_aliases returns mapping of aliases to names."""
        reg = CommandRegistry()
        cmd = MockCommand(name="test", aliases=["t", "tst"])
        reg.register(cmd)
        aliases = reg.get_aliases()
        assert aliases == {"t": "test", "tst": "test"}

    def test_unregister_command(self) -> None:
        """Can unregister a command."""
        reg = CommandRegistry()
        cmd = MockCommand()
        reg.register(cmd)
        result = reg.unregister("mock")
        assert result is True
        assert reg.has_command("mock") is False

    def test_unregister_removes_aliases(self) -> None:
        """Unregistering removes aliases too."""
        reg = CommandRegistry()
        cmd = MockCommand(name="test", aliases=["t"])
        reg.register(cmd)
        reg.unregister("test")
        assert reg.has_command("t") is False

    def test_unregister_nonexistent(self) -> None:
        """Unregistering nonexistent command returns False."""
        reg = CommandRegistry()
        result = reg.unregister("nonexistent")
        assert result is False

    def test_clear(self) -> None:
        """clear removes all commands."""
        reg = CommandRegistry()
        reg.register(MockCommand(name="cmd1"))
        reg.register(MockCommand(name="cmd2", aliases=["c2"]))
        reg.clear()
        assert reg.get_names() == []
        assert reg.get_aliases() == {}


class TestRegistryModeFiltering:
    """Tests for filtering commands by mode."""

    def test_get_commands_for_mode_all(self) -> None:
        """Commands with ALL mode appear for any mode."""
        reg = CommandRegistry()
        cmd = MockCommand(modes=CommandMode.ALL)
        reg.register(cmd)
        chat_cmds = reg.get_commands_for_mode(CommandMode.CHAT)
        cli_cmds = reg.get_commands_for_mode(CommandMode.CLI)
        interactive_cmds = reg.get_commands_for_mode(CommandMode.INTERACTIVE)
        assert "mock" in chat_cmds
        assert "mock" in cli_cmds
        assert "mock" in interactive_cmds

    def test_get_commands_for_mode_specific(self) -> None:
        """Commands with specific mode only appear for that mode."""
        reg = CommandRegistry()
        cmd = MockCommand(modes=CommandMode.CHAT)
        reg.register(cmd)
        chat_cmds = reg.get_commands_for_mode(CommandMode.CHAT)
        cli_cmds = reg.get_commands_for_mode(CommandMode.CLI)
        assert "mock" in chat_cmds
        assert "mock" not in cli_cmds

    def test_get_commands_for_mode_combined(self) -> None:
        """Commands with combined modes appear for included modes."""
        reg = CommandRegistry()
        cmd = MockCommand(modes=CommandMode.CHAT | CommandMode.CLI)
        reg.register(cmd)
        chat_cmds = reg.get_commands_for_mode(CommandMode.CHAT)
        cli_cmds = reg.get_commands_for_mode(CommandMode.CLI)
        interactive_cmds = reg.get_commands_for_mode(CommandMode.INTERACTIVE)
        assert "mock" in chat_cmds
        assert "mock" in cli_cmds
        assert "mock" not in interactive_cmds


class TestRegistryVisibility:
    """Tests for filtering hidden commands."""

    def test_get_visible_commands(self) -> None:
        """get_visible_commands excludes hidden commands."""
        reg = CommandRegistry()
        visible = MockCommand(name="visible")
        hidden = MockCommand(name="hidden", hidden=True)
        reg.register(visible)
        reg.register(hidden)
        visible_cmds = reg.get_visible_commands()
        assert "visible" in visible_cmds
        assert "hidden" not in visible_cmds

    def test_get_all_includes_hidden(self) -> None:
        """get_all includes hidden commands."""
        reg = CommandRegistry()
        visible = MockCommand(name="visible")
        hidden = MockCommand(name="hidden", hidden=True)
        reg.register(visible)
        reg.register(hidden)
        all_cmds = reg.get_all()
        assert "visible" in all_cmds
        assert "hidden" in all_cmds


class TestGlobalRegistry:
    """Tests for the global registry instance."""

    def test_global_registry_exists(self) -> None:
        """Global registry instance exists."""
        assert registry is not None
        assert isinstance(registry, CommandRegistry)

    def test_global_registry_is_command_registry(self) -> None:
        """Global registry is a CommandRegistry instance."""
        assert isinstance(registry, CommandRegistry)


