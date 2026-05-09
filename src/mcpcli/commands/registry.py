"""Command registry for managing and discovering commands.

Provides a central registry for all CLI commands with lookup by name or alias.
"""

from __future__ import annotations

from typing import Callable

from mcpcli.commands.base import CommandMode, UnifiedCommand


class CommandRegistry:
    """Registry for managing unified commands.

    Supports registration, lookup by name or alias, and filtering by mode.
    """

    def __init__(self) -> None:
        """Initialize an empty command registry."""
        self._commands: dict[str, UnifiedCommand] = {}
        self._aliases: dict[str, str] = {}

    def register(self, command: UnifiedCommand) -> None:
        """Register a command.

        Args:
            command: The command to register.
        """
        self._commands[command.name] = command
        for alias in command.aliases:
            self._aliases[alias] = command.name

    def unregister(self, name: str) -> bool:
        """Unregister a command by name.

        Args:
            name: The command name to unregister.

        Returns:
            True if command was found and removed, False otherwise.
        """
        if name not in self._commands:
            return False

        command = self._commands[name]
        del self._commands[name]

        aliases_to_remove = [
            alias for alias, cmd_name in self._aliases.items()
            if cmd_name == name
        ]
        for alias in aliases_to_remove:
            del self._aliases[alias]

        return True

    def get(self, name: str) -> UnifiedCommand | None:
        """Get a command by name or alias.

        Args:
            name: The command name or alias.

        Returns:
            The command if found, None otherwise.
        """
        if name in self._commands:
            return self._commands[name]

        if name in self._aliases:
            return self._commands.get(self._aliases[name])

        return None

    def get_all(self) -> dict[str, UnifiedCommand]:
        """Get all registered commands (primary names only).

        Returns:
            Dictionary of command name to command.
        """
        return self._commands.copy()

    def get_commands_for_mode(self, mode: CommandMode) -> dict[str, UnifiedCommand]:
        """Get commands that support a specific mode.

        Args:
            mode: The mode to filter by.

        Returns:
            Dictionary of matching command name to command.
        """
        return {
            name: cmd
            for name, cmd in self._commands.items()
            if mode in cmd.modes
        }

    def get_visible_commands(self) -> dict[str, UnifiedCommand]:
        """Get all non-hidden commands.

        Returns:
            Dictionary of visible command name to command.
        """
        return {
            name: cmd
            for name, cmd in self._commands.items()
            if not cmd.hidden
        }

    def get_names(self) -> list[str]:
        """Get all command names (not aliases).

        Returns:
            List of command names.
        """
        return list(self._commands.keys())

    def get_aliases(self) -> dict[str, str]:
        """Get all aliases mapped to their command names.

        Returns:
            Dictionary of alias to command name.
        """
        return self._aliases.copy()

    def has_command(self, name: str) -> bool:
        """Check if a command exists by name or alias.

        Args:
            name: The command name or alias.

        Returns:
            True if command exists, False otherwise.
        """
        return name in self._commands or name in self._aliases

    def clear(self) -> None:
        """Remove all registered commands."""
        self._commands.clear()
        self._aliases.clear()


def command(
    name: str | None = None,
    aliases: list[str] | None = None,
    description: str | None = None,
    modes: CommandMode = CommandMode.ALL,
    hidden: bool = False,
) -> Callable[[type[UnifiedCommand]], type[UnifiedCommand]]:
    """Decorator for defining commands with metadata.

    Args:
        name: Command name (defaults to class name lowercased).
        aliases: Alternative names for the command.
        description: Short description.
        modes: Which modes the command supports.
        hidden: Whether to hide from help.

    Returns:
        Decorator function.
    """
    def decorator(cls: type[UnifiedCommand]) -> type[UnifiedCommand]:
        original_init = cls.__init__

        def new_init(self: UnifiedCommand, *args: object, **kwargs: object) -> None:
            original_init(self, *args, **kwargs)
            if name is not None:
                object.__setattr__(self, "_name", name)
            if aliases is not None:
                object.__setattr__(self, "_aliases", aliases)
            if description is not None:
                object.__setattr__(self, "_description", description)
            object.__setattr__(self, "_modes", modes)
            object.__setattr__(self, "_hidden", hidden)

        cls.__init__ = new_init
        return cls

    return decorator


registry = CommandRegistry()


__all__ = [
    "CommandRegistry",
    "command",
    "registry",
]
