import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from backtester.events import DataEvent, SignalEvent
from backtester.portfolio import Portfolio


def test_portfolio_notional_cap():
    portfolio = Portfolio(initial_capital=100_000.0)
    portfolio.update_market_price(
        DataEvent(
            timestamp="2024-01-01",
            symbol="MSFT",
            open=200.0,
            high=200.0,
            low=200.0,
            close=200.0,
            volume=1000,
        )
    )

    order = portfolio.update_signal(
        SignalEvent(timestamp="2024-01-01", symbol="MSFT", signal_type="LONG")
    )

    assert order is not None
    assert order.direction == "BUY"
    assert order.quantity == 50
