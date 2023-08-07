from schema.schema import ProfitLoss, Price, TradeProfitLoss, Position, Trade
from datetime import datetime, timedelta, date as date_obj
from utils import market_calendar
from listeners.listener import listener_base
from redis import Redis
from utils import redis_utils
import json

class PLListener(listener_base):

    def get_handlers(self):
        return {
            "positionUpdates": self.position_updates_handler,
            "tradeUpdates": self.trade_updates_handler,
            "pricesUpdates": self.price_updates_handler
        }

    def position_updates_handler(self, msg):
        data: str= msg["data"]
        position_update= json.loads(data)
        position_update["date"]= date_obj.fromisoformat(position_update["date"])
        self.queue.put_nowait((self.fill_in_position_pl, position_update))

    def trade_updates_handler(self, msg):
        data: str= msg["data"]
        trade_update= json.loads(data)
        trade_update["date"]= date_obj.fromisoformat(trade_update["date"])
        self.queue.put_nowait((self.update_trade_pl, trade_update))

    def price_updates_handler(self, msg):
        if msg["data"] == "updated":
            self.queue.put_nowait((self.update_all_position_pl, {"date": datetime.now().date()}))

    def update_all_position_pl(self, date: date_obj):
        stocks= redis_utils.get_stocks(self.client)
        for stock_info in stocks:
            account, ticker= stock_info.split(":")
            self.update_position_pl(account, ticker, date)

    def fill_in_position_pl(self, account: str, ticker: str, date: date_obj, end_date: date_obj= datetime.now().date()):
        dates= market_calendar.get_market_dates(date, end_date)
        for market_date in dates:
            self.update_position_pl(account, ticker, market_date)

    def update_position_pl(self, account: str, ticker: str, date: date_obj):
        price = redis_utils.get_price(self.client, ticker, date)
        closing_price= self.get_previous_closing_price(self.client, ticker, date)
        position= self.get_position_by_day(self.client, account, ticker, date)
        if price == None:
            print(f"error: ticker: {ticker} does not have a live price")
            return
        if closing_price == None:
            print(f"error: ticker {ticker} does not have a closing price")
            return
        if position == None:
            print(f"account: {account} ticker: {ticker} does not have position")
            return
        pl= redis_utils.get_pl(self.client, account, ticker, date, ProfitLoss(account= account, ticker= ticker))
        pl.position_pl= self.calculate_position_pl(price.price, closing_price.price, position.amount)
        redis_utils.set_pl(self.client, account, ticker, date, pl)
        self.client.publish("pnlPositionUpdatesWS", "pnl: " + pl.json())

        print(f"position p&l: account: {account} stock ticker: {ticker} profit loss: {pl.position_pl}")

    def update_trade_pl(self, id: str, account: str, ticker: str, amount: int, price: float, date: date_obj):
        trading_day= market_calendar.get_upcoming_trading_day(date)
        closing_price= self.get_previous_closing_price(self.client, ticker, trading_day)
        if closing_price == None:
            print(f"error: ticker {ticker} does not have a closing price")
            return
        pl= redis_utils.get_pl(self.client, account, ticker, trading_day, ProfitLoss(account= account, ticker= ticker))
        trade_pl= self.calculate_trade_pl(closing_price.price, price, amount)
        pl.trade_pl+= trade_pl
        redis_utils.set_pl(self.client, account, ticker, trading_day, pl)

        if trading_day >= datetime.now().date():
            self.client.publish("pnlPositionUpdatesWS", "pnl: " + pl.json())

        trade_pl_obj = TradeProfitLoss(
            account= account, trade_id= id, trade_pl= trade_pl, closing_price= closing_price.price, trading_date= trading_day, date= date
        )
        redis_utils.set_trade_pl(self.client, id, date, trade_pl_obj)
        self.client.publish("pnlTradeUpdatesWS", "pnl: " + trade_pl_obj.json())
        print(f"trade p&l: account: {account} stock ticker: {ticker} profit loss: {pl.trade_pl}")

    @staticmethod
    def calculate_position_pl(price: float, closing_price: float, position: int) -> float:
        return (price - closing_price) * position

    @staticmethod
    def calculate_trade_pl(closing_price: float, price: float, amount) -> float:
        return (closing_price - price) * amount
    
    @staticmethod
    def get_previous_closing_price(client: Redis, ticker: str, date: date_obj) -> Price:
        date= market_calendar.get_most_recent_trading_day(date)
        price= redis_utils.get_price(client, ticker, date)
        if price == None or not price.is_closing_price():
            return None
        return price
    
    @staticmethod
    def get_position_by_day(client: Redis, account: str, ticker: str, date: date_obj) -> Position:
        now= datetime.now()
        if date == now.date():
            if now.time() >= market_calendar.closing_time:
                return None
            return redis_utils.get_position(client, account, ticker)
        return redis_utils.get_position_snapshot(client, account, date, ticker)
    
    # recover todays p&l
    def recover(self):
        date = datetime.now().date()
        self.client.delete("trade_p&l:"+ date.isoformat())
        end_date= market_calendar.get_upcoming_trading_day(date)
        start_date= market_calendar.get_most_recent_trading_day(end_date) + timedelta(1)
        for date in market_calendar.get_dates(start_date, end_date):
            self.recover_days_pl(date)

    def recover_days_pl(self, date):
        trades= redis_utils.get_trades_by_day(self.client, date)
        trading_day= market_calendar.get_upcoming_trading_day(date)

        if trading_day == date:
            self.update_all_position_pl(date)

        pl= self.calculate_days_pl(date, trading_day, trades)
        self.set_days_pl(pl, trading_day)

    def calculate_days_pl(self, date: date_obj, trading_day: date_obj, trades: list[Trade]) -> dict[str, int]:
        pl: dict[str, int]= dict()
        for trade in trades:
            closing_price= self.get_previous_closing_price(self.client, trade.stock_ticker, trading_day)
            if closing_price == None:
                print(f"error: ticker {trade.stock_ticker} does not have a closing price")
                continue
            key= trade.account+":"+trade.stock_ticker
            amount= pl.get(key, 0)
            trade_pl= self.calculate_trade_pl(closing_price.price, trade.price, trade.get_amount())
            amount+= trade_pl
            pl[key]= amount

            trade_pl_obj = TradeProfitLoss(
                account= trade.account, trade_id= trade.id, trade_pl=trade_pl, 
                closing_price= closing_price.price, trading_date= trading_day, date= date
            )

            redis_utils.set_trade_pl(self.client, trade.id, date, trade_pl_obj)
            self.client.publish("pnlTradeUpdatesWS", "pnl: " + trade_pl_obj.json())
        return pl

    def set_days_pl(self, pl: dict[str, int], trading_day: date_obj):
        now = datetime.now()
        for key, trade_pl in pl.items():
            account, ticker= key.split(":")
            profit_loss= redis_utils.get_pl(self.client, account, ticker, trading_day, ProfitLoss(account= account, ticker= ticker))
            profit_loss.trade_pl+= trade_pl
            redis_utils.set_pl(self.client, account, ticker, trading_day, profit_loss)
            if trading_day >= now.date():
                self.client.publish("pnlPositionUpdatesWS", "pnl: " + profit_loss.json())
            print(f"recovered trade p&l: trading day: {trading_day} account: {account} stock ticker: {ticker} profit loss: {profit_loss.trade_pl}")

    def rebuild(self):
        for key in self.client.scan_iter("p&l*"):
            self.client.delete(key)
        for key in self.client.scan_iter("trade_p&l*"):
            self.client.delete(key)
        now= datetime.now()
        startup_date = redis_utils.get_startup_date(self.client)
        dates= market_calendar.get_dates(startup_date, market_calendar.get_upcoming_trading_day(now.date()))
        for date in dates:
            self.recover_days_pl(date)
            
if "__main__" == __name__:
    PLListener().start()
