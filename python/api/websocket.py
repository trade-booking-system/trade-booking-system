from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from utils.redis_initializer import get_redis_client_zero
import json
from time import time
import asyncio
import redis

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
    pubsub = redis.pubsub(ignore_subscribe_messages= True)
    queue = asyncio.Queue()

    def handler(message):
        type, trade = message["data"].split(":", 1)
        data = {"type": type, "trade": trade.strip()}
        queue.put_nowait(data)
    
    pubsub.subscribe(**{"tradeUpdates":handler})
    pubsub.run_in_thread(daemon= True)

    try:
        while True:
            while not queue.empty():
                data = queue.get_nowait()
                await websocket.send_json(data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected")
