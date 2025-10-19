from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.api import api_router
from app.database.database import engine, Base, get_db
from app.models.user import User as UserModel
from app.models.device import Device, DeviceType  # 导入设备相关模型
from app.services.user_service import authenticate_user

# 创建数据库表（会自动包含所有继承自Base的模型）
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(title="ikun的后端工程", description="现代化的FastAPI后端工程示例")

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# 初始化默认用户
def init_default_user(db: Session):
    """
    初始化默认用户
    """
    user = db.query(UserModel).filter(UserModel.username == "admin").first()
    if not user:
        from app.schemas.user import UserCreate
        from app.services.user_service import get_password_hash
        
        user_create = UserCreate(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            password="admin123",
            disabled=False
        )
        
        db_user = UserModel(
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=get_password_hash(user_create.password),
            disabled=user_create.disabled
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

# 导入设备数据初始化函数
from app.database.init_device_data import init_device_types, init_devices

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """
    应用启动时初始化数据
    """
    db = next(get_db())
    try:
        # 确保默认用户存在（如果需要）
        # 这里暂时注释掉，因为我们没有看到init_default_user的导入
        # init_default_user(db)
        # 初始化设备类型和设备数据
        init_device_types(db)
        init_devices(db)
    finally:
        db.close()

# 主页路由
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # return {"主播": "我洗澡去了"}
    return templates.TemplateResponse("index.html", {"request": request})

# 登录页面路由
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

# 登录处理路由
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "用户名或密码错误"})
    # 在实际应用中，这里应该设置会话或JWT token
    return RedirectResponse(url="/dashboard", status_code=303)

# 仪表板路由（需要登录后访问）
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # 在实际应用中，这里应该有更完善的认证机制
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": "admin"})

# 蓝牙调试页面路由
@app.get("/bluetooth", response_class=HTMLResponse)
async def bluetooth_debug(request: Request):
    # 在实际应用中，这里应该有更完善的认证机制
    return templates.TemplateResponse("bluetooth.html", {"request": request, "username": "admin"})

# 设备控制台页面路由
@app.get("/device_console", response_class=HTMLResponse)
async def device_console(request: Request):
    # 在实际应用中，这里应该有更完善的认证机制
    return templates.TemplateResponse("device_console.html", {"request": request, "username": "admin"})

# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)