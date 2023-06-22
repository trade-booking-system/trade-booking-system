from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from time import time
import asyncio

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
