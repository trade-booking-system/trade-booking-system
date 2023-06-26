import pytest

import schema
from .conftest import System, generate_trades, trade_to_dict, assert_trades_equal

@pytest.mark.parametrize("trades", [generate_trades(3, x) for x in range(7000, 7200, 10)])
def test_trade_history(trades: list[schema.Trade], test_server: System, monkeypatch: pytest.MonkeyPatch):
    client = test_server.web
    response = client.put("/bookTrade/", json=trade_to_dict(trades[0]))
    id = response.json()["Field"]
    for i in range(1, len(trades)):
        trades[i].account = trades[0].account
        trades[i].date = trades[0].date
        response = client.post("/updateTrade", params={
            "trade_id": id,
            "account": trades[i].account,
            "date": str(trades[i].date),
            "updated_type": trades[i].type,
            "updated_amount": trades[i].amount,
            "updated_price": trades[i].price
        })
        assert response.status_code == 200
        assert response.json()["Version"] == str(i + 1)
        id = response.json()["Field"]
    response = client.get("/getTradeHistory", params={
        "trade_id": id,
        "account": trades[0].account,
        "date": str(trades[0].date)
    })
    assert response.status_code == 200
    data = response.json()
    history = schema.History(**data)
    assert history.current_version == len(trades)
    assert len(history.trades) == len(trades)
    for i in range(len(trades)):
        for key in ["account", "type", "amount", "price"]:
            assert getattr(trades[i], key) == getattr(history.trades[i], key)
        assert history.trades[i].version == i + 1
