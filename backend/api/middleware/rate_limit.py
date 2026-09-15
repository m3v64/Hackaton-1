from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from fastapi import Request
from fastapi.responses import JSONResponse


def rate_limit_key(request: Request) -> str:
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"

    return f"ip:{get_remote_address(request)}"


limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=[
        "120/minute",
    ],
    headers_enabled=True,
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "result": None,
            "error": "Rate limit exceeded",
        },
    )


def setup_rate_limiting(app):
    app.state.limiter = limiter

    app.add_exception_handler(
        RateLimitExceeded,
        rate_limit_exceeded_handler,
    )

    app.add_middleware(SlowAPIMiddleware)