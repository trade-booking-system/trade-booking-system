import pytest

from datetime import date, time, datetime
import listeners.pl_listener as pl_listener
from utils import redis_utils
from schema.schema import Price, History, Trade, Position
from .conftest import FakeClient

def test_price_listener():
    redis = FakeClient()

    history1= History()
    today = date(2023, 7, 25)
    ticker= "AAPL"

    # set closing price
    redis_utils.set_price(redis, ticker, date(2023, 7, 24), Price(price= 192.75, stock_ticker= ticker, last_updated= time(16, 0)))

    account = "account-1"
    trade1 = Trade(account= account, type= "buy", stock_ticker= ticker, amount= 10, date= today, time= time(14, 40), user= "user-1", price= 194.39)
    history1.trades.append(trade1)
    redis_utils.set_history(redis, account, today, trade1.id, history1)

    history2= History()
    trade2 = Trade(account= account, type= "sell", stock_ticker= ticker, amount= 6, date= today, time= time(15, 55), user= "user-1", price= 193.84)
    history2.trades.append(trade2)
    redis_utils.set_history(redis, account, today, trade2.id, history2)

    redis_utils.set_position_snapshot(redis, account, today, ticker, Position(account= account, stock_ticker= ticker, amount= 4, last_aggregation_time= datetime(2023, 7, 25, 15, 55), last_aggregation_host= "host"))

    # set current price
    redis_utils.set_price(redis, ticker, today, Price(price= 193.62, stock_ticker= ticker, last_updated= time(15, 58)))

    listener= pl_listener.PLListener(client= redis)
    listener.update_position_pl(account, ticker, today)
    listener.update_trade_pl(trade1.id, account, ticker, trade1.get_amount(), trade1.price, today)
    listener.update_trade_pl(trade2.id, account, ticker, trade2.get_amount(), trade2.price, today)

    pl= redis_utils.get_pl(redis, account, ticker, today)

    assert round(pl.trade_pl, 10) == -9.86
    assert round(pl.position_pl, 10) == 3.48
    assert round(pl.get_total_pl(), 10) == -6.38

    trade_pl1= redis_utils.get_trade_pl(redis, trade1.id, today)
    trade_pl2= redis_utils.get_trade_pl(redis, trade2.id, today)

    assert round(trade_pl1.trade_pl, 10) == -16.4
    assert round(trade_pl2.trade_pl, 10) == 6.54
    assert trade_pl1.closing_price == 192.75

def get_position(client, account, ticker, _):
    return redis_utils.get_position(client, account, ticker)
