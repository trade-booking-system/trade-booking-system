from datetime import datetime, date as date_obj
from schema import Trade, History
from utils.tickers import ValidTickers
from fastapi import HTTPException
from csv import DictReader
from pydantic import ValidationError
from io import StringIO
from uuid import uuid4
import redis
from utils import redis_utils

def booktrade(client: redis.Redis, trade: Trade, tickers: ValidTickers):
    if not tickers.is_valid_ticker(trade.stock_ticker):
        raise HTTPException(status_code= 400, detail= "invalid stock ticker")
    history= History()
    history.trades.append(trade)
    redis_utils.set_history(client, trade.account, trade.date, trade.id, history)
    trade_amount = trade.get_amount()
    client.publish("tradesInfo", f"{trade.account}:{trade.stock_ticker}:{trade_amount}:{trade.date.isoformat()}")
    client.publish("tradeUpdates", f"{trade.id}:{trade.account}:{trade.stock_ticker}:{trade_amount}:{trade.price}:{trade.date.isoformat()}")
    client.publish("tradeUpdatesWS", f"create: {trade.json()}")
    redis_utils.add_to_stocks(client, trade.account, trade.stock_ticker)
    return {"message" : "trade booked successfully", "id" : trade.id}

def booktrades_bulk(client: redis.Redis, trades: list[Trade]):
    for trade in trades:
        booktrade(client, trade)
    return {"message": "trades booked successfully"}

def update_trade(trade_id: str, account: str, date: date_obj, updated_type: str, updated_amount: int, updated_price: float, client: redis.Redis):
    history= redis_utils.get_history(client, account, date, trade_id)
    if history == None:
        raise HTTPException(status_code= 400, detail= "trade does not exist")
    old_trade= history.get_current_trade()
    if old_trade.date != datetime.now().date():
        raise HTTPException(status_code= 400, detail= "trade being updated was not created today")
    trade= create_updated_trade(updated_amount, updated_type, updated_price, old_trade)
    history.add_updated_trade(trade)
    if updated_amount != None or updated_type != None:
        # undo previous version of trade and add new trade
        client.publish("tradesInfo", f"{trade.account}:{trade.stock_ticker}:{trade.get_amount() - old_trade.get_amount()}")

    client.publish("tradeUpdates", f"{trade.id}:{trade.account}:{trade.stock_ticker}:{-old_trade.get_amount()}:{old_trade.price}:{trade.date.isoformat()}")
    client.publish("tradeUpdates", f"{trade.id}:{trade.account}:{trade.stock_ticker}:{trade.get_amount()}:{trade.price}:{trade.date.isoformat()}")

    client.publish("tradeUpdatesWS", f"update: {trade.json()}")
    redis_utils.set_history(client, trade.account, trade.date, trade.id, history)
    return {"message": "trade updated successfully", "id" : trade.id, "version" : trade.version}

def create_updated_trade(updated_amount, updated_type, updated_price, old_trade: Trade) -> Trade:
        if updated_amount == None:
            updated_amount= old_trade.amount
        if updated_type == None:
            updated_type= old_trade.type
        if updated_price == None:
            updated_price= old_trade.price
        version= old_trade.version+1
        return Trade(id= old_trade.id, account= old_trade.account, stock_ticker= old_trade.stock_ticker, user= old_trade.user,
                      version= version, type= updated_type, amount= updated_amount, price= updated_price)

def get_trade_history(trade_id: str, account: str, date: str, client: redis.Redis) -> History:
    history = redis_utils.get_history(client, account, date_obj.fromisoformat(date), trade_id)
    if history == None:
        raise HTTPException(status_code= 404, detail= "trade does not exist")
    return history

def get_accounts(client: redis.Redis) -> set[str]:
    accounts = set()
    for stock in redis_utils.get_stocks(client):
        accounts.add(stock.split(":")[0])
    return accounts

def csv_to_json(data: bytes):
    text: str = data.decode()
    reader = DictReader(StringIO(text))

    trades = []
    for row in reader:
        try:
            trade = create_trade_from_row(row)
            trades.append(trade_to_dict(trade))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail="Invalid trade data in CSV file.")

    return trades

def create_trade_from_row(row):
    return Trade(
        account=row["accounts"],
        type=row["buyOrSell"],
        stock_ticker=row["tickers"],
        amount=int(row["shares"]),
        user=row.get("user", "default user"),
        price=float(row["price"]) if row["price"] else None
    )

def trade_to_dict(trade: Trade):
    return {
        "tickers": trade.stock_ticker,
        "accounts": trade.account,
        "buyOrSell": trade.type,
        "shares": str(trade.amount),
        "price": str(trade.price)
    }

def book_many_trades(client: redis.Redis, trades: list[dict], tickers: ValidTickers):

    trade_responses = []
    request_group = str(uuid4())

    for trade_request in trades:
        trade = Trade(
            account=trade_request['account'],
            type=trade_request['type'],
            stock_ticker=trade_request['stock_ticker'],
            amount=trade_request['amount'],
            user="default user",
            price=trade_request['price']
        )

        tradebooked = booktrade(client, trade, tickers)

        response = {
            'id': tradebooked['id'],
            'booked_at': datetime.now().isoformat(),
            'request_group': request_group,
            'accounts': trade_request['account'],
            'buyOrSell': trade_request['type'],
            'tickers': trade_request['stock_ticker'],
            'shares': trade_request['amount'],
            'price': trade_request['price']
        }

        trade_responses.append(response)

    return trade_responses
