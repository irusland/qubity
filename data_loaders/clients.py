import abc
from functools import lru_cache
from typing import TypeVar, Generic, Iterable

import binance

from data_loaders.models.funding_rate import FundingRate
from data_loaders.models.open_interest import OpenInterest, Period
from data_loaders.models.timedata import TimeData
from data_loaders.models.trade import Trade, FutureTrade

TData = TypeVar('TData', bound=TimeData)


class IClient(abc.ABC, Generic[TData]):
    @abc.abstractmethod
    def get(self, symbol: str, start_time: int, end_time: int) -> Iterable[TData]:
        pass


class SpotClient(IClient[Trade]):
    def __init__(self, client: binance.Client):
        self._client = client
        self._get_aggregate_trades = lru_cache()(self._client.get_aggregate_trades)

    def get(self, symbol: str, start_time: int, end_time: int) -> Iterable[Trade]:
        for trade in self._get_aggregate_trades(symbol=symbol, startTime=start_time, endTime=end_time):
            yield Trade.model_validate(trade)


class PerpClient(IClient[FutureTrade]):
    def __init__(self, client: binance.Client):
        self._client = client
        self._futures_aggregate_trades = lru_cache()(self._client.futures_aggregate_trades)

    def get(self, symbol: str, start_time: int, end_time: int) -> Iterable[FutureTrade]:
        for trade in self._futures_aggregate_trades(symbol=symbol, startTime=start_time, endTime=end_time):
            yield FutureTrade.model_validate(trade)


class OpenInterestClient(IClient[OpenInterest]):
    def __init__(self, client: binance.Client):
        self._client = client
        self._futures_open_interest_hist = lru_cache()(self._client.futures_open_interest_hist)

    def get(self, symbol: str, start_time: int, end_time: int) -> Iterable[OpenInterest]:
        for raw_data in self._futures_open_interest_hist(symbol=symbol, period=Period.FIVE_MINUTES, startTime=start_time, endTime=end_time):
            yield OpenInterest.model_validate(raw_data)


class FundingRateClient(IClient[FundingRate]):
    def __init__(self, client: binance.Client):
        self._client = client
        self._futures_funding_rate = lru_cache()(self._client.futures_funding_rate)

    def get(self, symbol: str, start_time: int, end_time: int) -> Iterable[FundingRate]:
        for raw_data in self._futures_funding_rate(symbol=symbol, startTime=start_time, endTime=end_time):
            yield FundingRate.model_validate(raw_data)
