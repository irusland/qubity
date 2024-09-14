from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class FundingRate(BaseModel):
    symbol: str = Field(..., description="Trading pair symbol")
    funding_rate: float = Field(
        alias="fundingRate", description="Total open interest"
    )
    mark_price: float = Field(
        alias="markPrice", description="Total open interest value"
    )
    timestamp: datetime = Field(
        alias="fundingTime", description="Timestamp of the data in UTC"
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )
