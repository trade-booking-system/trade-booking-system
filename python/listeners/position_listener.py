from redis import Redis
from datetime import datetime
from schema import Position
from utils.redis_initializer import get_redis_client
import signal

class TradeHandler:
    def __init__(self, client: Redis):
        self.client: Redis = client
        self.cache: dict[str, dict[str, int]] = {}

    def get_trade_handler(self):
        def handler(msg):
            data: str= msg["data"]
            account, stock_ticker, amount= data.split(":")
            is_new= self.update_position(account, stock_ticker, int(amount))
            self.client.publish("positionUpdates", f"{account}:{stock_ticker}")
            if is_new:
                self.client.sadd("p&lStocks", account+":"+stock_ticker)
        return handler

    def update_position(self, account: str, stock_ticker: str, amount_added: int) -> bool:
        is_new= False
        key = "positions:"+account
        stock_tickers= self.cache.get(account, dict())
        self.cache[account]= stock_tickers
        old_amount= stock_tickers.get(stock_ticker)
        if old_amount == None:
            position_json= self.client.hget(key, stock_ticker)
            if position_json != None:
                old_position= Position.parse_raw(position_json)
                old_amount= old_position.amount
            else:
                old_amount= 0
                is_new= True
        amount= old_amount + amount_added

        stock_tickers[stock_ticker]= amount
        position= Position(account= account, stock_ticker= stock_ticker, amount= amount, 
                        last_aggregation_time= datetime.now(), last_aggregation_host= "host")
        
        self.client.hset(key, stock_ticker, position.json())
        self.client.publish("positionUpdatesWS", f"position:{position.json()}")
        return is_new

def termination_handler(signum, frame):
    thread.stop()
    thread.join()
    sub.close()
    client.close()

if __name__ == "__main__":
    client = get_redis_client()
    handler = TradeHandler(client)
    sub= client.pubsub(ignore_subscribe_messages= True)
    sub.subscribe(**{"tradesInfo": handler.get_trade_handler()})
    thread= sub.run_in_thread()
    signal.signal(signal.SIGTERM, termination_handler)
