from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . .database import folder_SessionLocal
from folder.folder_crud import create_folder
from folder.folder_schema import FolderCreate, FolderResponse
from models import Folder

router = APIRouter()

def get_db():
    db = folder_SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create-folder/", response_model=FolderResponse)
async def create_folder_endpoint(folder_data: FolderCreate, db: Session = Depends(get_db)):

    existing_folder = db.query(Folder).filter(Folder.folder_name == folder_data.folder_name).first()
    if existing_folder:
        raise HTTPException(status_code=400, detail="Folder already exists.")

    return create_folder(db=db, folder_data=folder_data)