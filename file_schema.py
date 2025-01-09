from pydantic import BaseModel

class FileBase(BaseModel):
    file_name: str
    user_id: int

class FileCreate(FileBase):
    pass

class File(FileBase):
    file_id: int

    class Config:
        orm_mode = True
