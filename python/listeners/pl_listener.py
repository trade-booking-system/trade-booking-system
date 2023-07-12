from utils.redis_initializer import get_redis_client
from schema.schema import ProfitLoss
from schema.schema import Position
from datetime import datetime, date as date_obj
from threading import Thread
from queue import Queue
from utils import market_calendar
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
    date= datetime.now().date()
    pl= get_pl(account, ticker)
    position= get_position(account, ticker)
    pl.position_pl= (get_price(ticker, date) - get_previous_closing_price(ticker)) * position.amount
    client.hset(f"p&l:{account}:{ticker}", date.isoformat(), pl.json())
    print(f"position p&l: account: {account} stock ticker: {ticker} profit loss: {pl}")

def update_trade_pl(account: str, ticker: str, amount, price):
    date= datetime.now().date()
    pl= get_pl(account, ticker)
    pl.trade_pl+= (get_previous_closing_price(ticker) - price) * amount
    client.hset(f"p&l:{account}:{ticker}", date.isoformat(), pl.json())
    print(f"realized p&l: account: {account} stock ticker: {ticker} profit loss: {pl.trade_pl}")

def get_price(ticker: str, date: date_obj) -> float:
    return float(client.hget("livePrices:"+ticker.upper(), date.isoformat()))

def get_position(account: str, ticker: str) -> Position:
    json_position= client.hget("positions:"+account, ticker)
    return Position.parse_raw(json_position).amount

def get_pl(account: str, ticker: str) -> ProfitLoss:
    date= datetime.now().date()
    pl_json= client.hget(f"p&l:{account}:{ticker}", date.isoformat())
    if pl_json == None:
        return ProfitLoss(trade_pl= 0, position_pl= 0)
    return ProfitLoss.parse_raw(pl_json)

def get_previous_closing_price(ticker: str) -> float:
    date= market_calendar.get_most_recent_trading_day()
    return get_price(ticker, date)

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
