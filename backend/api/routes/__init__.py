from fastapi import FastAPI

from src.api.routes import auth
from src.api.core.env import env
from src.api.routes import media, minecraft, mod, mod, posts, public, server, settings, users


_PREFIX = env.API_V1_STR

def register_routes(app: FastAPI) -> None:
    app.include_router(auth.router, prefix=_PREFIX, tags=["auth"])
    app.include_router(users.router, prefix=_PREFIX, tags=["users"])
    app.include_router(posts.router, prefix=_PREFIX, tags=["posts"])
    app.include_router(media.router, prefix=_PREFIX, tags=["media"])
    app.include_router(minecraft.router, prefix=_PREFIX, tags=["minecraft"])
    app.include_router(mod.router, prefix=_PREFIX, tags=["mods"])
    app.include_router(server.router, prefix=_PREFIX, tags=["server"])
    app.include_router(settings.router, prefix=_PREFIX, tags=["settings"])
    app.include_router(public.router, prefix=_PREFIX, tags=["system"])
