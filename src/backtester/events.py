# event types passed between the engine and the modules

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Event:
    pass


@dataclass(frozen=True)
class DataEvent(Event):
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class SignalEvent(Event):
    timestamp: str
    symbol: str
    signal_type: Literal["LONG", "SHORT", "EXIT"]
    strength: float = 1.0


@dataclass(frozen=True)
class OrderEvent(Event):
    symbol: str
    order_type: Literal["MARKET", "LIMIT"]
    direction: Literal["BUY", "SELL"]
    quantity: int


@dataclass(frozen=True)
class FillEvent(Event):
    timestamp: str
    symbol: str
    direction: Literal["BUY", "SELL"]
    quantity: int
    fill_price: float
    commission: float
    slippage: float
