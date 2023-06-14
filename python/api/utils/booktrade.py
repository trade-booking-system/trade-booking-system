from utils import redis_initializer as redis
import schema
import json

def booktrade(trade: schema.Trade):
    key = f"trades:{trade.account}:{schema.create_calendar(trade.date).strftime('%Y%m%d')}"
    data = trade.dict()
    json_data = json.dumps(data)
    redis.r.hset(key, trade.id, json_data)
    return {"Key": key, "Field": trade.id}

def getTrades():
    return redis.r.keys("*")
