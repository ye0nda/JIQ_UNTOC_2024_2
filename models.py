from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import FolderBase, FileBase, UserBase, QuizBase, RetryBase
import datetime

# Folder 테이블
class Folder(FolderBase):
    __tablename__ = "folder"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # VARCHAR(255)로 길이 지정

# File 테이블
class File(FileBase):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # VARCHAR(255)로 길이 지정

# User 테이블
class User(UserBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)  # VARCHAR(255)
    email = Column(String(255), unique=True, nullable=False)  # VARCHAR(255)
    hashed_password = Column(String(255), nullable=False)  # VARCHAR(255)
    retry_attempts = relationship("RetryAttempt", back_populates="user")

class Quiz(QuizBase):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(255), nullable=False)  # VARCHAR(255)
    answer = Column(String(255), nullable=False)  # VARCHAR(255)
    retry_attempts = relationship("RetryAttempt", back_populates="quiz")

class Retry(RetryBase):
    __tablename__ = "retry_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    is_correct = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="retries")
    quiz = relationship("Quiz", back_populates="retries")
