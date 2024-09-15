import csv
import re
from datetime import datetime

from data_loaders.models.funding_rate import FundingRate
from data_loaders.models.open_interest import OpenInterest
from paths import DATA_DIR, PROCESSED_DIR
from pydantic import BaseModel

from data_loaders.time_conversion import to_minute_timeframe
from data_processors.candle_filler import CandleFiller
from data_processors.models.candles import Candle

pattern = re.compile(
    r'^(?P<type>.*?)_'
    r'(?P<start_time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2})_'
    r'(?P<end_time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2})'
    r'\.csv$'
)

type_to_model: dict[str, type[BaseModel]] = {
    # 'spot': Trade,
    # 'perp': FutureTrade,
    'funding_rate': FundingRate,
    'open_interest': OpenInterest,
}

candles_by_time: dict[datetime, Candle] = {}

candle_filler = CandleFiller()
for path in DATA_DIR.glob("*.csv"):
    match = pattern.match(path.name)
    data_type = match.group('type')
    start_time = match.group('start_time')
    end_time = match.group('end_time')

    if data_type not in type_to_model:
        continue
    model = type_to_model[data_type]
    with open(path, mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data = model.model_validate(row)
            timeframe = to_minute_timeframe(data.timestamp)

            candle = candles_by_time.get(timeframe, Candle(timestamp=timeframe))
            candle_filler.fill_candle(data, candle)
            candles_by_time[timeframe] = candle

candles_by_time = sorted(candles_by_time.items())

fieldnames = list(Candle.__fields__.keys())

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
with open(PROCESSED_DIR / 'result_pythonic.csv', mode="w", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows((candle.dict() for time, candle in candles_by_time))

