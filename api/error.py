from __future__ import annotations

import enum
import logging
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, field_serializer

logger = logging.getLogger(__name__)


@dataclass
class ManagedError(Exception):
    code: AuthErrorCodeEnum | LogicErrorCodeEnum
    detail: dict[str, Any] | None = None


class AuthError(ManagedError):
    code: AuthErrorCodeEnum


class LogicError(ManagedError):
    code: LogicErrorCodeEnum


class AuthErrorCodeEnum(enum.Enum):
    NO_PERMISSION = "No permission"
    EXPIRED_TOKEN = "Expired token"  # noqa: S105
    TOKEN_DECODE_FAILED = "Token decode failed"  # noqa: S105
    INVALID_TOKEN = "Invalid token"  # noqa: S105


class LogicErrorCodeEnum(enum.Enum):
    NON_EXISTENT_OBJECT = "Non existent object"
    ALREADY_EXISTENT_OBJECT = "Already existent object"
    FILE_UPLOAD_ERROR = "File upload error"
    FILE_DELETE_ERROR = "File delete error"
    INACTIVE_USER = "Inactive user"
    OCR_API_ERROR = "OCR API error"


class AuthErrorResponse(BaseModel):
    code: AuthErrorCodeEnum
    message: str
    detail: dict[str, Any] | None = None

    @staticmethod
    def from_exc(exc: AuthError) -> AuthErrorResponse:
        return AuthErrorResponse(
            code=exc.code,
            message=exc.code.value,
            detail=exc.detail,
        )

    @field_serializer("code")
    def serialize_code(self, code: AuthErrorCodeEnum) -> str:
        return code.name


class LogicErrorResponse(BaseModel):
    code: LogicErrorCodeEnum
    message: str
    detail: dict[str, Any] | None = None

    @staticmethod
    def from_exc(exc: LogicError) -> LogicErrorResponse:
        return LogicErrorResponse(
            code=exc.code,
            message=exc.code.value,
            detail=exc.detail,
        )

    @field_serializer("code")
    def serialize_code(self, code: LogicErrorCodeEnum) -> str:
        return code.name
