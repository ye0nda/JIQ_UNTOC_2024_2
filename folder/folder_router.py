from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_folderdb
from folder.folder_crud import create_folder, delete_folder
from folder.folder_schema import FolderCreate, FolderResponse
from models import Folder

router = APIRouter()

@router.post("/create-folder/", response_model=FolderResponse)
async def create_folder_endpoint(
    folder_data: FolderCreate, db: Session = Depends(get_folderdb)
):
    existing_folder = db.query(Folder).filter(Folder.folder_name == folder_data.folder_name).first()
    if existing_folder:
        raise HTTPException(status_code=400, detail="Folder already exists.")

    return create_folder(db=db, folder_data=folder_data)

@router.delete("/delete-folder/{folder_name}")
async def delete_folder_endpoint(folder_name: str, db: Session = Depends(get_folderdb)):
    return delete_folder(db=db, folder_name=folder_name)