import redis
from fastapi import APIRouter, Depends
from utils import booktrade as tradebooker
from utils.redis_initializer import get_redis_client
from schema import Trade, History

router= APIRouter()

@router.put("/bookTrade")
async def book_trade(trade: Trade, client: redis.Redis = Depends(get_redis_client)) -> dict[str, str]:
    return tradebooker.booktrade(client, trade)

@router.post("/bookTradesBulk")
async def book_trades_bulk(trades: list[Trade], client: redis.Redis = Depends(get_redis_client)) -> dict[str, str]:
    return tradebooker.booktrades_bulk(client, trades)

@router.post("/updateTrade")
def update_trade(trade_id: str, account: str, date: str, updated_type: str= None, updated_amount: int= None, 
                 updated_price: int= None, client: redis.Redis = Depends(get_redis_client)) -> dict[str, str]:
    return tradebooker.update_trade(trade_id, account, date, updated_type, updated_amount, updated_price, client) 

@router.get("/getTrades")
async def get_trades(client: redis.Redis = Depends(get_redis_client)) -> list[Trade]:
    return tradebooker.get_trades(client)

@router.get("/queryTrades")
async def query_trades(account: str = "*", year: int = 0, month: int = 0, day: int = 0,
                       client: redis.Redis = Depends(get_redis_client)) -> list[Trade]:
    def default(value: int, pad: int) -> str:
        return "*" if value == 0 else str(value).zfill(pad)
    return tradebooker.query_trades(account, default(year, 4), default(month, 2), default(day, 2), client)

@router.get("/getTradeHistory")
def get_trade_history(trade_id: str, account: str, date: str, client: redis.Redis = Depends(get_redis_client)) -> History:
    return tradebooker.get_trade_history(trade_id, account, date, client)

@router.get("/getAccounts")
async def get_accounts(client: redis.Redis = Depends(get_redis_client)) -> set[str]:
    return tradebooker.get_accounts(client)
