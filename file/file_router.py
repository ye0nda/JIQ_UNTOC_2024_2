from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .file_crud import create_file, get_file, get_files
from .file_schema import FileCreate, FileResponse
from database import get_filedb

# 라우터 인스턴스 생성
router = APIRouter()

# 파일 생성 API
@router.post("/", response_model=FileResponse)
def upload_file(file: FileCreate, db: Session = Depends(get_filedb)):
    """
    파일 정보를 데이터베이스에 저장합니다.
    """
    return create_file(db=db, file=file)

# 특정 파일 조회 API
@router.get("/{file_id}", response_model=FileResponse)
def read_file(file_id: int, db: Session = Depends(get_filedb)):
    """
    주어진 file_id에 해당하는 파일 정보를 반환합니다.
    """
    db_file = get_file(db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

# 여러 파일 조회 API
@router.get("/", response_model=list[FileResponse])
def read_files(skip: int = 0, limit: int = 10, db: Session = Depends(get_filedb)):
    """
    저장된 파일 목록을 반환합니다.
    """
    return get_files(db, skip=skip, limit=limit)