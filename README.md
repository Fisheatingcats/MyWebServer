<!--
 * @Author: NICOLA 2841208085@qq.com
 * @Date: 2025-10-16 23:58:24
 * @LastEditors: NICOLA 2841208085@qq.com
 * @LastEditTime: 2025-10-17 00:22:08
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

## 内网穿透配置

如果您希望外部网络能够访问到局域网内的FastAPI应用，可以使用以下几种内网穿透方案：

### 方案1：使用pyngrok

1. 安装pyngrok：
```bash
pip install pyngrok
```

2. **获取ngrok认证令牌**：
   - 访问 https://dashboard.ngrok.com/signup 注册一个免费账户
   - 登录后，访问 https://dashboard.ngrok.com/get-started/your-authtoken 获取您的authtoken

3. **配置authtoken**：
   - 方式一：通过命令行设置（推荐）：
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```
   - 方式二：修改app/tunnel.py文件，添加authtoken配置：
   ```python
   from pyngrok import conf
   conf.get_default().auth_token = "YOUR_AUTHTOKEN"
   ```

4. 运行tunnel.py脚本：
```bash
cd app
python tunnel.py
```

5. 脚本会自动启动FastAPI应用并创建ngrok隧道，控制台会显示类似这样的输出：
```
* Serving FastAPI app 'main' (lazy loading)
* Environment: production
* Debug mode: off
* Running on http://127.0.0.1:8000 (Press CTRL+C to quit)
* ngrok tunnel "http://<random>.ngrok.io" -> "http://127.0.0.1:8000"
```

6. 使用显示的ngrok URL (格式为 http://<random>.ngrok.io) 从外部访问您的应用。

**注意事项：**
- 免费版ngrok的URL会在每次重启时随机变化
- 免费版有流量限制
- 确保您的防火墙允许8000端口的本地连接
- 必须配置authtoken才能使用ngrok服务

### 方案2：使用ngrok客户端

1. 下载并安装ngrok客户端：https://ngrok.com/download

2. 注册账号并获取auth token

3. 在命令行中运行：
```bash
ngrok http 8000
```

4. 查看控制台输出的公网URL

### 方案3：使用frp

1. 下载frp：https://github.com/fatedier/frp/releases

2. 配置frpc.ini文件：
```ini
[common]
server_addr = 你的服务器IP
server_port = 7000

[web]
type = http
local_port = 8000
custom_domains = 你的域名
```

3. 运行frp客户端：
```bash
./frpc -c frpc.ini
```

## 注意事项

- 内网穿透会使你的本地服务暴露到公网，请确保做好安全防护
- 免费的内网穿透服务通常有流量和连接数限制
- 生产环境建议使用固定公网IP或云服务器部署

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