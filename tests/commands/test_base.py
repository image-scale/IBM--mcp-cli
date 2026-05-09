"""Tests for command base classes."""

from __future__ import annotations

from typing import Any

import pytest

from mcpcli.commands.base import (
    CommandMode,
    CommandParameter,
    CommandResult,
    UnifiedCommand,
    CommandGroup,
)


class TestCommandMode:
    """Tests for CommandMode flag enum."""

    def test_chat_mode_exists(self) -> None:
        """CHAT mode is defined."""
        assert hasattr(CommandMode, "CHAT")

    def test_cli_mode_exists(self) -> None:
        """CLI mode is defined."""
        assert hasattr(CommandMode, "CLI")

    def test_interactive_mode_exists(self) -> None:
        """INTERACTIVE mode is defined."""
        assert hasattr(CommandMode, "INTERACTIVE")

    def test_all_mode_exists(self) -> None:
        """ALL mode is defined."""
        assert hasattr(CommandMode, "ALL")

    def test_all_mode_includes_chat(self) -> None:
        """ALL mode includes CHAT."""
        assert CommandMode.CHAT in CommandMode.ALL

    def test_all_mode_includes_cli(self) -> None:
        """ALL mode includes CLI."""
        assert CommandMode.CLI in CommandMode.ALL

    def test_all_mode_includes_interactive(self) -> None:
        """ALL mode includes INTERACTIVE."""
        assert CommandMode.INTERACTIVE in CommandMode.ALL

    def test_modes_can_be_combined(self) -> None:
        """Modes can be combined with bitwise OR."""
        combined = CommandMode.CHAT | CommandMode.CLI
        assert CommandMode.CHAT in combined
        assert CommandMode.CLI in combined
        assert CommandMode.INTERACTIVE not in combined

    def test_mode_membership_check(self) -> None:
        """Can check if a mode is in a combined mode."""
        chat_cli = CommandMode.CHAT | CommandMode.CLI
        assert CommandMode.CHAT in chat_cli
        assert CommandMode.CLI in chat_cli


class TestCommandParameter:
    """Tests for CommandParameter model."""

    def test_parameter_has_name(self) -> None:
        """Parameter has name field."""
        param = CommandParameter(name="test")
        assert param.name == "test"

    def test_parameter_has_param_type(self) -> None:
        """Parameter has param_type field defaulting to str."""
        param = CommandParameter(name="test")
        assert param.param_type is str

    def test_parameter_custom_type(self) -> None:
        """Parameter can have custom type."""
        param = CommandParameter(name="count", param_type=int)
        assert param.param_type is int

    def test_parameter_has_default(self) -> None:
        """Parameter has default field."""
        param = CommandParameter(name="test", default="value")
        assert param.default == "value"

    def test_parameter_default_is_none(self) -> None:
        """Parameter default is None by default."""
        param = CommandParameter(name="test")
        assert param.default is None

    def test_parameter_has_required(self) -> None:
        """Parameter has required field."""
        param = CommandParameter(name="test", required=True)
        assert param.required is True

    def test_parameter_required_defaults_false(self) -> None:
        """Parameter required defaults to False."""
        param = CommandParameter(name="test")
        assert param.required is False

    def test_parameter_has_help(self) -> None:
        """Parameter has help field."""
        param = CommandParameter(name="test", help="Help text")
        assert param.help == "Help text"

    def test_parameter_help_defaults_empty(self) -> None:
        """Parameter help defaults to empty string."""
        param = CommandParameter(name="test")
        assert param.help == ""

    def test_parameter_has_choices(self) -> None:
        """Parameter has choices field."""
        param = CommandParameter(name="format", choices=["json", "text"])
        assert param.choices == ["json", "text"]

    def test_parameter_choices_defaults_none(self) -> None:
        """Parameter choices defaults to None."""
        param = CommandParameter(name="test")
        assert param.choices is None

    def test_parameter_has_is_flag(self) -> None:
        """Parameter has is_flag field."""
        param = CommandParameter(name="verbose", is_flag=True)
        assert param.is_flag is True

    def test_parameter_is_flag_defaults_false(self) -> None:
        """Parameter is_flag defaults to False."""
        param = CommandParameter(name="test")
        assert param.is_flag is False


class TestCommandResult:
    """Tests for CommandResult model."""

    def test_result_has_success(self) -> None:
        """Result has success field."""
        result = CommandResult(success=True)
        assert result.success is True

    def test_result_has_output(self) -> None:
        """Result has output field."""
        result = CommandResult(success=True, output="test output")
        assert result.output == "test output"

    def test_result_output_defaults_none(self) -> None:
        """Result output defaults to None."""
        result = CommandResult(success=True)
        assert result.output is None

    def test_result_has_data(self) -> None:
        """Result has data field."""
        result = CommandResult(success=True, data={"key": "value"})
        assert result.data == {"key": "value"}

    def test_result_data_defaults_none(self) -> None:
        """Result data defaults to None."""
        result = CommandResult(success=True)
        assert result.data is None

    def test_result_has_error(self) -> None:
        """Result has error field."""
        result = CommandResult(success=False, error="Something went wrong")
        assert result.error == "Something went wrong"

    def test_result_error_defaults_none(self) -> None:
        """Result error defaults to None."""
        result = CommandResult(success=True)
        assert result.error is None

    def test_result_has_should_exit(self) -> None:
        """Result has should_exit field."""
        result = CommandResult(success=True, should_exit=True)
        assert result.should_exit is True

    def test_result_should_exit_defaults_false(self) -> None:
        """Result should_exit defaults to False."""
        result = CommandResult(success=True)
        assert result.should_exit is False

    def test_result_has_should_clear(self) -> None:
        """Result has should_clear field."""
        result = CommandResult(success=True, should_clear=True)
        assert result.should_clear is True


class SampleCommand(UnifiedCommand):
    """A concrete command implementation for testing."""

    @property
    def name(self) -> str:
        return "sample"

    @property
    def description(self) -> str:
        return "A sample command"

    async def execute(self, **kwargs: Any) -> CommandResult:
        return CommandResult(success=True, output="sample executed")


class CommandWithParameters(UnifiedCommand):
    """A command with parameters for testing validation."""

    @property
    def name(self) -> str:
        return "parameterized"

    @property
    def description(self) -> str:
        return "A command with parameters"

    @property
    def parameters(self) -> list[CommandParameter]:
        return [
            CommandParameter(name="required_param", required=True),
            CommandParameter(name="choice_param", choices=["a", "b", "c"]),
        ]

    async def execute(self, **kwargs: Any) -> CommandResult:
        return CommandResult(success=True, data=kwargs)


class CommandWithAliases(UnifiedCommand):
    """A command with aliases for testing."""

    @property
    def name(self) -> str:
        return "aliased"

    @property
    def aliases(self) -> list[str]:
        return ["al", "a"]

    @property
    def description(self) -> str:
        return "A command with aliases"

    async def execute(self, **kwargs: Any) -> CommandResult:
        return CommandResult(success=True)


class HiddenCommand(UnifiedCommand):
    """A hidden command for testing."""

    @property
    def name(self) -> str:
        return "hidden"

    @property
    def description(self) -> str:
        return "A hidden command"

    @property
    def hidden(self) -> bool:
        return True

    async def execute(self, **kwargs: Any) -> CommandResult:
        return CommandResult(success=True)


class ChatOnlyCommand(UnifiedCommand):
    """A command that only works in chat mode."""

    @property
    def name(self) -> str:
        return "chatonly"

    @property
    def description(self) -> str:
        return "Chat only command"

    @property
    def modes(self) -> CommandMode:
        return CommandMode.CHAT

    async def execute(self, **kwargs: Any) -> CommandResult:
        return CommandResult(success=True)


class TestUnifiedCommand:
    """Tests for UnifiedCommand abstract base class."""

    def test_command_has_name(self) -> None:
        """Command has name property."""
        cmd = SampleCommand()
        assert cmd.name == "sample"

    def test_command_has_description(self) -> None:
        """Command has description property."""
        cmd = SampleCommand()
        assert cmd.description == "A sample command"

    def test_command_has_aliases_default_empty(self) -> None:
        """Command aliases default to empty list."""
        cmd = SampleCommand()
        assert cmd.aliases == []

    def test_command_with_aliases(self) -> None:
        """Command can have aliases."""
        cmd = CommandWithAliases()
        assert cmd.aliases == ["al", "a"]

    def test_command_has_modes_default_all(self) -> None:
        """Command modes default to ALL."""
        cmd = SampleCommand()
        assert cmd.modes == CommandMode.ALL

    def test_command_with_specific_mode(self) -> None:
        """Command can specify specific modes."""
        cmd = ChatOnlyCommand()
        assert cmd.modes == CommandMode.CHAT

    def test_command_has_parameters_default_empty(self) -> None:
        """Command parameters default to empty list."""
        cmd = SampleCommand()
        assert cmd.parameters == []

    def test_command_with_parameters(self) -> None:
        """Command can have parameters."""
        cmd = CommandWithParameters()
        assert len(cmd.parameters) == 2

    def test_command_hidden_default_false(self) -> None:
        """Command hidden defaults to False."""
        cmd = SampleCommand()
        assert cmd.hidden is False

    def test_command_hidden_true(self) -> None:
        """Command can be hidden."""
        cmd = HiddenCommand()
        assert cmd.hidden is True

    def test_command_requires_context_default_true(self) -> None:
        """Command requires_context defaults to True."""
        cmd = SampleCommand()
        assert cmd.requires_context is True

    def test_command_help_text_defaults_to_description(self) -> None:
        """Command help_text defaults to description."""
        cmd = SampleCommand()
        assert cmd.help_text == cmd.description

    @pytest.mark.asyncio
    async def test_command_execute(self) -> None:
        """Command can execute."""
        cmd = SampleCommand()
        result = await cmd.execute()
        assert result.success is True
        assert result.output == "sample executed"


class TestUnifiedCommandValidation:
    """Tests for UnifiedCommand parameter validation."""

    def test_validate_missing_required(self) -> None:
        """Validates missing required parameters."""
        cmd = CommandWithParameters()
        error = cmd.validate_parameters()
        assert error is not None
        assert "required_param" in error

    def test_validate_required_provided(self) -> None:
        """Passes when required parameters provided."""
        cmd = CommandWithParameters()
        error = cmd.validate_parameters(required_param="value")
        assert error is None

    def test_validate_invalid_choice(self) -> None:
        """Validates invalid choices."""
        cmd = CommandWithParameters()
        error = cmd.validate_parameters(required_param="value", choice_param="invalid")
        assert error is not None
        assert "choice_param" in error

    def test_validate_valid_choice(self) -> None:
        """Passes when choice is valid."""
        cmd = CommandWithParameters()
        error = cmd.validate_parameters(required_param="value", choice_param="a")
        assert error is None


class TestUnifiedCommandFormatOutput:
    """Tests for UnifiedCommand format_output method."""

    def test_format_output_with_output(self) -> None:
        """Format returns output when present."""
        cmd = SampleCommand()
        result = CommandResult(success=True, output="test output")
        formatted = cmd.format_output(result, CommandMode.CLI)
        assert formatted == "test output"

    def test_format_output_with_error(self) -> None:
        """Format returns error message when output is None."""
        cmd = SampleCommand()
        result = CommandResult(success=False, error="test error")
        formatted = cmd.format_output(result, CommandMode.CLI)
        assert formatted == "Error: test error"

    def test_format_output_empty(self) -> None:
        """Format returns empty string when no output or error."""
        cmd = SampleCommand()
        result = CommandResult(success=True)
        formatted = cmd.format_output(result, CommandMode.CLI)
        assert formatted == ""


class TestCommandGroup:
    """Tests for CommandGroup class."""

    def test_group_has_empty_subcommands(self) -> None:
        """Group starts with empty subcommands."""

        class TestGroup(CommandGroup):
            @property
            def name(self) -> str:
                return "group"

            @property
            def description(self) -> str:
                return "Test group"

        group = TestGroup()
        assert group.subcommands == {}

    def test_add_subcommand(self) -> None:
        """Can add subcommand to group."""

        class TestGroup(CommandGroup):
            @property
            def name(self) -> str:
                return "group"

            @property
            def description(self) -> str:
                return "Test group"

        group = TestGroup()
        group.add_subcommand(SampleCommand())
        assert "sample" in group.subcommands

    def test_add_subcommand_with_aliases(self) -> None:
        """Subcommand aliases are registered."""

        class TestGroup(CommandGroup):
            @property
            def name(self) -> str:
                return "group"

            @property
            def description(self) -> str:
                return "Test group"

        group = TestGroup()
        group.add_subcommand(CommandWithAliases())
        assert "aliased" in group.subcommands
        assert "al" in group.subcommands
        assert "a" in group.subcommands

    def test_get_subcommand(self) -> None:
        """Can get subcommand by name."""

        class TestGroup(CommandGroup):
            @property
            def name(self) -> str:
                return "group"

            @property
            def description(self) -> str:
                return "Test group"

        group = TestGroup()
        cmd = SampleCommand()
        group.add_subcommand(cmd)
        assert group.get_subcommand("sample") is cmd

    def test_get_subcommand_not_found(self) -> None:
        """Returns None for unknown subcommand."""

        class TestGroup(CommandGroup):
            @property
            def name(self) -> str:
                return "group"

            @property
            def description(self) -> str:
                return "Test group"

        group = TestGroup()
        assert group.get_subcommand("nonexistent") is None

    @pytest.mark.asyncio
    async def test_execute_without_subcommand_lists_commands(self) -> None:
        """Execute without subcommand lists available commands."""

        class TestGroup(CommandGroup):
            @property
            def name(self) -> str:
                return "group"

            @property
            def description(self) -> str:
                return "Test group"

        group = TestGroup()
        group.add_subcommand(SampleCommand())
        result = await group.execute()
        assert result.success is True
        assert "sample" in result.output
        assert "A sample command" in result.output

    @pytest.mark.asyncio
    async def test_execute_with_subcommand(self) -> None:
        """Execute runs the specified subcommand."""

        class TestGroup(CommandGroup):
            @property
            def name(self) -> str:
                return "group"

            @property
            def description(self) -> str:
                return "Test group"

        group = TestGroup()
        group.add_subcommand(SampleCommand())
        result = await group.execute(subcommand="sample")
        assert result.success is True
        assert result.output == "sample executed"

    @pytest.mark.asyncio
    async def test_execute_with_unknown_subcommand(self) -> None:
        """Execute fails with unknown subcommand."""

        class TestGroup(CommandGroup):
            @property
            def name(self) -> str:
                return "group"

            @property
            def description(self) -> str:
                return "Test group"

        group = TestGroup()
        result = await group.execute(subcommand="unknown")
        assert result.success is False
        assert "unknown" in result.error
