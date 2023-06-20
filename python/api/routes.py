import redis
from fastapi import APIRouter, Depends
from utils import booktrade as tradebooker
from utils.redis_initializer import get_redis_client_zero
from typing import List, Dict, Set
from schema import Trade

app= APIRouter()

@app.put("/bookTrade/")
async def book_trade(trade: Trade, client: redis.Redis = Depends(get_redis_client_zero)) -> Dict[str, str]:
    return tradebooker.booktrade(client, trade)

@app.post("/updateTrade")
def update_trade(trade_id: str, account: str, date: str, updated_type: str= None, updated_amount: int= None, 
                 client: redis.Redis = Depends(get_redis_client_zero)):
    tradebooker.update_trade(trade_id, account, date, updated_type, updated_amount, client) 

@app.get("/getTrades/")
async def get_trades(client: redis.Redis = Depends(get_redis_client_zero)) -> List[Trade]:
    return tradebooker.get_trades(client)

@app.get("/queryTrades/")
async def query_trades(account: str = "*", year: int = 0, month: int = 0, day: int = 0,
                       client: redis.Redis = Depends(get_redis_client_zero)) -> List[Trade]:
    def default(value: int, pad: int) -> str:
        return "*" if value == 0 else str(value).zfill(pad)
    return tradebooker.query_trades(account, default(year, 4), default(month, 2), default(day, 2), client)

@app.get("/getAccounts/")
async def get_accounts(client: redis.Redis = Depends(get_redis_client_zero)) -> Set[str]:
    return tradebooker.get_accounts(client)
