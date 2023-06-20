
from pydantic import BaseModel, validator
from datetime import datetime

class Position(BaseModel):
    account: str
    stock_ticker: str
    amount: int
    last_aggregation_time: datetime
    last_aggregation_host: str

    @validator("amount")
    def validate_amount(cls, amount):
        if amount < 0:
            raise ValueError
        return amount
    