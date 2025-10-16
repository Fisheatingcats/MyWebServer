from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from typing import Optional

# 创建FastAPI应用
app = FastAPI(title="FastAPI 后端工程", description="现代化的FastAPI后端工程示例")

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# 密码加密上下文
# 使用sha256_crypt代替bcrypt以避免72字节的密码长度限制
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# 模拟数据库存储用户信息
# 使用预计算的哈希值，避免在导入时计算
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$LxR2P3k4Q5w6E7r8T9y0u1i2o3p4a5s6d7f8g9h0j1k2l3m4n5b",  # 模拟哈希值
        "disabled": False,
    }
}

# 由于使用了模拟哈希值，我们需要在运行时重新设置真正的哈希值
def init_users_db():
    # 确保密码不超过72字节
    password = "admin123"[:72]
    fake_users_db["admin"]["hashed_password"] = pwd_context.hash(password)

# 初始化用户数据库
init_users_db()

# 简单的用户模型
class User:
    def __init__(self, username: str, email: Optional[str] = None, full_name: Optional[str] = None, disabled: Optional[bool] = None):
        self.username = username
        self.email = email
        self.full_name = full_name
        self.disabled = disabled

    def dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "disabled": self.disabled
        }

# 获取当前用户
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return User(**user_dict)

# 验证用户凭证
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    # 确保密码不超过72字节
    password = password[:72]
    if not pwd_context.verify(password, fake_db[username]["hashed_password"]):
        return False
    return user

# 主页路由
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 登录页面路由
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

# 登录处理路由
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(fake_users_db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "用户名或密码错误"})
    return RedirectResponse(url="/dashboard", status_code=303)

# 仪表板路由（需要登录后访问）
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # 在实际应用中，这里应该有更完善的认证机制
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": "admin"})

# 运行应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)