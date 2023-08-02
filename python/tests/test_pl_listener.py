import pytest
from datetime import date, time, datetime
import listeners.pl_listener as pl_listener
from utils import redis_utils
from schema.schema import Price, History, Trade, Position
from .conftest import FakeClient

day1 = date(2023, 7, 21)
day2 = date(2023, 7, 24)
day3 = date(2023, 7, 25)
ticker= "AAPL"

def test_price_listener():
    client = FakeClient()

    # set closing price
    redis_utils.set_price(client, ticker, date(2023, 7, 24), Price(price= 192.75, stock_ticker= ticker, last_updated= time(16, 0)))

    account = "account-1"

    trade1 = create_trade(account, "buy", day2, 10, 194.39, client)
    trade2 = create_trade(account, "sell", day3, 6, 193.84, client)

    redis_utils.set_position_snapshot(client, account, day3, ticker, Position(account= account, stock_ticker= ticker, amount= 4, last_aggregation_time= datetime(2023, 7, 25, 15, 55), last_aggregation_host= "host"))

    # set current price
    redis_utils.set_price(client, ticker, day3, Price(price= 193.62, stock_ticker= ticker, last_updated= time(15, 58)))

    listener= pl_listener.PLListener(client= client)
    listener.update_position_pl(account, ticker, day3)
    listener.update_trade_pl(trade1.id, account, ticker, trade1.get_amount(), trade1.price, day3)
    listener.update_trade_pl(trade2.id, account, ticker, trade2.get_amount(), trade2.price, day3)

    pl= redis_utils.get_pl(client, account, ticker, day3)

    assert round(pl.trade_pl, 10) == -9.86
    assert round(pl.position_pl, 10) == 3.48
    assert round(pl.get_total_pl(), 10) == -6.38

    trade_pl1= redis_utils.get_trade_pl(client, trade1.id, day3)
    trade_pl2= redis_utils.get_trade_pl(client, trade2.id, day3)

    assert round(trade_pl1.trade_pl, 10) == -16.4
    assert round(trade_pl2.trade_pl, 10) == 6.54
    assert trade_pl1.closing_price == 192.75

def test_rebuild_listener():
    client = FakeClient()

    account = "account-1"

    client.set("startupDate", day1.isoformat())

    redis_utils.set_price(client, ticker, day1, Price(price= 187.75, stock_ticker= ticker, last_updated= time(16, 0)))
    redis_utils.set_price(client, ticker, day2, Price(price= 190.75, stock_ticker= ticker, last_updated= time(16, 0)))
    redis_utils.set_price(client, ticker, day3, Price(price= 192.75, stock_ticker= ticker, last_updated= time(16, 0)))

    trade1 = create_trade(account, "buy", day2, 10, 192.00, client)
    trade2 = create_trade(account, "sell", day3, 6, 193.00, client)
    redis_utils.add_to_stocks(client, account, ticker)

    redis_utils.set_position_snapshot(client, account, day2, ticker, Position(account= account, stock_ticker= ticker, amount= 10, last_aggregation_time= datetime(2023, 7, 24, 15, 55), last_aggregation_host= "host"))
    redis_utils.set_position_snapshot(client, account, day3, ticker, Position(account= account, stock_ticker= ticker, amount= 4, last_aggregation_time= datetime(2023, 7, 25, 15, 55), last_aggregation_host= "host"))

    listener = pl_listener.PLListener(client= client)
    listener.rebuild()

    pl_previous_day = redis_utils.get_pl(client, account, ticker, day2)
    assert round(pl_previous_day.trade_pl, 2) == -42.50
    assert round(pl_previous_day.position_pl, 2) == 30.00
    assert round(pl_previous_day.get_total_pl(), 2) == -12.50

    pl_today = redis_utils.get_pl(client, account, ticker, day3)
    assert round(pl_today.trade_pl, 2) == 13.50
    assert round(pl_today.position_pl, 2) == 8.00
    assert round(pl_today.get_total_pl(), 2) == 21.5

def add_trade(client: FakeClient, trade: Trade):
    history= redis_utils.get_history(client, trade.account, trade.date, trade.id)
    history= history if history != None else History()
    history.trades.append(trade)
    redis_utils.set_history(client, trade.account, trade.date, trade.id, history)

def create_trade(account: str, trade_type: str, trade_date: date, amount: int, price: float, client) -> Trade:
    trade = Trade(account=account, type=trade_type, stock_ticker=ticker, amount=amount, date=trade_date, time=time(14, 40), user="user-1", price=price)
    add_trade(client, trade)
    return trade
