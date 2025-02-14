from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..schemas.auth_schema import UserCreate, UserResponse, UserLogin, TokenResponse
from ..crud import auth_crud
from ..database import get_db
from ..util import (
    validate_hashed_password,
    generate_token,
    generate_hashed_password,
    user_auth_required,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """사용자 로그인"""
    user = auth_crud.get_user(db, user_id=user_login.id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    if not await validate_hashed_password(user_login.password, user.password):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")

    return TokenResponse(
        access_token=await generate_token(user.id), token_type="bearer"
    )


@router.post("/signup", response_model=TokenResponse)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """새로운 사용자 등록"""
    # 이미 존재하는 사용자 확인
    if auth_crud.get_user(db, user_id=user.id):
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자 ID입니다")

    if auth_crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다")

    # 비밀번호 해시화
    hashed_password = await generate_hashed_password(user.password)

    # 사용자 생성
    db_user = auth_crud.create_user(
        db=db,
        user_id=user.id,
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    return TokenResponse(
        access_token=await generate_token(db_user.id), token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: Session = Depends(get_db), current_user_id: str = Depends(user_auth_required)
):
    """현재 로그인한 사용자의 정보를 반환"""
    user = auth_crud.get_user(db, user_id=current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user


@router.get("/users", response_model=List[UserResponse])
async def get_users(limit: int = 10, db: Session = Depends(get_db)):
    """사용자 목록을 반환"""
    users = auth_crud.get_users(db, limit=limit)
    return users
