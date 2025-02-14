from sqlalchemy.orm import Session
from .. import models
from datetime import datetime

# 기존에 생성한 모델과 스키마 불러오기
from .. import models
from ..schemas.file_schema import FileResponse


def get_file(db: Session, file_id: str):
    return db.query(models.FileModel).filter(models.FileModel.id == file_id).first()


def get_file_by_name(db: Session, file_name: str):
    return db.query(models.FileModel).filter(models.FileModel.name == file_name).first()


def get_files(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.FileModel).offset(skip).limit(limit).all()


def create_file(db: Session, file_id: str, file_name: str, file_path: str, file_size: int):
    db_file = models.FileModel(
        id=file_id,
        name=file_name,
        path=file_path,
        size=file_size,
        created_at=datetime.now(),
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def delete_file(db: Session, db_file: models.FileModel) -> None:
    db.delete(db_file)
    db.commit()
