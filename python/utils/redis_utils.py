from typing import Generator
from redis import Redis
from datetime import datetime, date as date_obj
from schema.schema import (
    Trade, ProfitLoss, TradeProfitLoss, Position, Price, History, TradeWithPl, PositionWithPl
)


def set_position(client: Redis, account: str, ticker: str, position: Position):
    key= "positions:"+account
    client.hset(key, ticker, position.json())

def get_position(client: Redis, account: str, ticker: str) -> Position:
    key= "positions:"+account
    json_position= client.hget(key, ticker)
    if json_position == None:
        return None
    return Position.parse_raw(json_position)

def get_positions(client: Redis, account: str = "*") -> list[Position]:
    positions: list[Position] = []
    for key in client.scan_iter("positions:" + account):
        for _, value in client.hscan_iter(key):
            positions.append(Position.parse_raw(value))
    return positions

def set_position_snapshot(client: Redis, account: str, date: date_obj, ticker: str, position: Position):
    key= f"positionsSnapshots:{account}:{date.isoformat()}"
    client.hset(key, ticker, position.json())

def get_position_snapshot(client: Redis, account: str, date: date_obj, ticker: str) -> Position:
    key= f"positionsSnapshots:{account}:{date.isoformat()}"
    json_snapshot= client.hget(key, ticker)
    if json_snapshot == None:
        return None
    return Position.parse_raw(json_snapshot)

def set_pl(client: Redis, account: str, ticker: str, date: date_obj, pl: ProfitLoss):
    key = f"p&l:{account}:{ticker}"
    client.hset(key, date.isoformat(), pl.json())

def get_pl(client: Redis, account: str, ticker: str, date: date_obj, default= None) -> ProfitLoss:
    key = f"p&l:{account}:{ticker}"
    pl_json= client.hget(key, date.isoformat())
    if pl_json == None:
        return default
    return ProfitLoss.parse_raw(pl_json)

def get_all_pl(client: Redis, pattern: str) -> dict[str, dict[str, str]]:
    """Fetches all the fields and their values for the keys that match the provided pattern"""
    keys = client.keys(pattern)
    result = {key: client.hgetall(key) for key in keys}
    return result

def get_trade(client: Redis, account: str, id: str, date: date_obj, default = None) -> Trade:
    key = f"trades:{account}:{date.isoformat()}"
    history_json = client.hget(key, id)
    if history_json == None:
        return default
    return History.parse_raw(history_json).get_current_trade()

def set_trade_pl(client: Redis, id: str, date: date_obj, pl: TradeProfitLoss):
    key = f"trade_p&l:{date.isoformat()}"
    client.hset(key, id, pl.json())

def get_trade_pl(client: Redis, id: str, date: date_obj, default = None) -> TradeProfitLoss:
    pl_json = client.hget(f"trade_p&l:{date.isoformat()}", id)
    if pl_json == None:
        return default
    return TradeProfitLoss.parse_raw(pl_json)

def get_startup_date(client: Redis) -> date_obj:
    startup_date= client.get("startupDate")
    if startup_date == None:
        return datetime.now().date()
    return date_obj.fromisoformat(startup_date)

def get_stocks(client: Redis) -> list[str]:
    return client.smembers("stocks", )

def add_to_stocks(client: Redis, account: str, ticker: str):
    value= account+":"+ticker
    client.sadd("stocks", value)

def set_history(client: Redis, account: str, date: date_obj, id: str, history: History):
    key = f"trades:{account}:{date.isoformat()}"
    json_data= history.json()
    client.hset(key, id, json_data)

#def get_history()

#def get_trade():
#    return get_history().get_current_trade()

def set_price(client: Redis, stock_ticker: str, date: date_obj, price: Price):
    key= "livePrices:" + stock_ticker
    client.hset(key, date.isoformat(), price.json())

def get_price(client: Redis, ticker: str, date: date_obj) -> Price:
    key= "livePrices:"+ticker
    price_json= client.hget(key, date.isoformat())
    if price_json is None:
        return None
    return Price.parse_raw(price_json)

def get_trades_by_day_and_account(client: Redis, account: str, date: date_obj) -> list[Trade]:
    trades= list()
    key = f"trades:{account}:{date.isoformat()}"
    values= client.hgetall(key)
    for _, history_json in values.items():
        trade= History.parse_raw(history_json).get_current_trade()
        trades.append(trade)
    return trades

def get_trades_by_day(client: Redis, date: date_obj) -> list[Trade]:
    trades= list()
    for key in client.scan_iter(f"trades:*:{date.isoformat()}"):
        for _, history_json in client.hscan_iter(key):
            trade= History.parse_raw(history_json).get_current_trade()
            trades.append(trade)
    return trades

def query_trades(client: Redis, account: str = "*", year: str = "*",
                    month: str = "*", day: str = "*") -> Generator[Trade, None, None]:
    for key in client.scan_iter(f"trades:{account}:{year}-{month}-{day}"):
        for _, json_object in client.hscan_iter(key):
            yield History.parse_raw(json_object).get_current_trade()

def merge_trade(client: Redis, trade: Trade) -> TradeWithPl:
    pl = get_trade_pl(client, trade.id, trade.date)
    if pl == None:
        return TradeWithPl(**trade.dict(), **TradeProfitLoss(
            account=trade.account, trade_id=trade.id, date=date_obj(1, 1, 1)
        ).dict(exclude=set(["account", "date"])), pnl_valid=False)
    else:
        return TradeWithPl(**trade.dict(), **pl.dict(exclude=set(["account", "date"])), pnl_valid=True)

def merge_position(client: Redis, position: Position, date: date_obj) -> PositionWithPl:
    pl = get_pl(client, position.account, position.stock_ticker, date)
    if pl == None:
        return PositionWithPl(**position.dict(), **ProfitLoss(
            account=position.account, ticker=position.stock_ticker
        ).dict(exclude=set(["account"])), pnl_valid=False)
    else:
        return PositionWithPl(**position.dict(), **pl.dict(exclude=set(["account"])), pnl_valid=True)
