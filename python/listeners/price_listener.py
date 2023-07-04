from yahoo_fin.stock_info import get_live_price
from utils.tickers import ValidTickers
from time import sleep
import signal
import datetime
import redis
import sys
import os

class PriceHandler:
    def __init__(self, client: redis.Redis, tickers: list[str], price_getter, now):
        self.client = client
        self.tickers = tickers
        self.price_getter = price_getter
        self.now = now

    def get_stock_price(self, stock_ticker: str):
        try:
            stock_price = self.price_getter(stock_ticker)
        except AssertionError:
            stock_price = None
            print("invalid ticker: " + stock_ticker)
        except KeyError:
            stock_price= None
            print("missing data: " + stock_ticker)
        return stock_price
    
    def is_market_open(self) -> bool:
        if self.now == None:
            return True
        date_time= self.now()
        day= date_time.weekday()
        if day == 5 or day == 6:
            return False
        time= date_time.time()
        if time < datetime.time(9, 30) or datetime.time(16) < time:
            return False
        return True
    
    def update_stock_prices(self):
        if not self.is_market_open():
            print("market is closed")
            return
        for stock_ticker in self.tickers:
            stock_price = self.get_stock_price(stock_ticker)
            if stock_price != None:
                current_time = self.now()
                live_price_key= "livePrices:" + stock_ticker
                snapshot_key= f"snapshotPrices:{stock_ticker}:{current_time.date().isoformat()}"
                self.client.set(live_price_key, stock_price)
                self.client.hset(snapshot_key, current_time.time().isoformat(), stock_price)

def termination_handler(signum, frame):
    client.close()
    sys.exit()

if __name__ == "__main__":
    client = redis.Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 0, decode_responses= True)
    signal.signal(signal.SIGTERM, termination_handler)
    tickers= ValidTickers("utils/ListOfStocks.txt")
    handler = PriceHandler(client, tickers.get_all_tickers(), get_live_price,
        datetime.datetime.now if os.getenv("DEBUG_MODE", "off") == "off" else None)
    while True:
        handler.update_stock_prices()
        client.publish("prices", "updated")
        sleep(60)
