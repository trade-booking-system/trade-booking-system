import random

from aggregate.aggregate import TradeHandler
import schema
from .conftest import FakeClient

def test_aggregate():
    SEED = 1000
    gen = random.Random(SEED)
    redis = FakeClient()
    tickers = ["XYZ", "ABC", "QUE"]
    accounts = ["account" + str(i) for i in range(3)]
    handler = TradeHandler(redis)
    redis._add_channel("updatePositions")
    redis.pubsub().subscribe(**{"updatePositions": handler.get_trade_handler()})
    data: dict[str, int] = {}
    for i in range(5):
        for account in accounts:
            for ticker in tickers:
                amount = gen.randrange(1, 1000)
                redis.publish("updatePositions", f"{account}:{ticker}:{amount}")
                data[account + ticker] = amount + data.get(account + ticker, 0)
    for account in accounts:
        for ticker in tickers:
            position_data = redis.hget("positions:" + account, ticker)
            position = schema.Position.parse_raw(position_data)
            assert position.account == account
            assert position.stock_ticker == ticker
            assert position.amount == data[account + ticker]
