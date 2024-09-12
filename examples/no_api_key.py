import binance
import logging
logging.basicConfig(level=logging.DEBUG)

client = binance.Client()
r = client.get_historical_klines('BTCUSDT', client.KLINE_INTERVAL_1DAY, '1-Dec-2017', '10-Dec-2017')
for rr in r:
    print(rr)
