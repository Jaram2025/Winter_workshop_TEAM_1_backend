from __future__ import annotations

import asyncio
import binascii
import dataclasses
import datetime
import hashlib
import os
import string
from random import SystemRandom
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.sql import expression as sql_exp

from .models import User
from .database import get_db as get_db_session
from .settings import settings
from .error import AuthError, AuthErrorCodeEnum

_PBKDF2_SALT_LENGTH = 16
_PBKDF2_HASH_NAME = "SHA256"
_PBKDF2_ITERATIONS = 100000

_USER_LOGIN_TTL = 12  # 12 hours

# JWT 설정
SECRET_KEY = "your-secret-key"  # 실제로는 환경변수에서 가져와야 함
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


@dataclasses.dataclass
class AuthUtilError(Exception):
    code: str
    message: str
    detail: dict[str, Any] | None = None


def generate_random_token(length: int) -> str:
    return "".join(
        SystemRandom().choices(
            population=string.ascii_uppercase + string.digits,
            k=length,
        ),
    )


async def generate_hashed_password(password: str) -> str:
    def _inner() -> str:  # noqa: WPS430
        pbkdf2_salt = os.urandom(_PBKDF2_SALT_LENGTH)
        pw_hash = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH_NAME,
            password.encode(),
            pbkdf2_salt,
            _PBKDF2_ITERATIONS,
        )

        return (
            binascii.hexlify(pbkdf2_salt).decode()
            + ":"
            + binascii.hexlify(pw_hash).decode()
        )

    return await asyncio.get_event_loop().run_in_executor(None, _inner)


async def validate_hashed_password(password: str, hashed_password: str) -> bool:
    def _inner() -> bool:  # noqa: WPS430
        pbkdf2_salt_hex, pw_hash_hex = hashed_password.split(":")

        pw_challenge = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH_NAME,
            password.encode(),
            binascii.unhexlify(pbkdf2_salt_hex),
            _PBKDF2_ITERATIONS,
        )

        return pw_challenge == binascii.unhexlify(pw_hash_hex)

    return await asyncio.get_event_loop().run_in_executor(None, _inner)


async def generate_token(user_id: str) -> str:
    """JWT 토큰을 생성합니다."""
    expires_delta = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.datetime.now(datetime.UTC) + expires_delta

    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def user_auth_required(token: str = Depends(oauth2_scheme)) -> str:
    """
    토큰을 검증하고 사용자 ID를 반환합니다.
    이 함수는 보호된 엔드포인트에서 현재 사용자를 확인하는데 사용됩니다.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")


async def admin_auth_required(
    db_session: Session = Depends(get_db_session),
    user_id: int = Depends(user_auth_required),
) -> int:
    is_admin = await db_session.scalar(
        sql_exp.exists().where(User.id == user_id).where(User.is_admin).select(),
    )

    if not is_admin:
        raise AuthError(code=AuthErrorCodeEnum.NO_PERMISSION)

    return user_id
