import datetime

import pytest

from schema.schema import Price
from listeners.price_listener import PriceHandler
from .conftest import FakeClient, FakePrices

def test_is_market_closed():
    redis = FakeClient()
    handler= PriceHandler(redis, [])
    # closed for holiday
    date1= datetime.datetime(2023, 1, 1, 11, 23)
    # market not open yet
    date2= datetime.datetime(2023, 7, 12, 7, 23)
    # market already closed
    date3= datetime.datetime(2023, 7, 12, 20, 23)
    # market is open
    date4= datetime.datetime(2023, 7, 12, 12, 23)

    assert handler.is_market_closed(date1) == True
    assert handler.is_market_closed(date2) == True
    assert handler.is_market_closed(date3) == True
    assert handler.is_market_closed(date4) == False

def test_price_listener(monkeypatch: pytest.MonkeyPatch):
    redis = FakeClient()
    data = {"ABC": 12.3, "XYZ": 543.21, "QUE": 789.567}
    handler = PriceHandler(redis, data.keys())
    monkeypatch.setattr(handler, "tickers_info", FakePrices(data))
    date_time = datetime.datetime(2023, 7, 3, 11, 46, 51)
    handler.update_stock_prices(date_time= date_time, is_market_closed= False)
    for ticker in data:
        price_json= redis.hget("livePrices:" + ticker, date_time.date().isoformat())
        assert price_json != None
        price= Price.parse_raw(price_json)
        assert price.price == data[ticker]
        assert price.is_closing_price == False
