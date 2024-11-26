from pydantic import BaseModel

class FileCreate(BaseModel):
    file_name: str

class FileResponse(BaseModel):
    file_id: int
    file_name: str