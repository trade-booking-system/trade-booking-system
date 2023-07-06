from redis import Redis
from datetime import datetime
from schema import Position
from utils.redis_initializer import get_redis_client
import signal

class TradeHandler:
    def __init__(self, client: Redis):
        self.client: Redis = client
        self.cache: dict[str, dict[PositionInfo]] = {}

    def get_trade_handler(self):
        def handler(msg):
            data: str= msg["data"]
            account, stock_ticker, amount, price= data.split(":")
            self.update_position(account, stock_ticker, int(amount), float(price))
            self.client.publish("tradeInfo", data)
        return handler

    def update_position(self, account: str, stock_ticker: str, amount: int, price):
        key = "positions:"+account
        stock_tickers= self.cache.get(account, dict())
        self.cache[account]= stock_tickers
        position_info: PositionInfo= stock_tickers.get(stock_ticker)
        if position_info == None:
            position_json= self.client.hget(key, stock_ticker)
            if position_json != None:
                old_position= Position.parse_raw(position_json)
                position_info= PositionInfo(old_position.amount, old_position.total_price)
            else:
                position_info= PositionInfo(0, 0)
                self.client.sadd("p&lStocks", account+":"+stock_ticker)
            stock_tickers[stock_ticker]= position_info

        position_info.amount+= amount
        position_info.total_price+= price * amount

        position= Position(account= account, stock_ticker= stock_ticker, amount= position_info.amount, 
                        last_aggregation_time= datetime.now(), last_aggregation_host= "host",
                        total_price= position_info.total_price)
        
        self.client.hset(key, stock_ticker, position.json())
        self.client.publish("positionUpdates", f"position:{position.json()}")

def termination_handler(signum, frame):
    thread.stop()
    thread.join()
    sub.close()
    client.close()

if __name__ == "__main__":
    client = get_redis_client()
    handler = TradeHandler(client)
    sub= client.pubsub(ignore_subscribe_messages= True)
    sub.subscribe(**{"updatePositions": handler.get_trade_handler()})
    thread= sub.run_in_thread()
    signal.signal(signal.SIGTERM, termination_handler)

class PositionInfo:
    def __init__(self, amount: int, total_price: float):
        self.amount: int= amount
        self.total_price: float= total_price
