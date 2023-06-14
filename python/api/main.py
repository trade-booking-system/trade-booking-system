from fastapi import FastAPI
from time import sleep
from utils import redis_initializer
import routes

redis_initializer.initialize_redis()

app= FastAPI()
app.include_router(routes.app)

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
