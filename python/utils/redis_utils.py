import pandas as pd
import redis
from typing import Tuple

# Set up the Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def store_to_redis(account: str, date: str, id: str, trades: pd.DataFrame, positions: pd.DataFrame):
    redis_client.set(f"{account}:{date}:{id}:trades", trades.to_json())
    redis_client.set(f"{account}:{date}:{id}:positions", positions.to_json())

def get_from_redis(account: str, date: str, id: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    trades_data = redis_client.get(f"{account}:{date}:{id}:trades")
    trades_df = pd.DataFrame() if trades_data is None else pd.read_json(trades_data)

    positions_data = redis_client.get(f"{account}:{date}:{id}:positions")
    positions_df = pd.DataFrame() if positions_data is None else pd.read_json(positions_data)

    return trades_df, positions_df
