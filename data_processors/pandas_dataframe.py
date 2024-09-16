import csv
import time
from datetime import datetime, timedelta, timezone
from typing import Iterator

import binance
import pandas as pd

from data_loaders.clients import (
    SpotClient, PerpClient, OpenInterestClient,
    FundingRateClient, TData,
)
from data_loaders.loader import Loader
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


class PandasCandleProcessor:
    """
    Processes data with pandas and fills candles
    """
    def __init__(
        self,
        spot_client: SpotClient,
        perp_client: PerpClient,
        open_interest_client: OpenInterestClient,
        funding_rate_client: FundingRateClient,
    ):
        self._spot_loader = Loader(data_client=spot_client)
        self._perp_loader = Loader(data_client=perp_client)
        self._open_interest_loader = Loader(data_client=open_interest_client)
        self._funding_rate_loader = Loader(data_client=funding_rate_client)

    def _get_data_df(self, start_time: datetime, end_time: datetime, loader: Loader) -> pd.DataFrame:
        data = [
            data.dict() for data in loader.load(
                start_time=start_time,
                end_time=end_time,
            )
        ]
        if not data:
            return pd.DataFrame(columns=['timestamp'])
        return pd.DataFrame(data)

    def process(self, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        spot_df = self._get_data_df(start_time, end_time, self._spot_loader)
        perp_df = self._get_data_df(start_time, end_time, self._perp_loader)
        open_interest_df = self._get_data_df(start_time, end_time, self._open_interest_loader)
        funding_rate_df = self._get_data_df(start_time, end_time, self._funding_rate_loader)

        for df in [spot_df, perp_df]:
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True, drop=False)

        for df in [open_interest_df, funding_rate_df]:
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)

        def _aggregation(group):
            total_quantity = group['quantity'].sum()
            total_trades = group['trade_id'].nunique()
            open_price = group['price'].iloc[0]
            open_timestamp = group['timestamp'].iloc[0]
            close_price = group['price'].iloc[-1]
            close_timestamp = group['timestamp'].iloc[-1]
            high_price = group['price'].max()
            low_price = group['price'].min()

            buy_trades = group.loc[~group['is_buyer_maker']]
            buy_volume = buy_trades['quantity'].sum()
            buy_trade_count = buy_trades['trade_id'].nunique()

            sell_trades = group.loc[group['is_buyer_maker']]
            sell_volume = sell_trades['quantity'].sum()
            sell_trade_count = sell_trades['trade_id'].nunique()

            result = {
                'open': open_price,
                'open_timestamp': open_timestamp,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'close_timestamp': close_timestamp,
                'volume': total_quantity,
                'trades': total_trades,
                'buy_volume': buy_volume,
                'sell_volume': sell_volume,
                'buy_trades': buy_trade_count,
                'sell_trades': sell_trade_count,
            }
            return pd.Series(result)

        if not spot_df.empty:
            spot_resampled = spot_df.resample('5min').apply(_aggregation)
            spot_resampled = spot_resampled.rename(columns={
                'open': 'open_spot',
                'open_timestamp': 'open_timestamp_spot',
                'high': 'high_spot',
                'low': 'low_spot',
                'close': 'close_spot',
                'close_timestamp': 'close_timestamp_spot',
                'volume': 'volume_spot',
                'trades': 'trades_spot',
                'buy_volume': 'buy_volume_spot',
                'sell_volume': 'sell_volume_spot',
                'buy_trades': 'buy_trades_spot',
                'sell_trades': 'sell_trades_spot',
            })
        else:
            spot_resampled = pd.DataFrame()

        if not perp_df.empty:
            perp_resampled = perp_df.resample('5min').apply(_aggregation)
            perp_resampled = perp_resampled.rename(columns={
                'open': 'open_perp',
                'open_timestamp': 'open_timestamp_perp',
                'high': 'high_perp',
                'low': 'low_perp',
                'close': 'close_perp',
                'close_timestamp': 'close_timestamp_perp',
                'volume': 'volume_perp',
                'trades': 'trades_perp',
                'buy_volume': 'buy_volume_perp',
                'sell_volume': 'sell_volume_perp',
                'buy_trades': 'buy_trades_perp',
                'sell_trades': 'sell_trades_perp',
            })
        else:
            perp_resampled = pd.DataFrame()

        if not open_interest_df.empty:
            numeric_cols_oi = open_interest_df.select_dtypes(include='number').columns
            open_interest_resampled = open_interest_df[numeric_cols_oi].resample('5min').mean()
            if 'sum_open_interest' in open_interest_resampled.columns:
                open_interest_resampled.rename(columns={'sum_open_interest': 'open_interest'}, inplace=True)
        else:
            open_interest_resampled = pd.DataFrame(columns=['timestamp', 'open_interest'])

        if not funding_rate_df.empty:
            numeric_cols_fr = funding_rate_df.select_dtypes(include='number').columns
            funding_rate_resampled = funding_rate_df[numeric_cols_fr].resample('5min').mean()
            if 'funding_rate_column_name' in funding_rate_resampled.columns:
                funding_rate_resampled.rename(columns={'funding_rate_column_name': 'funding_rate'}, inplace=True)
        else:
            funding_rate_resampled = pd.DataFrame(columns=['timestamp', 'funding_rate'])

        combined_df = spot_resampled.join(perp_resampled, how='outer')

        combined_df['volume_total'] = combined_df[['volume_spot', 'volume_perp']].sum(axis=1, skipna=True)
        combined_df['buy_volume_total'] = combined_df[['buy_volume_spot', 'buy_volume_perp']].sum(axis=1, skipna=True)
        combined_df['sell_volume_total'] = combined_df[['sell_volume_spot', 'sell_volume_perp']].sum(axis=1, skipna=True)
        combined_df['trades_total'] = combined_df[['trades_spot', 'trades_perp']].sum(axis=1, skipna=True)
        combined_df['buy_trades_total'] = combined_df[['buy_trades_spot', 'buy_trades_perp']].sum(axis=1, skipna=True)
        combined_df['sell_trades_total'] = combined_df[['sell_trades_spot', 'sell_trades_perp']].sum(axis=1, skipna=True)

        combined_df['open_timestamp'] = combined_df[['open_timestamp_spot', 'open_timestamp_perp']].min(axis=1)
        combined_df['close_timestamp'] = combined_df[['close_timestamp_spot', 'close_timestamp_perp']].max(axis=1)

        if not open_interest_resampled.empty:
            combined_df = combined_df.join(open_interest_resampled, how='outer')
        if not funding_rate_resampled.empty:
            combined_df = combined_df.join(funding_rate_resampled, how='outer')

        combined_df.reset_index(inplace=True)

        combined_df.ffill(inplace=True)

        return combined_df


if __name__ == '__main__':
    client = binance.Client()
    spot_client = SpotClient(client=client)
    perp_client = PerpClient(client=client)
    open_interest_client = OpenInterestClient(client=client)
    funding_rate_client = FundingRateClient(client=client)
    processor = PandasCandleProcessor(
        spot_client=spot_client,
        perp_client=perp_client,
        open_interest_client=open_interest_client,
        funding_rate_client=funding_rate_client,
    )

    now = datetime(
        year=2024, month=9, day=13, hour=7, minute=0, second=0, tzinfo=timezone.utc
    )
    start = now - timedelta(days=1)
    # end = start + timedelta(days=1)
    end = start + timedelta(minutes=20)
    candles: pd.DataFrame = processor.process(start_time=start, end_time=end)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    candles.to_feather(PROCESSED_DIR / 'result_pandas.feather')
