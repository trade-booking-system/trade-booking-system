import random
import routes
import schema
import pytest
import datetime

class FakeClient:
    def __init__(self):
        self.trades = {}
    
    def hget(self, name, key):
        return self.trades[key]
    
    def hset(self, name, key, value):
        self.trades[key] = value
    
    def hvals(self, name):
        return self.trades.values()

class FakeRouter:
    def get(self, _path):
        return lambda func: func
    
    def put(self, _path):
        return lambda func: func

def trades_equal(trade1: schema.Trade, trade2: schema.Trade) -> bool:
    for key in ["account", "type", "stock_ticker", "amount", "date"]:
        if trade1.dict()[key] != trade2.dict()[key]:
            return False
    return True

def initialize(monkeypatch: pytest.MonkeyPatch) -> FakeClient:
    client = FakeClient()
    monkeypatch.setitem(globals(), "r", client) # TODO: change name of global
    monkeypatch.setattr(routes, "app", FakeRouter())
    return client

def generate_trade(seed: int) -> schema.Trade:
    random_gen = random.Random(seed)
    account = "account" + random_gen.randrange(1, 4)
    type = random_gen.choice(["buy", "sell"])
    stock_ticker = random_gen.choice(["ABC", "XYZ", "LMNOP"])
    amount = random_gen.randrange(1, 1000)
    date = datetime.date(random_gen.randrange(1900, 2100), random_gen.randrange(1, 13),
                         random_gen.randrange(1, 29))
    return schema.Trade(account=account, type=type, stock_ticker=stock_ticker,
                        amount=amount, date=date)

@pytest.mark.parametrize("trade", [generate_trade(x) for x in range(1000, 1025)])
def test_put(trade: schema.Trade, monkeypatch: pytest.MonkeyPatch):
    client = initialize(monkeypatch)
    result = routes.put(trade)
    assert result["key"] == "trades:" + trade.account + ":" + trade.date # TODO: format
    # TODO: result["value"] should be in uuid4 format
    trade2 = client.hget("trades", result["key"])
    assert trades_equal(trade, trade2)

@pytest.mark.parametrize("trade1,trade2",
                         [(generate_trade(x), generate_trade(x + 500)) for x in range(1025, 1050)])
def test_get(trade1: schema.Trade, trade2: schema.Trade, monkeypatch: pytest.MonkeyPatch):
    client = initialize(monkeypatch)
    client.hset("trades", "test1", trade1)
    client.hset("trades", "test2", trade2)
    trades = routes.get()
    assert len(trades) == 2
    if trades[0].account == "account1":
        assert trades_equal(trades[0], trade1)
        assert trades_equal(trades[1], trade2)
    else:
        assert trades_equal(trades[0], trade2)
        assert trades_equal(trades[1], trade1)
