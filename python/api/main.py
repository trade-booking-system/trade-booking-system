from utils.redis_initializer import get_redis_client
from fastapi import FastAPI, Depends
from datetime import datetime
from api import positions
from api import websocket
from api import pl_routes
from api import routes

def set_startup_date():
    client= get_redis_client()
    key= "startupDate"
    if client.get(key) == None:
        client.set(key, datetime.now().date().isoformat())

set_startup_date()
app = FastAPI(dependencies=[Depends(get_redis_client)])
app.include_router(routes.router)
app.include_router(positions.router, prefix="/positions")
app.include_router(websocket.router, prefix="/ws")
app.include_router(pl_routes.router, prefix="/pl")
