from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import FolderBase, FileBase, UserBase, QuizBase, RetryBase
from datetime import datetime

# Retry 테이블
class Retry(RetryBase):
    __tablename__ = "retry_attempts"
    retry_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    quiz_id = Column(Integer)
    is_correct = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)

# Folder 테이블
class Folder(FolderBase):
    __tablename__ = "folder"
    folder_id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String(255), nullable=False)

# File 테이블
class File(FileBase):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)  # VARCHAR(255)로 길이 지정

# User 테이블
class User(UserBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)  # VARCHAR(255)
    email = Column(String(255), unique=True, nullable=False)  # VARCHAR(255)
    hashed_password = Column(String(255), nullable=False)  # VARCHAR(255)

# Quiz 테이블
class Quiz(QuizBase):
    __tablename__ = "quizzes"
    quiz_id = Column(Integer, primary_key=True, index=True)
    quiz_number = Column(Integer, nullable=False)  # 새 필드 추가
    quiz_question = Column(String(255), nullable=False)
    quiz_answer = Column(String(255), nullable=False)
    quiz_type = Column(String(50), nullable=False)
    folder_id = Column(Integer, primary_key=True, index=True)