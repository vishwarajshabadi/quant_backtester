# simulates broker execution

from typing import Dict

from backtester.events import DataEvent, FillEvent, OrderEvent


class SimulatedExecutionHandler:
    def __init__(self, commission_rate: float = 0.0005, slippage_pct: float = 0.0002):
        self.commission_rate = commission_rate
        self.slippage_pct = slippage_pct
        self.current_prices: Dict[str, float] = {}

    def update_market_price(self, event: DataEvent) -> None:
        self.current_prices[event.symbol] = event.close

    def execute_order(self, event: OrderEvent, timestamp: str) -> FillEvent | None:
        if event.symbol not in self.current_prices:
            return None

        price = self.current_prices[event.symbol]
        direction_mult = 1.0 if event.direction == "BUY" else -1.0

        slippage = price * self.slippage_pct * direction_mult
        fill_price = price + slippage

        commission = (fill_price * event.quantity) * self.commission_rate

        return FillEvent(
            timestamp=timestamp,
            symbol=event.symbol,
            direction=event.direction,
            quantity=event.quantity,
            fill_price=fill_price,
            commission=commission,
            slippage=abs(slippage * event.quantity),
        )
