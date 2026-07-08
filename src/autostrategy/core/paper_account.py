"""Virtual account model for replay-first paper trading."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PaperPosition:
    """Single-symbol virtual position."""

    symbol: str
    quantity: float = 0.0
    avg_price: float = 0.0
    market_price: float = 0.0
    realized_pnl: float = 0.0

    @property
    def market_value(self) -> float:
        return self.quantity * self.market_price

    @property
    def unrealized_pnl(self) -> float:
        return (self.market_price - self.avg_price) * self.quantity

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "quantity": round(self.quantity, 6),
            "avg_price": round(self.avg_price, 4),
            "market_price": round(self.market_price, 4),
            "market_value": round(self.market_value, 2),
            "realized_pnl": round(self.realized_pnl, 2),
            "unrealized_pnl": round(self.unrealized_pnl, 2),
        }


@dataclass
class PaperAccount:
    """Cash and positions for deterministic paper replay."""

    initial_cash: float = 1_000_000.0
    cash: float | None = None
    positions: dict[str, PaperPosition] = field(default_factory=dict)
    trade_count: int = 0
    rejected_count: int = 0
    realized_pnl: float = 0.0

    def __post_init__(self) -> None:
        if self.cash is None:
            self.cash = self.initial_cash

    def apply_event(self, event: dict[str, Any]) -> dict[str, Any]:
        action = str(event.get("action") or "hold").lower()
        symbol = str(event.get("symbol") or "")
        price = _float_or_none(event.get("price", event.get("close")))
        if price is None:
            price = _float_or_none(event.get("close"))
        quantity = _float_or_none(event.get("quantity", event.get("size")))
        enriched = dict(event)

        if symbol and price is not None:
            self.mark(symbol, price)

        if action == "buy" and symbol and price is not None and quantity is not None:
            self._buy(symbol, price, quantity, enriched)
        elif action == "sell" and symbol and price is not None and quantity is not None:
            self._sell(symbol, price, quantity, enriched)
        else:
            enriched.setdefault("account_event", "hold")

        enriched["cash_after"] = round(float(self.cash or 0), 2)
        enriched["equity_after"] = round(self.equity, 2)
        if symbol in self.positions:
            enriched["position_after"] = round(self.positions[symbol].quantity, 6)
        return enriched

    def mark(self, symbol: str, price: float) -> None:
        position = self.positions.get(symbol)
        if position:
            position.market_price = price

    @property
    def equity(self) -> float:
        return float(self.cash or 0) + sum(
            position.market_value for position in self.positions.values()
        )

    @property
    def unrealized_pnl(self) -> float:
        return sum(position.unrealized_pnl for position in self.positions.values())

    def snapshot(self) -> dict[str, Any]:
        active_positions = [
            position.to_dict()
            for position in self.positions.values()
            if abs(position.quantity) > 1e-9
        ]
        return {
            "initial_cash": round(self.initial_cash, 2),
            "cash": round(float(self.cash or 0), 2),
            "equity": round(self.equity, 2),
            "final_value": round(self.equity, 2),
            "realized_pnl": round(self.realized_pnl, 2),
            "unrealized_pnl": round(self.unrealized_pnl, 2),
            "positions": active_positions,
            "position_count": len(active_positions),
            "trade_count": self.trade_count,
            "rejected_count": self.rejected_count,
        }

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> PaperAccount:
        initial_cash = _float_or_none(config.get("initial_cash")) or 1_000_000.0
        return cls(initial_cash=initial_cash)

    def _buy(self, symbol: str, price: float, quantity: float, event: dict[str, Any]) -> None:
        if quantity <= 0:
            self._reject(event, "quantity_must_be_positive")
            return
        cost = price * quantity
        if cost > float(self.cash or 0):
            self._reject(event, "insufficient_cash")
            return
        position = self.positions.setdefault(
            symbol, PaperPosition(symbol=symbol, market_price=price)
        )
        total_cost = position.avg_price * position.quantity + cost
        position.quantity += quantity
        position.avg_price = total_cost / position.quantity if position.quantity else 0.0
        position.market_price = price
        self.cash = float(self.cash or 0) - cost
        self.trade_count += 1
        event["account_event"] = "filled"

    def _sell(self, symbol: str, price: float, quantity: float, event: dict[str, Any]) -> None:
        position = self.positions.get(symbol)
        if quantity <= 0:
            self._reject(event, "quantity_must_be_positive")
            return
        if position is None or position.quantity < quantity:
            self._reject(event, "insufficient_position")
            return
        pnl = (price - position.avg_price) * quantity
        position.quantity -= quantity
        position.market_price = price
        position.realized_pnl += pnl
        self.realized_pnl += pnl
        self.cash = float(self.cash or 0) + price * quantity
        self.trade_count += 1
        event["account_event"] = "filled"
        if position.quantity <= 1e-9:
            self.positions.pop(symbol, None)

    def _reject(self, event: dict[str, Any], reason: str) -> None:
        self.rejected_count += 1
        event["account_event"] = "rejected"
        event["reject_reason"] = reason


def normalize_account(
    raw: dict[str, Any], fallback_initial_cash: float = 1_000_000.0
) -> dict[str, Any]:
    account = raw.get("account") if isinstance(raw.get("account"), dict) else None
    paper = raw.get("paper") if isinstance(raw.get("paper"), dict) else {}
    source = account or paper
    positions = source.get("positions") if isinstance(source.get("positions"), list) else []
    initial_cash = _float_or_none(source.get("initial_cash")) or fallback_initial_cash
    cash = _float_or_none(source.get("cash"))
    final_value = _float_or_none(source.get("final_value", source.get("equity")))
    if cash is None:
        cash = final_value if final_value is not None else initial_cash
    if final_value is None:
        final_value = cash + sum(
            _float_or_none(position.get("market_value")) or 0 for position in positions
        )
    realized_pnl = _float_or_none(source.get("realized_pnl")) or 0.0
    unrealized_pnl = _float_or_none(source.get("unrealized_pnl")) or 0.0
    return {
        "initial_cash": round(initial_cash, 2),
        "cash": round(cash, 2),
        "equity": round(final_value, 2),
        "final_value": round(final_value, 2),
        "realized_pnl": round(realized_pnl, 2),
        "unrealized_pnl": round(unrealized_pnl, 2),
        "positions": positions,
        "position_count": int(source.get("position_count", len(positions)) or 0),
        "trade_count": int(source.get("trade_count", source.get("total_trades", 0)) or 0),
        "rejected_count": int(source.get("rejected_count", 0) or 0),
    }


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
