import redis
from fastapi import APIRouter, Depends
from utils import booktrade as tradebooker
from utils.redis_initializer import get_redis_client_zero as get_redis_client
from typing import List, Dict, Set
from schema import Trade, History

app= APIRouter()

@app.put("/bookTrade")
async def book_trade(trade: Trade, client: redis.Redis = Depends(get_redis_client)) -> Dict[str, str]:
    return tradebooker.booktrade(client, trade)

@app.post("/updateTrade")
def update_trade(trade_id: str, account: str, date: str, updated_type: str= None, updated_amount: int= None, 
                 client: redis.Redis = Depends(get_redis_client)) -> Dict[str, str]:
    return tradebooker.update_trade(trade_id, account, date, updated_type, updated_amount, client) 

@app.get("/getTrades")
async def get_trades(client: redis.Redis = Depends(get_redis_client)) -> List[Trade]:
    return tradebooker.get_trades(client)

@app.get("/queryTrades")
async def query_trades(account: str = "*", year: int = 0, month: int = 0, day: int = 0,
                       client: redis.Redis = Depends(get_redis_client)) -> List[Trade]:
    def default(value: int, pad: int) -> str:
        return "*" if value == 0 else str(value).zfill(pad)
    return tradebooker.query_trades(account, default(year, 4), default(month, 2), default(day, 2), client)

@app.get("/getTradeHistory")
def get_trade_history(trade_id: str, account: str, date: str, client: redis.Redis = Depends(get_redis_client)) -> History:
    return tradebooker.get_trade_history(trade_id, account, date, client)

@app.get("/getAccounts")
async def get_accounts(client: redis.Redis = Depends(get_redis_client)) -> Set[str]:
    return tradebooker.get_accounts(client)
