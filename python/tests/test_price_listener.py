import datetime

import pytest

from listeners.price_listener import PriceHandler
from .conftest import FakeClient, FakePrices

def test_price_listener(monkeypatch: pytest.MonkeyPatch):
    redis = FakeClient()
    data = {"ABC": 12.3, "XYZ": 543.21, "QUE": 789.567}
    def now():
        return datetime.datetime(2023, 7, 3, 11, 46, 51)
    handler = PriceHandler(redis, data.keys(), now)
    monkeypatch.setattr(handler, "tickers_info", FakePrices(data))
    handler.update_stock_prices()
    for ticker in data:
        assert redis.get("livePrices:" + ticker) == data[ticker]
        snapshot = f"snapshotPrices:{ticker}:{now().date().isoformat()}"
        assert redis.hget(snapshot, now().time().isoformat()) == data[ticker]

def test_weekend_closed(monkeypatch: pytest.MonkeyPatch):
    redis = FakeClient()
    def now():
        return datetime.datetime(2023, 7, 2, 11, 46, 51)
    handler = PriceHandler(redis, ["ABC", "XYZ"], now)
    monkeypatch.setattr(handler, "tickers_info", FakePrices({}))
    handler.update_stock_prices()
    for ticker in ["ABC", "XYZ"]:
        assert redis.get("livePrices:" + ticker) == None
        snapshot = f"snapshotPrices:{ticker}:{now().date().isoformat()}"
        assert redis.hget(snapshot, now().time().isoformat()) == None

def test_after_hours(monkeypatch: pytest.MonkeyPatch):
    redis = FakeClient()
    def now():
        return datetime.datetime(2023, 7, 3, 4, 0, 5)
    handler = PriceHandler(redis, ["ABC", "XYZ"], now)
    monkeypatch.setattr(handler, "tickers_info", FakePrices({}))
    handler.update_stock_prices()
    for ticker in ["ABC", "XYZ"]:
        assert redis.get("livePrices:" + ticker) == None
        snapshot = f"snapshotPrices:{ticker}:{now().date().isoformat()}"
        assert redis.hget(snapshot, now().time().isoformat()) == None
