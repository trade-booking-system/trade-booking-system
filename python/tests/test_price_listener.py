import datetime

from listeners.price_listener import PriceHandler
from .conftest import FakeClient

def test_price_listener():
    redis = FakeClient()
    data = {"ABC": 12.3, "XYZ": 543.21, "QUE": 789.567}
    def get_price(ticker: str) -> float:
        return data[ticker]
    def now():
        return datetime.datetime(2023, 7, 3, 11, 46, 51)
    handler = PriceHandler(redis, data.keys(), get_price, now)
    handler.update_stock_prices()
    for ticker in data:
        assert redis.get("livePrices:" + ticker) == data[ticker]
        snapshot = f"snapshotPrices:{ticker}:{now().date().isoformat()}"
        assert redis.hget(snapshot, now().time().isoformat()) == data[ticker]

def test_weekend_closed():
    redis = FakeClient()
    def now():
        return datetime.datetime(2023, 7, 2, 11, 46, 51)
    handler = PriceHandler(redis, ["ABC", "XYZ"], lambda ticker: 123.45, now)
    handler.update_stock_prices()
    for ticker in ["ABC", "XYZ"]:
        assert redis.get("livePrices:" + ticker) == None
        snapshot = f"snapshotPrices:{ticker}:{now().date().isoformat()}"
        assert redis.hget(snapshot, now().time().isoformat()) == None

def test_after_hours():
    redis = FakeClient()
    def now():
        return datetime.datetime(2023, 7, 3, 4, 0, 5)
    handler = PriceHandler(redis, ["ABC", "XYZ"], lambda: 123.45, now)
    handler.update_stock_prices()
    for ticker in ["ABC", "XYZ"]:
        assert redis.get("livePrices:" + ticker) == None
        snapshot = f"snapshotPrices:{ticker}:{now().date().isoformat()}"
        assert redis.hget(snapshot, now().time().isoformat()) == None
