import pytest

import schema
from .conftest import AsyncSystem, generate_trades, trade_to_dict

from utils.redis_utils import set_trade_pl, get_trade_pl

@pytest.mark.asyncio
@pytest.mark.parametrize("trades", [generate_trades(6, x) for x in range(6000, 6050, 10)])
async def test_watch_trades(ws_server: AsyncSystem, trades: list[schema.Trade]):
    def pnl_to_dict(pnl: schema.TradeProfitLoss):
        pnl_dict = pnl.dict()
        pnl_dict["date"] = str(pnl_dict["date"])
        return pnl_dict
    types: list[str] = ["create" if i % 2 == 0 else "update" for i in range(6)]
    pnls: list[schema.TradeProfitLoss] = [
        schema.TradeProfitLoss(
            account=trade.account, trade_id=trade.id, trade_pl=25.0,
            closing_price=5.0, date=trade.date
        ) for trade in trades
    ]
    async with ws_server.web as client:
        redis = ws_server.redis
        redis._add_channel("tradeUpdatesWS")
        redis._add_channel("pnlTradeUpdatesWS")
        async with client.websocket_connect("/trades") as websocket:
            for (trade, pnl, trade_type) in zip(trades, pnls, types):
                set_trade_pl(redis, trade.id, trade.date, pnl)
                print("P&L:", get_trade_pl(redis, trade.id, trade.date))
                redis.publish("tradeUpdatesWS", f"{trade_type}: {trade.json()}")
                data = await websocket.receive_json()
                assert data == {"type": trade_type, "payload": trade_to_dict(trade) | pnl_to_dict(pnl)}
