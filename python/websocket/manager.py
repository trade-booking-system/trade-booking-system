from asyncio import Queue
from json import loads
from datetime import datetime, date, time

from fastapi import Depends
from redis import Redis

from utils.redis_initializer import get_redis_client
from utils.redis_utils import get_position, get_trade, get_pl, get_trade_pl

class Connection:
    def __init__(self, queue: Queue, accounts: str):
        self.queue = queue
        if accounts == "*":
            self.accounts = []
        else:
            self.accounts = accounts.split(",")
    
    def has_account(self, account: str) -> bool:
        if self.accounts == []:
            return True
        else:
            return account in self.accounts
    
    def add_message(self, data):
        self.queue.put_nowait(data)

class ConnectionManager():
    def __init__(self, client: Redis, channels: dict[str, any]):
        self.queue: Queue = Queue()
        self.connections: dict[int, Connection] = {}
        self.client = client
        self.pubsub = client.pubsub(ignore_subscribe_messages = True)
        self.pubsub.run_in_thread()
        self.pubsub.subscribe(**{key: self._handler(value) for key, value in channels.items()})
        self.key = 0
    
    async def subscribe(self, queue: Queue, accounts: str) -> int:
        self.connections[self.key] = Connection(queue, accounts)
        self.key += 1
        return self.key - 1
    
    async def unsubscribe(self, id: int):
        del self.connections[id]
    
    def _handler(self, func):
        def handle(message):
            type, payload = message["data"].split(":", 1)
            data = loads(payload)
            account = data["account"]
            if func(self.client, data) != None:
                data = data | func(self.client, data).dict()
                data["pnl_valid"] = True
            else:
                data["pnl_valid"] = False
            for key, value in data.items():
                if isinstance(value, (datetime, time, date)):
                    data[key] = str(value)
            for connection in self.connections.values():
                if connection.has_account(account):
                    connection.add_message({"type": type, "payload": data})
        return handle

def get_manager(channels: dict[str, any]):
    def sub(client: Redis = Depends(get_redis_client)):
        return ConnectionManager(client, channels)
    return sub

def get_trade_manager():
    return get_manager({
        "tradeUpdatesWS": lambda client, data : get_trade_pl(
            client, id=data["id"],
            date=datetime.fromisoformat(data["date"]).date()),
        "pnlTradeUpdatesWS": lambda client, data : get_trade(
            client, account=data["account"], id=data["trade_id"],
            date=datetime.fromisoformat(data["date"]).date()
        )
    })

def get_position_manager():
    return get_manager({
        "positionUpdatesWS": lambda client, data : get_pl(
            client, account=data["account"], ticker=data["stock_ticker"],
            date=datetime.fromisoformat(data["last_aggregation_time"]).date()
        ),
        "pnlPositionUpdatesWS": lambda client, data : get_position(
            client, account=data["account"], ticker=data["ticker"]
        )
    })
