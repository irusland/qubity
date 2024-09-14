import abc
from datetime import datetime, timedelta
from typing import Iterable

import binance

from data_loaders.clients import ITradeClient, SpotClient, PerpClient
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

    def __init__(self, trade_client: ITradeClient):
        self._trade_client = trade_client

    def load_trades(self, start_time: datetime, end_time: datetime) -> Iterable[Trade]:
        current_time = to_timestamp(start_time)
        end_time = to_timestamp(end_time)
        while current_time <= end_time:
            trades = self._trade_client.get_trades(
                symbol='BTCUSDT',
                start_time=current_time,
            )
            for raw_trade in trades:
                yield Trade.model_validate(raw_trade)
                current_time = raw_trade['T']


if __name__ == '__main__':
    client = binance.Client()
    # trade_client = SpotClient(client=client)
    trade_client = PerpClient(client=client)
    loader = TradeLoader(trade_client=trade_client)
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
