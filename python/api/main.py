from fastapi import FastAPI, Depends
from time import sleep
from utils.redis_initializer import get_redis_client
from api import routes
from api import positions
from api import websocket

app = FastAPI(dependencies=[Depends(get_redis_client)])
app.include_router(routes.router)
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
