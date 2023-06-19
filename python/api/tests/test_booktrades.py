import json
import random
import datetime
import fnmatch, re
from typing import List, Tuple
import sys, os

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath("."))
import main
import schema
from utils.redis_initializer import get_redis_client

class FakeClient:
    def __init__(self):
        self.data = {}
    
    def hget(self, name, key):
        return self.data[name][key]
    
    def hset(self, name, key, value):
        if name not in self.data:
            self.data[name] = {}
        self.data[name][key] = value
    
    def hgetall(self, name):
        return self.data[name]
    
    def keys(self, pattern):
        keys = []
        regex = re.compile(fnmatch.translate(pattern))
        for key in self.data.keys():
            if regex.match(key):
                keys.append(key)
        return keys

def trade_to_dict(trade: schema.Trade):
    trade_dict = trade.dict()
    for key in ["date", "time"]:
        trade_dict[key] = str(trade_dict[key])
    return trade_dict

def trades_equal(trade1, trade2):
    keys = []
    for key in ["account", "user", "type", "stock_ticker", "amount", "date", "time"]:
        if trade1[key] != trade2[key]:
            keys.append(key)
    assert len(keys) == 0, "keys not equal: " + ", ".join(keys) + f" {keys[0]} {type(trade1[keys[0]])} {type(trade2[keys[0]])}"

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
def test_put(trade: schema.Trade):
    client, redis = initialize()
    response = client.put("/bookTrade/", json=trade_to_dict(trade))
    assert response.status_code == 200
    result = response.json()
    assert result["Key"] == "trades:" + trade.account + ":" + str(trade.date)
    trade2 = redis.hget(result["Key"], result["Field"])
    trades_equal(trade_to_dict(trade), json.loads(trade2))

@pytest.mark.parametrize("trade1,trade2",
                         [(generate_trade(x), generate_trade(x + 500)) for x in range(1025, 1050)])
def test_get(trade1: schema.Trade, trade2: schema.Trade):
    client, redis = initialize()
    redis.hset("trades:a", "test1", trade1.json())
    redis.hset("trades:a", "test2", trade2.json())
    response = client.get("/getTrades/")
    assert response.status_code == 200
    trades = response.json()
    assert len(trades) == 2
    dict1 = trade_to_dict(trade1)
    dict2 = trade_to_dict(trade2)
    if trades[0]["account"] == trade1.account:
        trades_equal(trades[0], dict1)
        trades_equal(trades[1], dict2)
    else:
        trades_equal(trades[0], dict2)
        trades_equal(trades[1], dict1)

def test_get_accounts():
    client, redis = initialize()
    for i in range(25):
        trade = generate_trade(i + 500)
        account = "account" + str(i % 3)
        trade.account = account
        redis.hset("trades:" + account + ":" + str(trade.date), "test" + str(i), trade.json())
    response = client.get("/getAccounts/")
    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) == 3
    for i in range(3):
        assert "account" + str(i) in accounts
