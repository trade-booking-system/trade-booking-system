from datetime import datetime, date
from utils import redis_utils
from fastapi import APIRouter, Depends, HTTPException
from utils.redis_initializer import get_redis_client
from utils.redis_utils import get_trade_pl
from schema import ProfitLoss, TradeProfitLoss
import redis


router= APIRouter()

@router.get("/profitLoss")
async def get_profit_loss(account: str, ticker: str, date: date= datetime.now().date(), client: redis.Redis = Depends(get_redis_client)) -> ProfitLoss:
    pl = redis_utils.get_pl(client, account, ticker.upper(), date)
    if pl is None:
        raise HTTPException(status_code=404, detail="profit loss data not found")
    return pl

@router.get("/tradeProfitLoss")
async def get_trade_profit_loss(id: str, date: date= datetime.now().date(), client: redis.Redis = Depends(get_redis_client)) -> TradeProfitLoss:
    pl = get_trade_pl(client, id, date)
    if pl == None:
        raise HTTPException(status_code=404, detail="trade pnl information does not exist")
    return pl

@router.get("/allProfitLoss")
async def get_all_profit_loss(account: str= "*", ticker: str= "*", client: redis.Redis = Depends(get_redis_client)) -> list[ProfitLoss]:
    return redis_utils.get_all_pl(client, account, ticker.upper())
