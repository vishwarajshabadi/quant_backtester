import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from backtester.events import DataEvent, OrderEvent
from backtester.execution import SimulatedExecutionHandler


def test_execution_buy_frictions():
    broker = SimulatedExecutionHandler(commission_rate=0.0005, slippage_pct=0.0002)

    broker.update_market_price(
        DataEvent(
            timestamp="2024-01-01",
            symbol="AAPL",
            open=100.0,
            high=100.0,
            low=100.0,
            close=100.0,
            volume=1000,
        )
    )

    fill = broker.execute_order(
        OrderEvent(symbol="AAPL", order_type="MARKET", direction="BUY", quantity=100),
        timestamp="2024-01-01",
    )

    expected_price = 100.02
    expected_comm = (expected_price * 100) * 0.0005

    assert fill is not None
    assert fill.direction == "BUY"
    assert pytest.approx(fill.fill_price) == expected_price
    assert pytest.approx(fill.commission) == expected_comm
