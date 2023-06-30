from asyncio import Queue
import json

from fastapi import Depends
from redis import Redis

from utils.redis_initializer import get_redis_client

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

class ConnectionManager:
    def __init__(self, client: Redis, channel: str):
        self.queue: Queue = Queue()
        self.connections: dict[int, Connection] = {}
        self.pubsub = client.pubsub()
        self.pubsub.run_in_thread()
        self.pubsub.subscribe(**{channel: self._handler})
        self.key = 0
    
    async def subscribe(self, queue: Queue, accounts: str) -> int:
        self.connections[self.key] = Connection(queue, accounts)
        self.key += 1
        return self.key - 1
    
    async def unsubscribe(self, id: int):
        del self.connections[id]
    
    def _handler(self, message):
        type, payload = message["data"].split(":", 1)
        data = json.loads(payload)
        account = data["account"]
        for connection in self.connections.values():
            if connection.has_account(account):
                connection.add_message({"type": type, "payload": data})

def get_manager(channel: str) -> ConnectionManager:
    def sub(client: Redis = Depends(get_redis_client)):
        return ConnectionManager(client, channel)
    return sub
