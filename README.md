<!--
 * @Author: NICOLA 2841208085@qq.com
 * @Date: 2025-10-16 23:58:24
 * @LastEditors: NICOLA 2841208085@qq.com
 * @LastEditTime: 2025-10-17 00:27:27
 * @FilePath: \FastAPI\README.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
# FastAPI 现代化后端工程

这是一个基于FastAPI构建的现代化后端工程示例，包含用户认证系统和HTML登录页面。

## 功能特性

- 基于FastAPI的高性能后端服务
- 用户认证系统（用户名/密码登录）
- 现代化的HTML界面设计
- 响应式布局，支持各种设备
- 仪表盘页面，展示系统信息

## 技术栈

- **后端**: FastAPI, Python 3.8+
- **前端**: HTML5, CSS3
- **模板引擎**: Jinja2
- **密码加密**: Passlib (bcrypt)
- **ASGI服务器**: Uvicorn

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行项目

```bash
cd app
python main.py
```

或者使用uvicorn直接运行：

```bash
uvicorn app.main:app --reload
```

项目将在 http://127.0.0.1:8000 启动



## 测试账户

- 用户名: admin
- 密码: admin123

## 项目结构

```
FastAPI/
├── app/
│   ├── main.py          # FastAPI主应用
│   ├── templates/       # HTML模板
│   │   ├── index.html   # 首页
│   │   ├── login.html   # 登录页面
│   │   └── dashboard.html # 仪表盘页面
│   └── static/          # 静态文件
│       └── css/
│           └── style.css # 样式表
├── requirements.txt     # 项目依赖
└── README.md            # 项目文档
```

## 扩展建议

1. 添加数据库集成（SQLite, PostgreSQL等）
2. 实现更完善的用户权限系统
3. 添加更多API端点
4. 集成JWT令牌认证
5. 添加API文档页面