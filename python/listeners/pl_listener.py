from schema.schema import ProfitLoss, Position, Price
from datetime import datetime, date as date_obj
from utils.booktrade import query_trades, get_amount
from utils import market_calendar
from listener import listener_base
from redis import Redis

class PLListener(listener_base):

    def get_handlers(self):
        return {
            "positionUpdates": self.position_updates_handler,
            "tradeUpdates": self.trade_updates_handler,
            "pricesUpdates": self.price_updates_handler
        }
    
    def startup(self):
        self.recover_current_days_pl()

    def position_updates_handler(self, msg):
        data: str= msg["data"]
        account, ticker= data.split(":")
        self.queue.put_nowait((self.update_position_pl, (account, ticker, datetime.now().date())))

    def trade_updates_handler(self, msg):
        data: str= msg["data"]
        account, ticker, amount, price= data.split(":")
        self.queue.put_nowait((self.update_trade_pl, (account, ticker, int(amount), float(price), datetime.now().date())))

    def price_updates_handler(self, msg):
        if msg["data"] == "updated":
            self.queue.put_nowait((self.update_all_position_pl, (datetime.now().date(), )))

    def update_all_position_pl(self, date: date_obj):
        stocks= self.client.smembers("p&lStocks")
        for stock_info in stocks:
            account, ticker= stock_info.split(":")
            self.update_position_pl(account, ticker, date)

    def update_position_pl(self, account: str, ticker: str, date: date_obj):
        price = self.get_price(self.client, ticker, date)
        position= self.get_position(self.client, account, ticker)
        if price == None:
            print(f"error: ticker: {ticker} does not have a live price")
            return
        if position == None:
            return
        pl= self.get_pl(self.client, account, ticker)
        closing_price= self.get_previous_closing_price(ticker)
        pl.position_pl= self.calculate_position_pl(price, closing_price, position.amount)
        self.client.hset(f"p&l:{account}:{ticker}", date.isoformat(), pl.json())
        print(f"position p&l: account: {account} stock ticker: {ticker} profit loss: {pl.position_pl}")

    def update_trade_pl(self, account: str, ticker: str, amount: int, price: float, date: date_obj):
        pl= self.get_pl(self.client, account, ticker)
        closing_price = self.get_previous_closing_price(ticker)
        pl.trade_pl+= self.calculate_trade_pl(closing_price, price, amount)
        self.client.hset(f"p&l:{account}:{ticker}", date.isoformat(), pl.json())
        print(f"trade p&l: account: {account} stock ticker: {ticker} profit loss: {pl.trade_pl}")

    @staticmethod
    def calculate_position_pl(price: float, closing_price: float, position: int) -> float:
         return (price - closing_price) * position
    
    @staticmethod
    def calculate_trade_pl(closing_price: float, price: float, amount) -> float:
        return (closing_price - price) * amount

    def get_previous_closing_price(self, ticker: str) -> float:
        date= market_calendar.get_most_recent_trading_day()
        return self.get_price(self.client, ticker, date)

    @staticmethod
    def get_price(client: Redis, ticker: str, date: date_obj) -> float:
        price_json= client.hget("livePrices:"+ticker.upper(), date.isoformat())
        if price_json == None:
            return None
        price= Price.parse_raw(price_json)
        return price.price

    @staticmethod
    def get_position(client: Redis, account: str, ticker: str) -> Position:
        json_position= client.hget("positions:"+account, ticker)
        if json_position == None:
            return None
        return Position.parse_raw(json_position)
    
    @staticmethod
    def get_pl(client: Redis, account: str, ticker: str) -> ProfitLoss:
        date= datetime.now().date()
        pl_json= client.hget(f"p&l:{account}:{ticker}", date.isoformat())
        if pl_json == None:
            return ProfitLoss(trade_pl= 0, position_pl= 0)
        return ProfitLoss.parse_raw(pl_json)
    
    def recover_current_days_pl(self):
        now= datetime.now()
        self.update_all_position_pl(now.date())
        trades= query_trades("*", now.year, now.month, now.day, self.client)
        pl: dict[str, int]= dict()
        for trade in trades:
            closing_price= self.get_previous_closing_price(trade.stock_ticker)
            key= trade.account+":"+trade.stock_ticker
            amount= pl.get(key, 0)
            amount=+ self.calculate_trade_pl(closing_price, trade.price, get_amount(trade))
            pl[key]= amount

        for key, trade_pl in pl.items():
            account, ticker= key.split(":")
            profit_loss= self.get_pl(self.client, account, ticker)
            profit_loss.trade_pl= trade_pl
            self.client.hset(f"p&l:{account}:{ticker}", now.date().isoformat(), profit_loss.json())

    def rebuild(self):
        keys= self.client.keys("p&l:*")
        self.client.delete(*keys)

PLListener()
