import redis_initializer as redis
from api import schema
import json

def booktrade(trade: schema.Trade):
    key = f"trades:{trade.account}:{trade.date.strftime('%Y%m%d')}"
    data = trade.dict()
    json_data = json.dumps(data)
    redis.hset(key, trade.id, json_data)
    return {"Key": key, "Field": trade.id}

def getTrades():
    redis.r
