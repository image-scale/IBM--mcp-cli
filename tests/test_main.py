"""Tests for main CLI entry point."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from mcpcli.main import app, state, get_app, __version__


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def reset_state() -> None:
    """Reset shared state before each test."""
    state.config_file = "server_config.json"
    state.provider = "openai"
    state.model = "gpt-4o-mini"
    state.theme = "default"
    state.quiet = False
    state.verbose = False
    state.api_base = None
    state.api_key = None


class TestTyperApp:
    """Tests for Typer app setup."""

    def test_app_exists(self) -> None:
        """App is created."""
        assert app is not None

    def test_app_is_typer(self) -> None:
        """App is a Typer instance."""
        import typer

        assert isinstance(app, typer.Typer)

    def test_get_app_returns_app(self) -> None:
        """get_app returns the app instance."""
        assert get_app() is app


class TestMainCallback:
    """Tests for main callback (no subcommand)."""

    def test_no_subcommand_shows_help(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """No subcommand shows help."""
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "MCP CLI" in result.output

    def test_help_flag(self, runner: CliRunner) -> None:
        """--help shows usage."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "--config-file" in result.output
        assert "--provider" in result.output
        assert "--model" in result.output

    def test_config_file_option(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """--config-file sets config file."""
        result = runner.invoke(app, ["--config-file", "custom.json", "version"])
        assert result.exit_code == 0
        assert state.config_file == "custom.json"

    def test_provider_option(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """--provider sets provider."""
        result = runner.invoke(app, ["--provider", "anthropic", "version"])
        assert result.exit_code == 0
        assert state.provider == "anthropic"

    def test_model_option(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """--model sets model."""
        result = runner.invoke(app, ["--model", "claude-3", "version"])
        assert result.exit_code == 0
        assert state.model == "claude-3"

    def test_quiet_option(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """--quiet sets quiet mode."""
        result = runner.invoke(app, ["--quiet", "version"])
        assert result.exit_code == 0
        assert state.quiet is True

    def test_verbose_option(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """--verbose sets verbose mode."""
        result = runner.invoke(app, ["--verbose", "version"])
        assert result.exit_code == 0
        assert state.verbose is True


class TestVersionCommand:
    """Tests for version command."""

    def test_version_shows_version(self, runner: CliRunner) -> None:
        """version shows version info."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_version_shows_python(self, runner: CliRunner) -> None:
        """version shows Python version."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Python" in result.output


class TestConfigCommand:
    """Tests for config command."""

    def test_config_shows_settings(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """config shows current settings."""
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Provider:" in result.output
        assert "Model:" in result.output

    def test_config_all_shows_more(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """config --all shows additional settings."""
        result = runner.invoke(app, ["config", "--all"])
        assert result.exit_code == 0
        assert "Quiet mode:" in result.output
        assert "Verbose mode:" in result.output


class TestServersCommand:
    """Tests for servers command."""

    def test_servers_missing_config(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """servers fails with missing config."""
        state.config_file = "nonexistent.json"
        result = runner.invoke(app, ["--config-file", "nonexistent.json", "servers"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_servers_empty_config(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """servers shows no servers when empty."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({}, f)
            config_file = f.name

        result = runner.invoke(app, ["--config-file", config_file, "servers"])
        assert result.exit_code == 0
        assert "No servers configured" in result.output

        Path(config_file).unlink()

    def test_servers_lists_servers(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """servers lists configured servers."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({
                "mcpServers": {
                    "test-server": {"command": "node", "args": ["server.js"]},
                }
            }, f)
            config_file = f.name

        result = runner.invoke(app, ["--config-file", config_file, "servers"])
        assert result.exit_code == 0
        assert "test-server" in result.output

        Path(config_file).unlink()

    def test_servers_detailed(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """servers --detailed shows more info."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({
                "mcpServers": {
                    "test-server": {"command": "node", "args": ["server.js"]},
                }
            }, f)
            config_file = f.name

        result = runner.invoke(app, ["--config-file", config_file, "servers", "--detailed"])
        assert result.exit_code == 0
        assert "command:" in result.output
        assert "node" in result.output

        Path(config_file).unlink()

    def test_servers_invalid_json(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """servers fails with invalid JSON."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("invalid json")
            config_file = f.name

        result = runner.invoke(app, ["--config-file", config_file, "servers"])
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output

        Path(config_file).unlink()


class TestProvidersCommand:
    """Tests for providers command."""

    def test_providers_lists_providers(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """providers lists available providers."""
        result = runner.invoke(app, ["providers"])
        assert result.exit_code == 0
        assert "openai" in result.output
        assert "anthropic" in result.output

    def test_providers_shows_current(
        self, runner: CliRunner, reset_state: None
    ) -> None:
        """providers shows current provider."""
        result = runner.invoke(app, ["--provider", "anthropic", "providers"])
        assert result.exit_code == 0
        assert "Current provider: anthropic" in result.output
