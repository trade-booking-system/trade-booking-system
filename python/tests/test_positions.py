import pytest
from datetime import date, time, datetime
from listeners.position_listener import PositionListener
from schema.schema import Trade, History, Position, PositionResponse
from utils import redis_utils
from .conftest import System, FakeClient, generate_positions, assert_positions_equal, assert_positions_lists_equal, position_to_dict

@pytest.mark.parametrize("positions", [generate_positions(9, x) for x in range(2100, 2300, 10)])
def test_get_all_positions(test_server: System, positions: list[Position]):
    web = test_server.web
    redis = test_server.redis
    for i in range(9):
        positions[i].account = "account" + str(i % 3)
        positions[i].stock_ticker = "ABC" + str(i // 3)
    for position in positions:
        redis.hset("positions:" + position.account, position.stock_ticker, position.json())
    response = web.get("/positions")
    assert response.status_code == 200
    position_response = PositionResponse(**response.json())
    assert position_response.count == 9
    assert_positions_lists_equal(position_response.positions, positions)

@pytest.mark.parametrize("positions", [generate_positions(6, x) for x in range(2300, 2500, 10)])
def test_get_positions(test_server: System, positions: list[Position]):
    web = test_server.web
    redis = test_server.redis
    for i in range(len(positions)):
        if i % 2 == 0:
            positions[i].account = "us"
        else:
            positions[i].account = "them"
        positions[i].stock_ticker = "ABC" + str(i % 3)
    for position in positions:
        redis.hset("positions:" + position.account, position.stock_ticker, position.json())
    response = web.get("/positions/us")
    assert response.status_code == 200
    result = response.json()
    position_response = PositionResponse(**result)
    assert position_response.count == 3
    for i in range(3):
        assert_positions_equal(position_to_dict(position_response.positions[i]),
                               position_to_dict(positions[i * 2]))

@pytest.mark.parametrize("positions", [generate_positions(6, x) for x in range(2500, 2700, 10)])
def test_get_position(test_server: System, positions: list[Position]):
    web = test_server.web
    redis = test_server.redis
    for i in range(len(positions)):
        if i % 2 == 0:
            positions[i].account = "us"
        else:
            positions[i].account = "them"
        positions[i].stock_ticker = "ABC" + str(i % 3)
    for position in positions:
        redis.hset("positions:" + position.account, position.stock_ticker, position.json())
    response = web.get("/positions/them/abc1")
    assert response.status_code == 200
    result = response.json()
    result["last_aggregation_time"] = result["last_aggregation_time"].replace("T", " ")
    print((result["last_aggregation_time"]))
    print((position_to_dict(positions[1])["last_aggregation_time"]))
    assert_positions_equal(result, position_to_dict(positions[1]))

def test_update_snapshots_and_update_position():
    client= FakeClient()
    account= "account-1"
    ticker= "AMZN"
    listener= PositionListener(client= client)

    listener.update_position(account, ticker, 13, datetime(2023, 7, 20, 14, 20))
    listener.take_snapshot(date(2023, 7, 20))
    listener.update_position(account, ticker, -3, datetime(2023, 7, 20, 17, 20))

    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 20), ticker).amount == 13
    assert redis_utils.get_position(client, account, ticker).amount == 10

    listener.update_position(account, ticker, -5, datetime(2023, 7, 21, 12, 2))
    listener.take_snapshot(date(2023, 7, 21))

    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 21), ticker).amount == 5

    listener.update_position(account, ticker, 20, datetime(2023, 7, 23, 14, 20))
    listener.take_snapshot(date(2023, 7, 23))

    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 23), ticker) == None
    assert redis_utils.get_position(client, account, ticker).amount == 25

    listener.update_position(account, ticker, 1, datetime(2023, 7, 24, 12, 1))
    listener.take_snapshot(date(2023, 7, 24))

    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 24), ticker).amount == 26
    assert redis_utils.get_position(client, account, ticker).amount == 26

    listener.update_snapshots(account, ticker, -10, date(2023, 7, 19), time(15), date(2023, 7, 25), time(15))

    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 18), ticker) == None
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 19), ticker).amount == -10
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 20), ticker).amount == 3
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 21), ticker).amount == -5
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 22), ticker) == None
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 23), ticker) == None
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 24), ticker).amount == 16
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 25), ticker) == None


def test_position_recovery():

    def add_trade(client: FakeClient, trade: Trade):
        history= redis_utils.get_history(client, trade.account, trade.date, trade.id)
        history= history if history != None else History()
        history.trades.append(trade)
        redis_utils.set_history(client, trade.account, trade.date, trade.id, history)

    client= FakeClient()
    account= "account-1"
    ticker= "AAPL"
    user = "user-1"
    listener= PositionListener(client= client)
    redis_utils.add_to_stocks(client, account, ticker)
    redis_utils.add_to_stocks(client, account, "IBM")

    client.set("startupDate", "2023-07-23")
    add_trade(client, Trade(account= account, type= "buy", stock_ticker= ticker, amount= 10, date= date(2023, 7, 23), time= time(15, 12), user= user, price= 12))

    listener.recover()

    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 23), ticker) == None
    assert redis_utils.get_position(client, account, ticker).amount == 10

    add_trade(client, Trade(account= account, type= "sell", stock_ticker= ticker, amount= 4, date= date(2023, 7, 24), time= time(12, 2), user= user, price= 13))
    add_trade(client, Trade(account= account, type= "sell", stock_ticker= ticker, amount= 4, date= date(2023, 7, 24), time= time(11), user= user, price= 13))

    add_trade(client, Trade(account= account, type= "buy", stock_ticker= ticker, amount= 20, date= date(2023, 7, 25), time= time(15), user= user, price= 13))
    add_trade(client, Trade(account= account, type= "buy", stock_ticker= "IBM", amount= 20, date= date(2023, 7, 25), time= time(13), user= user, price= 32))

    listener.recover()
    
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 24), ticker).amount == 2
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 25), ticker).amount == 22
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 25), "IBM").amount == 20

    assert redis_utils.get_position(client, account, ticker).amount == 22

    add_trade(client, Trade(account= account, type= "buy", stock_ticker= "IBM", amount= 50, date= date(2023, 7, 25), time= time(15, 40), user= user, price= 32))

    listener.recover()

    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 25), "IBM").amount == 70

    listener.rebuild()

    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 23), ticker) == None
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 24), ticker).amount == 2
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 25), ticker).amount == 22
    assert redis_utils.get_position_snapshot(client, account, date(2023, 7, 25), "IBM").amount == 70

    assert redis_utils.get_position(client, account, ticker).amount == 22
    assert redis_utils.get_position(client, account, "IBM").amount == 70
