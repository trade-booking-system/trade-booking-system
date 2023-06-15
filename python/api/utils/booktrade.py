import redis
import schema
import json

def booktrade(client: redis.Redis, trade: schema.Trade):
    key = f"trades:{trade.account}:{trade.date.isoformat()}"
    json_data= trade.json()
    client.hset(key, trade.id, json_data)
    return {"Key": key, "Field": trade.id}

def getTrades(client: redis.Redis):
    trades = []
    for key in client.keys("*"):
        trade = client.hgetall(key)
        for trade_object in trade.items():
            trade_object = trade_object.decode("utf-8")
            trade_object = json.loads(trade_object)
            trades.append(trade_object)
    return trades

