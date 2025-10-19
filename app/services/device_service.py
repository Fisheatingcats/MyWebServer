# 设备服务层，处理设备相关的业务逻辑

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.device import Device, DeviceType
from app.schemas.device import (
    DeviceTypeCreate, DeviceTypeUpdate,
    DeviceCreate, DeviceUpdate, DeviceStatusUpdate
)

class DeviceTypeService:
    """
    设备类型服务类
    """
    
    @staticmethod
    def create_device_type(db: Session, device_type_data: DeviceTypeCreate) -> DeviceType:
        """
        创建设备类型
        """
        db_device_type = DeviceType(**device_type_data.model_dump())
        db.add(db_device_type)
        db.commit()
        db.refresh(db_device_type)
        return db_device_type
    
    @staticmethod
    def get_device_type(db: Session, device_type_id: int) -> Optional[DeviceType]:
        """
        根据ID获取设备类型
        """
        return db.query(DeviceType).filter(DeviceType.id == device_type_id).first()
    
    @staticmethod
    def get_device_type_by_name(db: Session, name: str) -> Optional[DeviceType]:
        """
        根据名称获取设备类型
        """
        return db.query(DeviceType).filter(DeviceType.name == name).first()
    
    @staticmethod
    def get_device_types(db: Session, skip: int = 0, limit: int = 100) -> List[DeviceType]:
        """
        获取所有设备类型列表
        """
        return db.query(DeviceType).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_device_type(db: Session, device_type_id: int, device_type_data: DeviceTypeUpdate) -> Optional[DeviceType]:
        """
        更新设备类型
        """
        db_device_type = DeviceTypeService.get_device_type(db, device_type_id)
        if not db_device_type:
            return None
        
        update_data = device_type_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_device_type, field, value)
        
        db.commit()
        db.refresh(db_device_type)
        return db_device_type
    
    @staticmethod
    def delete_device_type(db: Session, device_type_id: int) -> bool:
        """
        删除设备类型
        """
        db_device_type = DeviceTypeService.get_device_type(db, device_type_id)
        if not db_device_type:
            return False
        
        # 检查是否有设备使用该类型
        if db_device_type.devices:
            raise ValueError("无法删除该设备类型，因为有设备正在使用它")
        
        db.delete(db_device_type)
        db.commit()
        return True

class DeviceService:
    """
    设备服务类
    """
    
    @staticmethod
    def create_device(db: Session, device_data: DeviceCreate) -> Device:
        """
        创建设备
        """
        # 验证设备类型是否存在
        device_type = DeviceTypeService.get_device_type(db, device_data.device_type_id)
        if not device_type:
            raise ValueError(f"设备类型ID {device_data.device_type_id} 不存在")
        
        db_device = Device(**device_data.model_dump())
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device
    
    @staticmethod
    def get_device(db: Session, device_id: int) -> Optional[Device]:
        """
        根据ID获取设备
        """
        return db.query(Device).filter(Device.id == device_id).first()
    
    @staticmethod
    def get_device_by_device_id(db: Session, device_id: str) -> Optional[Device]:
        """
        根据设备唯一标识符获取设备
        """
        return db.query(Device).filter(Device.device_id == device_id).first()
    
    @staticmethod
    def get_devices(db: Session, skip: int = 0, limit: int = 100) -> List[Device]:
        """
        获取所有设备列表
        """
        return db.query(Device).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_devices_by_type(db: Session, device_type_id: int) -> List[Device]:
        """
        根据设备类型获取设备列表
        """
        return db.query(Device).filter(Device.device_type_id == device_type_id).all()
    
    @staticmethod
    def update_device(db: Session, device_id: int, device_data: DeviceUpdate) -> Optional[Device]:
        """
        更新设备信息
        """
        db_device = DeviceService.get_device(db, device_id)
        if not db_device:
            return None
        
        update_data = device_data.model_dump(exclude_unset=True)
        
        # 如果更新了设备类型，验证其是否存在
        if "device_type_id" in update_data:
            device_type = DeviceTypeService.get_device_type(db, update_data["device_type_id"])
            if not device_type:
                raise ValueError(f"设备类型ID {update_data['device_type_id']} 不存在")
        
        for field, value in update_data.items():
            setattr(db_device, field, value)
        
        db.commit()
        db.refresh(db_device)
        return db_device
    
    @staticmethod
    def update_device_status(db: Session, device_id: int, status_data: DeviceStatusUpdate) -> Optional[Device]:
        """
        更新设备状态
        """
        db_device = DeviceService.get_device(db, device_id)
        if not db_device:
            return None
        
        db_device.status = status_data.status
        db_device.is_online = status_data.is_online
        db_device.last_online = status_data.last_online or datetime.utcnow()
        
        db.commit()
        db.refresh(db_device)
        return db_device
    
    @staticmethod
    def delete_device(db: Session, device_id: int) -> bool:
        """
        删除设备
        """
        db_device = DeviceService.get_device(db, device_id)
        if not db_device:
            return False
        
        db.delete(db_device)
        db.commit()
        return True
    
    @staticmethod
    def update_device_private_data(db: Session, device_id: int, private_data: Dict[str, Any]) -> Optional[Device]:
        """
        更新设备私有数据
        """
        db_device = DeviceService.get_device(db, device_id)
        if not db_device:
            return None
        
        # 如果私有数据已存在，合并新数据
        if db_device.private_data:
            db_device.private_data.update(private_data)
        else:
            db_device.private_data = private_data
        
        db.commit()
        db.refresh(db_device)
        return db_device