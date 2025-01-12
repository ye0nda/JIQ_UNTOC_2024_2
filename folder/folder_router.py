from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_folderdb
from folder.folder_crud import create_folder, get_folders_by_user, delete_folder
from folder.folder_schema import FolderCreate, Folder
from typing import List

router = APIRouter(prefix="/folder", tags=["folder"])

@router.post("/folder/")
def create_new_folder(folder: FolderCreate, db: Session = Depends(get_folderdb)):
    new_folder = Folder(folder_name=folder.folder_name)  # 필드 이름 맞춤
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return new_folder

@router.get("/", response_model=List[Folder])
async def get_user_folders(user_id: int, db: Session = Depends(get_folderdb)):
    return get_folders_by_user(db, user_id)

@router.delete("/{folder_id}")
async def delete_user_folder(folder_id: int, user_id: int, db: Session = Depends(get_folderdb)):
    result = delete_folder(db, folder_id, user_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
