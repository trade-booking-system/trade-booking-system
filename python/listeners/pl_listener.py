from redis import Redis
from schema.schema import ProfitLoss, Position, Price
from datetime import datetime, date as date_obj
from utils import market_calendar
from listener import listener_base

class PLListener(listener_base):

    def get_handlers(self):
        return {
            "positionUpdates": self.position_updates_handler,
            "tradeUpdates": self.trade_updates_handler,
            "pricesUpdates": self.price_updates_handler
        }
    
    def startup(self):
        print("starting")

    def position_updates_handler(self, msg):
        data: str= msg["data"]
        account, ticker= data.split(":")
        self.queue.put_nowait((self.update_position_pl, (account, ticker)))

    def trade_updates_handler(self, msg):
        data: str= msg["data"]
        account, ticker, amount, price= data.split(":")
        self.queue.put_nowait((self.update_trade_pl, (account, ticker, int(amount), float(price))))

    def price_updates_handler(self, msg):
        if msg["data"] == "update":
            self.queue.put_nowait((self.update_position_pl, ()))

    def update_position_pl(self):
        stocks= self.client.smembers("p&lStocks")
        for stock_info in stocks:
            account, ticker= stock_info.split(":")
            self.update_position_pl(account, ticker)

    def update_position_pl(self, account: str, ticker: str):
        date= datetime.now().date()
        price = self.get_price(self.client, ticker, date)
        position= self.get_position(self.client, account, ticker)
        if price == None:
            print(f"error: ticker: {ticker} does not have a live price")
            return
        if position == None:
            return
        pl= self.get_pl(self.client, account, ticker)
        closing_price= self.get_previous_closing_price(ticker)
        pl.position_pl= (price - closing_price) * position.amount
        self.client.hset(f"p&l:{account}:{ticker}", date.isoformat(), pl.json())
        print(f"position p&l: account: {account} stock ticker: {ticker} profit loss: {pl.position_pl}")

    def update_trade_pl(self, account: str, ticker: str, amount: int, price: float):
        date= datetime.now().date()
        pl= self.get_pl(self.client, account, ticker)
        closing_price = self.get_previous_closing_price(ticker)
        pl.trade_pl+= (closing_price - price) * amount
        self.client.hset(f"p&l:{account}:{ticker}", date.isoformat(), pl.json())
        print(f"trade p&l: account: {account} stock ticker: {ticker} profit loss: {pl.trade_pl}")

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

PLListener()
