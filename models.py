from sqlalchemy import Column, Integer, String, JSON
from database import folder_Base

class Folder(folder_Base):
    __tablename__ = "folder"

    folder_id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String(255), unique=True, index=True, nullable=False)

class Quiz(folder_Base):
    __tablename__ = "quiz"

    quiz_id = Column(Integer, primary_key=True, index=True)
    question = Column(String(255), nullable=False)
    answer = Column(String(255), nullable=False)
    options = Column(JSON, nullable=False)
    category = Column(String(255), nullable=True)