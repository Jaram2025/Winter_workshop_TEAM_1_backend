from sqlalchemy.orm import Session
from .. import models
from ..schemas import auth_schema
from datetime import datetime


def get_user(db: Session, user_id: str):
    """ID로 사용자를 조회합니다."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """이메일로 사용자를 조회합니다."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    """사용자 목록을 조회합니다."""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(
    db: Session,
    user_id: str,
    email: str,
    hashed_password: str,
    first_name: str,
    last_name: str,
):
    """새로운 사용자를 생성합니다."""
    db_user = models.User(
        id=user_id,
        email=email,
        password=hashed_password,
        first_name=first_name,
        last_name=last_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session,
    db_user: models.User,
    email: str = None,
    first_name: str = None,
    last_name: str = None,
) -> models.User:
    """사용자 정보를 업데이트합니다."""
    if email is not None:
        db_user.email = email
    if first_name is not None:
        db_user.first_name = first_name
    if last_name is not None:
        db_user.last_name = last_name

    db.commit()
    db.refresh(db_user)
    return db_user
