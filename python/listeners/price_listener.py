from yahooquery import Ticker
from utils.tickers import ValidTickers
from time import sleep
import signal
import datetime
import redis
import sys
import os

class PriceHandler:
    def __init__(self, client: redis.Redis, tickers: list[str], now: datetime.datetime):
        self.client= client
        self.tickers= tickers
        self.tickers_info= Ticker(tickers)
        self.now= now
    
    def is_market_open(self) -> bool:
        date_time= self.now()
        if date_time == None:
            return True
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
        
        date= self.now().date()
        time= self.now().time()
        prices= self.tickers_info.price

        for stock_ticker in self.tickers:
            if stock_ticker in prices and "regularMarketPrice" in prices[stock_ticker]:
                stock_price= prices[stock_ticker]["regularMarketPrice"]
                live_price_key= "livePrices:" + stock_ticker
                snapshot_key= f"snapshotPrices:{stock_ticker}:{date.isoformat()}"
                self.client.set(live_price_key, stock_price)
                self.client.hset(snapshot_key, time.isoformat(), stock_price)
                print(f"stock: {stock_ticker} price: {stock_price}")
            else:
                print("error getting "+stock_ticker+"s price")

def termination_handler(signum, frame):
    client.close()
    sys.exit()

if __name__ == "__main__":
    client = redis.Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 0, decode_responses= True)
    signal.signal(signal.SIGTERM, termination_handler)
    tickers= ValidTickers("utils/ListOfStocks.txt")
    handler = PriceHandler(client, tickers.get_all_tickers(), datetime.datetime.now if os.getenv("DEBUG_MODE", "off") == "off" else None)
    while True:
        handler.update_stock_prices()
        client.publish("prices", "updated")
        sleep(60)
