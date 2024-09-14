from datetime import timedelta

import binance
import logging

from data_loaders.models.open_interest import OpenInterest, Period

logging.basicConfig(level=logging.DEBUG)

from datetime import datetime

def to_timestamp(date):
    return int(date.timestamp() * 1000)


# Example usage:
data = {
    "symbol": "BTCUSDT",
    "sumOpenInterest": "20403.63700000",
    "sumOpenInterestValue": "150570784.07809979",
    "timestamp": "1583127900000"
}

open_interest = OpenInterest(**data)
print(open_interest)



client = binance.Client()

def load_trades(start_time: datetime, end_time: datetime):
    start_time = to_timestamp(start_time)
    end_time = to_timestamp(end_time)
    print(start_time)
    while start_time < end_time:
        trades = client.futures_open_interest_hist(
            symbol='BTCUSDT',
            period=Period.FIVE_MINUTES,
            startTime=start_time,
        )
        for trade in trades:
            print(trade)
            start_time = trade['timestamp']
        print(start_time)
        print(len(trades))


load_trades(
    start_time=datetime.now() - timedelta(days=1),
    end_time=datetime.now() - timedelta(days=1) + timedelta(minutes=1),
)

