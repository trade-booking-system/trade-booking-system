from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from time import time
import asyncio
import redis
from utils.redis_initializer import get_redis_client_zero

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_text(f"current time: {time()}")
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected")


@router.websocket("/watchTrades")
async def websocket_endpoint_watchTrade(websocket: WebSocket, redis: redis.Redis = Depends(get_redis_client_zero)):
    await websocket.accept()
    pubsub = redis.pubsub()
    queue = asyncio.Queue()

    def handler(message):
      #  print("message: ", message)
        if message:
            type, trade = message["data"].split(":", 1)
            queue.put_nowait({"type": type, "trade": trade}) 
            

    pubsub.subscribe(tradeUpdates = handler)
    pubsub.run_in_thread()

    try:
        while True:
            await websocket.send_text(f"current time: {time()}")
            if not queue.empty():
                data = await queue.get()
                await websocket.send_json(data)
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        print("Client disconnected")