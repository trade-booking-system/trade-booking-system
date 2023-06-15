from utils import redis_initializer as redis
import schema
import json

def booktrade(trade: schema.Trade):
    key = f"trades:{trade.account}:{trade.date.isoformat()}"
    json_data= trade.json()
    redis.r.hset(key, trade.id, json_data)
    return {"Key": key, "Field": trade.id}

def getTrades():
    return (redis.r.hgetall(key) for key in redis.r.keys("*"))
