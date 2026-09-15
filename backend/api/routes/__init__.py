from fastapi import FastAPI

from api.core.env import env
from api.routes import courses, memberships, users


_PREFIX = env.API_V1_STR

def register_routes(app: FastAPI) -> None:
    app.include_router(users.router, prefix=_PREFIX, tags=["users"])
    app.include_router(courses.router, prefix=_PREFIX, tags=["courses"])
    app.include_router(memberships.router, prefix=_PREFIX, tags=["memberships"])
