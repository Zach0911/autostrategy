"""Tests for workspace management."""

import pytest

from autostrategy.core.workspace import Workspace


def test_workspace_root(tmp_path):
    ws = Workspace(root=tmp_path)
    assert ws.root == tmp_path
    assert ws.root.exists()


def test_create_strategy(tmp_path):
    ws = Workspace(root=tmp_path)
    strategy = ws.create_strategy("dual-ma", market="A股")
    assert strategy.name == "dual-ma"
    assert (tmp_path / "dual-ma" / "config.yaml").exists()
    assert (tmp_path / "dual-ma" / "STRATEGY_DESIGN.md").exists()


def test_list_strategies(tmp_path):
    ws = Workspace(root=tmp_path)
    ws.create_strategy("s1")
    ws.create_strategy("s2")
    strategies = ws.list_strategies()
    assert len(strategies) == 2


def test_get_strategy(tmp_path):
    ws = Workspace(root=tmp_path)
    created = ws.create_strategy("s1")
    fetched = ws.get_strategy("s1")
    assert fetched is not None
    assert fetched.slug == created.slug


def test_delete_strategy(tmp_path):
    ws = Workspace(root=tmp_path)
    ws.create_strategy("s1")
    ws.delete_strategy("s1")
    assert ws.get_strategy("s1") is None
