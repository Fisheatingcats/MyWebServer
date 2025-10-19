from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy.orm import Session
from pathlib import Path
import os
import shutil
import platform
import json
from urllib.parse import unquote, quote

# 直接从user_service导入authenticate_user函数
from app.services.user_service import authenticate_user
from app.database.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 默认云盘根目录
DEFAULT_CLOUD_ROOT = Path("cloud_storage")
DEFAULT_CLOUD_ROOT.mkdir(exist_ok=True)

# 存储用户挂载路径的字典（实际项目中应该存储在数据库中）
user_mount_paths = {}

def get_disk_partitions():
    """
    获取系统磁盘分区
    """
    system = platform.system()
    partitions = []
    
    if system == "Windows":
        # Windows系统获取盘符
        import string
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                partitions.append(drive)
    else:
        # Unix-like系统（Linux/Mac）
        partitions = ["/"]
        
    return partitions

@router.get("/", response_class=HTMLResponse)
async def cloud_dashboard(request: Request, cloud_user: str = Cookie(None)):
    """
    云盘页面
    """
    # 如果用户已经登录，则直接跳转到文件列表页面
    if cloud_user:
        return RedirectResponse(url="/api/v1/cloud/files")
    
    return templates.TemplateResponse("cloud.html", {"request": request})

@router.post("/login")
async def cloud_login(
    request: Request,
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    """
    云盘登录验证
    """
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("cloud.html", {
            "request": request, 
            "error": "用户名或密码错误"
        })
    
    # 设置登录cookie
    response = RedirectResponse(url="/api/v1/cloud/files", status_code=303)
    response.set_cookie(key="cloud_user", value=username)
    return response

@router.get("/files", response_class=HTMLResponse)
async def list_files(request: Request, path: str = "", cloud_user: str = Cookie(None)):
    """
    列出云盘文件
    """
    # 简单的身份验证检查
    if not cloud_user:
        return RedirectResponse(url="/api/v1/cloud/")
    
    # 获取用户的挂载路径
    mount_path = user_mount_paths.get(cloud_user, DEFAULT_CLOUD_ROOT)
    mount_path = Path(mount_path)
    
    # 解码路径参数
    decoded_path = unquote(path) if path else ""
    
    # 构建完整路径
    full_path = mount_path / decoded_path if decoded_path else mount_path
    
    # 检查路径是否在允许范围内（对于自定义路径，我们信任用户的选择）
    try:
        full_path = full_path.resolve()
        if not cloud_user in user_mount_paths:  # 只对默认路径进行限制
            if not str(full_path).startswith(str(mount_path.resolve())):
                raise HTTPException(status_code=403, detail="访问被拒绝")
    except Exception:
        raise HTTPException(status_code=403, detail="访问被拒绝")
    
    # 检查路径是否存在
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="路径不存在")
    
    try:
        # 获取当前目录下的所有文件和文件夹
        items = []
        # 系统保留文件/文件夹列表，需要过滤
        system_reserved = ['$RECYCLE.BIN', 'System Volume Information', 'pagefile.sys', 'hiberfil.sys', 'swapfile.sys']
        
        for item in full_path.iterdir():
            # 过滤系统保留文件
            if item.name in system_reserved:
                continue
                
            try:
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size": stat.st_size if item.is_file() else None,
                    "modified": stat.st_mtime,
                    "path": str(item.relative_to(mount_path)).replace("\\", "/")
                })
            except (PermissionError, OSError):
                # 跳过无权限访问的文件
                continue
        
        # 按名称排序，文件夹在前
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        
        # 构建面包屑导航路径
        breadcrumbs = []
        if decoded_path:
            parts = decoded_path.split("/")
            for i in range(len(parts)):
                breadcrumbs.append({
                    "name": parts[i],
                    "path": "/".join(parts[:i+1])
                })
        
        # 获取父目录路径
        parent_path = str(full_path.parent.relative_to(mount_path)).replace("\\", "/") if full_path != mount_path else ""
        
        # 获取系统磁盘分区
        disk_partitions = get_disk_partitions()
        
    except Exception as e:
        items = []
        breadcrumbs = []
        parent_path = ""
        disk_partitions = get_disk_partitions()
    
    return templates.TemplateResponse("cloud_files.html", {
        "request": request, 
        "files": items,
        "username": cloud_user,
        "current_path": decoded_path,
        "breadcrumbs": breadcrumbs,
        "parent_path": parent_path if parent_path != "." else "",
        "mount_path": str(mount_path),
        "disk_partitions": disk_partitions
    })

@router.post("/set_mount_path")
async def set_mount_path(
    request: Request,
    mount_path: str = Form(...),
    cloud_user: str = Cookie(None)
):
    """
    设置用户挂载路径
    """
    if not cloud_user:
        return RedirectResponse(url="/api/v1/cloud/")
    
    # 检查路径是否存在
    path_obj = Path(mount_path)
    if not path_obj.exists():
        # 尝试创建路径
        try:
            path_obj.mkdir(parents=True, exist_ok=True)
        except Exception:
            return RedirectResponse(url="/api/v1/cloud/files?error=路径不存在且无法创建", status_code=303)
    
    # 保存用户的挂载路径
    user_mount_paths[cloud_user] = mount_path
    
    return RedirectResponse(url="/api/v1/cloud/files", status_code=303)

@router.post("/validate_path")
async def validate_path(path: str = Form(...)):
    """
    验证路径是否存在
    """
    path_obj = Path(path)
    exists = path_obj.exists()
    return JSONResponse(content={"exists": exists})

@router.get("/logout")
async def cloud_logout():
    """
    云盘登出
    """
    response = RedirectResponse(url="/api/v1/cloud/")
    response.delete_cookie("cloud_user")
    return response

@router.post("/upload")
async def upload_file(
    request: Request, 
    files: list[UploadFile] = File(...), 
    path: str = Form(""), 
    cloud_user: str = Cookie(None)
):
    """
    上传文件（支持多文件）
    """
    if not cloud_user:
        return RedirectResponse(url="/api/v1/cloud/")
    
    # 获取用户的挂载路径
    mount_path = user_mount_paths.get(cloud_user, DEFAULT_CLOUD_ROOT)
    mount_path = Path(mount_path)
    
    # 解码路径参数
    decoded_path = unquote(path) if path else ""
    
    # 构建完整路径
    full_path = mount_path / decoded_path if decoded_path else mount_path
    
    # 检查路径是否在允许范围内
    try:
        full_path = full_path.resolve()
        # 对所有路径都进行限制，防止访问系统关键文件
        if not str(full_path).startswith(str(mount_path.resolve())):
            raise HTTPException(status_code=403, detail="访问被拒绝")
    except Exception:
        raise HTTPException(status_code=403, detail="访问被拒绝")
    
    try:
        # 确保目录存在
        full_path.mkdir(parents=True, exist_ok=True)
        
        # 处理所有上传的文件
        for file in files:
            try:
                # 保存上传的文件
                file_location = full_path / file.filename
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                # 记录单个文件上传失败，但继续处理其他文件
                print(f"文件 {file.filename} 上传失败: {str(e)}")
            finally:
                await file.close()  # 使用await关闭文件
    except (PermissionError, OSError) as e:
        # 处理权限错误和其他系统错误
        return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(decoded_path)}&error=文件上传失败：权限不足或系统限制", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(decoded_path)}&error=文件上传失败", status_code=303)
    
    # 重新加载文件列表
    return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(decoded_path)}", status_code=303)

@router.get("/download/{file_path:path}")
async def download_file(file_path: str, cloud_user: str = Cookie(None)):
    """
    下载文件
    """
    if not cloud_user:
        raise HTTPException(status_code=401, detail="未授权访问")
    
    # 获取用户的挂载路径
    mount_path = user_mount_paths.get(cloud_user, DEFAULT_CLOUD_ROOT)
    mount_path = Path(mount_path)
    
    # 解码路径参数
    decoded_path = unquote(file_path)
    
    # 构建完整路径
    full_path = mount_path / decoded_path
    
    # 检查路径是否在允许范围内
    try:
        full_path = full_path.resolve()
        if not cloud_user in user_mount_paths:  # 只对默认路径进行限制
            if not str(full_path).startswith(str(mount_path.resolve())):
                raise HTTPException(status_code=403, detail="访问被拒绝")
    except Exception:
        raise HTTPException(status_code=403, detail="访问被拒绝")
    
    if not full_path.exists() or full_path.is_dir():
        raise HTTPException(status_code=404, detail="文件未找到")
    
    # 检查是否为系统保留文件
    system_reserved = ['pagefile.sys', 'hiberfil.sys', 'swapfile.sys']
    if full_path.name in system_reserved:
        raise HTTPException(status_code=403, detail="无法下载系统保留文件")
    
    filename = full_path.name
    try:
        return FileResponse(path=full_path, filename=filename)
    except PermissionError:
        raise HTTPException(status_code=403, detail="没有权限访问此文件")
    except Exception as e:
        raise HTTPException(status_code=500, detail="文件下载失败")

@router.post("/delete/{file_path:path}")
async def delete_file(request: Request, file_path: str, cloud_user: str = Cookie(None)):
    """
    删除文件或文件夹
    """
    if not cloud_user:
        return RedirectResponse(url="/api/v1/cloud/")
    
    # 获取用户的挂载路径
    mount_path = user_mount_paths.get(cloud_user, DEFAULT_CLOUD_ROOT)
    mount_path = Path(mount_path)
    
    # 解码路径参数
    decoded_path = unquote(file_path)
    
    # 构建完整路径
    full_path = mount_path / decoded_path
    
    # 检查路径是否在允许范围内
    try:
        full_path = full_path.resolve()
        if not cloud_user in user_mount_paths:  # 只对默认路径进行限制
            if not str(full_path).startswith(str(mount_path.resolve())):
                raise HTTPException(status_code=403, detail="访问被拒绝")
    except Exception:
        raise HTTPException(status_code=403, detail="访问被拒绝")
    
    # 获取父目录用于重定向
    parent_dir = str(full_path.parent.relative_to(mount_path)).replace("\\", "/")
    redirect_path = parent_dir if parent_dir != "." else ""
    
    try:
        if full_path.exists():
            # 检查是否为系统保留文件/文件夹
            system_reserved = ['$RECYCLE.BIN', 'System Volume Information', 'pagefile.sys', 'hiberfil.sys', 'swapfile.sys']
            if full_path.name in system_reserved:
                return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(redirect_path)}&error=无法删除系统保留文件或文件夹", status_code=303)
                
            if full_path.is_file():
                full_path.unlink()
            else:
                shutil.rmtree(full_path)
    except PermissionError:
        return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(redirect_path)}&error=删除失败：权限不足", status_code=303)
    except OSError as e:
        return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(redirect_path)}&error=删除失败：系统限制", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(redirect_path)}&error=删除失败", status_code=303)
    
    # 重新加载文件列表
    return RedirectResponse(
        url=f"/api/v1/cloud/files?path={quote(redirect_path)}" if redirect_path else "/api/v1/cloud/files", 
        status_code=303
    )

@router.post("/create_folder")
async def create_folder(
    request: Request,
    folder_name: str = Form(...),
    path: str = Form(""), 
    cloud_user: str = Cookie(None)
):
    """
    创建文件夹
    """
    if not cloud_user:
        return RedirectResponse(url="/api/v1/cloud/")
    
    # 获取用户的挂载路径
    mount_path = user_mount_paths.get(cloud_user, DEFAULT_CLOUD_ROOT)
    mount_path = Path(mount_path)
    
    # 解码路径参数
    decoded_path = unquote(path) if path else ""
    
    # 构建完整路径
    full_path = mount_path / decoded_path if decoded_path else mount_path
    
    # 检查路径是否在允许范围内
    try:
        full_path = full_path.resolve()
        if not cloud_user in user_mount_paths:  # 只对默认路径进行限制
            if not str(full_path).startswith(str(mount_path.resolve())):
                raise HTTPException(status_code=403, detail="访问被拒绝")
    except Exception:
        raise HTTPException(status_code=403, detail="访问被拒绝")
    
    try:
        # 创建新文件夹
        new_folder_path = full_path / folder_name
        new_folder_path.mkdir(exist_ok=True)
    except PermissionError:
        return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(decoded_path)}&error=创建文件夹失败：权限不足", status_code=303)
    except OSError as e:
        return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(decoded_path)}&error=创建文件夹失败：系统限制", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(decoded_path)}&error=创建文件夹失败", status_code=303)
    
    # 重新加载文件列表
    return RedirectResponse(url=f"/api/v1/cloud/files?path={quote(decoded_path)}", status_code=303)