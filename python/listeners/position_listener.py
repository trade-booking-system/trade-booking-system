from datetime import datetime, date as date_obj, time
from schema import Position, Trade
from apscheduler.schedulers.background import BackgroundScheduler
from listeners.listener import listener_base
from utils import market_calendar
from utils import redis_utils
from redis import Redis

class PositionListener(listener_base):
    def __init__(self):
        super().__init__()
        self.cache: dict[str, dict[str, int]] = {}
        self.scheduler= BackgroundScheduler()
        self.scheduler.add_job(self.take_snapshot, "cron", day_of_week= "0-4", hour= 16)

    def start(self):
        super().start()
        self.scheduler.start()

    def get_handlers(self):
        return {
            "tradesInfo": self.trade_updates_handler
        }

    def trade_updates_handler(self, msg):
        data: str= msg["data"]
        account, stock_ticker, amount= data.split(":")
        self.queue.put_nowait((self.update_position_and_notify, (account, stock_ticker, int(amount), datetime.now())))

    def update_position_and_notify(self, account: str, stock_ticker: str, amount_added: int, now: datetime):
        self.update_position(account, stock_ticker, amount_added, now)
        self.client.publish("positionUpdates", f"{account}:{stock_ticker}")

    def update_position(self, account: str, stock_ticker: str, amount_added: int, now: datetime):
        stock_tickers= self.cache.get(account, dict())
        self.cache[account]= stock_tickers
        old_amount= stock_tickers.get(stock_ticker)
        if old_amount == None:
            old_position= redis_utils.get_position(self.client, account, stock_ticker)
            old_amount= old_position.amount if old_position != None else 0
        amount= old_amount + amount_added

        stock_tickers[stock_ticker]= amount
        position= Position(account= account, stock_ticker= stock_ticker, amount= amount, 
                        last_aggregation_time= now, last_aggregation_host= "host")
        
        redis_utils.set_position(self.client, account, stock_ticker, position)
        self.client.publish("positionUpdatesWS", f"position:{position.json()}")

    def take_snapshot(self, now= datetime.now()):
        if not market_calendar.is_trading_day(now.date()):
            return
        positions= redis_utils.get_positions(self.client)
        for position in positions:
            redis_utils.set_position_snapshot(self.client, position.account, now.date(), position.stock_ticker, position)

    def recover(self):
        now= datetime.now()
        stocks: list[str]= redis_utils.get_stocks(self.client)
        trades_cache: dict[str, list[Trade]]= dict()
        for stock in stocks:
            account, ticker= stock.split(":")
            last_aggregation_time= self.get_last_aggregation_time(self.client, account, ticker)
            
            dates = market_calendar.get_dates(last_aggregation_time.date(), now.date())
            for date in dates:
                trades= self.get_trades_by_ticker_and_date(account, ticker, date, trades_cache)
                if date == last_aggregation_time.date():
                    trades= [trade for trade in trades if last_aggregation_time.time() < trade.time]
                market_trades, after_market_trades= self.split_trades_by_time(trades)
                for trade in market_trades:
                    self.update_position(account, ticker, trade.get_amount(), datetime.combine(date, trade.time))
                
                position = redis_utils.get_position(self.client, account, ticker)
                if position != None:
                    if now.date() != position.last_aggregation_time.date() or now.time() > time(16):
                        redis_utils.set_position_snapshot(self.client, account, now.date(), ticker, position)
                        
                for trade in after_market_trades:
                    self.update_position(account, ticker, trade.get_amount(), datetime.combine(date, trade.time))

        self.client.publish("pricesUpdates", "updated")

    def get_trades_by_ticker_and_date(self, account: str, ticker: str, date: date_obj, cache: dict[str, Trade]) -> list[Trade]:
        days_trades= self.get_trades_by_day(account, date, cache)
        return [trade for trade in days_trades if trade.stock_ticker == ticker]

    def get_trades_by_day(self, account: str, date: date_obj, cache: dict[str, list[Trade]]) -> list[Trade]:
        key= f"{account}:{date.isoformat()}"
        trades= cache.get(key)
        if trades != None:
            return trades
        trades= redis_utils.get_trades_by_day_and_account(self.client, account, date)
        cache[key]= trades
        return trades

    @staticmethod
    def get_last_aggregation_time(client: Redis, account, ticker) -> datetime:
        position= redis_utils.get_position(client, account, ticker)
        if position != None:
             return position.last_aggregation_time
        return datetime.combine(redis_utils.get_startup_date(client), time())

    def rebuild(self):
        now= datetime.now()
        for key in self.client.scan_iter("positions*"):
            self.client.delete(key)
        self.cache= dict()
        startup_date= redis_utils.get_startup_date(self.client)
        for date in market_calendar.get_dates(startup_date, now.date()):
            trades= redis_utils.get_trades_by_day(self.client, date)
            market_trades, after_market_trades= self.split_trades_by_time(trades)
            for trade in market_trades:
                self.update_position(trade.account, trade.stock_ticker, trade.get_amount(), datetime.combine(date, trade.time))
            if date != now.date() or time(16) < now.time():
                self.take_snapshot(date)
            for trade in after_market_trades:
                self.update_position(trade.account, trade.stock_ticker, trade.get_amount(), datetime.combine(date, trade.time))

    @staticmethod
    def split_trades_by_time(trades: list[Trade]) -> tuple[list[Trade], list[Trade]]:
        before_four: list[Trade]= list()
        after_four: list[Trade]= list()
        for trade in trades:
            if trade.time < time(hour= 16):
                before_four.append(trade)
            else:
                after_four.append(trade)
        return before_four, after_four

if "__main__" == __name__:
    PositionListener().start()
