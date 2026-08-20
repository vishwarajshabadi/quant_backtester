# runs the engine

from collections import deque
from typing import Deque, Optional

from backtester.data import AbstractDataHandler
from backtester.events import DataEvent, Event, FillEvent, OrderEvent, SignalEvent
from backtester.execution import SimulatedExecutionHandler
from backtester.portfolio import Portfolio
from backtester.strategy import Strategy
from backtester.trade_logger import TradeLogger


class BacktestEngine:
    def __init__(
        self,
        data_handler: AbstractDataHandler,
        strategy: Strategy,
        portfolio: Portfolio,
        execution_handler: SimulatedExecutionHandler,
        trade_logger: Optional[TradeLogger] = None,
    ):
        self.data_handler = data_handler
        self.strategy = strategy
        self.portfolio = portfolio
        self.execution_handler = execution_handler
        self.trade_logger = trade_logger
        self.events: Deque[Event] = deque()

    def run(self) -> None:
        print("Spinning up engine...")
        for data_event in self.data_handler.stream_next_bar():
            self.events.append(data_event)

            while self.events:
                event = self.events.popleft()

                if isinstance(event, DataEvent):
                    self.portfolio.update_market_price(event)
                    self.execution_handler.update_market_price(event)
                    if sig := self.strategy.calculate_signal(event):
                        self.events.append(sig)

                elif isinstance(event, SignalEvent):
                    if order := self.portfolio.update_signal(event):
                        self.events.append(order)

                elif isinstance(event, OrderEvent):
                    ts = self.data_handler.get_latest_bar(event.symbol).timestamp
                    if fill := self.execution_handler.execute_order(event, ts):
                        self.events.append(fill)

                elif isinstance(event, FillEvent):
                    if self.trade_logger:
                        self.trade_logger.log_fill(event)
                    self.portfolio.update_fill(event)

        print("Backtest complete.")
