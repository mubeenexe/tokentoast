from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.core.config import settings
from app.routes import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    from app.core.redis import get_redis

    await get_redis()
    # Tables are managed by Alembic migrations; run: alembic upgrade head
    yield
    # shutdown
    from app.core.redis import _redis

    if _redis:
        await _redis.aclose()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
