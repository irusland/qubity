import abc
from datetime import datetime
from typing import Any

import binance


class ITradeClient(abc.ABC):
    @abc.abstractmethod
    def get_trades(self, symbol: str, start_time: datetime) -> list[dict[str,Any]]:
        pass


class SpotClient(ITradeClient):
    def __init__(self, client: binance.Client):
        self._client = client

    def get_trades(self, symbol: str, start_time: datetime) -> list[dict[str, Any]]:
        return self._client.get_aggregate_trades(symbol=symbol, startTime=start_time)


class PerpClient(ITradeClient):
    def __init__(self, client: binance.Client):
        self._client = client

    def get_trades(self, symbol: str, start_time: datetime) -> list[dict[str, Any]]:
        return self._client.futures_aggregate_trades(symbol=symbol, startTime=start_time)
