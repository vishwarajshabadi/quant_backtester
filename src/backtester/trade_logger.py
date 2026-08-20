# logs trades

from typing import List

from backtester.events import FillEvent


class TradeLogger:
    def __init__(self):
        self.trades: List[FillEvent] = []

    def log_fill(self, event: FillEvent) -> None:
        self.trades.append(event)

    def print_trade_book(self) -> None:
        if not self.trades:
            print("\n--- TRADE BOOK ---")
            print("No trades executed.")
            return

        print("\n--- TRADE BOOK ---")
        print(
            f"{'Timestamp':<20}{'Symbol':<8}{'Direction':<10}{'Quantity':>10}{'Price':>12}{'Commission':>14}{'Slippage':>12}"
        )
        print("-" * 86)
        for trade in self.trades:
            print(
                f"{trade.timestamp:<20}{trade.symbol:<8}{trade.direction:<10}{trade.quantity:>10}"
                f"{trade.fill_price:>12.2f}{trade.commission:>14.2f}{trade.slippage:>12.2f}"
            )
