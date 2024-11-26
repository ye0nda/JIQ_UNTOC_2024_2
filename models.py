from sqlalchemy import Column, Integer, String, JSON
from database import FolderBase
from database import QuizBase
from database import FileBase

class Folder(FolderBase):
    __tablename__ = "folder"

    folder_id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String(255), unique=True, index=True, nullable=False)

class Quiz(QuizBase):
    __tablename__ = "quiz"

    quiz_id = Column(Integer, primary_key=True, index=True)
    question = Column(String(255), nullable=False)
    answer = Column(String(255), nullable=False)
    options = Column(JSON, nullable=False)
    category = Column(String(255), nullable=True)

class File(FileBase):
    __tablename__ = "file"

    file_id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)