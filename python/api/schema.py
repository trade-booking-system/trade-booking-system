from pydantic import BaseModel, validator
from datetime import date
from uuid import uuid4

# prices represented as 1 penny = 1 and 1 dollar = 100
# dates represented as YYYYMMDD

def create_calendar(timedate: str):
    if not timedate.isalnum():
        raise ValueError("date is not made up of only numbers")
    if len(timedate) != 8:
        raise ValueError("date is not of length 8")
    year= int(timedate[:4])
    month= int(timedate[4:6])
    day= int(timedate[6:])
    return date(year, month, day)

def date_validator(cls, timedate: str):
    create_calendar(timedate)
    return timedate

def validate_is_positive(cls, value):
    if value >= 0:
        return value
    raise ValueError("value is negative")

class Trade(BaseModel):
    id: int= None
    account: str
    type: str
    stock_ticker: str
    amount: int
    date: str

    _amount_validator= validator("amount", allow_reuse= True)(validate_is_positive)
    _date_validator= validator("date", allow_reuse= True)(date_validator)

    @validator("id", pre= True, always= True)
    def create_id(id):
        if id != None:
            return id
        return int(uuid4())

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
    date: str
    price: int

    _date_validator= validator("date", allow_reuse= True)(date_validator)
    _price_validator= validator("price", allow_reuse= True)(validate_is_positive)
