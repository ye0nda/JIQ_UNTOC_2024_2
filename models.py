from sqlalchemy import Column, Integer, String, JSON, Text
from database import FolderBase, FileBase, QuizBase

class Folder(FolderBase):
    __tablename__ = "folder"

    folder_id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String(255), unique=True, index=True, nullable=False)

class File(FileBase):
    __tablename__ = "file"

    file_id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)

class Quiz(QuizBase):
    __tablename__ = "quiz"

    quiz_id = Column(Integer, primary_key=True, index=True)
    quiz_number = Column(Integer, nullable=False)
    quiz_question = Column(Text, nullable=False)
    quiz_answer = Column(Text, nullable=False)
    quiz_type = Column(String(50), nullable=False)