from redis import Redis
from datetime import datetime, date as date_obj
from schema.schema import ProfitLoss, Position, Price, History
from utils import market_calendar


def get_price(client: Redis, ticker: str, date: date_obj) -> Price:
    price_json= client.hget("livePrices:"+ticker, date.isoformat())
    if price_json is None:
        return None
    return Price.parse_raw(price_json)

def get_position(client: Redis, account: str, ticker: str) -> Position:
    json_position= client.hget("positions:"+account, ticker)
    if json_position == None:
        return None
    return Position.parse_raw(json_position)

# def set_positions():


def get_pl(client: Redis, account: str, ticker: str) -> ProfitLoss:
    date= datetime.now().date()
    pl_json= client.hget(f"p&l:{account}:{ticker}", date.isoformat())
    if pl_json == None:
        return ProfitLoss(trade_pl= 0, position_pl= 0, account= account, ticker= ticker)
    return ProfitLoss.parse_raw(pl_json)

# def set_pl():


def get_startup_date(client: Redis) -> date_obj:
    startup_date= client.get("startupDate")
    if startup_date == None:
        return datetime.now().date()
    return date_obj.fromisoformat(startup_date)

# def get_stocks() -> list[str]:

# def add_to_stocks(client: Redis, account: str, ticker: str):


def set_history(client: Redis, account: str, date: date_obj, id: str, history: History):
    key = f"trades:{account}:{date.isoformat()}"
    json_data= history.json()
    client.hset(key, id, json_data)



