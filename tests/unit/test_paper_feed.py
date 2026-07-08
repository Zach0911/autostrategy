"""Tests for local paper replay feed loading."""

from autostrategy.core.paper_feed import load_paper_feed


def test_load_paper_feed_filters_csv_rows(tmp_path):
    feed_path = tmp_path / "data.csv"
    feed_path.write_text(
        "at,symbol,open,high,low,close,volume\n"
        "2024-01-01,000001.SZ,10,11,9,10.5,1000\n"
        "2024-01-02,000001.SZ,10.5,12,10,11,1200\n"
        "2024-01-02,000002.SZ,20,21,19,20.5,900\n",
        encoding="utf-8",
    )

    rows, meta = load_paper_feed(
        tmp_path,
        {
            "paper_feed": {
                "path": "data.csv",
                "symbols": ["000001.SZ"],
                "start": "2024-01-02",
            }
        },
    )

    assert rows == [
        {
            "type": "bar",
            "at": "2024-01-02",
            "symbol": "000001.SZ",
            "open": 10.5,
            "high": 12.0,
            "low": 10.0,
            "close": 11.0,
            "volume": 1200.0,
        }
    ]
    assert meta and meta["bar_count"] == 1
    assert meta["symbols"] == ["000001.SZ"]


def test_load_paper_feed_returns_empty_without_config(tmp_path):
    rows, meta = load_paper_feed(tmp_path, {})

    assert rows == []
    assert meta is None
