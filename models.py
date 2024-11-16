from sqlalchemy import Column, Integer, String
from database import folder_Base

class Folder(folder_Base):
    __tablename__ = "folder"

    folder_id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String(255), unique=True, index=True, nullable=False)