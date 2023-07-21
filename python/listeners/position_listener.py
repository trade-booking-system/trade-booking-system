from datetime import datetime, date as date_obj, time
from schema import Position, Trade
from apscheduler.schedulers.background import BackgroundScheduler
from utils.booktrade import query_trades
from utils.get_positions import get_all_positions
from listener import listener_base
from utils import market_calendar
from redis import Redis

class PositionListener(listener_base):
    def __init__(self):
        self.cache: dict[str, dict[str, int]] = {}
        self.scheduler= BackgroundScheduler()
        super().__init__()
        self.scheduler.add_job(self.take_snapshot, "cron", day_of_week= "0-4", hour= 16)
        self.scheduler.start()

    def get_handlers(self):
        return {
            "tradesInfo": self.trade_updates_handler
        }
    
    def startup(self):
        self.recover()
        #self.rebuild()

    def trade_updates_handler(self, msg):
        data: str= msg["data"]
        account, stock_ticker, amount= data.split(":")
        self.queue.put_nowait((self.update_position_and_notify, (account, stock_ticker, int(amount), datetime.now())))

    def update_position_and_notify(self, account: str, stock_ticker: str, amount_added: int, now: datetime):
        self.update_position(account, stock_ticker, amount_added, now)
        self.client.publish("positionUpdates", f"{account}:{stock_ticker}")

    def update_position(self, account: str, stock_ticker: str, amount_added: int, now: datetime):
        key = "positions:"+account
        stock_tickers= self.cache.get(account, dict())
        self.cache[account]= stock_tickers
        old_amount= stock_tickers.get(stock_ticker)
        if old_amount == None:
            position_json= self.client.hget(key, stock_ticker)
            old_amount= 0
            if position_json != None:
                old_position= Position.parse_raw(position_json)
                old_amount= old_position.amount
        amount= old_amount + amount_added

        stock_tickers[stock_ticker]= amount
        position= Position(account= account, stock_ticker= stock_ticker, amount= amount, 
                        last_aggregation_time= now, last_aggregation_host= "host")
        
        self.client.hset(key, stock_ticker, position.json())
        self.client.publish("positionUpdatesWS", f"position:{position.json()}")

    def take_snapshot(self, now= datetime.now()):
        if not market_calendar.is_trading_day(now.date()):
            return
        positions= get_all_positions(self.client)
        for position in positions:
            self.set_snapshot(self.client, now, position)

    @staticmethod
    def set_snapshot(client: Redis, date: date_obj, position: Position):
        key= f"positionsSnapshots:{position.account}:{date.isoformat()}"
        client.hset(key, position.stock_ticker, position.json())

    @staticmethod
    def get_position(client: Redis, account: str, ticker: str) -> Position:
        json_position= client.hget("positions:"+account, ticker)
        if json_position == None:
            return None
        return Position.parse_raw(json_position)

    def recover(self):
        now= datetime.now()
        stocks: list[str]= self.client.smembers("p&lStocks")
        trades_cache: dict[str, list[Trade]]= dict()
        for stock in stocks:
            account, ticker= stock.split(":")
            last_aggregation_time= self.get_last_aggregation_time(self.client, account, ticker)
            
            dates = market_calendar.get_dates(last_aggregation_time.date(), now.date())
            for date in dates:
                trades= self.get_trades_by_ticker(account, ticker, date, trades_cache)
                if date == last_aggregation_time.date():
                    trades= [trade for trade in trades if last_aggregation_time.time() < trade.time]
                market_trades, after_market_trades= self.split_trades_by_time(trades)
                for trade in market_trades:
                    self.update_position(account, ticker, trade.get_amount(), datetime.combine(date, trade.time))
                
                position = self.get_position(self.client, account, ticker)
                if position != None:
                    if now.date() != position.last_aggregation_time.date() or now.time() > time(16):
                        self.set_snapshot(self.client, date, position)
                        
                for trade in after_market_trades:
                    self.update_position(account, ticker, trade.get_amount(), datetime.combine(date, trade.time))

        self.client.publish("pricesUpdates", "updated")

    def get_trades_by_ticker(self, account: str, ticker: str, date: date_obj, cache: dict[str, Trade]) -> list[Trade]:
        days_trades= self.get_trades_by_day(account, date, cache)
        return [trade for trade in days_trades if trade.stock_ticker == ticker]

    def get_trades_by_day(self, account: str, date: date_obj, cache: dict[str, list[Trade]]) -> list[Trade]:
        key= f"{account}:{date.isoformat()}"
        trades= cache.get(key)
        if trades != None:
            return trades
        trades= query_trades(account= account, year= str(date.year), month= str(date.month).zfill(2), day= str(date.day).zfill(2), client= self.client)
        cache[key]= trades
        return trades

    @staticmethod
    def get_last_aggregation_time(client: Redis, account, ticker) -> datetime:
        json_position= client.hget("positions:"+account, ticker)
        if json_position != None:
            return Position.parse_raw(json_position).last_aggregation_time
        return PositionListener.get_startup_date(client)

    def rebuild(self):
        now= datetime.now()
        for key in self.client.scan_iter("positions*"):
            self.client.delete(key)
        self.cache= dict()
        startup_date= PositionListener.get_startup_date(self.client)
        for date in market_calendar.get_dates(startup_date, datetime.now().date()):
            trades= query_trades(account= "*", year= str(date.year), month= str(date.month).zfill(2), day= str(date.day).zfill(2), client= self.client)
            market_trades, after_market_trades= self.split_trades_by_time(trades)
            for trade in market_trades:
                self.update_position(trade.account, trade.stock_ticker, trade.get_amount(), datetime.combine(date, trade.time))
            if date != now.date() or time(16) < now.time():
                self.take_snapshot(date)
            for trade in after_market_trades:
                self.update_position(trade.account, trade.stock_ticker, trade.get_amount(), datetime.combine(date, trade.time))

    @staticmethod
    def get_startup_date(client: Redis) -> date_obj:
        startup_date= client.get("startupDate")
        if startup_date == None:
            return datetime.now().date()
        return date_obj.fromisoformat(startup_date)

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

PositionListener()