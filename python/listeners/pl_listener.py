from queue import Queue
from threading import Thread
from schema.schema import Position
from utils.redis_initializer import get_redis_client
import signal
import sys

def termination_handler(signum, frame):
    thread.stop()
    thread.join()
    queue.join()
    sub.close()
    client.close()
    sys.exit()

def trade_updates_handler(msg):
    data: str= msg["data"]
    account, ticker, amount, price= data.split(":")
    queue.put_nowait((update_unrealized_pl, (account, ticker)))
    if int(amount) < 0:
        queue.put_nowait((update_realized_pl, (account, ticker, int(amount), float(price))))

def price_updates_handler(msg):
     if msg["data"] == "update":
          queue.put((update_unrealized_pl, ()))

def update_unrealized_pl():
    stocks= client.smembers("p&lStocks")
    for stock_info in stocks:
        account, ticker= stock_info.split(":")
        update_unrealized_pl(account, ticker)

def update_unrealized_pl(account: str, ticker: str):
    position= get_position(account, ticker)
    pl= position.amount * get_stock_price(ticker) - position.total_price
    client.hset(f"p&l:{account}:{ticker}", "unrealized", pl)
    print(f"unrealized p&l: account: {account} stock ticker: {ticker} profit loss: {pl}")

def update_realized_pl(account: str, ticker: str, amount, price):
    average_price= get_average_price_of_stock(account, ticker)
    pl= (price - average_price) * abs(amount)
    client.hset(f"p&l:{account}:{ticker}", "realized", pl)
    print(f"realized p&l: account: {account} stock ticker: {ticker} profit loss: {pl}")

def get_average_price_of_stock(account: str, ticker: str) -> float:
    position= get_position(account, ticker)
    return position.total_price / position.amount

def get_stock_price(ticker: str) -> float:
    return float(client.get("livePrices:"+ticker.upper()))

def get_position(account: str, ticker: str) -> Position:
    json_position= client.hget("positions:"+account, ticker)
    return Position.parse_raw(json_position)

def process_queue():
    while True:
        func, args= queue.get()
        func(*args)
        queue.task_done()

queue= Queue()
client = get_redis_client()
sub= client.pubsub(ignore_subscribe_messages= True)
sub.subscribe(**{"tradeInfo": trade_updates_handler})
sub.subscribe(**{"prices": price_updates_handler})
thread= sub.run_in_thread()
queue_processor_thread= Thread(target= process_queue, daemon= True)
queue_processor_thread.run()
signal.signal(signal.SIGTERM, termination_handler)
