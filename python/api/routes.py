import redis
from fastapi import APIRouter, Depends
from utils import booktrade as tradebooker
from utils.redis_initializer import get_redis_client
import schema

app= APIRouter()

"""

@app.put("/put/{key}/{val}")
async def put(key : str, val):
    r.set(key, val)

@app.get("/get/{key}")
async def get(key : str):
    return {"Key" : r.get(key)}

"""

@app.put("/put")
async def put(trade: schema.Trade, client: redis.Redis = Depends(get_redis_client)):
    print(trade)
    return tradebooker.booktrade(client, trade)

@app.get("/get/")
async def get(client: redis.Redis = Depends(get_redis_client)):
    return tradebooker.getTrades(client)
