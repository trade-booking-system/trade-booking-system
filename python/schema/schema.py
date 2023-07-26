from pydantic import BaseModel, validator
from datetime import date, time, datetime
from uuid import uuid4

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
    price: float | None
    version: int= 1

    def get_amount(cls) -> int:
        return cls.amount if cls.type == "buy" else -cls.amount

    _amount_validator= validator("amount", allow_reuse= True)(validate_is_positive)

    @validator("stock_ticker")
    def validate_is_uppercase(stock_ticker: str):
        if stock_ticker.isupper():
            return stock_ticker
        return stock_ticker.upper()

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
        if type == "b":
            type= "buy"
        if type == "s":
            type= "sell"
        if type in ("sell", "buy"):
            return type
        raise ValueError("type does not equal sell or buy")

class Position(BaseModel):
    account: str
    stock_ticker: str
    amount: int
    last_aggregation_time: datetime
    last_aggregation_host: str

class Price(BaseModel):
    price: float
    stock_ticker: str
    last_updated: time

    def is_closing_price(cls) -> bool:
        return cls.last_updated >= time(hour= 16)

    _price_validator= validator("price", allow_reuse= True)(validate_is_positive)

class History(BaseModel):
    trades: list[Trade]= list()
    current_version: int= 1

    def get_current_trade(cls):
        return cls.trades[cls.current_version-1]
    
    def add_updated_trade(cls, trade: Trade):
        cls.trades.append(trade)
        cls.current_version= trade.version

class ProfitLoss(BaseModel):
    trade_pl: float= 0
    position_pl: float= 0
    account: str
    ticker: str

    def get_total_pl(cls) -> float:
        return cls.trade_pl + cls.position_pl

class TradeProfitLoss(BaseModel):
    account: str
    trade_id: str
    trade_pl: float = 0
    closing_price: float = 0
    date: date

class TradeWithPl(Trade, TradeProfitLoss):
    pnl_valid: bool

class PositionWithPl(Position, ProfitLoss):
    pnl_valid: bool

class PositionResponse(BaseModel):
    positions: list[PositionWithPl]
    count: int
    
    _count_validator = validator("count", allow_reuse=True)(validate_is_positive)
