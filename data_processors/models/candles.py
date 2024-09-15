
from pydantic import BaseModel, Field
from datetime import datetime


class Candle(BaseModel):
    timestamp: datetime = Field(description="Timestamp of the candle")
    open_timestamp: datetime | None = Field(None, description="Timestamp of the open price")
    close_timestamp: datetime | None = Field(None, description="Timestamp of the open price")

    # Open prices
    open_spot: float | None = Field(None, description="Open price on spot market")
    open_perp: float | None = Field(None, description="Open price on perpetual futures market")

    # High prices
    high_spot: float | None = Field(None, description="High price on spot market")
    high_perp: float | None = Field(None, description="High price on perpetual futures market")

    # Low prices
    low_spot: float | None = Field(None, description="Low price on spot market")
    low_perp: float | None = Field(None, description="Low price on perpetual futures market")

    # Close prices
    close_spot: float | None = Field(None, description="Close price on spot market")
    close_perp: float | None = Field(None, description="Close price on perpetual futures market")

    # Total volumes
    volume_total: float | None = Field(None, description="Total traded volume across all markets")
    volume_spot: float | None = Field(None, description="Traded volume on spot market")
    volume_perp: float | None = Field(None, description="Traded volume on perpetual futures market")

    # Buy volumes
    buy_volume_total: float | None = Field(None, description="Total buy volume across all markets")
    buy_volume_spot: float | None = Field(None, description="Buy volume on spot market")
    buy_volume_perp: float | None = Field(None, description="Buy volume on perpetual futures market")

    # Sell volumes
    sell_volume_total: float | None = Field(None, description="Total sell volume across all markets")
    sell_volume_spot: float | None = Field(None, description="Sell volume on spot market")
    sell_volume_perp: float | None = Field(None, description="Sell volume on perpetual futures market")

    # Total trades
    trades_total: int | None = Field(None, description="Total number of trades across all markets")
    trades_spot: int | None = Field(None, description="Number of trades on spot market")
    trades_perp: int | None = Field(None, description="Number of trades on perpetual futures market")

    # Buy trades
    buy_trades_total: int | None = Field(None, description="Total number of buy trades across all markets")
    buy_trades_spot: int | None = Field(None, description="Number of buy trades on spot market")
    buy_trades_perp: int | None = Field(None, description="Number of buy trades on perpetual futures market")

    # Sell trades
    sell_trades_total: int | None = Field(None, description="Total number of sell trades across all markets")
    sell_trades_spot: int | None = Field(None, description="Number of sell trades on spot market")
    sell_trades_perp: int | None = Field(None, description="Number of sell trades on perpetual futures market")

    # Additional fields
    open_interest: float | None = Field(None, description="Open interest value for perpetual futures")
    funding_rate: float | None = Field(None, description="Funding rate for perpetual futures")
