# 设备数据模型

from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class DeviceType(Base):
    """
    设备类型数据模型
    用于对设备进行分类管理
    """
    __tablename__ = "device_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, comment="设备类型名称")
    description = Column(String, nullable=True, comment="设备类型描述")
    icon = Column(String, nullable=True, comment="设备类型图标")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系定义：一个设备类型可以有多个设备
    devices = relationship("Device", back_populates="device_type")
    
    def to_dict(self):
        """
        将设备类型对象转换为字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Device(Base):
    """
    设备数据模型
    存储具体设备信息
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, nullable=False, index=True, comment="设备唯一标识符")
    name = Column(String, nullable=False, comment="设备名称")
    device_type_id = Column(Integer, ForeignKey("device_types.id"), nullable=False, comment="设备类型ID")
    status = Column(String, default="inactive", nullable=False, comment="设备状态：active/inactive/maintenance/error")
    private_data = Column(JSON, default={}, nullable=True, comment="设备私有数据，以JSON格式存储")
    firmware_version = Column(String, nullable=True, comment="固件版本")
    last_online = Column(DateTime, nullable=True, comment="最后在线时间")
    is_online = Column(Boolean, default=False, nullable=False, comment="设备是否在线")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系定义：一个设备属于一个设备类型
    device_type = relationship("DeviceType", back_populates="devices")
    
    def to_dict(self):
        """
        将设备对象转换为字典
        """
        return {
            "id": self.id,
            "device_id": self.device_id,
            "name": self.name,
            "device_type_id": self.device_type_id,
            "device_type": self.device_type.to_dict() if self.device_type else None,
            "status": self.status,
            "private_data": self.private_data,
            "firmware_version": self.firmware_version,
            "last_online": self.last_online.isoformat() if self.last_online else None,
            "is_online": self.is_online,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }