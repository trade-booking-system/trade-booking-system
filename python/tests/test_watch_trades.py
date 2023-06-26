from fastapi import WebSocketDisconnect
import pytest

import schema
from .conftest import System, AsyncSystem, generate_trades

@pytest.mark.skip
@pytest.mark.parametrize("trades", [generate_trades(6, x) for x in range(6000, 6200, 10)])
def test_watch_trades(test_server: System, trades: list[schema.Trade]):
    client = test_server.web
    redis = test_server.redis[0]
    types: list[str] = ["create" if i % 2 == 0 else "update" for i in range(6)]
    print("test1")
    redis._add_channel("tradeUpdates")
    print("test2")
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/watchTrades") as websocket:
            print(websocket)
            for (trade, trade_type) in zip(trades, types):
                redis.publish("tradeUpdates", f"{trade_type}: {trade.json()}")
                print("test6")
                data = websocket.receive_json()
                print("test7")
                print(data)
                print(data == {"type": trade_type, "trade": trade.json()})
                assert data == {"type": trade_type, "trade": trade.json()}
                print(data)
            print("done")
            print(websocket)
            websocket.send({"type": "websocket.disconnect", "code": 1000})
            websocket.close()
            print(websocket)
    print("done2")
