import datetime

import pytest

import listeners.price_listener as price_listener
from schema.schema import Price
from .conftest import FakeClient, FakePrices

def test_price_listener(monkeypatch: pytest.MonkeyPatch):
    redis = FakeClient()
    data = {"ABC": 12.3, "XYZ": 543.21, "QUE": 789.567}
    monkeypatch.setattr(price_listener, "client", redis)
    monkeypatch.setattr(price_listener, "tickers", data.keys())
    monkeypatch.setattr(price_listener, "tickers_info", FakePrices(data))

    date_time = datetime.datetime(2023, 7, 3, 11, 46, 51)
    price_listener.update_stock_prices(date= date_time.date())
    for ticker in data:
        price_json= redis.hget("livePrices:" + ticker, date_time.date().isoformat())
        assert price_json != None
        price= Price.parse_raw(price_json)
        assert price.price == data[ticker]
        assert price.is_closing_price == False
