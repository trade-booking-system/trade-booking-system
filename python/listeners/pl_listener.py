from utils.redis_initializer import get_redis_client
from schema.schema import Position
from threading import Thread
from queue import Queue
import signal
import sys

def termination_handler(signum, frame):
    thread.stop()
    thread.join()
    queue.join()
    sub.close()
    client.close()
    sys.exit()

def position_updates_handler(msg):
    data: str= msg["data"]
    account, ticker= data.split(":")
    queue.put_nowait((update_position_pl, (account, ticker)))

def trade_updates_handler(msg):
    data: str= msg["data"]
    account, ticker, amount, price= data.split(":")
    queue.put_nowait((update_trade_pl, (account, ticker, amount, price)))

def price_updates_handler(msg):
     if msg["data"] == "update":
          queue.put((update_position_pl, ()))

def update_position_pl():
    stocks= client.smembers("p&lStocks")
    for stock_info in stocks:
        account, ticker= stock_info.split(":")
        update_position_pl(account, ticker)

def update_position_pl(account: str, ticker: str):
    pl= (get_live_price(ticker) - get_opening_price(ticker)) * get_position()
    client.hset(f"p&l:{account}:{ticker}", "position", pl)
    print(f"position p&l: account: {account} stock ticker: {ticker} profit loss: {pl}")

def update_trade_pl(account: str, ticker: str, amount, price):
    trade_pl= get_trade_pl(account, ticker)
    trade_pl+= (get_opening_price() - price) * amount
    client.hset(f"p&l:{account}:{ticker}", "trade", trade_pl)
    print(f"realized p&l: account: {account} stock ticker: {ticker} profit loss: {trade_pl}")

def get_live_price(ticker: str) -> float:
    return float(client.get("livePrices:"+ticker.upper()))

def get_position(account: str, ticker: str) -> int:
    json_position= client.hget("positions:"+account, ticker)
    if json_position != None:
        return Position.parse_raw(json_position).amount
    return 0

def get_opening_price(ticker: str)-> float:
    get_last_day_with_market_open()

def process_queue():
    while True:
        func, args= queue.get()
        func(*args)
        queue.task_done()

queue= Queue()
client = get_redis_client()
sub= client.pubsub(ignore_subscribe_messages= True)
sub.subscribe(**{"positionUpdates": position_updates_handler})
sub.subscribe(**{"tradeUpdates": trade_updates_handler})
sub.subscribe(**{"pricesUpdates": price_updates_handler})
thread= sub.run_in_thread()
queue_processor_thread= Thread(target= process_queue, daemon= True)
queue_processor_thread.run()
signal.signal(signal.SIGTERM, termination_handler)
