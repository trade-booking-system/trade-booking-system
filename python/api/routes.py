from fastapi import APIRouter
from utils import booktrade as tradebooker
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
async def put(trade: schema.Trade):
    print(trade)
    return tradebooker.booktrade(trade)

@app.get("/get/")
async def get():
    return tradebooker.getTrades()