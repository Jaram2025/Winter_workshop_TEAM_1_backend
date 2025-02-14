from fastapi import APIRouter, UploadFile, Query, HTTPException, Depends
from fastapi.responses import FileResponse as FastAPIFileResponse

import os, uuid
from datetime import datetime
from sqlalchemy.orm import Session

from ..crud import file_crud

from ..schemas.file_schema import FileResponse, FileList
from .. import models
from ..database import get_db

router = APIRouter(prefix="/api/drive", tags=["drive"])

UPLOAD_DIR = "/uploads"  # 기본 업로드 디렉토리


@router.post("/upload", response_model=FileResponse)
async def create_file(file_body: UploadFile, db: Session = Depends(get_db)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_extension = os.path.splitext(file_body.filename)[1]
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        content = await file_body.read()
        with open(file_path, "wb") as fp:
            fp.write(content)

        # DB에 메타데이터 저장
        file_model = models.FileModel(
            id=file_id, name=safe_filename, path=file_path, size=len(content)
        )
        db.add(file_model)
        db.commit()
        db.refresh(file_model)

        # FileResponse 스키마로 응답 생성
        return FileResponse(
            id=file_model.id,
            name=file_model.name,
            path=file_model.path,
            size=file_model.size,
            created_at=file_model.created_at,
            updated_at=file_model.created_at,  # created_at을 updated_at으로도 사용
        )

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")


@router.get("/file/{safe_filename}")
async def download_file(safe_filename: str):
    file_path = os.path.join(UPLOAD_DIR, f"{safe_filename}")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

    return FastAPIFileResponse(
        file_path,
        filename=os.path.basename(file_path),
        media_type="application/octet-stream",
    )


@router.delete("/file/{safe_filename}", response_model=None, status_code=204)
async def delete_file(safe_filename: str, db: Session = Depends(get_db)):
    file_id = os.path.splitext(safe_filename)[0]
    file = file_crud.get_file(db, file_id=file_id)
    if file is None:  # DB에서 파일을 찾지 못한 경우
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

    file_path = os.path.join(UPLOAD_DIR, f"{safe_filename}")
    if not os.path.exists(file_path):  # 실제 파일이 없는 경우
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

    try:
        # 파일 시스템에서 삭제
        os.remove(file_path)
        # DB에서 삭제
        file_crud.delete_file(db, db_file=file)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 삭제 실패: {str(e)}")


@router.get("/file", response_model=FileList)
async def list_files(
    path: str = Query(default="/", description="조회할 경로")
) -> FileList:
    """파일 목록을 반환합니다."""
    target_path = os.path.join(UPLOAD_DIR, path.lstrip("/"))

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="경로를 찾을 수 없습니다")

    files = []
    total = 0

    for entry in os.scandir(target_path):
        stats = entry.stat()
        files.append(
            FileResponse(
                id=str(uuid.uuid4()),
                name=entry.name,
                path=os.path.join(path, entry.name),
                size=stats.st_size,
                type="directory" if entry.is_dir() else "file",
                created_at=datetime.fromtimestamp(stats.st_ctime),
                updated_at=datetime.fromtimestamp(stats.st_mtime),
            )
        )
        total += 1

    return FileList(items=files, total=total)
