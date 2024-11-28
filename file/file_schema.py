from pydantic import BaseModel
from typing import Optional

class FileCreate(BaseModel):
    file_name: str

class FileResponse(BaseModel):
    file_id: int
    file_name: str

class FileUploadResponse(BaseModel):
    filename: str
    message: str
    content: Optional[str]