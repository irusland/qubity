from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, ConfigDict


class OpenInterest(BaseModel):
    symbol: str = Field(..., description="Trading pair symbol")
    sum_open_interest: float = Field(
        alias="sumOpenInterest", description="Total open interest"
    )
    sum_open_interest_value: float = Field(
        alias="sumOpenInterestValue", description="Total open interest value"
    )
    timestamp: datetime = Field(
        alias="timestamp", description="Timestamp of the data in UTC"
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class Period(StrEnum):
    ONE_MINUTE = '1m'
    FIVE_MINUTES = '5m'
    FIFTEEN_MINUTES = '15m'
    THIRTY_MINUTES = '30m'
    ONE_HOUR = '1h'
    TWO_HOURS = '2h'
    FOUR_HOURS = '4h'
    SIX_HOURS = '6h'
    TWELVE_HOURS = '12h'
    ONE_DAY = '1d'
