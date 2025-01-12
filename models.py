from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import FolderBase, QuizBase, RetryBase
from datetime import datetime

# Retry 테이블
class Retry(RetryBase):
    __tablename__ = "retry_attempts"
    retry_id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer)
    is_correct = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)

# Folder 테이블
class Folder(FolderBase):
    __tablename__ = "folder"
    folder_id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String(255), nullable=False)

# Quiz 테이블
class Quiz(QuizBase):
    __tablename__ = "quizzes"
    quiz_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # autoincrement 추가
    quiz_number = Column(Integer, nullable=False)
    quiz_question = Column(String(255), nullable=False)
    quiz_answer = Column(String(255), nullable=False)
    quiz_type = Column(String(50), nullable=False)
    folder_id = Column(Integer, nullable=True)  # folder_id도 수정 필요