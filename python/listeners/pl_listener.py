from schema.schema import ProfitLoss, Price, TradeProfitLoss, Position
from datetime import datetime, timedelta, date as date_obj
from utils import market_calendar
from listeners.listener import listener_base
from redis import Redis
from utils import redis_utils

class PLListener(listener_base):

    def get_handlers(self):
        return {
            "positionUpdates": self.position_updates_handler,
            "tradeUpdates": self.trade_updates_handler,
            "pricesUpdates": self.price_updates_handler
        }

    def position_updates_handler(self, msg):
        data: str= msg["data"]
        account, ticker= data.split(":")
        self.queue.put_nowait((self.update_position_pl, (account, ticker, datetime.now().date())))

    def trade_updates_handler(self, msg):
        data: str= msg["data"]
        id, account, ticker, amount, price, date= data.split(":")
        self.queue.put_nowait((self.update_trade_pl, (id, account, ticker, int(amount), float(price), date_obj.fromisoformat(date))))

    def price_updates_handler(self, msg):
        if msg["data"] == "updated":
            self.queue.put_nowait((self.update_all_position_pl, (datetime.now().date(), )))

    def update_all_position_pl(self, date: date_obj):
        stocks= redis_utils.get_stocks(self.client)
        for stock_info in stocks:
            account, ticker= stock_info.split(":")
            self.update_position_pl(account, ticker, date)

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
        closing_price = self.get_previous_closing_price(self.client, ticker, date)
        if closing_price == None:
            print(f"error: ticker {ticker} does not have a closing price")
            return
        pl= redis_utils.get_pl(self.client, account, ticker, date, ProfitLoss(account= account, ticker= ticker))
        trade_pl= self.calculate_trade_pl(closing_price.price, price, amount)
        pl.trade_pl+= trade_pl
        redis_utils.set_pl(self.client, account, ticker, date, pl)

        self.client.publish("pnlPositionUpdatesWS", "pnl: " + pl.json())

        trade_pl_obj = TradeProfitLoss(
            account= account, trade_id= id, trade_pl= trade_pl, closing_price= closing_price.price, date= date
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
        trading_day= market_calendar.get_most_recent_trading_day(date + timedelta(1))
        if trading_day == market_calendar.get_most_recent_trading_day(datetime.now().date() + timedelta(1)):
            return redis_utils.get_position(client, account, ticker)
        return redis_utils.get_position_snapshot(client, account, trading_day, ticker)
    
    # recover todays p&l
    def recover(self):
        date = datetime.now().date()
        return self.recover_days_pl(date)

    def recover_days_pl(self, date):
        self.update_all_position_pl(date)
        trades= redis_utils.get_trades_by_day(self.client, date)
        pl: dict[str, int]= dict()

        for trade in trades:
            closing_price= self.get_previous_closing_price(self.client, trade.stock_ticker, date)
            if closing_price == None:
                print(f"error: ticker {ticker} does not have a closing price")
                return
            key= trade.account+":"+trade.stock_ticker
            amount= pl.get(key, 0)
            trade_pl= self.calculate_trade_pl(closing_price.price, trade.price, trade.get_amount())
            amount+= trade_pl
            pl[key]= amount
            redis_utils.set_trade_pl(self.client, trade.id, date, TradeProfitLoss(
                account= trade.account, trade_id= trade.id, trade_pl=trade_pl, 
                closing_price= closing_price.price, date= date
            ))

        for key, trade_pl in pl.items():
            account, ticker= key.split(":")
            profit_loss= redis_utils.get_pl(self.client, account, ticker, date, ProfitLoss(account= account, ticker= ticker))
            profit_loss.trade_pl= trade_pl
            redis_utils.set_pl(self.client, account, ticker, date, profit_loss)
            print(f"recovered trade p&l: date: {date} account: {account} stock ticker: {ticker} profit loss: {profit_loss.trade_pl}")

    def rebuild(self):
        now= datetime.now()
        for key in self.client.scan_iter("p&l*"):
            self.client.delete(key)
        dates= market_calendar.get_market_dates(redis_utils.get_startup_date(self.client), now.date())
        for date in dates:
            self.recover_days_pl(date)
            
if "__main__" == __name__:
    PLListener().start()
