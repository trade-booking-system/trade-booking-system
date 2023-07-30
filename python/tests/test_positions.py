import pytest

import schema
from .conftest import System, generate_positions, assert_positions_equal, assert_positions_lists_equal, position_to_dict

@pytest.mark.parametrize("positions", [generate_positions(9, x) for x in range(2100, 2300, 10)])
def test_get_all_positions(test_server: System, positions: list[schema.Position]):
    web = test_server.web
    redis = test_server.redis
    for i in range(9):
        positions[i].account = "account" + str(i % 3)
        positions[i].stock_ticker = "ABC" + str(i // 3)
    for position in positions:
        redis.hset("positions:" + position.account, position.stock_ticker, position.json())
    response = web.get("/positions")
    assert response.status_code == 200
    position_response = schema.PositionResponse(**response.json())
    assert position_response.count == 9
    assert_positions_lists_equal(position_response.positions, positions)

@pytest.mark.parametrize("positions", [generate_positions(6, x) for x in range(2300, 2500, 10)])
def test_get_positions(test_server: System, positions: list[schema.Position]):
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
    position_response = schema.PositionResponse(**result)
    assert position_response.count == 3
    for i in range(3):
        assert_positions_equal(position_to_dict(position_response.positions[i]),
                               position_to_dict(positions[i * 2]))

@pytest.mark.parametrize("positions", [generate_positions(6, x) for x in range(2500, 2700, 10)])
def test_get_position(test_server: System, positions: list[schema.Position]):
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
