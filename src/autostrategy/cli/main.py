"""CLI entry point for autostrategy."""

from pathlib import Path

import typer

from autostrategy import __version__
from autostrategy.config import init_settings, load_settings
from autostrategy.core.template_registry import TemplateRegistry
from autostrategy.core.workspace import Workspace

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


def _workspace_root_option(workspace_root: str | None) -> Path | None:
    return Path(workspace_root) if workspace_root else None


@strategy_app.command("list")
def strategy_list(
    workspace_root: str | None = typer.Option(
        None, "--workspace-root", help="Workspace root directory."
    ),
) -> None:
    """List all strategies in workspace."""
    workspace = Workspace(root=_workspace_root_option(workspace_root))
    strategies = workspace.list_strategies()
    if not strategies:
        typer.echo("No strategies yet. Use `autostrategy strategy create` to add one.")
        return
    typer.echo(f"{'SLUG':20} {'MARKET':8} {'STATUS':12} NAME")
    for strategy in strategies:
        typer.echo(
            f"{strategy.slug:20} {strategy.market:8} {strategy.status.value:12} {strategy.name}"
        )


@strategy_app.command("create")
def strategy_create(
    name: str = typer.Argument(..., help="Strategy name."),
    template: str | None = typer.Option(None, "--template", help="Template name to use."),
    market: str = typer.Option("A股", "--market", help="Target market."),
    workspace_root: str | None = typer.Option(
        None, "--workspace-root", help="Workspace root directory."
    ),
) -> None:
    """Create a new strategy workspace."""
    if template and template not in TemplateRegistry.list_templates():
        typer.echo(
            f"Template '{template}' not found. "
            f"Available: {', '.join(TemplateRegistry.list_templates())}"
        )
        raise typer.Exit(1)

    workspace = Workspace(root=_workspace_root_option(workspace_root))
    try:
        strategy = workspace.create_strategy(name, market=market, template=template)
        typer.echo(f"Strategy '{strategy.name}' created at {strategy.workspace_dir}")
    except FileExistsError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)


@strategy_app.command("show")
def strategy_show(
    slug: str = typer.Argument(..., help="Strategy slug."),
    workspace_root: str | None = typer.Option(
        None, "--workspace-root", help="Workspace root directory."
    ),
) -> None:
    """Show strategy details."""
    workspace = Workspace(root=_workspace_root_option(workspace_root))
    strategy = workspace.get_strategy(slug)
    if not strategy:
        typer.echo(f"Strategy '{slug}' not found.")
        raise typer.Exit(1)
    typer.echo(f"Name: {strategy.name}")
    typer.echo(f"Slug: {strategy.slug}")
    typer.echo(f"Market: {strategy.market}")
    typer.echo(f"Status: {strategy.status.value}")
    typer.echo(f"Template: {strategy.template or 'none'}")


@strategy_app.command("delete")
def strategy_delete(
    slug: str = typer.Argument(..., help="Strategy slug."),
    workspace_root: str | None = typer.Option(
        None, "--workspace-root", help="Workspace root directory."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a strategy workspace."""
    workspace = Workspace(root=_workspace_root_option(workspace_root))
    strategy = workspace.get_strategy(slug)
    if not strategy:
        typer.echo(f"Strategy '{slug}' not found.")
        raise typer.Exit(1)
    if not yes:
        confirm = typer.confirm(f"Delete strategy '{strategy.name}'?")
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit(0)
    workspace.delete_strategy(slug)
    typer.echo(f"Strategy '{slug}' deleted.")


if __name__ == "__main__":
    app()
