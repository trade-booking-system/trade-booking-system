import redis
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from utils import booktrade as tradebooker
from utils.redis_initializer import get_redis_client
from utils.tickers import ValidTickers
from schema import Trade, History
from typing import IO, Union
from csv import DictReader
from pydantic import ValidationError
from io import StringIO
from datetime import datetime
from uuid import uuid4


router= APIRouter()
tickers= ValidTickers("utils/ListOfStocks.txt")

def create_trade_from_row(row):
    return Trade(
        account=row["accounts"],
        type=row["buyOrSell"],
        stock_ticker=row["tickers"],
        amount=int(row["shares"]),
        user=row.get("user", "101010"),
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

@router.put("/bookTrade")
async def book_trade(trade: Trade, client: redis.Redis = Depends(get_redis_client)) -> dict[str, str]:
    return tradebooker.booktrade(client, trade, tickers)

@router.post("/bookTradesBulk")
async def book_trades_bulk(trades: list[Trade], client: redis.Redis = Depends(get_redis_client)) -> dict[str, str]:
    return tradebooker.booktrades_bulk(client, trades)

"""
@router.post("/bookTradesBulkCSV")
async def book_trades_bulk_csv(file: UploadFile = File(...), client: redis.Redis = Depends(get_redis_client)):

    data: bytes = await file.read()
    text: str = data.decode()
    reader = DictReader(StringIO(text))
    for row in reader:
        trade = Trade(**row)
        tradebooker.booktrade(client, trade)
    return {"message": "Trades with csv file booked successfully"}

"""

@router.post("/csvToJson")
async def csv_to_json(file: UploadFile = File(...)) -> list[dict[str, Union[str, int, float]]]:
    data: bytes = await file.read()
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

@router.post("/bookManyTrades")
async def book_trades(trades: list[dict], client: redis.Redis = Depends(get_redis_client)) -> list[dict]:
    trade_responses = []
    request_group = str(uuid4())

    for trade_request in trades:

        trade = Trade(
            account=trade_request['account'],
            type=trade_request['type'],
            stock_ticker=trade_request['stock_ticker'],
            amount=trade_request['amount'],
            user="101010",
            price=trade_request['price']
        )

        tradebooked = tradebooker.booktrade(client, trade, tickers)

        response = {
            'id': tradebooked['Field'],
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

@router.post("/updateTrade")
def update_trade(trade_id: str, account: str, date: str, updated_type: str= None, updated_amount: int= None, 
                 updated_price: int= None, client: redis.Redis = Depends(get_redis_client)) -> dict[str, str]:
    return tradebooker.update_trade(trade_id, account, date, updated_type, updated_amount, updated_price, client) 

@router.get("/getTrades")
async def get_trades(client: redis.Redis = Depends(get_redis_client)) -> list[Trade]:
    return tradebooker.get_trades(client)

@router.get("/queryTrades")
async def query_trades(account: str = "*", year: int = 0, month: int = 0, day: int = 0,
                       client: redis.Redis = Depends(get_redis_client)) -> list[Trade]:
    def default(value: int, pad: int) -> str:
        return "*" if value == 0 else str(value).zfill(pad)
    return tradebooker.query_trades(account, default(year, 4), default(month, 2), default(day, 2), client)

@router.get("/getTradeHistory")
def get_trade_history(trade_id: str, account: str, date: str, client: redis.Redis = Depends(get_redis_client)) -> History:
    return tradebooker.get_trade_history(trade_id, account, date, client)

@router.get("/getAccounts")
async def get_accounts(client: redis.Redis = Depends(get_redis_client)) -> set[str]:
    return tradebooker.get_accounts(client)

@router.get("/tickers")
async def get_tickers(tickers: ValidTickers = Depends(lambda: ValidTickers("utils/ListOfStocks.txt"))) -> list[str]:
    return tickers.get_all_tickers()
