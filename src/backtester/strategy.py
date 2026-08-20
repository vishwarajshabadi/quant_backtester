# simple moving average crossover strategy

from abc import ABC, abstractmethod
from collections import deque
from typing import Deque, Dict, Optional

import numpy as np

from backtester.events import DataEvent, SignalEvent


class Strategy(ABC):
    @abstractmethod
    def calculate_signal(self, event: DataEvent) -> Optional[SignalEvent]:
        pass


class MovingAverageCrossoverStrategy(Strategy):
    # Dual MA Crossover using fixed-length deques

    def __init__(self, fast_window: int = 20, slow_window: int = 50):
        if fast_window >= slow_window:
            raise ValueError("fast_window must be less than slow_window.")

        self.fast_window = fast_window
        self.slow_window = slow_window
        self.history: Dict[str, Deque[float]] = {}
        self.current_position: Dict[str, str] = {}

    def calculate_signal(self, event: DataEvent) -> Optional[SignalEvent]:
        sym = event.symbol

        if sym not in self.history:
            self.history[sym] = deque(maxlen=self.slow_window)
            self.current_position[sym] = "FLAT"

        self.history[sym].append(event.close)

        if len(self.history[sym]) < self.slow_window:
            return None

        prices = np.array(self.history[sym])
        fast_ma, slow_ma = np.mean(prices[-self.fast_window :]), np.mean(
            prices[-self.slow_window :]
        )
        pos = self.current_position[sym]

        if fast_ma > slow_ma and pos != "LONG":
            self.current_position[sym] = "LONG"
            return SignalEvent(
                timestamp=event.timestamp, symbol=sym, signal_type="LONG"
            )

        if fast_ma < slow_ma and pos == "LONG":
            self.current_position[sym] = "FLAT"
            return SignalEvent(
                timestamp=event.timestamp, symbol=sym, signal_type="EXIT"
            )

        return None
