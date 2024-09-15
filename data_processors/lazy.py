import csv
import os
from datetime import datetime, timedelta, timezone
from itertools import chain
from typing import Iterator, Any, Iterable

from data_loaders.clients import (
    SpotClient, PerpClient, OpenInterestClient,
    FundingRateClient, TData,
)
from data_loaders.loader import Loader
import binance
from data_loaders.time_conversion import to_timestamp, to_minute_timeframe
from data_processors.candle_filler import CandleFiller
from data_processors.models.candles import Candle
from paths import PROCESSED_DIR


class CommitIterator(Iterator[TData]):
    """
    Iterator that repeats the last element if it was not committed
    """
    def __init__(self, iterator: Iterator[TData]):
        self._iterator = iterator
        self._uncommitted: TData | None = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._uncommitted is None:
            self._uncommitted = next(self._iterator)
        return self._uncommitted

    def commit(self):
        if self._uncommitted is None:
            raise ValueError('No uncommitted data')
        self._uncommitted = None


class LazyCandleProcessor:
    """
    Processes data lazily and fills candles
    """
    def __init__(
        self,
        spot_client: SpotClient,
        perp_client: PerpClient,
        open_interest_client: OpenInterestClient,
        funding_rate_client: FundingRateClient,
        candle_filler: CandleFiller,
    ):
        self._spot_loader = Loader(data_client=spot_client)
        self._perp_loader = Loader(data_client=perp_client)
        self._open_interest_loader = Loader(data_client=open_interest_client)
        self._funding_rate_loader = Loader(data_client=funding_rate_client)
        self._candle_filler = candle_filler

    def _get_commit_iterator(self, start_time: datetime, end_time: datetime, loader: Loader) -> CommitIterator:
        return CommitIterator(
            iter(
                loader.load(
                    start_time=start_time,
                    end_time=end_time,
                )
            )
        )

    def process(self, start_time: datetime, end_time: datetime) -> Iterable[Candle]:
        spot_iterator = self._get_commit_iterator(start_time, end_time, self._spot_loader)
        perp_iterator = self._get_commit_iterator(start_time, end_time, self._perp_loader)
        open_interest_iterator = self._get_commit_iterator(start_time, end_time, self._open_interest_loader)
        funding_rate_iterator = self._get_commit_iterator(start_time, end_time, self._funding_rate_loader)

        current_timeframe = to_minute_timeframe(start_time)
        next_timeframe = to_minute_timeframe(start_time+timedelta(minutes=5))
        current_candle = Candle(timestamp=current_timeframe)

        while current_timeframe - end_time < timedelta(seconds=1):
            was_filled = False
            was_filled = self._fill_with_iterator(current_candle, current_timeframe, spot_iterator, next_timeframe) or was_filled
            was_filled = self._fill_with_iterator(current_candle, current_timeframe, perp_iterator, next_timeframe) or was_filled
            was_filled = self._fill_with_iterator(current_candle, current_timeframe, open_interest_iterator, next_timeframe) or was_filled
            was_filled = self._fill_with_iterator(current_candle, current_timeframe, funding_rate_iterator, next_timeframe) or was_filled

            if not was_filled:
                continue

            yield current_candle

            current_timeframe = next_timeframe
            next_timeframe = current_timeframe + timedelta(minutes=5)

            current_candle = Candle(timestamp=current_timeframe)

    def _fill_with_iterator(
        self, current_candle: Candle, current_timeframe: datetime, iterator: CommitIterator, next_timeframe: datetime
    ):
        was_filled = False
        while True:
            try:
                data = next(iterator)
                if current_timeframe <= data.timestamp < next_timeframe:
                    iterator.commit()
                    self._candle_filler.fill_candle(data, current_candle)
                    was_filled = True
                else:
                    break
            except StopIteration:
                break
        return was_filled


if __name__ == '__main__':
    candle_filler = CandleFiller()
    client = binance.Client()
    spot_client = SpotClient(client=client)
    perp_client = PerpClient(client=client)
    open_interest_client = OpenInterestClient(client=client)
    funding_rate_client = FundingRateClient(client=client)
    processor = LazyCandleProcessor(
        spot_client=spot_client,
        perp_client=perp_client,
        open_interest_client=open_interest_client,
        funding_rate_client=funding_rate_client,
        candle_filler=candle_filler,
    )

    now = datetime(
        year=2024, month=9, day=13, hour=7, minute=0, second=0, tzinfo=timezone.utc
    )
    start = now - timedelta(days=1)
    # end = start + timedelta(days=1)
    end = start + timedelta(minutes=20)
    candles = processor.process(start_time=start, end_time=end)

    fieldnames = list(Candle.__fields__.keys())
    fieldnames.remove('open_timestamp')
    fieldnames.remove('close_timestamp')

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_DIR / 'result_lazy.csv', mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows((candle.dict(exclude=['open_timestamp', 'close_timestamp']) for candle in candles))
