from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from time import sleep, time
from utils.redis_initializer import get_redis_client_zero, get_redis_client_one
from api import routes
from api import positions
import asyncio

app = FastAPI(dependencies=[Depends(get_redis_client_zero), Depends(get_redis_client_one)])
app.include_router(routes.app)
app.include_router(positions.router, prefix="/positions")

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
        ptime = time()
        while True:
            if time() > ptime + 1:
                await websocket.send_text(f"current time: {ptime}")
                ptime = time()
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print("Client disconnected")


