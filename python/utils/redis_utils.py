from typing import Generator
from redis import Redis
from datetime import datetime, date as date_obj
from schema.schema import Trade, ProfitLoss, Position, Price, History


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

def set_pl(client: Redis, account: str, ticker: str, date:date_obj, pl: ProfitLoss):
    key = f"p&l:{account}:{ticker}"
    client.hset(key, date.isoformat(), pl.json())

def get_pl(client: Redis, account: str, ticker: str, default= None) -> ProfitLoss:
    date= datetime.now().date()
    pl_json= client.hget(f"p&l:{account}:{ticker}", date.isoformat())
    if pl_json == None:
        return default
    return ProfitLoss.parse_raw(pl_json)

def get_startup_date(client: Redis) -> date_obj:
    startup_date= client.get("startupDate")
    if startup_date == None:
        return datetime.now().date()
    return date_obj.fromisoformat(startup_date)

def get_stocks(client: Redis) -> list[str]:
    return client.smembers("p&lStocks")

# def add_to_stocks(client: Redis, account: str, ticker: str):


def set_history(client: Redis, account: str, date: date_obj, id: str, history: History):
    key = f"trades:{account}:{date.isoformat()}"
    json_data= history.json()
    client.hset(key, id, json_data)

def query_trades(client: Redis, account: str = "*", year: str = "*",
                    month: str = "*", day: str = "*") -> Generator[Trade, None, None]:
    for key in client.scan_iter(f"trades:{account}:{year}-{month}-{day}"):
        for _, json_object in client.hscan_iter(key):
            yield History.parse_raw(json_object).get_current_trade()
