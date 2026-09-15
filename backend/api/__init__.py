from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware.logging import LoggingMiddleware
from api.middleware.rate_limit import setup_rate_limiting
from api.db.base import Base
from api.db.session import engine
import api.db.models

from .routes import register_routes
from .core.env import env


def create_app() -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        Base.metadata.create_all(bind=engine)
        yield

    app = FastAPI(
        title="Hackaton 1 API",
        description="API for Hackaton 1",
        version="1.0.0",
        lifespan=lifespan,
        openapi_url=f"{env.API_V1_STR}/openapi.json",
        docs_url=f"{env.API_V1_STR}/docs"
    )

    origins = [
        "*"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(LoggingMiddleware)

    setup_rate_limiting(app)
    
    register_routes(app)

    return app

app = create_app()