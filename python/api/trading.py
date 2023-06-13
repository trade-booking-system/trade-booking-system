from fastapi import APIRouter
import redis
import os

app= APIRouter()
r= redis.Redis(host= os.getenv("REDIS_HOST"), port= 6379, db= 0)

@app.put("/put/{key}/{val}")
async def put(key : str, val):
    r.set(key, val)

@app.get("/get/{key}")
async def get(key : str):
    return {"Key" : r.get(key)}
