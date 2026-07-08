"""Tests for virtual paper trading accounts."""

from autostrategy.core.paper_account import PaperAccount, normalize_account


def test_paper_account_buys_and_sells_positions():
    account = PaperAccount(initial_cash=1000)

    buy = account.apply_event({"action": "buy", "symbol": "000001.SZ", "price": 10, "size": 50})
    sell = account.apply_event({"action": "sell", "symbol": "000001.SZ", "price": 12, "size": 20})

    snapshot = account.snapshot()
    assert buy["account_event"] == "filled"
    assert sell["account_event"] == "filled"
    assert snapshot["cash"] == 740
    assert snapshot["equity"] == 1100
    assert snapshot["realized_pnl"] == 40
    assert snapshot["unrealized_pnl"] == 60
    assert snapshot["positions"][0]["quantity"] == 30
    assert snapshot["trade_count"] == 2


def test_paper_account_rejects_invalid_orders():
    account = PaperAccount(initial_cash=100)

    buy = account.apply_event({"action": "buy", "symbol": "000001.SZ", "price": 10, "size": 20})
    sell = account.apply_event({"action": "sell", "symbol": "000001.SZ", "price": 10, "size": 1})

    assert buy["account_event"] == "rejected"
    assert buy["reject_reason"] == "insufficient_cash"
    assert sell["account_event"] == "rejected"
    assert sell["reject_reason"] == "insufficient_position"
    assert account.snapshot()["rejected_count"] == 2


def test_normalize_account_keeps_existing_snapshot():
    account = normalize_account(
        {
            "account": {
                "initial_cash": 1000,
                "cash": 900,
                "equity": 1100,
                "positions": [{"symbol": "000001.SZ", "quantity": 10}],
                "trade_count": 1,
            }
        }
    )

    assert account["initial_cash"] == 1000
    assert account["cash"] == 900
    assert account["equity"] == 1100
    assert account["position_count"] == 1
    assert account["trade_count"] == 1
