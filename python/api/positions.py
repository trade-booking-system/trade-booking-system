from redis import Redis
from fastapi import APIRouter, Depends

from schema import Position, PositionResponse
from utils.redis_initializer import get_redis_client_one as get_redis_client
from utils.get_positions import get_positions, get_position

router = APIRouter()

@router.get("/{account}")
async def get_account_positions(account: str, client: Redis = Depends(get_redis_client)) -> PositionResponse:
    positions = get_positions(client, account)
    return PositionResponse(positions=positions, count=len(positions))

@router.get("/{account}/{ticker}")
async def get_ticker_position(account: str, ticker: str, client: Redis = Depends(get_redis_client)) -> Position:
    return get_position(client, account, ticker)
