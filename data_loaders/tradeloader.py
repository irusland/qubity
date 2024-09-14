import abc
from datetime import datetime, timedelta
from typing import Iterable

import binance

from data_loaders.models.trade import Trade
from data_loaders.time_conversion import to_timestamp


class ITradeLoader(abc.ABC):
    @abc.abstractmethod
    def load_trades(self, start_time: datetime, end_time: datetime) -> Iterable[Trade]:
        pass


class TradeLoader(ITradeLoader):
    """
    Loads trades within specified time bounds
    """

    def __init__(self, client: binance.Client):
        self._client = client

    def load_trades(self, start_time: datetime, end_time: datetime) -> Iterable[Trade]:
        current_time = to_timestamp(start_time)
        end_time = to_timestamp(end_time)
        while current_time <= end_time:
            trades = self._client.get_aggregate_trades(
                symbol='BTCUSDT',
                startTime=current_time,
            )
            for trade in trades:
                yield Trade.model_validate(trade)
                current_time = trade['T']


if __name__ == '__main__':
    client = binance.Client()
    loader = TradeLoader(client=client)
    now = datetime.now()
    start = now - timedelta(days=1)
    end = start + timedelta(seconds=10)
    trades = list(
        loader.load_trades(
            start_time=start,
            end_time=end,
        )
    )
    print(trades)
    print(len(trades))
