# 主API路由

from fastapi import APIRouter

from app.api.endpoints import users, bluetooth, cloud

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(bluetooth.router, prefix="/bluetooth", tags=["bluetooth"])
api_router.include_router(cloud.router, prefix="/cloud", tags=["cloud"])

# 可以在这里添加更多路由端点
# api_router.include_router(items.router, prefix="/items", tags=["items"])