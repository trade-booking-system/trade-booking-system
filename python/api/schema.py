from pydantic import BaseModel, validator
from datetime import date
from uuid import uuid4

# prices represented as 1 penny = 1 and 1 dollar = 100
# dates represented as YYYYMMDD

def date_parser(cls, timedate: str):
    if not timedate.isalnum():
        raise ValueError("date is not made up of only numbers")
    if len(timedate) != 8:
        raise ValueError("date is not of length 8")
    year= int(timedate[:4])
    month= int(timedate[4:6])
    day= int(timedate[6:])
    return date(year, month, day)

def validate_is_positive(cls, value):
    if value >= 0:
        return value
    raise ValueError("value is negative")

class Trade(BaseModel):
    id: int= int(uuid4())
    account: str
    type: str
    stock_ticker: str
    amount: int
    date: date

    _amount_validator= validator("amount", allow_reuse= True)(validate_is_positive)
    _date_validator= validator("date", allow_reuse= True, pre= True)(date_parser)

    @validator("type")
    def validate_type(cls, type):
        if type in ("sell", "buy"):
            return type
        raise ValueError("type does not equal sell or buy")

class Position(BaseModel):
    account: str
    stock_ticker: str
    amount: int

    _amount_validator= validator("amount", allow_reuse= True)(validate_is_positive)

class Price(BaseModel):
    stock_ticker: str
    date: date
    price: int

    _date_validator= validator("date", allow_reuse= True, pre= True)(date_parser)
    _price_validator= validator("price", allow_reuse= True)(validate_is_positive)
