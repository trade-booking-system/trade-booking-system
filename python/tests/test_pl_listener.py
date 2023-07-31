import pytest

from datetime import date, time, datetime
import listeners.pl_listener as pl_listener
from utils import redis_utils
from schema.schema import Price, History, Trade, Position
from .conftest import FakeClient

def test_price_listener():

    def add_trade(client: FakeClient, trade: Trade):
        history= redis_utils.get_history(client, trade.account, trade.date, trade.id)
        history= history if history != None else History()
        history.trades.append(trade)
        redis_utils.set_history(client, trade.account, trade.date, trade.id, history)

    client = FakeClient()

    today = date(2023, 7, 25)
    ticker= "AAPL"

    # set closing price
    redis_utils.set_price(client, ticker, date(2023, 7, 24), Price(price= 192.75, stock_ticker= ticker, last_updated= time(16, 0)))

    account = "account-1"
    trade1 = Trade(account= account, type= "buy", stock_ticker= ticker, amount= 10, date= today, time= time(14, 40), user= "user-1", price= 194.39)
    add_trade(client, trade1)

    trade2 = Trade(account= account, type= "sell", stock_ticker= ticker, amount= 6, date= today, time= time(15, 55), user= "user-1", price= 193.84)
    add_trade(client, trade2)

    redis_utils.set_position_snapshot(client, account, today, ticker, Position(account= account, stock_ticker= ticker, amount= 4, last_aggregation_time= datetime(2023, 7, 25, 15, 55), last_aggregation_host= "host"))

    # set current price
    redis_utils.set_price(client, ticker, today, Price(price= 193.62, stock_ticker= ticker, last_updated= time(15, 58)))

    listener= pl_listener.PLListener(client= client)
    listener.update_position_pl(account, ticker, today)
    listener.update_trade_pl(trade1.id, account, ticker, trade1.get_amount(), trade1.price, today)
    listener.update_trade_pl(trade2.id, account, ticker, trade2.get_amount(), trade2.price, today)

    pl= redis_utils.get_pl(client, account, ticker, today)

    assert round(pl.trade_pl, 10) == -9.86
    assert round(pl.position_pl, 10) == 3.48
    assert round(pl.get_total_pl(), 10) == -6.38

    trade_pl1= redis_utils.get_trade_pl(client, trade1.id, today)
    trade_pl2= redis_utils.get_trade_pl(client, trade2.id, today)

    assert round(trade_pl1.trade_pl, 10) == -16.4
    assert round(trade_pl2.trade_pl, 10) == 6.54
    assert trade_pl1.closing_price == 192.75
