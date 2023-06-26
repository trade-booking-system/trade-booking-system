import json
import random
import datetime

import pytest
from fastapi.testclient import TestClient

import schema
from .conftest import System, generate_trade, trade_to_dict, assert_trades_equal

@pytest.mark.parametrize("trade", [generate_trade(x) for x in range(1000, 1025)])
def test_put(test_server: System, trade: schema.Trade):
    client = test_server.web
    redis = test_server.redis[0]
    response = client.put("/bookTrade/", json=trade_to_dict(trade))
    assert response.status_code == 200
    result = response.json()
    assert result["Key"] == "trades:" + trade.account + ":" + str(trade.date)
    history = redis.hget(result["Key"], result["Field"])
    assert_trades_equal(trade_to_dict(trade), json.loads(history)["trades"][0])

@pytest.mark.parametrize("trade1,trade2",
                         [(generate_trade(x), generate_trade(x + 500)) for x in range(1025, 1050)])
def test_get(test_server: System, trade1: schema.Trade, trade2: schema.Trade):
    client = test_server.web
    redis = test_server.redis[0]
    redis.hset("trades:a", "test1", schema.History(trades=[trade1]).json())
    redis.hset("trades:a", "test2", schema.History(trades=[trade2]).json())
    response = client.get("/getTrades/")
    assert response.status_code == 200
    trades = response.json()
    assert len(trades) == 2
    dict1 = trade_to_dict(trade1)
    dict2 = trade_to_dict(trade2)
    if trades[0]["account"] == trade1.account:
        assert_trades_equal(trades[0], dict1)
        assert_trades_equal(trades[1], dict2)
    else:
        assert_trades_equal(trades[0], dict2)
        assert_trades_equal(trades[1], dict1)

def test_query_trades(test_server: System):
    client = test_server.web
    redis = test_server.redis[0]
    def try_pattern(client: TestClient, rules: dict[str, str]):
        response = client.get("/queryTrades/", params=rules)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 625 / (5 ** len(rules))
        for item in data:
            if "account" in rules:
                assert item["account"] == rules["account"]
            date = datetime.datetime.strptime(item["date"], "%Y-%m-%d").date()
            for key in ["year", "month", "day"]:
                if key in rules:
                    assert getattr(date, key) == int(rules[key])
    for i in range(625):
        trade = generate_trade(i + 3000)
        account = "account" + str(i % 5)
        i //= 5
        year = 2000 + (i % 5) * 7
        i //= 5 
        month = 1 + (i % 5)
        i //= 5
        day = 1 + (i % 5) * 3
        trade.account = account
        date = datetime.date(year, month, day)
        trade.date = date
        history = schema.History(trades=[trade])
        redis.hset("trades:" + account + ":" + str(date), "test" + str(i), history.json())
    for i in range(25):
        random_gen = random.Random(i + 4000)
        rules: dict[str, str] = {}
        if (random_gen.choice([True, False])):
            rules["account"] = "account" + str(random_gen.randrange(0, 5))
        if (random_gen.choice([True, False])):
            rules["year"] = str(2000 + random_gen.randrange(0, 5) * 7)
        if (random_gen.choice([True, False])):
            rules["month"] = str(1 + random_gen.randrange(0, 5))
        if (random_gen.choice([True, False])):
            rules["day"] = str(1 + random_gen.randrange(0, 5) * 3)
        try_pattern(client, rules)

@pytest.mark.parametrize("trade", [generate_trade(x) for x in range(3400, 3425)])
def test_booktrade_channel(trade: schema.Trade, test_server: System):
    client = test_server.web
    redis = test_server.redis[0]
    handled = False
    def handler(message):
        nonlocal handled
        assert message == {"data": f"create: {trade.json()}"}
        handled = True
    client.put("/bookTrade", json=trade_to_dict(trade))
    redis.pubsub().subscribe(**{"tradeUpdates": handler})
    assert handled

def test_get_accounts(test_server: System):
    client = test_server.web
    redis = test_server.redis[0]
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
