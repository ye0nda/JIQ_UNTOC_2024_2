from pydantic import BaseModel

class FolderBase(BaseModel):
    folder_name: str
    user_id: int

class FolderCreate(FolderBase):
    pass

class Folder(FolderBase):
    folder_id: int

    class Config:
        orm_mode = True
