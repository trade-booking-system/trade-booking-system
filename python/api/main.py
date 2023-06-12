from fastapi import FastAPI
from time import sleep
import trading

app= FastAPI()
app.include_router(trading.app)

@app.get("/sum/")
def sum(a: int, b: int):
    return {"sum": a + b}

@app.get("/echo/")
def echo(text: str, delay: int):
    sleep(delay / 1000.0)
    return {"text": text}
