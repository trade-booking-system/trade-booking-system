from fastapi import APIRouter
from time import sleep

app= APIRouter()

@app.get("/sum/")
def sum(a: int, b: int):
    return {"sum": a + b}

@app.get("/echo/")
def echo(text: str, delay: int):
    sleep(delay / 1000.0)
    return {"text": text}
