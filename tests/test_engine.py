from backtester.data import AbstractDataHandler
from backtester.engine import BacktestEngine
from backtester.events import DataEvent
from backtester.execution import SimulatedExecutionHandler
from backtester.portfolio import Portfolio
from backtester.strategy import MovingAverageCrossoverStrategy
from backtester.trade_logger import TradeLogger


class ListDataHandler(AbstractDataHandler):
    def __init__(self, bars):
        self.bars = bars
        self.latest_bars = {}
        self._stream = iter(bars)

    def get_latest_bar(self, symbol):
        return self.latest_bars[symbol]

    def stream_next_bar(self):
        for event in self._stream:
            self.latest_bars[event.symbol] = event
            yield event


def make_bars(symbol, prices):
    return [
        DataEvent(
            timestamp=str(i),
            symbol=symbol,
            open=p,
            high=p,
            low=p,
            close=p,
            volume=1000.0,
        )
        for i, p in enumerate(prices)
    ]


def test_engine_fills_at_next_bar_open():
    prices = [100.0] * 17 + [110.0] * 30 + [90.0] * 30
    trade_logger = TradeLogger()
    engine = BacktestEngine(
        data_handler=ListDataHandler(make_bars("XYZ", prices)),
        strategy=MovingAverageCrossoverStrategy(fast_window=5, slow_window=10),
        portfolio=Portfolio(initial_capital=100_000.0),
        execution_handler=SimulatedExecutionHandler(commission_rate=0.0, slippage_pct=0.0),
        trade_logger=trade_logger,
    )

    engine.run()

    trades = trade_logger.trades
    assert len(trades) == 2

    buy, sell = trades
    assert buy.timestamp == "18"
    assert buy.direction == "BUY"
    assert buy.quantity == 90
    assert buy.fill_price == 110.0

    assert sell.timestamp == "48"
    assert sell.direction == "SELL"
    assert sell.quantity == 90
    assert sell.fill_price == 90.0
