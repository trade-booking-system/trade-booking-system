from typing import Optional
from redis import Redis
from datetime import datetime, date as date_obj
from schema.schema import ProfitLoss, Position, Price
from utils import market_calendar


def calculate_position_pl(price: float, closing_price: float, position: int) -> float:
    return (price - closing_price) * position

def calculate_trade_pl(closing_price: float, price: float, amount) -> float:
    return (closing_price - price) * amount

def get_price(client: Redis, ticker: str, date: date_obj) -> Optional[float]:
    price_json= client.hget("livePrices:"+ticker, date.isoformat())
    if price_json is None:
        return None
    price= Price.parse_raw(price_json)
    return price.price

def get_position(client: Redis, account: str, ticker: str) -> Optional[Position]:
    json_position= client.hget("positions:"+account, ticker)
    if json_position == None:
        return None
    return Position.parse_raw(json_position)

def get_pl(client: Redis, account: str, ticker: str) -> ProfitLoss:
    date= datetime.now().date()
    pl_json= client.hget(f"p&l:{account}:{ticker}", date.isoformat())
    if pl_json == None:
        return ProfitLoss(trade_pl= 0, position_pl= 0, account= account, ticker= ticker)
    return ProfitLoss.parse_raw(pl_json)

def get_previous_closing_price(client: Redis, ticker: str) -> Optional[float]:
    date= market_calendar.get_most_recent_trading_day()
    return get_price(client, ticker, date)

def get_startup_date(client: Redis) -> date_obj:
    startup_date= client.get("startupDate")
    if startup_date == None:
        return datetime.now().date()
    return date_obj.fromisoformat(startup_date)
