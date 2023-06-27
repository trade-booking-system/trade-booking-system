from redis import Redis
from datetime import datetime
from schema import Position
import signal
import os

class TradeHandler:
    def __init__(self, client: Redis):
        self.client: Redis = client
        self.cache = {}

    def get_trade_handler(self):
        def handler(msg):
            data= msg["data"]
            account, stock_ticker, amount= data.split(":")
            self.update_position(account, stock_ticker, int(amount))
        return handler

    def update_position(self, account: str, stock_ticker: str, amount: int):
        key = "positions:"+account
        stock_tickers= self.cache.get(account)
        if stock_tickers == None:
            stock_tickers= dict()
            self.cache[account]= stock_tickers
        old_amount= stock_tickers.get(stock_ticker)
        if old_amount == None:
            position_json= self.client.hget(key, stock_ticker)
            old_amount= 0
            if position_json != None:
                old_amount= Position.parse_raw(position_json).amount
        new_amount= old_amount+amount
        stock_tickers[stock_ticker]= new_amount
        position= Position(account= account, stock_ticker= stock_ticker, amount= new_amount, 
                        last_aggregation_time= datetime.now(), last_aggregation_host= "host")
        self.client.hset(key, stock_ticker, position.json())

def termination_handler(signum, frame):
    thread.stop()
    thread.join()
    sub.close()
    client.close()

if __name__ == "__main__":
    client = Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 0, decode_responses = True)
    handler = TradeHandler(client)
    sub= client.pubsub(ignore_subscribe_messages= True)
    sub.subscribe(**{"updatePositions": handler.get_trade_handler()})
    thread= sub.run_in_thread()
    signal.signal(signal.SIGTERM, termination_handler)
