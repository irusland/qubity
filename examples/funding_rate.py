import logging
from datetime import timedelta


import binance

logging.basicConfig(level=logging.DEBUG)

from datetime import datetime

def to_timestamp(date):
    return int(date.timestamp() * 1000)


client = binance.Client()

def load_trades(start_time: datetime, end_time: datetime):
    start_time = to_timestamp(start_time)
    end_time = to_timestamp(end_time)
    print(start_time)
    while start_time < end_time:
        trades = client.futures_funding_rate(
            symbol='BTCUSDT',
            startTime=start_time,
        )
        for trade in trades:
            print(trade)
            time = datetime.fromtimestamp(trade['fundingTime'] / 1000)
            print(time)
            start_time = trade['fundingTime']
        print(start_time)
        print(len(trades))


load_trades(
    start_time=datetime.now() - timedelta(days=1),
    end_time=datetime.now() - timedelta(days=1) + timedelta(minutes=100),
)

