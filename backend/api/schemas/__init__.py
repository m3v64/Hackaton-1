from src.api.schemas.common import ApiResponse, PaginatedResult
from src.api.schemas.auth import LoginRequest, RegisterRequest, GoogleAuthRequest, TokenResponse
from src.api.schemas.user import UserPublic, UserPrivate, UserUpdateRequest
from api.schemas.post import PostOut, PostCreateRequest, PostUpdateRequest, TagOut
from api.schemas.comment import CommentOut, CommentCreateRequest, CommentUpdateRequest
from api.schemas.media import MediaOut
from api.schemas.notification import NotificationOut
from api.schemas.minecraft import McVersionOut, NewsArticleOut
from api.schemas.mod import ModOut, ModVersionOut
from api.schemas.server import MinecraftServerOut
from src.api.schemas.settings import UserSettingsOut, UserSettingsUpdateRequest

__all__ = [
    "ApiResponse", 
    "PaginatedResult",
    "LoginRequest", 
    "RegisterRequest", 
    "GoogleAuthRequest", 
    "TokenResponse",
    "UserPublic", 
    "UserPrivate",
    "UserUpdateRequest",
    "PostOut", 
    "PostCreateRequest", 
    "PostUpdateRequest", 
    "TagOut",
    "CommentOut", 
    "CommentCreateRequest", 
    "CommentUpdateRequest",
    "MediaOut",
    "NotificationOut",
    "McVersionOut", 
    "NewsArticleOut",
    "ModOut", 
    "ModVersionOut",
    "MinecraftServerOut",
    "UserSettingsOut",
    "UserSettingsUpdateRequest"
]
