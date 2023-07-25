from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from utils.redis_initializer import get_redis_client
from datetime import datetime, timedelta, date as date_obj
from utils.tickers import ValidTickers
from utils import market_calendar
from yahooquery import Ticker
from utils import redis_utils
from redis import Redis
import pandas
import signal
import sys
import os


def update_stock_prices(date: date_obj= datetime.now().date()):
    if not market_calendar.is_trading_day(date):
        return
    print("updating prices")
    prices= tickers_info.price

    for stock_ticker in tickers:
        if stock_ticker in prices and "regularMarketPrice" in prices[stock_ticker]:
            stock_price= prices[stock_ticker]["regularMarketPrice"]
            redis_utils.set_price(client, stock_ticker, date, stock_price, False)
            print(f"stock: {stock_ticker} price: {stock_price}")
        else:
            print("error getting "+stock_ticker+"s price")
    client.publish("pricesUpdates", "updated")

def has_closing_prices(dates: list[date_obj]) -> bool:
    for date in dates:
        for stock_ticker in tickers:
            price= redis_utils.get_price(client, stock_ticker, date)
            if price == None:
                return False
            if not price.is_closing_price:
                return False
    return True

def fill_in_closing_prices(start_date: date_obj= datetime.now().date(), end_date: date_obj= datetime.now().date()):
    print("filling in closing prices")
    history= tickers_info.history(start=start_date, end= end_date + timedelta(1))
    dates= market_calendar.get_market_dates(start_date, end_date)
    has_prices= has_closing_prices(dates)
    runs= 0
    while has_prices != True and runs <= 5:
        has_prices= set_closing_prices(dates, history)
        runs+= 1

def set_closing_prices(dates: list[date_obj], history: pandas.DataFrame) -> bool:
    successful= True
    for date in dates:
        for stock_ticker in tickers:
            price= redis_utils.get_price(client, stock_ticker, date)

            if not(price and price.is_closing_price):
                closing_price= get_closing_price(history, date, stock_ticker)
                if closing_price == None:
                    print(f"No closing price found for {stock_ticker} on {date}")
                    successful= False
                else:
                    print(f"stock ticker: {stock_ticker} date: {date.isoformat()} closing price: {str(closing_price)}")
                    redis_utils.set_price(client, stock_ticker, date, closing_price, True)
    return successful

def get_closing_price(history: pandas.DataFrame, date: date_obj, stock_ticker: str):
    ticker = history.loc[stock_ticker]
    if not date in ticker.index:
        return None
    stock_info: pandas.Series= ticker.loc[date]
    closing_price= stock_info.get("adjclose", None)
    return closing_price

def termination_handler(signum, frame):
    scheduler.shutdown(wait= False)
    client.close()
    sys.exit()

def schedule_jobs(scheduler: BlockingScheduler, starting_date: date_obj):
    current_date= datetime.now().date()
    price_updates_trigger= OrTrigger(triggers= [CronTrigger(day_of_week= "0-4", hour= "10-15", minute= "*"), CronTrigger(day_of_week= "0-4", hour= 9, minute= "30-59")])
    closing_price_updates_trigger= OrTrigger(triggers= [CronTrigger(day_of_week= "0-4", hour= "16"), CronTrigger(day_of_week= "0-4", hour= 23, minute= 59)])
    scheduler.add_job(func= fill_in_closing_prices, args= [starting_date - timedelta(1), current_date - timedelta(1)])
    scheduler.add_job(func= update_stock_prices, trigger= price_updates_trigger)
    scheduler.add_job(func= fill_in_closing_prices, trigger= closing_price_updates_trigger)

def get_starting_date(client: Redis) -> date_obj:
    mode= os.getenv("RECOVERY_MODE")
    if mode == "rebuild":
        return redis_utils.get_startup_date(client)
    elif mode == "recover":
        return datetime.now().date - timedelta(5)

client = get_redis_client()
tickers= ValidTickers("utils/ListOfStocks.txt").get_all_tickers()
tickers_info= Ticker(tickers)
signal.signal(signal.SIGTERM, termination_handler)
scheduler= BlockingScheduler()
if __name__ == "__main__":
    starting_date= get_starting_date(client)
    schedule_jobs(scheduler, starting_date)
    scheduler.start()
