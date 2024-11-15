from pydantic import BaseModel

class FolderCreate(BaseModel):
    folder_name: str
    parent_dir: str = "."

class FolderResponse(BaseModel):
    folder_id: int
    folder_name: str
    parent_dir: str
    path: str