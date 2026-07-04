"""Workspace management for strategies."""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from autostrategy.core.strategy import Strategy, StrategyStatus


DEFAULT_WORKSPACE_ROOT = Path.home() / ".autostrategy" / "strategies"


class Workspace:
    """Manages a directory of strategy workspaces."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or DEFAULT_WORKSPACE_ROOT
        self.root.mkdir(parents=True, exist_ok=True)

    def _strategy_dir(self, slug: str) -> Path:
        return self.root / slug

    def create_strategy(
        self,
        name: str,
        description: str = "",
        market: str = "A股",
        template: str | None = None,
        tags: list[str] | None = None,
    ) -> Strategy:
        """Create a new strategy workspace."""
        strategy = Strategy(
            name=name,
            description=description,
            market=market,
            template=template,
            tags=tags or [],
        )
        strategy_dir = self._strategy_dir(strategy.slug)
        if strategy_dir.exists():
            raise FileExistsError(f"Strategy '{name}' ({strategy.slug}) already exists.")

        strategy_dir.mkdir(parents=True)
        self._write_strategy_meta(strategy_dir, strategy)
        self._write_default_files(strategy_dir)
        return strategy

    def _write_strategy_meta(self, strategy_dir: Path, strategy: Strategy) -> None:
        meta_path = strategy_dir / "strategy.yaml"
        with open(meta_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(strategy.model_dump(mode="json"), f, allow_unicode=True)

    def _write_default_files(self, strategy_dir: Path) -> None:
        config_path = strategy_dir / "config.yaml"
        config_path.write_text(
            "# Strategy configuration\n"
            "market: A股\n"
            "symbols: []\n"
            "period:\n"
            "  start: 2022-01-01\n"
            "  end: 2024-01-01\n",
            encoding="utf-8",
        )
        design_path = strategy_dir / "STRATEGY_DESIGN.md"
        design_path.write_text(
            f"# {strategy_dir.name}\n\n"
            "## 策略概述\n\n"
            "待补充...\n\n"
            "## 买入条件\n\n"
            "- 待补充\n\n"
            "## 卖出条件\n\n"
            "- 待补充\n",
            encoding="utf-8",
        )

    def list_strategies(self) -> list[Strategy]:
        """List all strategies in the workspace."""
        strategies = []
        for entry in sorted(self.root.iterdir()):
            if entry.is_dir():
                strategy = self._load_strategy(entry)
                if strategy:
                    strategies.append(strategy)
        return strategies

    def get_strategy(self, slug: str) -> Strategy | None:
        """Get a strategy by slug."""
        strategy_dir = self._strategy_dir(slug)
        if not strategy_dir.exists():
            return None
        return self._load_strategy(strategy_dir)

    def _load_strategy(self, strategy_dir: Path) -> Strategy | None:
        meta_path = strategy_dir / "strategy.yaml"
        if not meta_path.exists():
            return None
        with open(meta_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Strategy(**data)

    def delete_strategy(self, slug: str) -> None:
        """Delete a strategy workspace."""
        strategy_dir = self._strategy_dir(slug)
        if strategy_dir.exists():
            shutil.rmtree(strategy_dir)

    def update_strategy_status(self, slug: str, status: StrategyStatus) -> Strategy:
        """Update the status of a strategy."""
        strategy = self.get_strategy(slug)
        if not strategy:
            raise FileNotFoundError(f"Strategy '{slug}' not found.")
        strategy.status = status
        strategy_dir = self._strategy_dir(slug)
        self._write_strategy_meta(strategy_dir, strategy)
        return strategy
