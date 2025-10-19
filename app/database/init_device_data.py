# 初始化设备数据脚本
# 用于创建演示用的设备类型和设备数据

from datetime import datetime
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.models.device import Base, Device, DeviceType


def init_device_types(db: Session):
    """
    初始化设备类型数据
    """
    # 预定义的设备类型
    device_types = [
        {
            "name": "智能网关",
            "description": "负责连接和管理多个传感器或执行器的中央设备",
            "icon": "gateway"
        },
        {
            "name": "温度传感器",
            "description": "用于监测环境温度的传感器",
            "icon": "temperature"
        },
        {
            "name": "湿度传感器",
            "description": "用于监测环境湿度的传感器",
            "icon": "humidity"
        },
        {
            "name": "光照传感器",
            "description": "用于监测环境光照强度的传感器",
            "icon": "light"
        },
        {
            "name": "智能开关",
            "description": "用于远程控制电路通断的智能设备",
            "icon": "switch"
        },
        {
            "name": "智能插座",
            "description": "具有远程控制和监测功能的智能插座",
            "icon": "socket"
        }
    ]

    # 创建设备类型
    for dt_data in device_types:
        # 检查是否已存在
        existing = db.query(DeviceType).filter(DeviceType.name == dt_data["name"]).first()
        if not existing:
            device_type = DeviceType(**dt_data)
            db.add(device_type)
            print(f"创建设备类型: {dt_data['name']}")
    
    db.commit()
    print("设备类型初始化完成")


def init_devices(db: Session):
    """
    初始化设备数据
    """
    # 获取所有设备类型
    device_types = db.query(DeviceType).all()
    device_type_map = {dt.name: dt for dt in device_types}

    # 预定义的设备数据
    devices = [
        {
            "device_id": "GATEWAY-001",
            "name": "主网关",
            "device_type_id": device_type_map["智能网关"].id,
            "status": "active",
            "is_online": True,
            "last_online": datetime.utcnow(),
            "firmware_version": "v1.2.3",
            "private_data": {
                "ip_address": "192.168.1.100",
                "connected_devices": 15,
                "signal_strength": 95
            }
        },
        {
            "device_id": "TEMP-001",
            "name": "客厅温度传感器",
            "device_type_id": device_type_map["温度传感器"].id,
            "status": "active",
            "is_online": True,
            "last_online": datetime.utcnow(),
            "firmware_version": "v1.0.2",
            "private_data": {
                "current_temperature": 23.5,
                "min_temperature": 10.0,
                "max_temperature": 30.0,
                "battery_level": 85
            }
        },
        {
            "device_id": "HUM-001",
            "name": "卧室湿度传感器",
            "device_type_id": device_type_map["湿度传感器"].id,
            "status": "active",
            "is_online": True,
            "last_online": datetime.utcnow(),
            "firmware_version": "v1.0.2",
            "private_data": {
                "current_humidity": 45.2,
                "min_humidity": 30.0,
                "max_humidity": 60.0,
                "battery_level": 90
            }
        },
        {
            "device_id": "LIGHT-001",
            "name": "书房光照传感器",
            "device_type_id": device_type_map["光照传感器"].id,
            "status": "active",
            "is_online": True,
            "last_online": datetime.utcnow(),
            "firmware_version": "v1.0.1",
            "private_data": {
                "current_lux": 350,
                "battery_level": 75
            }
        },
        {
            "device_id": "SWITCH-001",
            "name": "客厅灯开关",
            "device_type_id": device_type_map["智能开关"].id,
            "status": "active",
            "is_online": True,
            "last_online": datetime.utcnow(),
            "firmware_version": "v1.1.0",
            "private_data": {
                "power_state": False,
                "power_consumption": 0
            }
        },
        {
            "device_id": "SOCKET-001",
            "name": "卧室智能插座",
            "device_type_id": device_type_map["智能插座"].id,
            "status": "active",
            "is_online": True,
            "last_online": datetime.utcnow(),
            "firmware_version": "v1.2.0",
            "private_data": {
                "power_state": True,
                "power_consumption": 5.2,
                "current": 0.023,
                "voltage": 220.5
            }
        },
        # 离线设备示例
        {
            "device_id": "TEMP-002",
            "name": "阳台温度传感器",
            "device_type_id": device_type_map["温度传感器"].id,
            "status": "error",
            "is_online": False,
            "last_online": datetime.utcnow().replace(hour=8, minute=0, second=0),  # 模拟早上8点离线
            "firmware_version": "v1.0.2",
            "private_data": {
                "last_temperature": 25.0,
                "battery_level": 10,
                "error_code": "BATTERY_LOW"
            }
        }
    ]

    # 创建设备
    for device_data in devices:
        # 检查是否已存在
        existing = db.query(Device).filter(Device.device_id == device_data["device_id"]).first()
        if not existing:
            device = Device(**device_data)
            db.add(device)
            print(f"创建设备: {device_data['name']} ({device_data['device_id']})")
    
    db.commit()
    print("设备数据初始化完成")


def main():
    """
    主函数，执行数据初始化
    """
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 初始化数据
        print("开始初始化设备数据...")
        init_device_types(db)
        init_devices(db)
        print("设备数据初始化完成！")
    except Exception as e:
        print(f"初始化数据时出错: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()