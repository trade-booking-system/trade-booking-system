from pydantic import BaseModel, validator
from datetime import date, time, datetime
from typing import List
from uuid import uuid4

# prices represented as 1 penny = 1 and 1 dollar = 100
# dates represented as YYYY-MM-DD
# time represented as HH:MM:SS

def validate_is_positive(cls, value):
    if value >= 0:
        return value
    raise ValueError("value is negative")

class Trade(BaseModel):
    id: str | None
    account: str
    type: str
    stock_ticker: str
    amount: int
    date: date | None
    time: time | None
    user: str
    version: int= 1

    _amount_validator= validator("amount", allow_reuse= True)(validate_is_positive)

    @validator("id", pre= True, always= True)
    def create_id(id):
        if id != None:
            return id
        return str(uuid4())
    
    @validator("date", pre= True, always= True)
    def create_date(date_of_trade):
        if date_of_trade != None:
            return date_of_trade
        return date.today()
    
    @validator("time", pre= True, always= True)
    def create_time(time_of_trade) -> time:
        if time_of_trade != None:
            return time_of_trade
        return datetime.now().time()

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
    current_version: int= 1

    def get_current_trade(cls):
        return cls.trades[cls.current_version-1]
    
    def add_updated_trade(cls, trade: Trade):
        cls.trades.append(trade)
        cls.current_version= trade.version

class PositionResponse(BaseModel):
    positions: List[Position]
    count: int
    
    _count_validator = validator("count", allow_reuse=True)(validate_is_positive)