from sqlalchemy.orm import Session
from models import Folder

def create_folder(db: Session, folder_name: str, user_id: int):
    new_folder = Folder(folder_name=folder_name, user_id=user_id)
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return new_folder

def get_folders_by_user(db: Session, user_id: int):
    return db.query(Folder).filter(Folder.user_id == user_id).all()

def delete_folder(db: Session, folder_id: int, user_id: int):
    folder = db.query(Folder).filter(Folder.folder_id == folder_id, Folder.user_id == user_id).first()
    if folder:
        db.delete(folder)
        db.commit()
        return {"message": "Folder deleted successfully"}
    return {"error": "Folder not found or not authorized"}
