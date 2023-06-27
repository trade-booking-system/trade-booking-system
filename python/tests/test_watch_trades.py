import pytest

import schema
from .conftest import AsyncSystem, generate_trades

@pytest.mark.asyncio
@pytest.mark.parametrize("trades", [generate_trades(6, x) for x in range(6000, 6050, 10)])
async def test_watch_trades(ws_server: AsyncSystem, trades: list[schema.Trade]):
    types: list[str] = ["create" if i % 2 == 0 else "update" for i in range(6)]
    async with ws_server.web as client:
        redis = ws_server.redis[0]
        redis._add_channel("tradeUpdates")
        async with client.websocket_connect("/watchTrades") as websocket:
            for (trade, trade_type) in zip(trades, types):
                redis.publish("tradeUpdates", f"{trade_type}: {trade.json()}")
                data = await websocket.receive_json()
                assert data == {"type": trade_type, "trade": trade.json()}
            await websocket.close()
