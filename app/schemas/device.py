# 设备相关的数据验证模式

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DeviceTypeBase(BaseModel):
    """
    设备类型基础模型
    """
    name: str = Field(..., description="设备类型名称")
    description: Optional[str] = Field(None, description="设备类型描述")
    icon: Optional[str] = Field(None, description="设备类型图标")

class DeviceTypeCreate(DeviceTypeBase):
    """
    创建设备类型模型
    """
    pass

class DeviceTypeUpdate(BaseModel):
    """
    更新设备类型模型
    """
    name: Optional[str] = Field(None, description="设备类型名称")
    description: Optional[str] = Field(None, description="设备类型描述")
    icon: Optional[str] = Field(None, description="设备类型图标")

class DeviceTypeResponse(DeviceTypeBase):
    """
    设备类型响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DeviceBase(BaseModel):
    """
    设备基础模型
    """
    device_id: str = Field(..., description="设备唯一标识符")
    name: str = Field(..., description="设备名称")
    device_type_id: int = Field(..., description="设备类型ID")
    private_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="设备私有数据")
    firmware_version: Optional[str] = Field(None, description="固件版本")

class DeviceCreate(DeviceBase):
    """
    创建设备模型
    """
    pass

class DeviceUpdate(BaseModel):
    """
    更新设备模型
    """
    name: Optional[str] = Field(None, description="设备名称")
    device_type_id: Optional[int] = Field(None, description="设备类型ID")
    status: Optional[str] = Field(None, description="设备状态")
    private_data: Optional[Dict[str, Any]] = Field(None, description="设备私有数据")
    firmware_version: Optional[str] = Field(None, description="固件版本")

class DeviceResponse(DeviceBase):
    """
    设备响应模型
    """
    id: int
    status: str
    is_online: bool
    last_online: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    device_type: Optional[DeviceTypeResponse] = None
    
    class Config:
        from_attributes = True

class DeviceStatusUpdate(BaseModel):
    """
    更新设备状态模型
    """
    status: str = Field(..., description="设备状态")
    is_online: bool = Field(..., description="设备是否在线")
    last_online: Optional[datetime] = Field(None, description="最后在线时间")