# 用户Pydantic数据模式

from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    """
    用户基础数据模式
    """
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserCreate(UserBase):
    """
    用户创建数据模式
    """
    password: str

class UserUpdate(UserBase):
    """
    用户更新数据模式
    """
    password: Optional[str] = None

class UserInDB(UserBase):
    """
    用户数据库数据模式
    """
    id: int
    hashed_password: str

    class Config:
        orm_mode = True

class UserResponse(UserBase):
    """
    用户响应数据模式
    """
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    """
    JWT Token数据模式
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    JWT Token数据模式
    """
    username: Optional[str] = None