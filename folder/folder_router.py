from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_folderdb
from folder.folder_crud import create_folder
from folder.folder_schema import FolderCreate, Folder
from typing import List

router = APIRouter(prefix="/folder", tags=["folder"])

@router.post("/create", response_model=Folder)
def create_new_folder(folder: FolderCreate, db: Session = Depends(get_folderdb)):
    try:
        new_folder = create_folder(db, folder.folder_name)
        return new_folder
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating folder: {str(e)}")
