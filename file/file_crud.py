from sqlalchemy.orm import Session
from .file_schema import FileCreate
from models import File

# 파일 생성 함수
def create_file(db: Session, file: FileCreate):
    db_file = File(file_name=file.file_name)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

# 특정 파일 가져오기
def get_file(db: Session, file_id: int):
    return db.query(File).filter(File.file_id == file_id).first()

# 파일 목록 가져오기
def get_files(db: Session, skip: int = 0, limit: int = 10):
    return db.query(File).offset(skip).limit(limit).all()