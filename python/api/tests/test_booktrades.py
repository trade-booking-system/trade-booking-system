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

class FakeRouter:
    def get(self, _path):
        return lambda func: func
    
    def put(self, _path):
        return lambda func: func

def test_put(monkeypatch: pytest.MonkeyPatch):
    client = FakeClient()
    monkeypatch.setattr(routes, "r", client)
    monkeypatch.setattr(routes, "app", FakeRouter())
    trade = schema.Trade(account="account", type="buy", stock_ticker="XYZ",
                             amount=123, date=datetime.date.fromisoformat("20010804"))
    result = routes.put(trade)
    assert result["key"] == "trades:account:20010804"
    # TODO: result["value"] should be in uuid4 format
    trade2 = client.hget("trades", result["key"])
    for key in ["account", "type", "stock_ticker", "amount", "date"]:
        assert trade.dict()[key] == trade2.dict()[key]
