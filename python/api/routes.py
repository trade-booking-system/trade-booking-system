from fastapi import APIRouter
import redis
import os
from uuid import uuid4
import json
import schema

app= APIRouter()
r= redis.Redis(host= os.getenv("REDIS_HOST"), port= 6379, db= 0)

"""

@app.put("/put/{key}/{val}")
async def put(key : str, val):
    r.set(key, val)

@app.get("/get/{key}")
async def get(key : str):
    return {"Key" : r.get(key)}

"""

@app.put("/put")
async def put(trade: schema.Trade):

    trade_id = str(uuid4())
    key = f"trades:{trade.account}:{trade.date.strftime('%Y%m%d')}"

    data = trade.dict()
    data["id"] = trade_id
    json_data = json.dumps(data)

    r.hset(key, trade_id, json_data)

    return {"Key": key, "Field": trade_id}

@app.get("/get/{key}")
async def get(key : str):
    return {"Key" : r.get(key)}


