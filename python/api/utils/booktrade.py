import redis
from schema import Trade

def booktrade(client: redis.Redis, trade: Trade):
    key = f"trades:{trade.account}:{trade.date.isoformat()}"
    json_data= trade.json()
    client.hset(key, trade.id, json_data)
    return {"Key": key, "Field": trade.id}

def getTrades(client: redis.Redis):
    trades= []
    for key in client.keys("trades:*"):
        data= client.hgetall(key)
        for json_object in data.values():
            trade_object= Trade.parse_raw(json_object)
            trades.append(trade_object)
    return trades
