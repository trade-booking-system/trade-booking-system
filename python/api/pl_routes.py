import redis
from fastapi import APIRouter, Depends, UploadFile, File
from utils import booktrade as tradebooker
from utils.redis_initializer import get_redis_client
from schema import ProfitLoss


router= APIRouter()

@router.get("/profitLoss")
def get_profit_loss(account: str, ticker: str, client: redis.Redis = Depends(get_redis_client)) -> ProfitLoss:
    return tradebooker.get_pl(client, account, ticker)

@router.get("/allProfitLoss")
def get_all_profit_loss(account: str, client: redis.Redis = Depends(get_redis_client)) -> list[ProfitLoss]:
    return tradebooker.get_all_pl(client, account)
