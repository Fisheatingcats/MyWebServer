# 用户数据模型

from sqlalchemy import Column, Integer, String, Boolean
from app.database.database import Base

class User(Base):
    """
    用户数据模型
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)

    def to_dict(self):
        """
        将用户对象转换为字典
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "disabled": self.disabled
        }