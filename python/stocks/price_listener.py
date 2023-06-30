from yahoo_fin.stock_info import get_live_price
from tickers import ValidTickers
from time import sleep
import signal
import datetime
import redis
import sys
import os

def termination_handler(signum, frame):
    client.close()
    sys.exit()

def is_market_open() -> bool:
    date_time= datetime.datetime.now()
    day= date_time.weekday()
    if day == 5 or day == 6:
        return False
    time= date_time.time()
    if time < datetime.time(9, 30) or datetime.time(16) < time:
        return False
    return True

def get_stock_price(stock_ticker: str):
    try:
        stock_price= get_live_price(stock_ticker)
    except AssertionError:
        stock_price= None
        print("invalid ticker: "+stock_ticker)
    except KeyError:
        stock_price= None
        print("missing data: "+stock_ticker)
    return stock_price

def update_stock_prices(tickers: list[str]):
    if not is_market_open():
        print("markets closed")
        return

    for stock_ticker in tickers:
        stock_price = get_stock_price(stock_ticker)
        if stock_price != None:
            curent_time= datetime.datetime.now()
            live_price_key= "livePrices:"+stock_ticker
            snapshot_key= f"snapshotPrices:{stock_ticker}:{curent_time.date().isoformat()}"
            client.set(live_price_key, stock_price)
            client.hset(snapshot_key, curent_time.time().isoformat(), stock_price)

client = redis.Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 0, decode_responses= True)
signal.signal(signal.SIGTERM, termination_handler)
tickers= ValidTickers("ListOfStocks.txt")
valid_tickers= tickers.get_all_tickers()

while True:
    update_stock_prices(valid_tickers)
    sleep(60)
