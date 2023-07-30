from redis import Redis
from fastapi import APIRouter, Depends, HTTPException

from schema import PositionResponse, PositionWithPl
from utils.redis_initializer import get_redis_client
from utils import redis_utils
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_all_accounts_positions(client: Redis = Depends(get_redis_client)) -> PositionResponse:
    positions: list[PositionWithPl] = []
    for position in redis_utils.get_positions(client, "*"):
        positions.append(redis_utils.merge_position(client, position, datetime.now().date()))
    return PositionResponse(positions=positions, count=len(positions))

@router.get("/{account}")
async def get_account_positions(account: str, client: Redis = Depends(get_redis_client)) -> PositionResponse:
    positions: list[PositionWithPl] = []
    for position in redis_utils.get_positions(client, account):
        positions.append(redis_utils.merge_position(client, position, datetime.now().date()))
    return PositionResponse(positions=positions, count=len(positions))

@router.get("/{account}/{ticker}")
async def get_ticker_position(account: str, ticker: str, client: Redis = Depends(get_redis_client)) -> PositionWithPl:
    position = redis_utils.get_position(client, account, ticker.upper())
    if position == None:
        raise HTTPException(status_code= 400, detail= "position does not exist")
    return redis_utils.merge_position(client, position, datetime.now().date())
