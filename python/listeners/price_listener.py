from utils.redis_initializer import get_redis_client
from utils.tickers import ValidTickers
from utils import market_calendar
from yahooquery import Ticker
from time import sleep
from schema.schema import Price
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

    def has_closing_prices(self, date_time: datetime.datetime) -> bool:
        # market hasn't opened yet
        if self.now.time() < market_calendar.default_closing_time():
            return True
        # markets closed today
        if market_calendar.is_trading_day(date_time.now().date()):
            return True
        for stock_ticker in self.tickers:
            price_json= client.hget("livePrices"+stock_ticker, date_time.date().isoformat())
            if price_json == None: 
                return False
            price= Price.parse_raw(price_json)
            if price.time < market_calendar.default_closing_time():
                return False
        return True

    def update_stock_prices(self):
        now = datetime.datetime.fromtimestamp(0) if self.now is None else self.now()
        if not market_calendar.is_market_open():
            print("market is closed")
            if self.has_closing_prices(now):
                return
        time= now.time()
        date= now.date()
        prices= self.tickers_info.price

        for stock_ticker in self.tickers:
            if stock_ticker in prices and "regularMarketPrice" in prices[stock_ticker]:
                stock_price= prices[stock_ticker]["regularMarketPrice"]
                live_price_key= "livePrices:" + stock_ticker
                self.client.hset(live_price_key, date.isoformat(), Price(stock_price, time).json())
                print(f"stock: {stock_ticker} price: {stock_price}")
            else:
                print("error getting "+stock_ticker+"s price")
        client.publish("pricesUpdates", "updated")

def termination_handler(signum, frame):
    client.close()
    sys.exit()

if __name__ == "__main__":
    client = get_redis_client()
    signal.signal(signal.SIGTERM, termination_handler)
    tickers= ValidTickers("utils/ListOfStocks.txt")
    handler = PriceHandler(client, tickers.get_all_tickers(), datetime.datetime.now if os.getenv("DEBUG_MODE", "off") == "off" else None)
    while True:
        handler.update_stock_prices()
        sleep(60)
