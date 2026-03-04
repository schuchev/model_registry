from fastapi import FastAPI
from app.api import router
from app.db import init_db
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Model Registry MVP")

app.include_router(router)

Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
async def startup():
    await init_db()