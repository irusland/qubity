from datetime import datetime, timedelta

import binance
import logging
logging.basicConfig(level=logging.DEBUG)

client = binance.Client()

def to_timestamp(date):
    return int(date.timestamp() * 1000)


# trades = client.get_aggregate_trades(symbol='BTCUSDT',
#     startTime=to_timestamp(datetime.now()-timedelta(days=1)),
#     limit=1
# )
# trade = trades[0]
# trade_id = trade['a']
#
#
# has_new_trades = True
# print(trade_id)
# while has_new_trades:
#     trades = client.get_historical_trades(
#         symbol='BTCUSDT',
#         fromId=trade_id,
#     )
#     for trade in trades:
#         print(trade)
#
#         time = datetime.fromtimestamp(trade['time'] / 1000)
#         print(time)
#         trade_id = trade['id']
#         print(trade_id)
#     print(len(trades))

def load_trades(start_time: datetime, end_time: datetime):
    start_time = to_timestamp(start_time)
    end_time = to_timestamp(end_time)
    has_new_trades = True
    print(start_time)
    while start_time < end_time:
        trades = client.get_aggregate_trades(
            symbol='BTCUSDT',
            startTime=start_time,
        )
        for trade in trades:
            print(trade)
            time = datetime.fromtimestamp(trade['T'] / 1000)
            start_time = trade['T']
        print(start_time)
        print(len(trades))



load_trades(
    start_time=datetime.now() - timedelta(days=1),
    end_time=datetime.now() - timedelta(days=1) + timedelta(minutes=1),
)

