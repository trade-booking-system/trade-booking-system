from asyncio import Queue

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect

from .manager import ConnectionManager, get_manager

app = FastAPI(dependencies=[Depends(get_manager)])

@app.websocket("/positions")
async def watch_positions(websocket: WebSocket, accounts: str = "*", manager: ConnectionManager = Depends(get_manager("positionUpdatesWS"))):
    await loop(websocket, manager, accounts)

@app.websocket("/trades")
async def watch_trades(websocket: WebSocket, accounts: str = "*", manager: ConnectionManager = Depends(get_manager("tradeUpdatesWS"))):
    await loop(websocket, manager, accounts)

async def loop(websocket: WebSocket, manager: ConnectionManager, accounts: str):
    await websocket.accept()
    queue: Queue = Queue()
    id = await manager.subscribe(queue, accounts)
    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        manager.unsubscribe(id)
