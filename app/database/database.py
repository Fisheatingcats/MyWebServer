# 数据库连接与管理模块

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库URL配置
# 示例使用SQLite数据库，实际项目中可以替换为PostgreSQL、MySQL等
SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi_app.db"

# 创建数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """
    获取数据库会话依赖项
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()