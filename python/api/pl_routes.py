from datetime import datetime
import redis
from fastapi import APIRouter, Depends, HTTPException
from utils import booktrade as tradebooker
from utils.redis_initializer import get_redis_client
from utils.redis_utils import get_trade_pl
from schema import ProfitLoss, TradeProfitLoss


router= APIRouter()

@router.get("/profitLoss")
def get_profit_loss(account: str, ticker: str, client: redis.Redis = Depends(get_redis_client)) -> ProfitLoss:
    return tradebooker.get_pl(client, account, ticker)

@router.get("/tradeProfitLoss")
def get_trade_profit_loss(id: str, client: redis.Redis = Depends(get_redis_client)) -> TradeProfitLoss:
    pl = get_trade_pl(client, id, datetime.now().date())
    if pl == None:
        raise HTTPException(status_code=404, detail="trade pnl information does not exist")
    return pl

@router.get("/allProfitLoss")
def get_all_profit_loss(account: str, client: redis.Redis = Depends(get_redis_client)) -> list[ProfitLoss]:
    return tradebooker.get_all_pl(client, account)
