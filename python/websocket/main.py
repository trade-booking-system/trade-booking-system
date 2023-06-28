from asyncio import Queue

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect

from .manager import ConnectionManager, get_manager

app = FastAPI(dependencies=[Depends(get_manager)])

@app.websocket("/positions")
async def watch_positions(websocket: WebSocket, manager: ConnectionManager = Depends(get_manager("positionUpdates"))):
    await loop(websocket, manager)

@app.websocket("/trades")
async def watch_trades(websocket: WebSocket, manager: ConnectionManager = Depends(get_manager("tradeUpdates"))):
    await loop(websocket, manager)

async def loop(websocket: WebSocket, manager: ConnectionManager):
    await websocket.accept()
    queue: Queue = Queue()
    await manager.subscribe(queue)
    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        manager.unsubscribe(queue)
