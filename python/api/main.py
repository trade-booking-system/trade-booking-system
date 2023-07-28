from utils.redis_initializer import get_redis_client
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from utils import redis_utils
from api import positions
from api import websocket
from api import pl_routes
from api import routes

@asynccontextmanager
async def startup(app: FastAPI):
    client= get_redis_client()
    redis_utils.set_startup_date(client)
    yield
    client.shutdown()

app = FastAPI(dependencies=[Depends(get_redis_client)], lifespan= startup)
app.include_router(routes.router)
app.include_router(positions.router, prefix="/positions")
app.include_router(websocket.router, prefix="/ws")
app.include_router(pl_routes.router, prefix="/pl")
