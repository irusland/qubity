from functools import singledispatch, singledispatchmethod
from typing import Any

from data_loaders.models.funding_rate import FundingRate
from data_loaders.models.open_interest import OpenInterest
from data_loaders.models.trade import Trade, FutureTrade
from data_processors.models.candles import Candle


class CandleFiller:
    @singledispatchmethod
    def fill_candle(self, data: Any, candle: Candle):
        raise NotImplementedError(f'Data of type {type(data)} is not yet supported')

    @fill_candle.register(Trade)
    def fill_candle_trade(self, data: Trade, candle: Candle):
        self._base_process_candle_trade(data, candle)

        candle.high_spot = max(candle.high_spot or data.price, data.price)
        candle.low_spot = min(candle.low_spot or data.price, data.price)

        candle.volume_spot = data.quantity if not candle.volume_spot else candle.volume_spot + data.quantity
        candle.trades_spot = 1 if not candle.trades_spot else candle.trades_spot + 1

        if data.is_buyer_maker:
            candle.buy_volume_spot = data.quantity if not candle.buy_volume_spot else candle.buy_volume_spot + data.quantity
            candle.buy_trades_spot = 1 if not candle.buy_trades_spot else candle.buy_trades_spot + 1
        else:
            candle.sell_volume_spot = data.quantity if not candle.sell_volume_spot else candle.sell_volume_spot + data.quantity
            candle.sell_trades_spot = 1 if not candle.sell_trades_spot else candle.sell_trades_spot + 1

    @fill_candle.register(FutureTrade)
    def fill_candle_future_trade(self, data: Trade, candle: Candle):
        self._base_process_candle_trade(data, candle)

        candle.high_perp = max(candle.high_perp or data.price, data.price)
        candle.low_perp = min(candle.low_perp or data.price, data.price)

        candle.volume_perp = data.quantity if not candle.volume_perp else candle.volume_perp + data.quantity
        candle.trades_perp = 1 if not candle.trades_perp else candle.trades_perp + 1

        if data.is_buyer_maker:
            candle.buy_volume_perp = data.quantity if not candle.buy_volume_perp else candle.buy_volume_perp + data.quantity
            candle.buy_trades_perp = 1 if not candle.buy_trades_perp else candle.buy_trades_perp + 1
        else:
            candle.sell_volume_perp = data.quantity if not candle.sell_volume_perp else candle.sell_volume_perp + data.quantity
            candle.sell_trades_perp = 1 if not candle.sell_trades_perp else candle.sell_trades_perp + 1

    @fill_candle.register(FundingRate)
    def fill_candle_funding_rate(self, data: FundingRate, candle: Candle):
        candle.funding_rate = data.funding_rate

    @fill_candle.register(OpenInterest)
    def fill_candle_open_interest(self, data: OpenInterest, candle: Candle):
        candle.open_interest = data.sum_open_interest

    def _base_process_candle_trade(self, data: Trade, candle: Candle):
        candle.open_timestamp = min(
            candle.open_timestamp or data.timestamp, data.timestamp
        )
        candle.close_timestamp = max(
            candle.close_timestamp or data.timestamp, data.timestamp
        )

        candle.volume_total = data.quantity if not candle.volume_total else candle.volume_total + data.quantity
        candle.trades_total = 1 if not candle.trades_total else candle.trades_total + 1

        if data.is_buyer_maker:
            candle.buy_volume_total = data.quantity if not candle.buy_volume_total else candle.buy_volume_total + data.quantity
            candle.buy_trades_total = 1 if not candle.buy_trades_total else candle.buy_trades_total + 1
        else:
            candle.sell_volume_total = data.quantity if not candle.sell_volume_total else candle.sell_volume_total + data.quantity
            candle.sell_trades_total = 1 if not candle.sell_trades_total else candle.sell_trades_total + 1

        if candle.open_timestamp == data.timestamp:
            candle.open_spot = data.price
        if candle.close_timestamp == data.timestamp:
            candle.close_spot = data.price
