from schema.schema import ProfitLoss, Price, TradeProfitLoss
from datetime import datetime, date as date_obj
from utils import market_calendar
from listener import listener_base
from redis import Redis
from utils import redis_utils

class PLListener(listener_base):

    def get_handlers(self):
        return {
            "positionUpdates": self.position_updates_handler,
            "tradeUpdates": self.trade_updates_handler,
            "pricesUpdates": self.price_updates_handler
        }
    
    def startup(self):
        self.recover_current_days_pl()
        #self.rebuild()

    def position_updates_handler(self, msg):
        data: str= msg["data"]
        account, ticker= data.split(":")
        self.queue.put_nowait((self.update_position_pl, (account, ticker, datetime.now().date())))

    def trade_updates_handler(self, msg):
        data: str= msg["data"]
        id, account, ticker, amount, price= data.split(":")
        self.queue.put_nowait((self.update_trade_pl, (id, account, ticker, int(amount), float(price), datetime.now().date())))

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
        closing_price= self.get_previous_closing_price(self.client, ticker)
        position= redis_utils.get_position(self.client, account, ticker)
        if price == None:
            print(f"error: ticker: {ticker} does not have a live price")
            return
        if closing_price == None:
            print(f"error: ticker {ticker} does not have a closing price")
            return
        if position == None:
            return
        pl= redis_utils.get_pl(self.client, account, ticker, date, ProfitLoss(account= account, ticker= ticker))
        pl.position_pl= self.calculate_position_pl(price.price, closing_price.price, position.amount)
        redis_utils.set_pl(self.client, account, ticker, date, pl)
        self.client.publish("pnlPositionUpdatesWS", pl.json())

        print(f"position p&l: account: {account} stock ticker: {ticker} profit loss: {pl.position_pl}")

    def update_trade_pl(self, account: str, ticker: str, amount: int, price: float, date: date_obj):
        closing_price = self.get_previous_closing_price(self.client, ticker)
        if closing_price == None:
            print(f"error: ticker {ticker} does not have a closing price")
            return
        pl= redis_utils.get_pl(self.client, account, ticker, date, ProfitLoss(account= account, ticker= ticker))
        trade_pl= self.calculate_trade_pl(closing_price.price, price, amount)
        pl.trade_pl+= trade_pl
        redis_utils.set_pl(self.client, account, ticker, date, pl)
        self.client.publish("pnlPositionUpdatesWS", pl.json())

        trade_pl_obj = TradeProfitLoss(
            trade_id= id, trade_pl= trade_pl, price_at_calc= price, date= date
        )
        redis_utils.set_trade_pl(self.client, id, date, trade_pl_obj)
        self.client.publish("pnlTradeUpdatesWS", trade_pl_obj.json())
        print(f"trade p&l: account: {account} stock ticker: {ticker} profit loss: {pl.trade_pl}")

    @staticmethod
    def calculate_position_pl(price: float, closing_price: float, position: int) -> float:
        return (price - closing_price) * position

    @staticmethod
    def calculate_trade_pl(closing_price: float, price: float, amount) -> float:
        return (closing_price - price) * amount
    
    @staticmethod
    def get_previous_closing_price(client: Redis, ticker: str) -> Price:
        date= market_calendar.get_most_recent_trading_day()
        return redis_utils.get_price(client, ticker, date)
    
    def recover_current_days_pl(self):
        now= datetime.now()
        date = now.date()
        self.update_all_position_pl(date)
        trades= redis_utils.get_trades_by_day(self.client, date)
        pl: dict[str, int]= dict()

        for trade in trades:
            closing_price= self.get_previous_closing_price(self.client, trade.stock_ticker)
            if closing_price == None:
                print(f"error: ticker {ticker} does not have a closing price")
                return
            key= trade.account+":"+trade.stock_ticker
            amount= pl.get(key, 0)
            trade_pl= self.calculate_trade_pl(closing_price.price, trade.price, trade.get_amount())
            amount+= trade_pl
            pl[key]= amount
            redis_utils.set_trade_pl(self.client, trade.id, now.date(), TradeProfitLoss(
                trade_id=trade.id, trade_pl=trade_pl, price_at_calc=closing_price.price,
                date=now.date()
            ))

        for key, trade_pl in pl.items():
            account, ticker= key.split(":")
            profit_loss= redis_utils.get_pl(self.client, account, ticker, date, ProfitLoss(account= account, ticker= ticker))
            profit_loss.trade_pl= trade_pl
            redis_utils.set_pl(self.client, account, ticker, date, profit_loss)
            print(f"recovered trade p&l: account: {account} stock ticker: {ticker} profit loss: {profit_loss.trade_pl}")

    def rebuild(self):
        now= datetime.now()
        for key in self.client.scan_iter("p&l*"):
            self.client.delete(key)
            dates= market_calendar.get_market_dates(redis_utils.get_startup_date, now.date())

PLListener().start()
