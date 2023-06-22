from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from time import sleep, time
from utils.redis_initializer import get_redis_client_zero, get_redis_client_one
from api import routes
from api import positions
import asyncio
from api import websocket

app = FastAPI(dependencies=[Depends(get_redis_client_zero), Depends(get_redis_client_one)])
app.include_router(routes.app)
app.include_router(positions.router, prefix="/positions")
app.include_router(websocket.router, prefix="/ws")


@app.get("/sum/")
def sum(a: int, b: int):
    return {"sum": a + b}

@app.get("/echo/")
def echo(text: str, delay: int):
    sleep(delay / 1000.0)
    return {"text": text}

@app.get("/hello")
async def hello():
    return {"hello": "hello"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_text(f"current time: {time()}")
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected")
