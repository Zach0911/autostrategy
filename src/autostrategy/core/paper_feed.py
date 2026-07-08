"""Local deterministic feed for replay-first paper runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

_BAR_FIELDS = ("at", "symbol", "open", "high", "low", "close", "volume")


def load_paper_feed(
    strategy_dir: Path, config: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    feed_config = _feed_config(config)
    if not feed_config:
        return [], None

    path_value = feed_config.get("path") or feed_config.get("feed_path")
    if not path_value:
        return [], None

    feed_path = _resolve_feed_path(strategy_dir, str(path_value))
    rows = _read_feed_rows(feed_path)
    rows = _filter_rows(rows, feed_config)
    symbols = sorted({str(row["symbol"]) for row in rows if row.get("symbol")})
    meta = {
        "source": str(feed_path),
        "format": feed_path.suffix.lstrip(".").lower(),
        "bar_count": len(rows),
        "symbols": symbols,
        "symbol_count": len(symbols),
        "start": rows[0]["at"] if rows else feed_config.get("start"),
        "end": rows[-1]["at"] if rows else feed_config.get("end"),
    }
    return rows, meta


def _feed_config(config: dict[str, Any]) -> dict[str, Any]:
    paper_feed = config.get("paper_feed")
    if isinstance(paper_feed, dict):
        return paper_feed
    if config.get("feed_path"):
        return {
            "path": config.get("feed_path"),
            "start": config.get("feed_start"),
            "end": config.get("feed_end"),
            "symbols": config.get("feed_symbols", config.get("symbols")),
        }
    return {}


def _resolve_feed_path(strategy_dir: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return strategy_dir / path


def _read_feed_rows(feed_path: Path) -> list[dict[str, Any]]:
    suffix = feed_path.suffix.lower()
    if suffix == ".csv":
        with open(feed_path, newline="", encoding="utf-8") as file:
            return [_normalize_row(row) for row in csv.DictReader(file)]
    if suffix in {".jsonl", ".ndjson"}:
        rows = []
        with open(feed_path, encoding="utf-8") as file:
            for line in file:
                stripped = line.strip()
                if stripped:
                    rows.append(_normalize_row(json.loads(stripped)))
        return rows
    if suffix == ".json":
        with open(feed_path, encoding="utf-8") as file:
            payload = json.load(file)
        rows = payload if isinstance(payload, list) else payload.get("bars", [])
        return [_normalize_row(row) for row in rows]
    raise ValueError(f"Unsupported paper feed format: {feed_path.suffix}")


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    at = row.get("at", row.get("timestamp", row.get("date")))
    normalized = {
        "type": "bar",
        "at": str(at),
        "symbol": str(row.get("symbol", "")),
    }
    for field in _BAR_FIELDS[2:]:
        normalized[field] = _number(row.get(field, 0))
    return normalized


def _filter_rows(rows: list[dict[str, Any]], feed_config: dict[str, Any]) -> list[dict[str, Any]]:
    symbols = _symbols(feed_config.get("symbols"))
    start = str(feed_config.get("start")) if feed_config.get("start") else None
    end = str(feed_config.get("end")) if feed_config.get("end") else None
    filtered = []
    for row in rows:
        if symbols and row["symbol"] not in symbols:
            continue
        if start and row["at"] < start:
            continue
        if end and row["at"] > end:
            continue
        filtered.append(row)
    return sorted(filtered, key=lambda row: (row["at"], row["symbol"]))


def _symbols(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        result = set()
        for item in value:
            if isinstance(item, dict):
                symbol = item.get("symbol") or item.get("code")
            else:
                symbol = item
            if symbol:
                result.add(str(symbol))
        return result
    return set()


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
