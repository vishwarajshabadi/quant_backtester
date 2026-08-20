# tracks portfolio

from collections import deque
from typing import Any, Deque, Dict, List, Optional

import numpy as np
import pandas as pd

from backtester.events import DataEvent, FillEvent, OrderEvent, SignalEvent


class Portfolio:
    ATR_WINDOW = 20
    RISK_ALLOCATION = 0.01
    MAX_NOTIONAL_ALLOCATION = 0.10

    def __init__(self, initial_capital: float = 100_000.0):
        self.current_cash = initial_capital
        self.holdings: Dict[str, int] = {}
        self.current_prices: Dict[str, float] = {}

        self.true_range_history: Dict[str, Deque[float]] = {}
        self.previous_close: Dict[str, float] = {}
        self.equity_curve_history: List[Dict[str, Any]] = []

    def _get_total_equity(self) -> float:
        holdings_value = sum(
            qty * self.current_prices.get(sym, 0.0)
            for sym, qty in self.holdings.items()
        )
        return self.current_cash + holdings_value

    def update_market_price(self, event: DataEvent) -> None:
        sym = event.symbol
        self.current_prices[sym] = event.close

        if sym not in self.true_range_history:
            self.true_range_history[sym] = deque(maxlen=self.ATR_WINDOW)

        if sym in self.previous_close:
            tr = max(
                event.high - event.low,
                abs(event.high - self.previous_close[sym]),
                abs(event.low - self.previous_close[sym]),
            )
            self.true_range_history[sym].append(tr)

        self.previous_close[sym] = event.close

        self.equity_curve_history.append(
            {
                "timestamp": event.timestamp,
                "total_equity": self._get_total_equity(),
            }
        )

    def update_signal(self, event: SignalEvent) -> Optional[OrderEvent]:
        sym = event.symbol
        price = self.current_prices.get(sym, 0.0)
        qty = self.holdings.get(sym, 0)

        if price == 0.0:
            return None

        atr = (
            np.mean(self.true_range_history[sym])
            if self.true_range_history.get(sym)
            else 0.0
        )
        equity = self._get_total_equity()
        max_notional_qty = int((equity * self.MAX_NOTIONAL_ALLOCATION) / price)

        if atr > 0:
            target_qty = max(
                1, min(int((equity * self.RISK_ALLOCATION) / atr), max_notional_qty)
            )
        else:
            target_qty = max(1, max_notional_qty)

        if event.signal_type == "LONG" and qty == 0:
            return OrderEvent(
                symbol=sym, order_type="MARKET", direction="BUY", quantity=target_qty
            )
        elif event.signal_type == "EXIT" and qty > 0:
            return OrderEvent(
                symbol=sym, order_type="MARKET", direction="SELL", quantity=qty
            )

        return None

    def update_fill(self, event: FillEvent) -> None:
        self.current_cash -= event.commission + event.slippage
        notional = event.fill_price * event.quantity

        if event.direction == "BUY":
            self.current_cash -= notional
            self.holdings[event.symbol] = (
                self.holdings.get(event.symbol, 0) + event.quantity
            )
        else:
            self.current_cash += notional
            self.holdings[event.symbol] = (
                self.holdings.get(event.symbol, 0) - event.quantity
            )

    def get_equity_curve(self) -> pd.DataFrame:
        df = pd.DataFrame(self.equity_curve_history)
        if not df.empty:
            df = df.groupby("timestamp").last()
            df.index = pd.to_datetime(df.index)
        return df
