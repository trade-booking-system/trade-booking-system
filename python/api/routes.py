import redis
from fastapi import APIRouter, Depends, UploadFile, File
from utils import booktrade as tradebooker
from utils.redis_initializer import get_redis_client
from utils import redis_utils
from utils.tickers import ValidTickers
from schema import Trade, History, TradeWithPl


router= APIRouter()
tickers= ValidTickers("utils/ListOfStocks.txt")


@router.put("/bookTrade")
async def book_trade(trade: Trade, client: redis.Redis = Depends(get_redis_client)) -> dict[str, str]:
    return tradebooker.booktrade(client, trade, tickers)

@router.post("/bookTradesBulk")
async def book_trades_bulk(trades: list[Trade], client: redis.Redis = Depends(get_redis_client)) -> dict[str, str]:
    return tradebooker.booktrades_bulk(client, trades)

@router.post("/csvToJson")
async def csv_to_json(file: UploadFile = File(...)):
    return tradebooker.csv_to_json(await file.read())


@router.post("/bookManyTrades")
async def book_trades(trades: list[dict], client: redis.Redis = Depends(get_redis_client)) -> list[dict]:
    return tradebooker.book_many_trades(client, trades, tickers)


@router.post("/updateTrade")
def update_trade(trade_id: str, account: str, date: str, updated_type: str= None, updated_amount: int= None, 
                 updated_price: int= None, client: redis.Redis = Depends(get_redis_client)) -> dict[str, str]:
    return tradebooker.update_trade(trade_id, account, date, updated_type, updated_amount, updated_price, client) 

@router.get("/getTrades")
async def get_trades(client: redis.Redis = Depends(get_redis_client)) -> list[Trade]:
    return tradebooker.get_trades(client)

@router.get("/queryTrades")
async def query_trades(account: str = "*", year: int = 0, month: int = 0, day: int = 0,
                       client: redis.Redis = Depends(get_redis_client)) -> list[TradeWithPl]:
    def default(value: int, pad: int) -> str:
        return "*" if value == 0 else str(value).zfill(pad)
    return [
        redis_utils.merge_trade(client, trade) for trade in
        redis_utils.query_trades(client, account, default(year, 4), default(month, 2), default(day, 2))
    ]

@router.get("/getTradeHistory")
def get_trade_history(trade_id: str, account: str, date: str, client: redis.Redis = Depends(get_redis_client)) -> History:
    return tradebooker.get_trade_history(trade_id, account, date, client)

@router.get("/getAccounts")
async def get_accounts(client: redis.Redis = Depends(get_redis_client)) -> set[str]:
    return tradebooker.get_accounts(client)

@router.get("/tickers")
async def get_tickers(tickers: ValidTickers = Depends(lambda: ValidTickers("utils/ListOfStocks.txt"))) -> list[str]:
    return tickers.get_all_tickers()
