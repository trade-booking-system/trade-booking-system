from utils.redis_initializer import get_redis_client
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from utils import redis_utils
from api import position_endpoints
from api import pl_endpoints
from api import trade_endpoints
from api import websocket

@asynccontextmanager
async def startup(app: FastAPI):
    client= get_redis_client()
    redis_utils.set_startup_date(client)
    yield
    client.shutdown()

app = FastAPI(dependencies=[Depends(get_redis_client)], lifespan= startup)
app.include_router(trade_endpoints.router)
app.include_router(position_endpoints.router, prefix="/positions")
app.include_router(pl_endpoints.router, prefix="/pl")
app.include_router(websocket.router, prefix="/ws")
