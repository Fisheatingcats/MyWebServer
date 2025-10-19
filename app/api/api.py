# 主API路由

from fastapi import APIRouter

# 导入存在的模块
from app.api.endpoints import device, cloud

api_router = APIRouter()
# 注册设备管理路由
api_router.include_router(device.router, prefix="/device", tags=["device"])
# 注册云盘服务路由
api_router.include_router(cloud.router, prefix="/cloud", tags=["cloud"])

# 可以在这里添加更多路由端点
# api_router.include_router(items.router, prefix="/items", tags=["items"])