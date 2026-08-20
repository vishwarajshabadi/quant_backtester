# loads the data from yfinance


from abc import ABC, abstractmethod
from typing import Dict, Generator, List

import pandas as pd
import yfinance as yf

from backtester.events import DataEvent


class AbstractDataHandler(ABC):
    @abstractmethod
    def get_latest_bar(self, symbol: str) -> DataEvent:
        pass

    @abstractmethod
    def stream_next_bar(self) -> Generator[DataEvent, None, None]:
        pass


class YFinanceDataHandler(AbstractDataHandler):
    def __init__(self, symbols: List[str], start_date: str, end_date: str):
        self.symbols = symbols
        self.symbol_data: Dict[str, pd.DataFrame] = {}
        self.latest_bars: Dict[str, DataEvent] = {}
        self._load_data(start_date, end_date)

    def _load_data(self, start: str, end: str) -> None:
        for symbol in self.symbols:
            df = yf.download(symbol, start=start, end=end, progress=False)
            if df.empty:
                raise ValueError(f"No data returned for {symbol}")

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.columns = [col.lower() for col in df.columns]
            self.symbol_data[symbol] = df.sort_index()

    def get_latest_bar(self, symbol: str) -> DataEvent:
        if symbol not in self.latest_bars:
            raise KeyError(f"No bars received yet for {symbol}")
        return self.latest_bars[symbol]

    def stream_next_bar(self) -> Generator[DataEvent, None, None]:
        combined_index = pd.DatetimeIndex([])
        for df in self.symbol_data.values():
            combined_index = combined_index.union(df.index)
        combined_index = combined_index.sort_values()

        for timestamp in combined_index:
            ts_str = str(timestamp)
            for symbol, df in self.symbol_data.items():
                if timestamp in df.index:
                    row = df.loc[timestamp]
                    event = DataEvent(
                        timestamp=ts_str,
                        symbol=symbol,
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row["volume"]),
                    )
                    self.latest_bars[symbol] = event
                    yield event
