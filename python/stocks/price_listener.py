from yahoo_fin.stock_info import get_live_price
from time import sleep
import signal
import datetime
import redis
import sys
import os


def termination_handler(signum, frame):
    client.close()
    sys.exit()

def is_market_open(date_time: datetime.datetime) -> bool:
    day= date_time.weekday()
    if day == 5 or day == 6:
        return False
    time= date_time.time()
    if time < datetime.time(9, 30) or datetime.time(16) < time:
        return False
    return True

def update_stock_prices():
    date_time= datetime.datetime.now()
    if not is_market_open(date_time):
        print("markets closed")
        return
    date= date_time.date().isoformat()
    time= date_time.time().isoformat()

    for stock_ticker in client.sscan_iter("stockTickers"):
        live_price_key= "livePrices:"+stock_ticker
        snapshot_key= f"snapshotPrices:{stock_ticker}:{date}"

        stock_price= get_live_price(stock_ticker)
        print(f"Stock ticker: {stock_ticker}: {stock_price}")

        client.set(live_price_key, stock_price)
        client.hset(snapshot_key, time, stock_price)

client = redis.Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 1, decode_responses= True)
signal.signal(signal.SIGTERM, termination_handler)

while True:
    update_stock_prices()
    sleep(60)
