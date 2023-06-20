from typing import List
from pydantic import BaseModel, validator
from datetime import date, time, datetime
from uuid import uuid4

# prices represented as 1 penny = 1 and 1 dollar = 100
# dates represented as YYYY-MM-DD
# time represented as HH:MM:SS

def validate_is_positive(cls, value):
    if value >= 0:
        return value
    raise ValueError("value is negative")

class Trade(BaseModel):
    id: str= None
    account: str
    type: str
    stock_ticker: str
    amount: int
    date: date
    time: time
    user: str
    version: int= 1

    _amount_validator= validator("amount", allow_reuse= True)(validate_is_positive)

    @validator("id", pre= True, always= True)
    def create_id(id):
        if id != None:
            return id
        return str(uuid4())

    @validator("type")
    def validate_type(cls, type):
        if type in ("sell", "buy"):
            return type
        raise ValueError("type does not equal sell or buy")

class Position(BaseModel):
    account: str
    stock_ticker: str
    amount: int
    last_aggregation_time: datetime
    last_aggregation_host: str

    _amount_validator= validator("amount", allow_reuse= True)(validate_is_positive)

class Price(BaseModel):
    stock_ticker: str
    date: date
    price: int

    _price_validator= validator("price", allow_reuse= True)(validate_is_positive)

class History(BaseModel):
    trades: List[Trade]= list()
    current_trade: int= 1

    def get_current_trade(cls):
        return cls.trades[cls.current_trade-1]
    
    def update_trade(cls, updated_type: str, updated_amount: str, old_trade: Trade):
        updates= dict()
        if updated_amount:
            updates["amount"]= updated_amount
        if updated_type:
            updates["type"]= updated_type
        trade= old_trade.copy(update= updates)
        trade.version= trade.version+1
        cls.trades.append(trade)
        cls.current_trade+= 1
        return trade

class PositionResponse(BaseModel):
    positions: List[Position]
    count: int
    
    _count_validator = validator("count", allow_reuse=True)(validate_is_positive)
