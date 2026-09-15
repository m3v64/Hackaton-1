from __future__ import annotations
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    result: T | None = None
    error: str | None = None


class PaginatedResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int
