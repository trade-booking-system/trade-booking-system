from redis import Redis
from fastapi import HTTPException
from schema import Position

def get_all_positions(client: Redis) -> list[Position]:
    positions: list[Position] = []
    for key in client.scan_iter("positions:*"):
        for _, value in client.hscan_iter(key):
            positions.append(Position.parse_raw(value))
    return positions

def get_positions(client: Redis, account: str) -> list[Position]:
    positions: list[Position] = []
    for _, value in client.hscan_iter("positions:" + account):
        positions.append(Position.parse_raw(value))
    return positions

def get_position(client: Redis, account: str, ticker: str) -> Position:
    data = client.hget("positions:" + account, ticker)
    if data == None:
        raise HTTPException(status_code= 404, detail= "position does not exist")
    return Position.parse_raw(data)
