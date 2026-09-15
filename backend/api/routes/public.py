from fastapi import APIRouter, Request, Response
from src.api.middleware.rate_limit import limiter
from src.api.schemas.common import ApiResponse


router = APIRouter()

@router.get("/health", response_model=ApiResponse[dict], summary="Health check")
@limiter.limit("30/second")
async def health(request: Request, response: Response) -> ApiResponse[dict]:
    return ApiResponse(result={"status": "ok"})
