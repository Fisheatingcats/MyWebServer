# Models模块初始化文件
from app.models.user import User
from app.models.device import Device, DeviceType

__all__ = ["User", "Device", "DeviceType"]