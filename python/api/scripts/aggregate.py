import sys, os
from typing import Dict
from redis import Redis
from datetime import datetime

sys.path.append(os.path.abspath("."))
from schema import Position, Trade

def aggregate(client: Redis, account: str):
    positions: Dict[str, int] = {}
    trade_keys = client.keys("trades:" + account + ":*")
    for key in trade_keys:
        trade_data = client.hvals(key)
        for item in trade_data:
            trade = Trade.parse_raw(item)
            amount = trade.amount if trade.type == "buy" else -trade.amount
            if trade.stock_ticker in positions:
                positions[trade.stock_ticker] += amount
            else:
                positions[trade.stock_ticker] = amount
    positions_data = {key: Position(account=account, stock_ticker=key, amount=value,
                            last_aggregation_time=datetime.now(), last_aggregation_host="test").json()
                      for key, value in positions.items()}
    client.hset("positions:" + account, mapping=positions_data)

client = Redis(host = "localhost", port = 6379, db = 0, decode_responses = True)
aggregate(client, sys.argv[1])
