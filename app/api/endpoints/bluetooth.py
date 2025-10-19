import asyncio
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from bleak import BleakScanner, BleakClient
import platform
import subprocess
import re
from urllib.parse import unquote

router = APIRouter(prefix="/bluetooth", tags=["bluetooth"])

# 存储当前连接的设备
connected_devices: Dict[str, BleakClient] = {}

# 解析传统蓝牙扫描结果（跨平台适配）
def parse_bt_scan_output(output: str) -> List[Dict]:
    devices = []
    lines = output.strip().split('\n')
    current_device = None
    
    for line in lines:
        line = line.strip()
        # 匹配MAC地址行（Linux格式）
        mac_match = re.match(r'([0-9A-Fa-f:]{17})\s+(.+)', line)
        # 匹配RSSI行（Linux格式）
        rssi_match = re.match(r'.+RSSI\s+(-?\d+)', line)
        
        if mac_match:
            if current_device:
                devices.append(current_device)
            mac = mac_match.group(1)
            name = mac_match.group(2).strip() or "Unknown"
            current_device = {
                "id": mac,  # 使用MAC作为唯一ID
                "name": name,
                "mac": mac,
                "rssi": None,
                "type": "BT"
            }
        elif rssi_match and current_device:
            current_device["rssi"] = int(rssi_match.group(1))
    
    if current_device:
        devices.append(current_device)
    return devices

# 传统蓝牙扫描（依赖系统工具）
async def scan_bt_devices_real() -> List[Dict]:
    try:
        system = platform.system()
        if system == "Linux":
            # Linux使用hcitool扫描
            result = subprocess.run(
                ["hcitool", "scan", "--flush"],
                capture_output=True,
                text=True,
                check=True
            )
            # 补充获取RSSI（需要root权限）
            rssi_result = subprocess.run(
                ["hcitool", "rssi", "hci0"],
                capture_output=True,
                text=True
            )
            full_output = result.stdout + rssi_result.stdout
            return parse_bt_scan_output(full_output)
            
        elif system == "Darwin":  # macOS
            result = subprocess.run(
                ["blueutil", "--inquiry", "5"],
                capture_output=True,
                text=True,
                check=True
            )
            devices = []
            for line in result.stdout.split('\n'):
                if line.strip() and "Address:" in line:
                    mac = line.split("Address:")[1].split()[0].strip()
                    name = line.split("Name:")[1].strip() if "Name:" in line else "Unknown"
                    devices.append({
                        "id": mac,
                        "name": name,
                        "mac": mac,
                        "rssi": None,
                        "type": "BT"
                    })
            return devices
            
        elif system == "Windows":
            result = subprocess.run(
                ["powershell", "Get-BluetoothDevice -Discoverable"],
                capture_output=True,
                text=True
            )
            devices = []
            for line in result.stdout.split('\n'):
                if "Address" in line and "Name" in line:
                    mac = line.split("Address:")[1].split()[0].strip()
                    name = line.split("Name:")[1].strip()
                    devices.append({
                        "id": mac,
                        "name": name,
                        "mac": mac,
                        "rssi": None,
                        "type": "BT"
                    })
            return devices
            
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"传统蓝牙扫描不支持 {system} 系统"
            )
            
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"蓝牙扫描失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"扫描出错: {str(e)}"
        )

# BLE扫描（使用bleak）
async def scan_ble_devices_real() -> List[Dict]:
    try:
        devices = await BleakScanner.discover(timeout=5)
        result = []
        for device in devices:
            # 获取设备信息，处理不同版本的bleak库差异
            device_info = {
                "id": device.address,
                "name": device.name or device.address,
                "mac": device.address,
                "type": "BLE"
            }
            
            # 尝试获取RSSI值（不同版本的bleak可能有不同的属性）
            if hasattr(device, 'rssi'):
                device_info["rssi"] = device.rssi
            elif hasattr(device, 'details') and hasattr(device.details, 'RawSignalStrengthInDBm'):
                device_info["rssi"] = device.details.RawSignalStrengthInDBm
            else:
                device_info["rssi"] = None
                
            result.append(device_info)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BLE扫描失败: {str(e)}"
        )

@router.get("/scan/ble", response_model=List[Dict])
async def scan_ble_devices():
    """扫描真实BLE设备"""
    return await scan_ble_devices_real()

@router.get("/scan/bt", response_model=List[Dict])
async def scan_bt_devices():
    """扫描真实传统蓝牙设备"""
    return await scan_bt_devices_real()

@router.get("/scan/all", response_model=List[Dict])
async def scan_all_devices():
    """扫描所有真实蓝牙设备（BLE+传统蓝牙）"""
    ble_devices = await scan_ble_devices_real()
    bt_devices = await scan_bt_devices_real()
    # 去重（避免同一设备被重复扫描）
    all_devices = ble_devices + bt_devices
    seen_macs = set()
    unique_devices = []
    for device in all_devices:
        if device["mac"] not in seen_macs:
            seen_macs.add(device["mac"])
            unique_devices.append(device)
    return unique_devices

@router.post("/connect/{device_id}")
async def connect_device(device_id: str):
    """连接指定蓝牙设备（仅支持BLE）"""
    # 解码URL编码的设备ID
    decoded_device_id = unquote(device_id)
    
    # 先确认设备存在
    all_devices = await scan_all_devices()
    device = next((d for d in all_devices if d["id"] == decoded_device_id), None)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备 {decoded_device_id} 未找到"
        )
    
    if device["type"] != "BLE":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="目前仅支持BLE设备连接"
        )
    
    # 检查是否已连接
    if decoded_device_id in connected_devices:
        return {
            "message": f"已连接到 {device['name']}",
            "device": device
        }
    
    try:
        client = BleakClient(decoded_device_id)
        await client.connect()
        connected_devices[decoded_device_id] = client
        return {
            "message": f"成功连接到 {device['name']}",
            "device": device
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"连接失败: {str(e)}"
        )

@router.post("/disconnect/{device_id}")
async def disconnect_device(device_id: str):
    """断开指定设备连接（仅支持BLE）"""
    # 解码URL编码的设备ID
    decoded_device_id = unquote(device_id)
    
    if decoded_device_id not in connected_devices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备 {decoded_device_id} 未连接"
        )
    
    try:
        client = connected_devices[decoded_device_id]
        if client.is_connected:
            await client.disconnect()
        del connected_devices[decoded_device_id]
        
        # 获取设备名称
        all_devices = await scan_all_devices()
        device = next((d for d in all_devices if d["id"] == decoded_device_id), None)
        device_name = device["name"] if device else "未知设备"
        
        return {
            "message": f"成功断开与 {device_name} 的连接"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"断开连接失败: {str(e)}"
        )

@router.post("/send_data/{device_id}")
async def send_data_to_device(device_id: str, data: Dict):
    """向指定设备发送数据（仅支持BLE）"""
    # 解码URL编码的设备ID
    decoded_device_id = unquote(device_id)
    
    if decoded_device_id not in connected_devices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备 {decoded_device_id} 未连接"
        )
    
    try:
        client = connected_devices[decoded_device_id]
        if not client.is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="设备连接已断开"
            )
        
        # 注意：实际发送需要知道目标特征值UUID
        # 这里仅作为示例，需要根据实际设备的GATT特征值修改
        # 例如：await client.write_gatt_char("0000ffe1-0000-1000-8000-00805f9b34fb", data_bytes)
        
        # 模拟数据发送（实际应用中需要替换为真实的特征值写入）
        data_bytes = str(data).encode('utf-8')
        return {
            "message": f"成功向设备发送数据",
            "sent_data": data,
            "bytes_sent": len(data_bytes)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送数据失败: {str(e)}"
        )