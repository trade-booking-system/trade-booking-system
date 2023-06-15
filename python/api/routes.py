import redis
from fastapi import APIRouter, Depends
from utils import booktrade as tradebooker
from utils.redis_initializer import get_redis_client
from typing import List, Dict
from schema import Trade

app= APIRouter()

@app.put("/put")
async def put(trade: Trade, client: redis.Redis = Depends(get_redis_client)) -> Dict[str, str]:
    return tradebooker.booktrade(client, trade)

@app.get("/get/")
async def get(client: redis.Redis = Depends(get_redis_client)) -> List[Trade]:
    return tradebooker.getTrades(client)

@app.get("/accounts/")
async def get_accounts(client: redis.Redis = Depends(get_redis_client)) -> List[str]:
    return tradebooker.get_accounts(client)
