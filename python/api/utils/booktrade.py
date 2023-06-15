import redis
import schema
import json

def booktrade(client: redis.Redis, trade: schema.Trade):
    key = f"trades:{trade.account}:{trade.date.isoformat()}"
    json_data= trade.json()
    client.hset(key, trade.id, json_data)
    return {"Key": key, "Field": trade.id}

def getTrades(client: redis.Redis):
    return (client.hgetall(key) for key in client.keys("*"))
