from asyncio import Queue
import json

from fastapi import WebSocket, Depends
from redis import Redis

from utils.redis_initializer import get_redis_client

class ConnectionManager:
    def __init__(self, client: Redis, channel: str):
        self.subsribers: list[Queue] = []
        self.queue: Queue = Queue()
        self.connections: list[WebSocket] = []
        self.pubsub = client.pubsub()
        self.pubsub.run_in_thread()
        self.pubsub.subscribe(**{channel: self._handler})
    
    async def subscribe(self, queue: Queue):
        self.subsribers.append(queue)
    
    async def unsubscribe(self, queue: Queue):
        self.subsribers.remove(queue)
    
    def _handler(self, message):
        type, payload = message["data"].split(":", 1)
        data = {"type": type, "payload": json.loads(payload)}
        for queue in self.subsribers:
            queue.put_nowait(data)

def get_manager(channel: str) -> ConnectionManager:
    def sub(client: Redis = Depends(get_redis_client)):
        return ConnectionManager(client, channel)
    return sub
