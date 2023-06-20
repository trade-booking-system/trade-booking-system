from fastapi import HTTPException
from schema import Trade
import redis

def booktrade(client: redis.Redis, trade: Trade):
    key = f"trades:{trade.account}:{trade.date.isoformat()}"
    json_data= trade.json()
    client.hset(key, trade.id, json_data)
    client.publish("updatePositions", f"{trade.account}:{trade.stock_ticker}:{get_amount(trade)}")
    return {"Key": key, "Field": trade.id}

def update_trade(trade_id, account, date, updated_type, updated_amount, client: redis.Redis):
    key= f"trades:{account}:{date}"
    json_trade= client.hget(key, trade_id)
    if json_trade == None:
        raise HTTPException(status_code= 404, detail= "trade does not exist")
    trade= Trade.parse_raw(json_trade)
    # undo previous version of trade
    amount= -get_amount(trade)
    if updated_amount:
        trade.amount= updated_amount
    if updated_type:
        trade.type= updated_type
    amount+= get_amount(trade)
    client.publish("updatePositions", f"{trade.account}:{trade.stock_ticker}:{amount}")
    trade.version= trade.version+1
    client.hset(key, trade_id, trade.json())

def get_trades(client: redis.Redis):
    trades= []
    for key in client.keys("trades:*"):
        data= client.hgetall(key)
        for json_object in data.values():
            trade_object= Trade.parse_raw(json_object)
            trades.append(trade_object)
    return trades

def query_trades(account: str, year: str, month: str, day: str, client: redis.Redis):
    trades = []
    for key in client.keys(f"trades:{account}:{year}-{month}-{day}"):
        data = client.hgetall(key)
        for json_object in data.values():
            trades.append(Trade.parse_raw(json_object))
    return trades

def get_accounts(client: redis.Redis):
    keys = client.keys("trades:*")
    accounts = set()
    for key in keys:
        accounts.add(key.split(":")[1])
    return accounts

def get_amount(trade: Trade):
    return trade.amount if trade.type == "buy" else -trade.amount
