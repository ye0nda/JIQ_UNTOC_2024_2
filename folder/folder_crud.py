from sqlalchemy.orm import Session
from models import Folder
from folder.folder_schema import FolderCreate

def create_folder(db: Session, folder_data: FolderCreate):
    folder_path = f"{folder_data.parent_dir}/{folder_data.folder_name}"

    db_folder = Folder(folder_name=folder_data.folder_name, parent_dir=folder_data.parent_dir, path=folder_path)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)

    return db_folder