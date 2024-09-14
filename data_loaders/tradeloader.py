import abc
import csv
import itertools
import logging
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Iterable, Generic, TypeVar
import tqdm
import binance
from binance.exceptions import BinanceAPIException

from data_loaders.clients import IClient, SpotClient, PerpClient, FundingRateClient, OpenInterestClient
from data_loaders.models.timedata import TimeData
from data_loaders.models.trade import Trade
from data_loaders.paths import DATA_DIR
from data_loaders.time_conversion import to_timestamp
logger = logging.getLogger(__name__)
TData = TypeVar('TData', bound=TimeData)


class ILoader(abc.ABC, Generic[TData]):
    @abc.abstractmethod
    def load(self, start_time: datetime, end_time: datetime) -> Iterable[TData]:
        pass


class Loader(ILoader[TData]):
    """
    Loads data within specified time bounds
    """

    def __init__(self, data_client: IClient[TData]):
        self._data_client = data_client

    def load(self, start_time: datetime, end_time: datetime) -> Iterable[Trade]:
        start_timestamp = to_timestamp(start_time)
        current_timestamp = start_timestamp
        end_timestamp = to_timestamp(end_time)
        current_time = start_time
        with tqdm.tqdm(total=end_timestamp-start_timestamp, desc=f"Processing {data_client.__class__.__name__}", unit="s") as pbar:
            is_timestamp_changed = True

            yield from self.load_by_timestamp(
                current_time,
                current_timestamp,
                end_time,
                end_timestamp,
                is_timestamp_changed,
                pbar,
                start_timestamp,
            )

    def load_by_timestamp(
        self, current_time: datetime,
        current_timestamp: int,
        end_time: datetime,
        end_timestamp: int,
        is_timestamp_changed: bool,
        pbar: tqdm.tqdm,
        start_timestamp: int,
    ):
        while current_time - end_time < timedelta(seconds=1) and is_timestamp_changed:
            try:
                timed_data = self._data_client.get(
                    symbol='BTCUSDT',
                    start_time=current_timestamp,
                    end_time=end_timestamp,
                )

                is_timestamp_changed = False
                for data in timed_data:
                    yield data
                if data.timestamp > current_time:
                    is_timestamp_changed = True
                    current_time = data.timestamp
                    current_timestamp = to_timestamp(current_time)
                pbar.n = current_timestamp - start_timestamp
                pbar.refresh()

            except BinanceAPIException:
                logger.exception('Exception, sleeping')
                sleep(42)
            except KeyboardInterrupt:
                break


def peek_and_iterate(iterator):
    iterator = iter(iterator)

    # Peek one element
    try:
        first_element = next(iterator)
    except StopIteration:
        # Handle the case where the iterator is empty
        return iter([])  # Return an empty iterator

    # Prepend the first element back to the front of the iterator
    return itertools.chain([first_element], iterator)


if __name__ == '__main__':
    client = binance.Client()
    spot_client = SpotClient(client=client)
    perp_client = PerpClient(client=client)
    open_interest_client = OpenInterestClient(client=client)
    funding_rate_client = FundingRateClient(client=client)

    # now = datetime.now(timezone.utc)
    now = datetime(year=2024, month=9, day=13, hour=17, minute=0, second=0, tzinfo=timezone.utc)
    start = now - timedelta(days=1, hours=10)
    end = start + timedelta(hours=7)

    for data_name, data_client in {
        'spot': spot_client,
        'perp': perp_client,
        'open_interest': open_interest_client,
        'funding_rate': funding_rate_client,
    }.items():
        loader = Loader(data_client=data_client)
        all_data = (
            loader.load(
                start_time=start,
                end_time=end,
            )
        )
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        csv_file_path = DATA_DIR / f"{data_name}_{start}_{end}.csv"

        first_data = next(all_data)
        fieldnames = list(first_data.__class__.__fields__.keys())

        with open(csv_file_path, mode="w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows((data.dict() for data in itertools.chain([first_data], all_data)))

        print(f"Saved data to {csv_file_path}")
