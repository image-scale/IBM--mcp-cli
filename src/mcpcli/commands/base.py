"""Base command interface for unified command system.

Provides a single command abstraction that works across:
- Chat mode (slash commands like /servers)
- CLI mode (typer subcommands like `mcpcli servers`)
- Interactive mode (shell commands)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Flag, auto
from typing import Any

from pydantic import BaseModel, Field


class CommandMode(Flag):
    """Flags indicating which modes a command supports."""

    CHAT = auto()
    CLI = auto()
    INTERACTIVE = auto()
    ALL = CHAT | CLI | INTERACTIVE


class CommandParameter(BaseModel):
    """Definition of a command parameter."""

    name: str = Field(description="Parameter name")
    param_type: type = Field(default=str, description="Parameter type")
    default: Any = Field(default=None, description="Default value")
    required: bool = Field(default=False, description="Whether parameter is required")
    help: str = Field(default="", description="Help text for parameter")
    choices: list[Any] | None = Field(default=None, description="Valid choices")
    is_flag: bool = Field(default=False, description="Whether this is a boolean flag")

    model_config = {
        "frozen": False,
        "arbitrary_types_allowed": True,
    }


class CommandResult(BaseModel):
    """Result from command execution."""

    success: bool = Field(description="Whether the command succeeded")
    output: str | None = Field(default=None, description="Output text")
    data: Any = Field(default=None, description="Structured data result")
    error: str | None = Field(default=None, description="Error message")
    should_exit: bool = Field(default=False, description="Whether to exit after command")
    should_clear: bool = Field(default=False, description="Whether to clear screen")

    model_config = {"frozen": False, "arbitrary_types_allowed": True}


class UnifiedCommand(ABC):
    """Base class for all unified commands.

    Commands implement this interface once and work in all modes.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The primary command name (e.g., 'servers')."""
        pass

    @property
    def aliases(self) -> list[str]:
        """Alternative names for the command."""
        return []

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what the command does."""
        pass

    @property
    def help_text(self) -> str:
        """Extended help text with usage examples."""
        return self.description

    @property
    def modes(self) -> CommandMode:
        """Which modes this command supports."""
        return CommandMode.ALL

    @property
    def parameters(self) -> list[CommandParameter]:
        """Parameters this command accepts."""
        return []

    @property
    def hidden(self) -> bool:
        """Whether this command should be hidden from help."""
        return False

    @property
    def requires_context(self) -> bool:
        """Whether this command needs an active context (tool manager, etc)."""
        return True

    @abstractmethod
    async def execute(self, **kwargs: Any) -> CommandResult:
        """Execute the command with the given parameters.

        Args:
            **kwargs: Parameters passed to the command.

        Returns:
            CommandResult indicating success/failure and any output.
        """
        pass

    def format_output(self, result: CommandResult, mode: CommandMode) -> str:
        """Format the command output for a specific mode.

        Can be overridden for mode-specific formatting.
        """
        if result.output:
            return result.output
        if result.error:
            return f"Error: {result.error}"
        return ""

    def validate_parameters(self, **kwargs: Any) -> str | None:
        """Validate parameters before execution.

        Returns:
            Error message if validation fails, None if valid.
        """
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                return f"Missing required parameter: {param.name}"

            if param.name in kwargs and param.choices:
                if kwargs[param.name] not in param.choices:
                    return f"Invalid choice for {param.name}. Must be one of: {param.choices}"

        return None


class CommandGroup(UnifiedCommand):
    """A command that contains subcommands (e.g., 'tools list', 'tools call')."""

    def __init__(self) -> None:
        super().__init__()
        self._subcommands: dict[str, UnifiedCommand] = {}

    @property
    def subcommands(self) -> dict[str, UnifiedCommand]:
        """Get all registered subcommands."""
        return self._subcommands

    def add_subcommand(self, command: UnifiedCommand) -> None:
        """Add a subcommand to this group."""
        self._subcommands[command.name] = command
        for alias in command.aliases:
            self._subcommands[alias] = command

    def get_subcommand(self, name: str) -> UnifiedCommand | None:
        """Get a subcommand by name or alias."""
        return self._subcommands.get(name)

    async def execute(
        self,
        subcommand: str | None = None,
        **kwargs: Any,
    ) -> CommandResult:
        """Execute a subcommand or the default action."""
        if not subcommand:
            commands_list = "\n".join(
                f"  {name}: {cmd.description}"
                for name, cmd in self._subcommands.items()
                if name == cmd.name
            )
            return CommandResult(
                success=True,
                output=f"Available {self.name} commands:\n{commands_list}",
            )

        if subcommand not in self._subcommands:
            return CommandResult(
                success=False,
                error=f"Unknown {self.name} subcommand: {subcommand}",
            )

        return await self._subcommands[subcommand].execute(**kwargs)


__all__ = [
    "CommandMode",
    "CommandParameter",
    "CommandResult",
    "UnifiedCommand",
    "CommandGroup",
]
