"""Entry point for the MCP CLI."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import typer

from mcpcli.config.defaults import (
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    DEFAULT_THEME,
)

__version__ = "0.1.0"

app = typer.Typer(
    add_completion=False,
    help="MCP CLI - Model Context Protocol Command Line Interface",
)


class ContextState:
    """Shared state for CLI commands."""

    def __init__(self) -> None:
        self.config_file: str = "server_config.json"
        self.provider: str = DEFAULT_PROVIDER
        self.model: str = DEFAULT_MODEL
        self.theme: str = DEFAULT_THEME
        self.quiet: bool = False
        self.verbose: bool = False
        self.api_base: str | None = None
        self.api_key: str | None = None


state = ContextState()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    config_file: str = typer.Option(
        "server_config.json",
        "--config-file",
        "-c",
        help="Configuration file path",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        "-p",
        help="LLM provider name",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="Model name",
    ),
    api_base: str | None = typer.Option(
        None,
        "--api-base",
        help="API base URL",
    ),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        help="API key",
    ),
    quiet: bool = typer.Option(
        False,
        "-q",
        "--quiet",
        help="Suppress most output",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Enable verbose output",
    ),
    theme: str = typer.Option(
        "default",
        "--theme",
        help="UI theme",
    ),
) -> None:
    """MCP CLI - If no subcommand is given, show help."""
    state.config_file = config_file
    state.provider = provider or DEFAULT_PROVIDER
    state.model = model or DEFAULT_MODEL
    state.theme = theme
    state.quiet = quiet
    state.verbose = verbose
    state.api_base = api_base
    state.api_key = api_key

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command("version")
def version_command() -> None:
    """Show version information."""
    typer.echo(f"mcpcli version {__version__}")
    typer.echo(f"Python {sys.version}")


@app.command("config")
def config_command(
    show_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all configuration values",
    ),
) -> None:
    """Show current configuration."""
    typer.echo(f"Configuration file: {state.config_file}")
    typer.echo(f"Provider: {state.provider}")
    typer.echo(f"Model: {state.model}")
    typer.echo(f"Theme: {state.theme}")

    if show_all:
        typer.echo(f"Quiet mode: {state.quiet}")
        typer.echo(f"Verbose mode: {state.verbose}")
        if state.api_base:
            typer.echo(f"API base: {state.api_base}")


@app.command("servers")
def servers_command(
    detailed: bool = typer.Option(
        False,
        "--detailed",
        "-d",
        help="Show detailed server information",
    ),
) -> None:
    """List configured MCP servers."""
    config_path = Path(state.config_file)

    if not config_path.exists():
        typer.echo(f"Configuration file not found: {config_path}")
        raise typer.Exit(1)

    try:
        import json

        with open(config_path) as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})
        if not servers:
            typer.echo("No servers configured")
            return

        typer.echo(f"Found {len(servers)} server(s):")
        for name, server_config in servers.items():
            if detailed:
                typer.echo(f"\n  {name}:")
                if "command" in server_config:
                    typer.echo(f"    command: {server_config['command']}")
                if "args" in server_config:
                    typer.echo(f"    args: {server_config['args']}")
                if "url" in server_config:
                    typer.echo(f"    url: {server_config['url']}")
            else:
                typer.echo(f"  - {name}")

    except json.JSONDecodeError:
        typer.echo(f"Invalid JSON in configuration file: {config_path}")
        raise typer.Exit(1)


@app.command("providers")
def providers_command() -> None:
    """List available LLM providers."""
    providers = ["openai", "anthropic", "groq", "ollama", "deepseek"]

    typer.echo("Available providers:")
    for provider in providers:
        marker = "*" if provider == state.provider else " "
        typer.echo(f"  {marker} {provider}")

    typer.echo(f"\nCurrent provider: {state.provider}")
    typer.echo(f"Current model: {state.model}")


def get_app() -> typer.Typer:
    """Get the Typer app instance."""
    return app


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
