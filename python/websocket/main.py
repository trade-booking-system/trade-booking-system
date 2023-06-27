from asyncio import Queue

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect

from .manager import ConnectionManager, get_manager

app = FastAPI(dependencies=[Depends(get_manager)])

@app.websocket("/watchTrades")
async def watch(websocket: WebSocket, manager: ConnectionManager = Depends(get_manager)):
    await websocket.accept()
    queue: Queue = Queue()
    await manager.subscribe(queue)
    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        manager.unsubscribe(queue)
