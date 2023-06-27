from asyncio import Queue

from fastapi import WebSocket, Depends
from redis import Redis

from utils.redis_initializer import get_redis_client

class ConnectionManager:
    def __init__(self, client: Redis):
        print("test1")
        self.subsribers: list[Queue] = []
        self.queue: Queue = Queue()
        self.connections: list[WebSocket] = []
        self.pubsub = client.pubsub()
        self.pubsub.run_in_thread()
        self.pubsub.subscribe(**{"tradeUpdates": self._handler})
    
    async def subscribe(self, queue: Queue):
        self.subsribers.append(queue)
    
    async def unsubscribe(self, queue: Queue):
        self.subsribers.remove(queue)
    
    def _handler(self, message):
        type, trade = message["data"].split(":", 1)
        data = {"type": type, "trade": trade.strip()}
        for queue in self.subsribers:
            queue.put_nowait(data)

def get_manager(client: Redis = Depends(get_redis_client)) -> ConnectionManager:
    return ConnectionManager(client)
