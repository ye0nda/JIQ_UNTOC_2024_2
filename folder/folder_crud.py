from sqlalchemy.orm import Session
from models import Folder
from folder.folder_schema import FolderCreate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

def create_folder(db: Session, folder_data: FolderCreate):
    db_folder = Folder(
        folder_name=folder_data.folder_name,
    )
    try:
        db.add(db_folder)
        db.commit()
        db.refresh(db_folder)
        return db_folder
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Folder already exists.")

def delete_folder(db: Session, folder_name: str):
    folder = db.query(Folder).filter(Folder.folder_name == folder_name).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found.")
    db.delete(folder)
    db.commit()
    return {"detail": f"Folder '{folder_name}' has been deleted."}