from redis import Redis
from fastapi import APIRouter, Depends

from schema import PositionResponse, PositionWithPl
from utils.redis_initializer import get_redis_client
from utils.redis_utils import get_position, get_positions, merge_position
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_all_accounts_positions(client: Redis = Depends(get_redis_client)) -> PositionResponse:
    positions: list[PositionWithPl] = []
    for position in get_positions(client, "*"):
        positions.append(merge_position(client, position, datetime.now().date()))
    return PositionResponse(positions=positions, count=len(positions))

@router.get("/{account}")
async def get_account_positions(account: str, client: Redis = Depends(get_redis_client)) -> PositionResponse:
    positions: list[PositionWithPl] = []
    for position in get_positions(client, account):
        positions.append(merge_position(client, position, datetime.now().date()))
    return PositionResponse(positions=positions, count=len(positions))

@router.get("/{account}/{ticker}")
async def get_ticker_position(account: str, ticker: str, client: Redis = Depends(get_redis_client)) -> PositionWithPl:
    return merge_position(client, get_position(client, account, ticker), datetime.now().date())
