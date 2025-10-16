# 主API路由

from fastapi import APIRouter
from app.api.endpoints import users

api_router = APIRouter()
api_router.include_router(users.router)

# 可以在这里添加更多路由端点
# api_router.include_router(items.router, prefix="/items", tags=["items"])