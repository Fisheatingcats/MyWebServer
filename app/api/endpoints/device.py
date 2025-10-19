# 设备相关的API端点

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.device import (
    DeviceTypeCreate, DeviceTypeUpdate, DeviceTypeResponse,
    DeviceCreate, DeviceUpdate, DeviceResponse, DeviceStatusUpdate
)
from app.services.device_service import DeviceService, DeviceTypeService

router = APIRouter(prefix="/api/v1", tags=["devices"])

# 设备类型相关端点
@router.post("/device-type", response_model=DeviceTypeResponse, status_code=status.HTTP_201_CREATED)
def create_device_type(
    device_type_data: DeviceTypeCreate,
    db: Session = Depends(get_db)
):
    """
    创建设备类型
    """
    # 检查设备类型名称是否已存在
    existing_type = DeviceTypeService.get_device_type_by_name(db, device_type_data.name)
    if existing_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"设备类型 '{device_type_data.name}' 已存在"
        )
    
    try:
        device_type = DeviceTypeService.create_device_type(db, device_type_data)
        return device_type.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建设备类型失败: {str(e)}"
        )

@router.get("/device-type", response_model=List[DeviceTypeResponse])
def get_device_types(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取设备类型列表
    """
    device_types = DeviceTypeService.get_device_types(db, skip=skip, limit=limit)
    return [device_type.to_dict() for device_type in device_types]

@router.get("/device-type/{device_type_id}", response_model=DeviceTypeResponse)
def get_device_type(
    device_type_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取设备类型详情
    """
    device_type = DeviceTypeService.get_device_type(db, device_type_id)
    if not device_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备类型ID {device_type_id} 不存在"
        )
    return device_type.to_dict()

@router.put("/device-type/{device_type_id}", response_model=DeviceTypeResponse)
def update_device_type(
    device_type_id: int,
    device_type_data: DeviceTypeUpdate,
    db: Session = Depends(get_db)
):
    """
    更新设备类型
    """
    try:
        device_type = DeviceTypeService.update_device_type(db, device_type_id, device_type_data)
        if not device_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备类型ID {device_type_id} 不存在"
            )
        return device_type.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新设备类型失败: {str(e)}"
        )

@router.delete("/device-type/{device_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device_type(
    device_type_id: int,
    db: Session = Depends(get_db)
):
    """
    删除设备类型
    """
    try:
        success = DeviceTypeService.delete_device_type(db, device_type_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备类型ID {device_type_id} 不存在"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除设备类型失败: {str(e)}"
        )

# 设备相关端点
@router.post("/device", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db)
):
    """
    创建设备
    """
    # 检查设备ID是否已存在
    existing_device = DeviceService.get_device_by_device_id(db, device_data.device_id)
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"设备ID '{device_data.device_id}' 已存在"
        )
    
    try:
        device = DeviceService.create_device(db, device_data)
        return device.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建设备失败: {str(e)}"
        )

@router.get("/device", response_model=List[DeviceResponse])
def get_devices(
    skip: int = 0,
    limit: int = 100,
    device_type_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取设备列表，可选择按设备类型筛选
    """
    if device_type_id:
        devices = DeviceService.get_devices_by_type(db, device_type_id)
    else:
        devices = DeviceService.get_devices(db, skip=skip, limit=limit)
    return [device.to_dict() for device in devices]

@router.get("/device/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取设备详情
    """
    device = DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备ID {device_id} 不存在"
        )
    return device.to_dict()

@router.get("/device/by-device-id/{device_unique_id}", response_model=DeviceResponse)
def get_device_by_device_id(
    device_unique_id: str,
    db: Session = Depends(get_db)
):
    """
    根据设备唯一标识符获取设备详情
    """
    device = DeviceService.get_device_by_device_id(db, device_unique_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备唯一标识符 '{device_unique_id}' 不存在"
        )
    return device.to_dict()

@router.put("/device/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db)
):
    """
    更新设备信息
    """
    try:
        device = DeviceService.update_device(db, device_id, device_data)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备ID {device_id} 不存在"
            )
        return device.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新设备失败: {str(e)}"
        )

@router.put("/device/{device_id}/status", response_model=DeviceResponse)
def update_device_status(
    device_id: int,
    status_data: DeviceStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    更新设备状态
    """
    device = DeviceService.update_device_status(db, device_id, status_data)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备ID {device_id} 不存在"
        )
    return device.to_dict()

@router.delete("/device/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    删除设备
    """
    try:
        success = DeviceService.delete_device(db, device_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备ID {device_id} 不存在"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除设备失败: {str(e)}"
        )