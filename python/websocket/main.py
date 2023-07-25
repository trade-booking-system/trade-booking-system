from asyncio import Queue

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect

from .manager import ConnectionManager, get_trade_manager, get_position_manager

app = FastAPI()

@app.websocket("/positions")
async def watch_positions(websocket: WebSocket, accounts: str = "*", manager: ConnectionManager = Depends(get_position_manager())):
    await loop(websocket, manager, accounts)

@app.websocket("/trades")
async def watch_trades(websocket: WebSocket, accounts: str = "*", manager: ConnectionManager = Depends(get_trade_manager())):
    await loop(websocket, manager, accounts)

async def loop(websocket: WebSocket, manager: ConnectionManager, accounts: str):
    await websocket.accept()
    print("Connected: " + accounts)
    queue: Queue = Queue()
    id = await manager.subscribe(queue, accounts)
    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        manager.unsubscribe(id)
