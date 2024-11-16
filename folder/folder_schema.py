from pydantic import BaseModel

class FolderCreate(BaseModel):
    folder_name: str

class FolderResponse(BaseModel):
    folder_id: int
    folder_name: str