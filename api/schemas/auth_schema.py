from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: str = Field(..., max_length=200)
    first_name: str = Field(..., max_length=200)
    last_name: str = Field(..., max_length=200)


class UserCreate(UserBase):
    id: str
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: str
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    id: str
    password: str


class ErrorResponse(BaseModel):
    detail: str
    code: str = Field(..., description="에러 코드")
