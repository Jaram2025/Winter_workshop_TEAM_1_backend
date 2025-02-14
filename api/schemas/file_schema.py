from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import os


class FileBase(BaseModel):
    id: str = Field(..., example="test-123-2")
    name: str = Field(..., example="document.pdf")
    path: str = Field(..., example="/documents/work")
    size: int = Field(..., ge=0, example=1024, description="파일 크기(bytes)")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v):
        if ".." in v or "//" in v:
            raise ValueError("잘못된 경로입니다")
        return os.path.normpath(v)


class FileResponse(FileBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "document.pdf",
                "path": "/documents/work/document.pdf",
                "size": 1024,
                "created_at": "2024-03-20T10:00:00Z",
                "updated_at": "2024-03-20T10:00:00Z",
            }
        }


class FileList(BaseModel):
    items: list[FileResponse]
    total: int = Field(..., ge=0)
