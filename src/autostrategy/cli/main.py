"""CLI entry point for autostrategy."""

from __future__ import annotations

import typer

from autostrategy import __version__
from autostrategy.config import init_settings, load_settings

app = typer.Typer(
    name="autostrategy",
    help="面向个人投资者的本地开源量化策略平台",
    no_args_is_help=True,
    invoke_without_command=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"autostrategy {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """autostrategy CLI."""


config_app = typer.Typer(help="Manage autostrategy configuration.")
app.add_typer(config_app, name="config")


@config_app.command("init")
def config_init() -> None:
    """Initialize user settings directory."""
    settings = init_settings()
    typer.echo("Settings initialized at ~/.autostrategy/settings.yaml")
    typer.echo(f"Default LLM provider: {settings.llm.provider}")


@config_app.command("show")
def config_show() -> None:
    """Show current settings."""
    settings = load_settings()
    typer.echo(f"Version: {settings.version}")
    typer.echo(f"LLM provider: {settings.llm.provider}")
    typer.echo(f"LLM model: {settings.llm.model}")


strategy_app = typer.Typer(help="Manage trading strategies.")
app.add_typer(strategy_app, name="strategy")


@strategy_app.command("list")
def strategy_list() -> None:
    """List all strategies in workspace."""
    typer.echo("No strategies yet. Use `autostrategy strategy create` to add one.")


@strategy_app.command("create")
def strategy_create(
    name: str = typer.Argument(..., help="Strategy name."),
) -> None:
    """Create a new strategy workspace."""
    typer.echo(f"Strategy '{name}' creation will be implemented in Phase 1.")


if __name__ == "__main__":
    app()
