import random
import datetime
from typing import Tuple
import sys
import os

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath("."))
import main
import schema
from utils.redis_initializer import get_redis_client

class FakeClient:
    def __init__(self):
        self.trades = {}
    
    def hget(self, name, key):
        return self.trades[key]
    
    def hset(self, name, key, value):
        self.trades[key] = value
    
    def hvals(self, name):
        return self.trades.values()
    
    def keys(self, pattern):
        return ["trades"]

def trades_equal(trade1: schema.Trade, trade2: schema.Trade) -> bool:
    for key in ["account", "user", "type", "stock_ticker", "amount", "date", "time"]:
        if trade1.dict()[key] != trade2.dict()[key]:
            return False
    return True

def initialize() -> Tuple[TestClient, FakeClient]:
    redis_client = FakeClient()
    main.app.dependency_overrides[get_redis_client] = lambda: redis_client
    web_client = TestClient(main.app)
    return web_client, redis_client

def generate_trade(seed: int) -> schema.Trade:
    random_gen = random.Random(seed)
    account = "account" + str(random_gen.randrange(1, 4))
    user = "user" + str(random_gen.randrange(1, 4))
    type = random_gen.choice(["buy", "sell"])
    stock_ticker = random_gen.choice(["ABC", "XYZ", "LMNOP"])
    amount = random_gen.randrange(1, 1000)
    date = datetime.date(random_gen.randrange(1900, 2100), random_gen.randrange(1, 13),
                         random_gen.randrange(1, 29))
    time = datetime.time(random_gen.randrange(0, 24), random_gen.randrange(0, 60),
                         random_gen.randrange(0, 60))
    return schema.Trade(account=account, user=user, type=type, stock_ticker=stock_ticker,
                        amount=amount, date=date, time=time)

@pytest.mark.parametrize("trade", [generate_trade(x) for x in range(1000, 1025)])
def test_put(trade: schema.Trade, monkeypatch: pytest.MonkeyPatch):
    client, redis = initialize()
    result = client.put("/put/", json=trade.dict())
    assert result["key"] == "trades:" + trade.account + ":" + trade.date # TODO: format
    # TODO: result["value"] should be in uuid4 format
    trade2 = redis.hget("trades", result["key"])
    assert trades_equal(trade, trade2)

@pytest.mark.parametrize("trade1,trade2",
                         [(generate_trade(x), generate_trade(x + 500)) for x in range(1025, 1050)])
def test_get(trade1: schema.Trade, trade2: schema.Trade, monkeypatch: pytest.MonkeyPatch):
    client, redis = initialize()
    redis.hset("trades", "test1", trade1)
    redis.hset("trades", "test2", trade2)
    trades = client.get("/get/")
    assert len(trades) == 2
    if trades[0].account == "account1":
        assert trades_equal(trades[0], trade1)
        assert trades_equal(trades[1], trade2)
    else:
        assert trades_equal(trades[0], trade2)
        assert trades_equal(trades[1], trade1)
