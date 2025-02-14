from fastapi import FastAPI
from api.routers import auth, files
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(files.router)
