from typing import List
from redis import Redis

from schema import Position

def get_positions(client: Redis, account: str) -> List[Position]:
    positions: List[Position] = []
    positions_dict = client.hgetall("positions:" + account)
    for data in positions_dict.values():
        positions.append(Position.parse_raw(data))
    return positions

def get_position(client: Redis, account: str, ticker: str) -> Position:
    data = client.hget("positions:" + account, ticker)
    return Position.parse_raw(data)
