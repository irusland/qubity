from datetime import datetime

from pydantic import Field

from data_loaders.models.timedata import TimeData


class Trade(TimeData):
    trade_id: int = Field(alias='a', description='Aggregate tradeId')
    price: float = Field(alias='p', description='Price')
    quantity: float = Field(alias='q', description='Quantity')
    first_trade_id: int = Field(0, alias='f', description='First tradeId')
    last_trade_id: int = Field(0, alias='l', description='Last tradeId')
    timestamp: datetime = Field(alias='T', description='Timestamp')
    is_buyer_maker: bool = Field(alias='m', description='Was the buyer the maker?')
    is_best_price_match: bool = Field(False, alias='M', description='Was the trade the best price match?')
