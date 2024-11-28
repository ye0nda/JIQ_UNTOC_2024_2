from sqlalchemy.orm import Session
from .file_schema import FileCreate
from models import File
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

def create_file(db: Session, file: FileCreate):
    db_file = File(file_name=file.file_name)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def delete_file(db: Session, file_id: int):
    file = db.query(File).filter(File.file_id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found.")
    db.delete(file)
    db.commit()
    return {"detail": f"File has been deleted."}