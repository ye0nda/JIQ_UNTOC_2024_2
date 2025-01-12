from sqlalchemy.orm import Session
from models import Folder

def create_folder(db: Session, folder_name: str):
    new_folder = Folder(folder_name=folder_name)
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return new_folder