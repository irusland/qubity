import time
from datetime import datetime, timedelta, timezone

import binance

from data_loaders.clients import (
    SpotClient, PerpClient, OpenInterestClient,
    FundingRateClient,
)
from data_processors.candle_filler import CandleFiller
from data_processors.lazy import LazyCandleProcessor
from data_processors.pandas_dataframe import PandasCandleProcessor

client = binance.Client()
spot_client = SpotClient(client=client)
perp_client = PerpClient(client=client)
open_interest_client = OpenInterestClient(client=client)
funding_rate_client = FundingRateClient(client=client)
candle_filler = CandleFiller()

pandas_processor = PandasCandleProcessor(
    spot_client=spot_client,
    perp_client=perp_client,
    open_interest_client=open_interest_client,
    funding_rate_client=funding_rate_client,
)
lazy_processor = LazyCandleProcessor(
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
end = start + timedelta(minutes=2)
# end = start + timedelta(hours=1)

# warmup caches
for processor in (pandas_processor, lazy_processor):
    candles = processor.process(start_time=start, end_time=end)

EXPERIMENT_COUNT = 4

results = {}
for experiment in range(EXPERIMENT_COUNT):
    for processor in (pandas_processor, lazy_processor):
        start_process_time = time.monotonic()
        candles = processor.process(start_time=start, end_time=end)
        elapsed = timedelta(seconds=time.monotonic() - start_process_time)
        times = results.get(processor, [])
        times.append(elapsed)
        results[processor] = times


def mean_timedelta(timedelta_list: list[timedelta]) -> timedelta:
    if not timedelta_list:
        return timedelta(0)
    total = sum(timedelta_list, timedelta(0))
    mean = total / len(timedelta_list)
    return mean

processor_mean = {}
for processor, times in results.items():
    mean = mean_timedelta(times)
    processor_mean[processor] = mean
    print(f"{processor.__class__.__name__}: mean {mean} (from {len(times)} experiments {times})")

processor_mean = dict(sorted(processor_mean.items(), key=lambda item: item[1]))
it = iter(processor_mean.items())
best_processor, best_mean = next(it)
worst_processor, worst_mean = next(it)

print(f'Best processor: {best_processor.__class__.__name__} with mean {best_mean} increase in performance x{worst_mean / best_mean:.2f}')
