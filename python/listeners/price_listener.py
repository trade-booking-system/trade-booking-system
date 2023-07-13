from utils.redis_initializer import get_redis_client
from utils.tickers import ValidTickers
from utils import market_calendar
from yahooquery import Ticker
from time import sleep
from schema.schema import Price
from datetime import datetime, timedelta
import signal
import redis
import sys

class PriceHandler:
    def __init__(self, client: redis.Redis, tickers: list[str]):
        self.client= client
        self.tickers= tickers
        self.tickers_info= Ticker(tickers)
        self.now= datetime.now

    def price_handler(self):
        date_time = self.now()
        is_market_closed = self.is_market_closed(date_time)
        if is_market_closed:
            print("market is closed")
            if not self.has_closing_prices(date_time):
                self.update_stock_prices(date_time, is_market_closed)
        else:
            self.update_stock_prices(date_time, is_market_closed)

    def update_stock_prices(self, date_time: datetime, is_market_closed: bool):
        date= date_time.date()
        prices= self.tickers_info.price

        for stock_ticker in self.tickers:
            if stock_ticker in prices and "regularMarketPrice" in prices[stock_ticker]:
                stock_price= prices[stock_ticker]["regularMarketPrice"]
                live_price_key= "livePrices:" + stock_ticker
                self.client.hset(live_price_key, date.isoformat(), Price(price= stock_price, is_closing_price= is_market_closed).json())
                print(f"stock: {stock_ticker} price: {stock_price}")
            else:
                print("error getting "+stock_ticker+"s price")
        self.client.publish("pricesUpdates", "updated")

    def is_market_closed(self, date_time: datetime) -> bool:
        if not market_calendar.is_trading_day(date_time.date()):
            return True
        if date_time.time() < market_calendar.default_opening_time():
            return True
        if date_time.time() > market_calendar.default_closing_time():
            return True
        return False

    def has_closing_prices(self, date_time: datetime) -> bool:
        # market hasn't opened yet
        if date_time.time() < market_calendar.default_closing_time():
            return True
        # markets closed today
        if market_calendar.is_trading_day(date_time.date()):
            return True
        for stock_ticker in self.tickers:
            price_json= self.client.hget("livePrices"+stock_ticker, date_time.date().isoformat())
            if price_json == None: 
                return False
            price= Price.parse_raw(price_json)
            if not price.is_closing_price:
                return False
        return True

def fill_in_closing_prices(tickers: list[str], tickers_info: Ticker, previous_trading_day: datetime):
    history= tickers_info.history(start= previous_trading_day, end= previous_trading_day + timedelta(1))

    for stock in tickers:
        key= "livePrices:"+stock
        price_json= client.hget(key, previous_trading_day.isoformat())
        if not(price_json != None and Price.parse_raw(price_json).is_closing_price):
            print("stock ticker "+stock)
            closing_price= 
            print(closing_price)
            price= Price(price= closing_price, is_closing_price= True)
            client.hset(key, previous_trading_day.isoformat(), price.json())

def termination_handler(signum, frame):
    client.close()
    sys.exit()

if __name__ == "__main__":
    print("starting")
    client = get_redis_client()
    signal.signal(signal.SIGTERM, termination_handler)
    tickers= ValidTickers("utils/ListOfStocks.txt")
    handler = PriceHandler(client, tickers.get_all_tickers())
    previous_trading_day= market_calendar.get_most_recent_trading_day()
    if not PriceHandler.has_closing_prices(previous_trading_day):
        fill_in_closing_prices(handler.tickers, handler.tickers_info, previous_trading_day)
    print("price_listener running")

    while True:
        handler.price_handler()
        sleep(60)
